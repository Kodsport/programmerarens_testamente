# Programmerarens Testamente

Programmerarens Testamente is a group activity where teams race to solve challenges and run around campus.

## Setup

* To setup a game copy `app/user/config.json.example` to `app/usr/config.json` and change it.
* Create new problems. You can see the different problem types in [this file](app/problems/problemTypes.md) and their requirements.
* Run the docker container with `docker compose up -d --build`

## Gameplay

* Each user needs to select their team when they first visit the website. It will be saved for 24h so users may need to select their team again in very long competitions.
* The users get a problem, when they solve it they will get a room number where a qr code will be located. Once someone from a team scans the qr code the entire team can view the new problem. This repeats until they solve all the problems and get to the final room where we recommend you give them some [fika](https://en.wikipedia.org/wiki/Coffee_in_Sweden#Fika).
* (For problems where the users need to write and submit their own code we recommend that they develop and test locally to make debuging easier)