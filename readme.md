# GDKP helper

Automation tool for gdkp's based on warcraft logs.

## Requirements
Python 3
GraphAPI credentials for Warcraft Logs
Google OAuth credentials for Google API (only for sheet command)

## Setup
Copy .env.example to .env and fill in the details

A Warcraft logs access token can be generated with an API tool like Insomnia.

If you want to use the sheet command you must get some credentials from Google.\
Follow this guide to create credentials: https://developers.google.com/workspace/guides/create-credentials#oauth-client-id \
Download and save them as `google/credentials.json`.\
Then go into the google directory and run oauth.py.
```
$ cd google
$ python3 oauth.py
```
This will allow you to login and the script will create the file `google/token.json` that contains an access token that will be used by the main script.

## Usage
To fetch log and print a list
```
$ python3 main.py fetch <warcraft logs id>
```

To fetch log and paste into google sheet
```
$ python3 main.py sheet <warcraft logs id> <sheet id>
```

The warcraft logs id can be found in the url of the report `/reports/<log id>#blablabla`.\

The spreadsheet id and sheet id can be found at the end the document url `/spreadsheets/d/<spreadsheet id>/edit#gid=<sheet id>`.\
The spreadsheet id is for the whole document, while the sheet id is for the tab within the document.
