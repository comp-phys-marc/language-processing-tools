FROM ubuntu:latest

RUN apt-get -y update
RUN apt-get -y upgrade
RUN apt-get -y install python3 pip

COPY . .

RUN pip install -r requirements.txt

ENTRYPOINT ["tail", "-f", "/dev/null"]