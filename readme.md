# GDKP helper

Automation tool for gdkp's based on warcraft logs.

## Setup
Copy .env.example to .env and fill in the details

## Usage
To fetch log and print a copy-pastable list
```$ py main.py fetch <warcraft logs id>```

To fetch log and paste into google sheet
```$ py main.py sheet <warcraft logs id> <sheet tab number>```
Sheet tab number the tab in the document, starting with 1 for the first tab, 2 for the second and so on.