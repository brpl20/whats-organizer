# fix: Backend deployment breakage after WeasyPrint migration

## Overview

After merging PR #1 (`feat/weasyprint-pdf`), the backend stopped working in production. The deployment pipeline completes without visible errors, but the Flask application fails to start. The user observes CORS-like errors in the browser, but the root cause is the backend being completely down.

**Three cascading bugs** were introduced (or surfaced) by the merge, and **two have already been fixed** in subsequent commits. One significant bug remains, plus several hardening items.

## Problem Statement

### Timeline

| Action Run | Commit | Status | Notes |
|---|---|---|---|
| [21460374609](https://github.com/brpl20/whats-organizer/actions/runs/21460374609) | `8b857a2a` | OK | "test deploy" -- last known good state |
| [21531809256](https://github.com/brpl20/whats-organizer/actions/runs/21531809256) | `672187c7` | BROKEN | Merge PR #1 (WeasyPrint migration) |
| [21544531486](https://github.com/brpl20/whats-organizer/actions/runs/21544531486) | `7c80be80` or `be0fe475` | BROKEN? | Fix attempts |
| [21544617226](https://github.com/brpl20/whats-organizer/actions/runs/21544617226) | `be0fe475` | SHOULD WORK | Final fix for venv + env var |

### Root Causes (3 bugs)

#### BUG 1 (FIXED in `7c80be80`): `int("", base=10)` crash at startup

- **File**: `back/app.py:42`
- When `PUBLIC_MAX_UPLOAD_MB` env var is missing, `int("" or "", base=10)` raises `ValueError`, crashing Flask on startup
- **Fix applied**: Changed to `int(max_upload_mb_env or 100) * MEGABYTE`

#### BUG 2 (FIXED in `be0fe475`): Broken pip / venv not recreated

- **File**: `.github/workflows/back.yml`
- If `.venv` directory existed but pip was corrupted, the deploy script skipped venv creation
- `pip3 install -r requirements.txt` silently failed (no `set -e` in heredoc), so `weasyprint` was never installed
- Flask crashed on `import weasyprint`
- **Fix applied**: Added pip health check + `set -e` inside heredoc

#### BUG 3 (NOT FIXED -- still present): Nginx only generates 1 upstream server

- **File**: `infra/generate_nginx_conf.sh:28`
- The while loop says `while [ "$p" -le "${FLASK_PORT_START}" ]` but should be `while [ "$p" -le "${FLASK_PORT_END}" ]`
- This means only **1 backend instance** is load-balanced even though 8 instances run (ports 3000-3007)
- All traffic hits port 3000; ports 3001-3007 receive zero traffic

### Why CORS appeared broken

CORS headers are set by Flask (`flask-cors`), not nginx. When the Flask backend is down, nginx returns `502 Bad Gateway` **without CORS headers**. The browser reports this as a CORS error, masking the real issue (backend crash).

## Proposed Solution

### Phase 1: Fix the remaining nginx upstream bug

Fix the off-by-one in `infra/generate_nginx_conf.sh:28`:

```bash
# BEFORE (broken) -- only generates 1 server
while [ "$p" -le "${FLASK_PORT_START}" ]; do

# AFTER (correct) -- generates servers for all ports
while [ "$p" -le "${FLASK_PORT_END}" ]; do
```

### Phase 2: Add nginx-level CORS fallback headers

When the backend is down, nginx should still return basic CORS headers so the browser shows the real error (502) instead of a misleading CORS error.

**File**: `infra/nginx.conf.tpl` -- add to the API server block:

```nginx
# Fallback CORS headers for when backend is down
add_header 'Access-Control-Allow-Origin' '$http_origin' always;
add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS' always;
add_header 'Access-Control-Allow-Headers' 'Content-Type' always;
```

The `always` directive ensures headers are sent even on error responses (502, 503).

### Phase 3: Add backend health check to deploy script

After restarting services in `.github/workflows/back.yml`, verify at least one backend instance is actually healthy:

```bash
# After systemctl restart, wait and check health
sleep 5
for p in $(seq ${FLASK_PORT_START} ${FLASK_PORT_END}); do
  if curl -sf "http://localhost:${p}/health" >/dev/null 2>&1; then
    echo "Backend on port ${p} is healthy"
    HEALTHY=true
    break
  fi
done
if [ "${HEALTHY:-false}" != "true" ]; then
  echo "WARNING: No backend instance is responding to health checks!"
  journalctl -u "back@${FLASK_PORT_START}.service" --no-pager -n 50
  export ERROR=true
fi
```

### Phase 4: Harden deploy script error handling

Currently `.github/workflows/back.yml` uses `export ERROR=true` but still continues. Several improvements:

1. Log `journalctl` output for failed services into the Action output
2. Report which specific service instances failed
3. Add the health check from Phase 3

## Acceptance Criteria

- [ ] `infra/generate_nginx_conf.sh:28` uses `FLASK_PORT_END` instead of `FLASK_PORT_START`
- [ ] Nginx config template includes fallback CORS headers with `always` directive
- [ ] Deploy script checks at least one backend health endpoint after restart
- [ ] Deploy script logs service journal on failure for debugging
- [ ] Verify the two previous fixes are still in place:
  - `back/app.py:42` -- `int(max_upload_mb_env or 100)` (no `base=10`)
  - `.github/workflows/back.yml` -- pip health check before venv activation

## Files to Modify

| File | Change |
|---|---|
| `infra/generate_nginx_conf.sh:28` | Fix `FLASK_PORT_START` -> `FLASK_PORT_END` |
| `infra/nginx.conf.tpl` | Add fallback CORS headers with `always` |
| `.github/workflows/back.yml` | Add post-restart health check + journalctl logging |

## Dependencies & Risks

- **Low risk**: The nginx upstream fix is a one-character change but affects load balancing. After deploy, verify all 8 backend ports appear in the generated nginx config.
- **Medium risk**: The `always` CORS headers in nginx could conflict with Flask's CORS headers when the backend IS running (duplicate headers). Test that browsers handle this correctly, or use `proxy_hide_header` to strip Flask's CORS headers and let nginx handle them exclusively.
- **No risk**: Health check and logging are additive -- they don't change existing behavior.

## Verification Plan

After deploying the fixes:

1. SSH into the server and check the generated nginx config: `cat /etc/nginx/nginx.conf | grep -A2 "upstream backend"`
   - Should show 8 servers (ports 3000-3007), not just 1
2. Check all backend instances: `for p in $(seq 3000 3007); do curl -s http://localhost:$p/health; done`
3. Check nginx is proxying to all instances: `journalctl -u nginx --no-pager -n 20`
4. Test CORS from browser dev tools: verify `Access-Control-Allow-Origin` header is present on responses

## References

### Commits (chronological)

| SHA | Description |
|---|---|
| `8b857a2a` | Last known good deploy ("test deploy") |
| `68c769c4` | feat(pdf): replace Playwright with WeasyPrint |
| `01fdf518` | "general fixes" -- bumped weasyprint to 68.0, env var renames |
| `54b85c08` | fix(deploy): add WeasyPrint system deps |
| `672187c7` | Merge PR #1 -- this is where master broke |
| `faecdd6d` | fix(deploy): increase front SSH timeout to 30m |
| `7c80be80` | fix(back): default MAX_FORM_MEMORY_SIZE to 50MB |
| `be0fe475` | fix(deploy): recreate venv when pip is broken |

### Action Runs

- [21460374609](https://github.com/brpl20/whats-organizer/actions/runs/21460374609) -- OK (test deploy)
- [21531809256](https://github.com/brpl20/whats-organizer/actions/runs/21531809256) -- First broken run
- [21544531486](https://github.com/brpl20/whats-organizer/actions/runs/21544531486) -- Fix attempt
- [21544617226](https://github.com/brpl20/whats-organizer/actions/runs/21544617226) -- Should be fixed

### Related

- PR #1: `feat/weasyprint-pdf` -- the merge that triggered the cascade
- `REVIEW.md` -- 7 deferred review items from WeasyPrint migration
