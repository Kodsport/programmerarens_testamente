FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt /app
RUN pip3 install -r requirements.txt

COPY . /app

# Create a debian filesystem to use with nsjail
RUN mkdir /debian_filesystem
RUN apt update && apt install -y debootstrap
RUN debootstrap --variant minbase --include python3 --arch amd64 bookworm /debian_filesystem http://deb.debian.org/debian

CMD ["python3", "app.py"]
