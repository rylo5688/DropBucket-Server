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

### GET `/users`

### POST `/users`

Create a user

**POST body**
```json
{
	"access_token":"a",
	"refresh_token":"b",
	"bucket_name":"c"
}
```


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
