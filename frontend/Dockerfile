FROM alpine:3.20 AS builder
WORKDIR /build

COPY frontend/index.html ./index.html
COPY frontend/styles.css ./styles.css
COPY frontend/app.js ./app.js

FROM nginxinc/nginx-unprivileged:1.27-alpine

COPY --from=builder /build/index.html /usr/share/nginx/html/index.html
COPY --from=builder /build/styles.css /usr/share/nginx/html/styles.css
COPY --from=builder /build/app.js /usr/share/nginx/html/app.js

EXPOSE 8080
