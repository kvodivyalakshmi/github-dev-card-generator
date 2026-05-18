FROM nginx:alpine

# Copy index.html to the default nginx public folder
# Note: We name it index.html.template so we can run envsubst on it
COPY index.html /usr/share/nginx/html/index.html.template

# Default environment variable
ENV BACKEND_URL=http://localhost:8080

# Run envsubst to replace the placeholder in index.html and then start nginx
CMD ["/bin/sh", "-c", "envsubst '${BACKEND_URL}' < /usr/share/nginx/html/index.html.template > /usr/share/nginx/html/index.html && nginx -g 'daemon off;'"]

EXPOSE 80
