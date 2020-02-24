# Use an official Python runtime as a parent image
FROM ubuntu:16.04
FROM python:2.7-slim

# install packages
RUN apt-get -y update && apt-get install -y vim net-tools iputils-ping nmap awscli openssh-server tcpreplay tcpdump
RUN pip install scapy pyexcel xlrd pyPdf

# setting up SSH server, and configure host user as allowed user for ssh into container
RUN mkdir /var/run/sshd

RUN echo 'root:zingbox123' | chpasswd
RUN sed -i 's/PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config
RUN sed -i 's/PermitRootLogin without-password/PermitRootLogin yes/' /etc/ssh/sshd_config

# SSH login fix. Otherwise user is kicked off after login
RUN sed 's@session\s*required\s*pam_loginuid.so@session optional pam_loginuid.so@g' -i /etc/pam.d/sshd

ENV NOTVISIBLE "in users profile"
RUN echo "export VISIBLE=now\nexport DOCKER_MACHINE=true" >> /etc/profile

# export port and start ssh service
EXPOSE 22
ENTRYPOINT /usr/sbin/sshd -D


