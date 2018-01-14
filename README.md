# Photo Shares

This is a project for my CS460 class, SUMMER term I 2017. It is a **photo sharing web application**. User can upload images, browse images in the system and leave comments.

## Purpose
The app allows simple photo sharing. It provides a system that store images submitted by registered users. So each user can browse his own image or image submitted by other users.

## Dependencies
### Backend
* [Flask](https://pypi.python.org/pypi/Flask)

### Frontend
* HTML

### Database
* [Mysql](https://www.mysql.com)

## Run the app

### Install dependencies
Make sure that you have [python 2.7](https://www.python.org/downloads/), [Flask](https://pypi.python.org/pypi/Flask) and [Mysql](https://www.mysql.com) correctly installed before running the app.

## Initiate App
After dependencies are installed and [mysql is correctly configured](https://dev.mysql.com/doc/mysql-shell-excerpt/5.7/en/), open the app directory and create the sql database using schema.sql, which already defined the required tables for this app.

After created the database, open *users.py* to modify the following credentials 

```
app.secret_key = 'YOUR SUPER KEY'
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'YOUR MYSQL PASSWORD'
```

After done with above steps, you can run the app by running
```
python user.py
```
in your command prompt. 

Now open *http://localhost:5000* in any browser to enjoy the app! See ```/Documentation/Description.md``` for full description of function provides by this app.
