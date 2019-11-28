# DropBucket-Server

## Setting up environment
* Create a python virtual environment `virtualenv <path to environment>`
	* An example would be `virtualenv ~/.envs/dropbucket`
* Activate the virtual environment `source <path to environment>/bin/activate`
* Install packages `pip3 install --requirement requirements.txt`

* Setup database `python3 dropbucket/manage.py makemigrations app; python3 dropbucket/manage.py migrate`


## Starting the server
```
python3 dropbucket/manage.py runserver <port>
```

## Endpoints




### POST `/users/signup`

Create a user

**POST body**
```json
{
	"username":"name",
	"password":"pass123",
}
```

**Response**
```json
{
	"message":"msg"
}
```

**Status Code**
* `201`: Successfully created the new account
* `400`: Incorrectly formatted body
* `409`: User already has an account



### POST `/users/signin`

Sign in as a user

**POST body**
```json
{
	"username":"name",
	"password":"pass123",
}
```

**Response**
```json
{
	"message":"msg"
}
```

**Status Code**
* `200`: Successfully signed in (username and password match)
* `400`: Incorrectly formatted body
* `409`: Username or password is incorrect


## Query the database manually
* Command line: `sqlite3 dropbucket/db.sqlite3`
* To show tables: `.tables`
* NOTE: Django generates table with the name `app_<model name>`
	* Example: `app_users`

## Django Deadlock error with virtual environment
* Not much info online about why this is an issue, but one way to get it to work:
```
pip install django
python3 dropbucket/manage.py runserver <port>
```
* Otherwise, rerunning `python3 dropbucket/manage.py runserver <port>` many times seems to fix it
