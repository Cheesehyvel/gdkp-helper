# GDKP helper

Automation tool for gdkp's based on warcraft logs.

## Requirements
Python 3
GraphAPI credentials for Warcraft Logs
Google OAuth credentials for Google API (only for sheets command)

## Setup
Copy .env.example to .env and fill in the details
Go into google directory and run oauth.py
```
$ cd google
$ python3 oauth.py
```

## Usage
To fetch log and print a list
```
$ python3 main.py fetch <warcraft logs id>
```

To fetch log and paste into google sheet
```
$ python3 main.py sheet <warcraft logs id> <sheet id>
```