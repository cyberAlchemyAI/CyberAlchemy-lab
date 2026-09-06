FROM node:26.8.1-alpine@sha256:2d984a15c9b54fd0aeb608b8e0d0d83529eb34d2966db27a1fb4f1edc3d298a3 AS build
WORKDIR /workspace/projects/domainspec-v2/impl
COPY toolchains/node-typescript/tsconfig /workspace/toolchains/node-typescript/tsconfig
COPY projects/domainspec-v2/impl/package.json ./package.json
COPY projects/domainspec-v2/impl/tsconfig.json ./tsconfig.json
RUN npm install --ignore-scripts --no-audit --no-fund
COPY projects/domainspec-v2/impl/operational-resilience ./operational-resilience
RUN npm exec -- tsc --project operational-resilience/body-war-canary-gateway.tsconfig.json --outDir /workspace/dist --noEmit false

FROM node:26.8.1-alpine@sha256:2d984a15c9b54fd0aeb608b8e0d0d83529eb34d2966db27a1fb4f1edc3d298a3 AS runtime
WORKDIR /app
ENV NODE_ENV=production
COPY --from=build /workspace/dist ./dist
RUN mkdir -p /run/orodi && chown node:node /run/orodi
USER node
EXPOSE 18080 18081 9464
CMD ["node", "dist/src/body-war-canary-gateway-entry.js"]
