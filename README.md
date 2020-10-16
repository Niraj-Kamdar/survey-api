# Survey API

This is a REST API service which allows creating, taking and viewing survey. You can try it live on [survey-rest-api.herokuapp.com](https://survey-rest-api.herokuapp.com/).


## Usage

You can see documentation of API in both [swagger](https://survey-rest-api.herokuapp.com/docs) and [redoc](https://survey-rest-api.herokuapp.com/redoc) style.

### How to use it?
- Create a new user account by POST request to `/users` endpoint.
- Create new token by POST request to `/token` endpoint.
- You can create new survey by POST request to `/surveys` endpoint.
- You can take or update response of a survey by PUT request to `/surveys/{survey_id}` endpoint.
- You can view responses of any survey by GET request to `/surveys/{survey_id}` endpoint.

 
## Getting Started
These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. If you want to use it in production you can skip to the deployment section.

### Prerequisites

- python 3.8 
- pipenv

### Installing
After cloning/downloading this repository you have to install necessary packages from Pipfile with following command

```console
pipenv install
```

This will install all dependencies needed to run the server.

### Starting server

After installation you just need to run following command to start server.

```console
uvicorn app.main:app
```
> You can stop server by pressing ctrl+c.

## Deployment

If you want to deploy this application. You can do this easily by running following command

```console
docker-compose up
```

This will build docker image and will start all required services to run server. You can visit server on `localhost:80`.
You can see documentation of API on `localhost/docs` or `localhost/redoc`. 
