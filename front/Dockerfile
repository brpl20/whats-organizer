# ---- Build stage ----
FROM node:20-slim AS builder

WORKDIR /app
COPY package.json yarn.lock ./
RUN corepack enable && yarn install --immutable

COPY . .

ARG PUBLIC_API_URL=http://localhost:3000
ARG PUBLIC_FRONT_URL=http://localhost:3001
ARG PUBLIC_NODE_ENV=development
ARG PUBLIC_MAX_UPLOAD_MB=100

ENV PUBLIC_API_URL=${PUBLIC_API_URL}
ENV PUBLIC_FRONT_URL=${PUBLIC_FRONT_URL}
ENV PUBLIC_NODE_ENV=${PUBLIC_NODE_ENV}
ENV PUBLIC_MAX_UPLOAD_MB=${PUBLIC_MAX_UPLOAD_MB}

RUN yarn build

# ---- Runtime stage ----
FROM node:20-slim

WORKDIR /app
COPY --from=builder /app/build ./build
COPY --from=builder /app/package.json .
COPY --from=builder /app/node_modules ./node_modules

ENV PORT=3001
EXPOSE 3001

CMD ["node", "build"]
