## Setup & Run
```
pip install -e .
export FLASK_APP=sjtuface.sjtuface
flask run
```

## Database

Edit the username and password in config.py, and then run scripts below to initialize database.
```
$ python manage.py create_db
$ python manage.py create_user -u admin -p 123456
```