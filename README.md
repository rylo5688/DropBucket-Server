# DropBucket-Server

## Deploying to compute engine
* Copy files `gcloud compute scp --project="dropbucket" --zone="us-central1-a" --recurse . django-server:~/`
* SSH into server `gcloud beta compute --project "dropbucket" ssh --zone "us-central1-a" "django-server"`
* Set GCP environment variable `export GCP_APPLICATION_CREDENTIALS=<PATH TO JSON>`
* Run server `nohup python3 dropbucket/manage.py runserver 0.0.0.0:8000 &`
    * NOTE: You need to kill the server if it is currently running
    ```
    ps -ef | grep runserver
    kill <pid>
    ```

## GCP Service Account Setup for Django
* Goto the google console
* Open navigation menu > IAM & admin > Service Accounts
* Select `dropbucket-server@dropbucket.iam.gserviceaccount.com`
* Click `Edit`
* Create new key and download it as a JSON
* Set environment variable: `export GOOGLE_APPLICATION_CREDENTIALS="<PATH TO JSON>"`

## Setting up environment
* Create a python virtual environment `virtualenv <path to environment>`
	* An example would be `virtualenv ~/.envs/dropbucket`
* Activate the virtual environment `source <path to environment>/bin/activate`
* Install packages `pip3 install --requirement requirements.txt`

* Setup database
```
python3 dropbucket/manage.py makemigrations app
python3 dropbucket/manage.py migrate
```
* Update database
```
rm -rf dropbucket/app/migrations dropbucket/db.sqlite3
python3 dropbucket/manage.py makemigrations app
python3 dropbucket/manage.py migrate
```


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
	"device_id":"device123"
}
```

**Response**
```json
{
	"message":"msg",
    "fs_objects": [
        {
            "abc.png": "351a7f843149e7fda0f89c59cea2c799"
        },
        {
            "dir/test.py": "806b50398b52ddeac079d8a69c39999c"
        },
        {
            "handsomesquidward_2_1200x1200.png": "d40fa9705faca772df6a69dac851d11b"
        },
        {
            "testfile.txt": "d41d8cd98f00b204e9800998ecf8427e"
        }
    ],
    "directories": [
        "dir/",
        "dir/dir2/"
    ],
}
```

**Status Code**
* `200`: Successfully signed in (username and password match)
* `400`: Incorrectly formatted body
* `409`: Username or password is incorrect

### POST `/file/`

Upload a file

**POST body**<br/>

A file object along with

```json
{
	"device_id": "device123_45",
	"relative_path": "file.txt"
}
```

**Response**
```json
{
	"message":"msg"
}
```

**Status Code**
* `201`: Successfully posted file
* `400`: Incorrectly formatted body

### GET `/file/`

Download a file

**POST body**
```json
{
	"relative_path": "file.txt"
}
```

**Response**
A force-downloaded file.

**Status Code**
* `200`: Successfully downloaded file
* `400`: Incorrectly formatted body


### DELETE `/file/`

Delete a file

**POST body**
```json
{
	"relative_path": "file.txt",
}
```

**Response**
```json
{
	"message":"msg"
}
```

**Status Code**
* `200`: Successfully deleted file
* `400`: Incorrectly formatted body
* `409`: User already has an account


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
