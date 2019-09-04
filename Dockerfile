FROM nginx
COPY docs/build/html /usr/share/nginx/html
COPY nginx.conf /etc/nginx/
EXPOSE 9081
CMD ["nginx", "-g", "daemon off;"]