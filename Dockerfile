FROM python:3.9-alpine3.13  

# ^Alpine is a lightweight version of Linux, and it's ideal for running Docker containers because it is very stripped back.
# It doesn't have any unnecessary dependencies that you would need.

LABEL maintainer="RaaidKhan"

ENV PYTHONUNBUFFERED 1

# ^The output from Python will be printed directly to the console, which prevents any delays of messages

COPY ./requirements.txt /tmp/requirements.txt  
COPY ./requirements.dev.txt /tmp/requirements.dev.txt  
# ^copies the requirements file that we added earlier into the Docker image.

COPY ./app /app

WORKDIR /app

# ^working directory and it's the default directory that will commands are going to be run from when we run commands on our Docker image.

EXPOSE 8000

# ^expose Port 8000 from our container to our machine when we run the container.
# this way we can connect to the Django Development Server.

ARG DEV=false
# DEV=false if NOT run by our 'docker-compose' configuration

RUN python -m venv /py && \                              
    /py/bin/pip install --upgrade pip && \
    apk add --update --no-cache postgresql-client jpeg-dev && \ 
    apk add --update --no-cache --virtual .tmp-build-deps \
        build-base postgresql-dev musl-dev zlib zlib-dev && \
    /py/bin/pip install -r /tmp/requirements.txt && \
    if [ $DEV = "true" ]; \
        then /py/bin/pip install -r /tmp/requirements.dev.txt ; \
    fi && \
    rm -rf /tmp && \
    apk del .tmp-build-deps && \
    adduser \
        --disabled-password \
        --no-create-home \
        django-user && \
    mkdir -p /vol/web/media && \
    mkdir -p /vol/web/static && \
    chown -R django-user:django-user /vol && \
    chmod -R 755 /vol

# - Create Python Virtual Environment
# - Upgrade Pip in our VENV
# - Installing Postgresql Client Package inside our Alpine Image in order to Psycopg2 package to able to connect to Postgresql
# - [A] Set a virual dependency packages - groups packages that we need to install into '.tmp-duild-deps' {packages = build-base , postgresql-dev , musl-dev} > required to install Psycopg2
# - Install requirements in our Docker Image as specified in requirements.txt
# - {BASH script condition} > Install DEV requirements if we are running through "docker-compose".  {fi  > ending an if statement}
# - Remove tmp directory {we don't want any extra dependencies on our image. Once it's being created, it's best practice to keep Docker images as lightweight as possible.}
# - Remove dependencies installed in step [A]
# - adduser > Add new user inside image. {It is best practice to not use 'root' user (security purpose if image is compromised)}
    # disable password for login
    # do not create 'home' directory
    # name of user

ENV PATH="/py/bin:$PATH"

# ^when we run any command in our project, we don't want to have to specify the full path of our virtual environment.


# Everything upto this line is being run as 'root' user

USER django-user

# ^Switch user to 'django-user'  {root privileges revoked}


# Commands in this file are run when creating a Docker Image. 
# Docker employs Caching, i.e. it will take more time on first-run and less time later on
