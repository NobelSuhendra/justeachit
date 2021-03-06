# Justeachit
Justeach.it is a website to help teachers and students arrange tutoring sessions or meetings. It has a built-in calendar to show the availability of both teachers and students. Chat integration is in the works to make communication more convenient.

> This was built using HTML, CSS, JS, Flask (including jinja2) and SQLite.

## SQLite

### Users Table
```sql
CREATE TABLE users (username TEXT, email TEXT, logged TEXT, password TEXT, type TEXT, age TEXT, id INTEGER, PRIMARY KEY(id));
```

### Times Table
```sql
CREATE TABLE times (time TEXT, month TEXT, date TEXT, id INTEGER, status TEXT, teacher TEXT, student TEXT, id2 INTEGER, PRIMARY KEY(id2));
```


## Key Features

### Account management
- Via "/account"

### Schedule management
- Via "/dashboard/{month}/{day}"
- Uses colour codes to represent time-availability

### User searching
- Via "/users/%{query}%"

### User schedules (Available primarily to accounts registered as teachers)
- Via "/@{username}/{month}/{day}"
- Uses colour codes to represent time-availability

### Login/Register
- Via "/login" and "/register"

## Others
> The calendar is currently limited to 2022, but will can be easily updated by an admin accordingly


##### Built by Nobel Suhendra from December 2021 - Janaury 2022
