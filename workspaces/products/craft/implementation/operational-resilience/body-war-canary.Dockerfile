FROM node:26.8.1-alpine@sha256:2d984a15c9b54fd0aeb608b8e0d0d83529eb34d2966db27a1fb4f1edc3d298a3 AS build
WORKDIR /workspace

RUN npm install --global pnpm@10.34.5
RUN printf 'packages:\n  - projects/auth-user-management\n  - projects/body-war/app\n' > pnpm-workspace.yaml

COPY projects/auth-user-management/package.json ./projects/auth-user-management/package.json
COPY projects/body-war/app/package.json ./projects/body-war/app/package.json
RUN pnpm install --no-frozen-lockfile

COPY toolchains/node-typescript/tsconfig ./toolchains/node-typescript/tsconfig
COPY projects/auth-user-management/src ./projects/auth-user-management/src
COPY projects/auth-user-management/drizzle ./projects/auth-user-management/drizzle
COPY projects/auth-user-management/tsconfig.json ./projects/auth-user-management/tsconfig.json
COPY projects/body-war/app/server.ts ./projects/body-war/app/server.ts
COPY projects/body-war/app/src ./projects/body-war/app/src
COPY projects/body-war/app/drizzle ./projects/body-war/app/drizzle
COPY projects/body-war/app/static ./projects/body-war/app/static
COPY projects/body-war/app/tsconfig.json ./projects/body-war/app/tsconfig.json
RUN pnpm --filter @domainspec/body-war-app build

FROM node:26.8.1-alpine@sha256:2d984a15c9b54fd0aeb608b8e0d0d83529eb34d2966db27a1fb4f1edc3d298a3 AS runtime
WORKDIR /workspace/projects/body-war/app
ENV NODE_ENV=production \
    BODY_WAR_HOST=0.0.0.0 \
    BODY_WAR_PORT=5174 \
    BODY_WAR_AUTH_BACKEND=memory \
    BODY_WAR_STRAVA_FAKE=1 \
    BODY_WAR_SECURE_COOKIES=0
COPY --from=build /workspace/node_modules /workspace/node_modules
COPY --from=build /workspace/projects/auth-user-management/package.json /workspace/projects/auth-user-management/package.json
COPY --from=build /workspace/projects/auth-user-management/node_modules /workspace/projects/auth-user-management/node_modules
COPY --from=build /workspace/projects/auth-user-management/dist /workspace/projects/auth-user-management/dist
COPY --from=build /workspace/projects/body-war/app/package.json ./package.json
COPY --from=build /workspace/projects/body-war/app/node_modules ./node_modules
COPY --from=build /workspace/projects/body-war/app/dist ./dist
COPY --from=build /workspace/projects/body-war/app/drizzle ./drizzle
COPY --from=build /workspace/projects/body-war/app/static ./static
RUN mkdir -p data && chown -R node:node /workspace/projects/body-war/app /workspace/projects/auth-user-management
USER node
EXPOSE 5174
CMD ["node", "dist/server.js"]
