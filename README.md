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

### Installation

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

DEBUG_VALUE=True
```

Next, install the dependencies using [pip](http://www.pip-installer.org/en/latest/), from the
current directory:
```
$ pip install -r requirements.txt
```

Update DB and run application server
```
$ python manage.py migrate

$ python manage.py loaddata dumped_data.json

$ python manage.py runserver
```