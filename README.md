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

## Config

### `seed` (required)

Seed used to ensure that random operations are reproduced when restarted

### `competition-name` (required)

Name of your competition

### `admin-password` (required)

Password for the admin page (`/admin`). Currently, HTTP Basic Auth is used, where the username is ignored.

CHANGE THIS PASSWORD! If left empty, no password will be required

### `teams` (required)

List of team names. The team names will be used as-is, and will be stored in places such as cookies. This means that they probably should be URL safe

### `rooms` (required)

Each room should be associated with one (unique) UUID. To generate a UUID, you can use the following command:

```bash
python3 -c 'import uuid; print(uuid.uuid4())'
```

There has to be at least as many rooms (including the `final-room`) as there are problems. If there are more rooms than problems, the teams will not get all the same rooms

### `final-room` (required)

The final room, which all teams will have as the last room. This is preferably the place where the organizer sits and monitors the game through the admin page

### `unused-rooms` (required)

This is a list of real room names that is used in certain problems where there are multiple options, but only one correct. This config entry ensures that the incorrect rooms does not have QR codes

### `problems` (required)

The (ordered) list of problems that the players get. As the rooms are random, players will be dispersed even though they are working on the same problems at the same time. The entries here are the directory name for the specific problem in the `app/problems` directory

### `override-nsjail` (optional)

If `True`, nsjail will not be used, and the result of the submission will instead be randomized, while waiting a random (within the `max_time`) time before responding
