#!/bin/bash

docker-compose up -d mongo
echo "Start mongo-db..."
sleep 10
docker-compose up -d mongo-express
echo "Start mongo-express!"
docker-compose up -d --build web 
# echo "Start web!"