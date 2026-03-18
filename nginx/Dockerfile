FROM nginx:alpine

RUN echo 'events { worker_connections 1024; }\n\
http {\n\
  upstream frontend { server frontend:3000; }\n\
  upstream backend { server backend:8000; }\n\
  server {\n\
    listen 80;\n\
    location / { proxy_pass http://frontend; proxy_http_version 1.1; proxy_set_header Host $$host; }\n\
    location /api/ { proxy_pass http://backend; proxy_http_version 1.1; proxy_set_header Host $$host; }\n\
    location /ws/ { proxy_pass http://backend; proxy_http_version 1.1; proxy_set_header Upgrade $$http_upgrade; proxy_set_header Connection "upgrade"; }\n\
  }\n\
}' > /etc/nginx/nginx.conf
