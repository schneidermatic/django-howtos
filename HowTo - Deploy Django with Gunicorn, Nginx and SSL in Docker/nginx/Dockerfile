FROM nginx:1.30-alpine

# openssl creates the self-signed certificate on the first start
RUN apk add --no-cache openssl

COPY conf.d/default.conf /etc/nginx/conf.d/default.conf

# The nginx image runs all executable scripts in /docker-entrypoint.d/ before Nginx starts
COPY 40-create-self-signed-cert.sh /docker-entrypoint.d/
RUN chmod +x /docker-entrypoint.d/40-create-self-signed-cert.sh
