FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt /app
RUN pip3 install -r requirements.txt
RUN pip3 install gunicorn

COPY . /app

ENV AM_I_A_DOCKER_CONTIANER=Yes

# Create a debian filesystem to use with nsjail
RUN mkdir /app/debian_filesystem
RUN apt update && apt install -y debootstrap
RUN debootstrap --variant minbase --include python3 --arch amd64 bookworm /app/debian_filesystem http://deb.debian.org/debian
RUN apt install libprotobuf32 libnl-3-200 libnl-route-3-200 libexpat1

CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:6969"]
