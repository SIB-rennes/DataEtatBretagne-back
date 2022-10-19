# set base image (host OS)
FROM python:3.9.9-slim-buster


RUN apt-get update -y && \
apt-get upgrade -y && \
apt-get install -y p7zip

# set the working directory in the container
WORKDIR /appli

RUN mkdir workdir

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app/ ./app/
COPY config/ ./config/
COPY manage.py ./
COPY migrations ./migrations
RUN rm /appli/config/config_template.yml

EXPOSE 80

CMD ["waitress-serve","--port=80","--call", "app:create_app"]
