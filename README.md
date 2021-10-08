# StrizhProject

### Clearing all images, volumes

`docker-compose down`

`docker system prune -a`

`docker volume prune`

### Run docker build and up

`docker-compose -f docker-compose.yml up`

`docker ps`, get container_name = name of web container

### **Create superuser to get access to admin**

`docker exec -it {{container_name}} bash`

`python manage.py createsuperuser`