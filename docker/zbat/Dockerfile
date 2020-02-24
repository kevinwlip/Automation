# Use an official Python runtime as a parent image
FROM ubuntu:16.04
FROM python:2.7-slim
FROM java:9

# Set the working directory to /app
WORKDIR /home/automation/zbat

# Copy the current directory contents into the container at /app
ADD . /home/automation/zbat
ADD ./.bash_profile_enc /root

# Define environment variable
ENV NODE_ENV testing
ENV DECRYPTION_KEY password_from_qa
ENV DOCKER_MACHINE true

# Decrypt environment variables
RUN openssl enc -aes-256-cbc -d -in /root/.bash_profile_enc -out /root/.bash_profile -k $DECRYPTION_KEY

RUN apt-get -y update

# Install text editor
RUN apt-get -y install vim

# Install tre for image processing
RUN apt-get -y install tesseract-ocr poppler-utils libjpeg-dev imagemagick tre-agrep libtre5 libtre-dev
RUN apt-get -y install python-dev build-essential libssl-dev libffi-dev libxml2-dev libxslt1-dev zlib1g-dev

# Install chromium
#RUN apt-get -y install build-essential libssl-dev php5-mcrypt python-setuptools libffi-dev
RUN easy_install pip
RUN easy_install -U pip
#RUN apt-get -y install chromium # chromium-browser is not in package list, install chromium instead

# Install xvfb and run
#RUN apt-get -y install xvfb
#ENV DBUS_SESSION_BUS_ADDRESS /dev/null
#RUN export DBUS_SESSION_BUS_ADDRESS=/dev/null
#RUN mkdir -p /logs/selenium

# Install node and webdriver
#RUN curl -sL https://deb.nodesource.com/setup_7.x | bash -
#RUN apt-get install -y nodejs
#RUN npm install -g webdriver-manager && \
#  webdriver-manager update
#  nohup xvfb-run webdriver-manager start < /dev/null >> /logs/selenium/webdriver.log &

# Intall nmap
RUN apt-get -y install nmap

# Need for ruleengine tests
RUN apt-get -y install sshpass

# Install geoip library dependency
RUN apt-get install libgeoip-dev -y

# Install zbat python dependencies
RUN cat requirements.txt | xargs -n 1 -L 1 pip install; exit 0
RUN pip install requests --upgrade
