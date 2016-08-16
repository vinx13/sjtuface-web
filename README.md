## Setup & Run
```
pip install -e .
python run.py
```

## Database

Edit the username and password in config.py, and then run scripts below to initialize database.
```
$ python manage.py create_db
$ python manage.py create_user -u admin -p 123456
```
