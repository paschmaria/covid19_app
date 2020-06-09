# COVID-19 Triaging USSD App

A USSD app for COVID-19 Self Assessment

## Getting started

These instructions will help get a copy of this project up and running on your local machine in no time.

### Prerequisites

What you will need you will need to run this app successfully:
```
Python 3.7.x

Django 3.0.x

PostgreSQL 12.2
```

You can get Python [here](https://www.python.org/downloads/release/python-370/) and PostgreSQL [here](https://www.postgresql.org/download/)

### Set Up Locally

You can install and setup this project locally using the following steps:

Download the app from the Azure Repo
```
$ git clone https://dev.azure.com/glo-epid/_git/gloepid-ussd

$ cd covid19_app
```

Setup a virtual environment

I'll recommend using [virtualenv](http://www.virtualenv.org/en/latest/).
```
$ virtualenv venv

$ source venv/bin/activate
```

Create a `local.env` file in the `env` directory

Create database and add DB settings to the `local.env` file

Update the following on the `local.env` file:
```
DJANGO_SETTINGS_MODULE=core.settings.local

SECRET_KEY=YOUR_SECRET_KEY

DB_NAME=YOUR_DB_NAME

DB_USER=YOUR_DB_USERNAME

DB_PASSWORD=YOUR_DB_PASSWORD

DB_HOST=YOUR_DB_HOST

DB_PORT=YOUR_DB_PORT
```

Next, install the dependencies using [pip](http://www.pip-installer.org/en/latest/), from the
current directory:
```
(venv) $ pip install -r requirements.txt
```

Update DB and run application server
```
(venv) $ python manage.py migrate

(venv) $ python manage.py loaddata dumped_data.json5432

(venv) $ python manage.py runserver
```

### Deploying to Production

First, update the `prod.env` file using the following:
```
DB_NAME=YOUR_DB_NAME

DB_USER=YOUR_DB_USERNAME

DB_PASSWORD=YOUR_DB_PASSWORD

DB_HOST=YOUR_DB_HOST

DB_PORT=YOUR_DB_PORT

EMAIL_PORT=587
```

If you're using SendGrid for the mails, also update the following:
```
SENDGRID_API_KEY=YOUR_SENDGRID_API_KEY

SENDGRID_PASSWORD=YOUR_SENDGRID_API_KEY

SENDGRID_USERNAME=apikey

EMAIL_HOST=smtp.sendgrid.net
```

If you need to, you can read up on how to deploy a Django app on Azure App Services [here](https://medium.com/@DawlysD/deploying-django-apps-with-postgresql-on-azure-app-services-from-scratch-fe4a10db5e7c) and [here](https://stories.mlh.io/deploying-a-basic-django-app-using-azure-app-services-71ec3b21db08).
