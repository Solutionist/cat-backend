#!/bin/bash
# Setup docker
docker volume create db-data
docker-compose up

# Create database
curl -X PUT \
  http://localhost:5984/twitter \
  -H 'Accept: */*' \
  -H 'Accept-Encoding: gzip, deflate' \
  -H 'Authorization: Basic YWRtaW46YWRtaW50ZXN0' \
  -H 'Cache-Control: no-cache' \
  -H 'Connection: keep-alive' \
  -H 'Content-Length: 0' \
  -H 'Host: localhost:5984' \
  -H 'Postman-Token: 02574780-3f8f-426f-a8f5-803a0b8ee3cf,10bb05f0-9be7-4d26-86c6-44fe543808c6' \
  -H 'User-Agent: PostmanRuntime/7.20.1' \
  -H 'cache-control: no-cache'

  # Run python
  pip3 install requirements.txt
  python3 twitter.py