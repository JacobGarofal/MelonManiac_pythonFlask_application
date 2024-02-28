## Setting up requirements:

1. Create a virtual environment:
```sh
$ python -m venv ./.venv
```

2. Activate virtual environment:
```sh
$ Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
$ .\.venv\Scripts\Activate  
```

3. Install requirements
```sh
$ pip install -r ./requirements.txt
```

## Setting up and seeding the database

1. Create the database:
```sh
$ python ./create_db.py
```

2. Seed the database:
```sh
$ python ./seed_db.py
```

If you want to rebuild the DB, just delete `instance/data.sqlite` and redo these steps.


## Running the project

1. Run app
```sh
$ python ./main.py
```
OR
```sh
$ flask --app melomaniac run
```

## Developer's guide

Here is a section containing more information about the technology used and how requirements are being met.

### Background tasks

In a real application, task scheduling would be done through something like [celery](https://docs.celeryq.dev/en/stable/index.html). In this small assignment, tasks are done before each relevant request instead, meaning before any page is built and served, tasks are performed.

Below is a list of all background tasks:

1. Setting ended event status to 'Inactive' on Open events that have expired (end date is in the past).