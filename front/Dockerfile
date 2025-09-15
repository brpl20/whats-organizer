FROM node:21-alpine AS base
ENV PNPM_HOME="/pnpm"
ENV PATH="$PNPM_HOME:$PATH"
RUN corepack enable
USER node
WORKDIR /app

FROM base AS prod-deps
COPY --chown=node:node package.json .
COPY --chown=node:node package-lock.json .
COPY --chown=node:node pnpm-lock.yaml .
COPY --chown=node:node amplify.yml .
RUN --mount=type=cache,id=pnpm,target=/pnpm/store pnpm install --prod --frozen-lockfile

FROM base AS build
COPY --chown=node:node --from=prod-deps /app/node_modules /app/node_modules
COPY --chown=node:node package.json .
COPY --chown=node:node package-lock.json .
COPY --chown=node:node pnpm-lock.yaml .
COPY --chown=node:node amplify.yml .
RUN --mount=type=cache,id=pnpm,target=/pnpm/store pnpm install --frozen-lockfile
COPY --chown=node:node . .
RUN pnpm run build
RUN cp package.json build/

FROM node:21-alpine AS prod
RUN apk update && apk upgrade
USER node
ENV NODE_ENV="production"
WORKDIR /app
COPY --chown=node:node .env .
COPY --chown=node:node --from=build /app/build /app/build
COPY --chown=node:node --from=prod-deps /app/node_modules /app/node_modules
EXPOSE 8000
# --env-file from https://kit.svelte.dev/docs/adapter-node#environment-variables
CMD ["node", "--env-file=.env", "build/index"]
