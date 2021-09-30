#!/bin/sh
echo "Clearing images, volumes"
docker-compose down
docker system prune -a
docker volume prune
