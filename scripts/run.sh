#!/bin/sh

# ^ This `shebang` marks this file as a shell script. 

set -e
# ^ This will make the script exit if any command in it fails. (Instead of conitnuing with the execution.)

python manage.py wait_for_db
# ^ This will wait for the database to be available.

python manage.py collectstatic --noinput
# ^ This will collect static files.
# Static files are put in configured static file directory.
# All static files of all different apps in our project are copied in same directory
# This directory will be made accessible by NGiNX Reverese Proxy.

python manage.py migrate
# Run migrations automatically when App starts. 
# So that database migrated to correct state. (If there are changes in App)

uwsgi --socket :9000 --workers 4 --master --enable-threads --module app.wsgi
#^ Running uWSGI server.
# Creating a TCP socket on port 9000. (This is the port on which NGiNX will listen.)
# 4 WSGI workers are created.
# --master > this will make uWSGI / running application as master thread.
# --enable-threads > this will enable threads (multi-threading) in uWSGI.
# --module > this will tell uWSGI which WSGI module to run. (i.e. app/wsgi.py)
# app.wsgi.py > this is the entry point to Application. (app.wsgi > auto generated by Django)