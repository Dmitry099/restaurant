# Restaurant App.

##### This restaurant app presents API to create, read, update and delete restaurants and entities that chained with restaurants like employees, persons and addresses.
##### To use this app you should have installed [Docker and Docker Compose](https://www.docker.com)

##### For begin using app you should:
1. Clone repository from GitHub
2. Go to restaurant project folder in terminal
3. Run docker-compose
```
docker-compose up
```
4. Run in another terminal exec commands
```
docker-compose exec web python manage.py loaddata initial_fixture
docker-compose exec web python manage.py createsuperuser --username admin --email admin@admin.ru
```

Also if you don't want to use Docker, you can:
1. Clone repository from GitHub
2. change DATABASES settings in settings.py file (/restaurant/restaurant/settings.py) - i.e. host name from "db" to "localhost" (if you have local postgres base with name 'postgres', user 'postgres' and password: 'postgres', if you don't have these you can create it or write you own settings)
3. Go to restaurant project folder in terminal
4. Run commands by order
```
python manage.py migrate
python manage.py loaddata initial_fixture
python manage.py createsuperuser --username admin --email admin@admin.ru
python manage.py runserver 0.0.0.0:8000
```

##### To test API you can use Postman OpenAPI scheme
[Postman OpenAPI link](https://documenter.getpostman.com/view/16713673/TzsWspLg)
