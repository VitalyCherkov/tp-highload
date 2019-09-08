#!/bin/sh

docker stop highload
docker rm highload
docker build -t=highload .
docker run -p 80:8877 -v ~/Projects/tp/tp-highload/httpd.docker.conf:/etc/httpd.conf:ro -v ~/Projects/http-test-suite:/var/www/html:ro --memory 1G --rm --name highload highload
