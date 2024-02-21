# theminator

Discord bot for choosing users each week to pick a server theme.

## Deployment

### Pre-Requisites

- A clone of this repository
- Docker
- Python 3.11

### Deploy

Create a file `data.json` with the following contents within the repository's directory.

```json
{
    "active": [], 
    "inactive": [], 
    "running": false, 
    "channel_id": -1
}
```

Build the docker container, do this any time you make changes to the code.

```bash
$ docker build theminator .
```

Run the container using the below command, you will need to have created a `.env` file with a variable `DISCORD_API_TOKEN` containing the token of your bot.

```bash
$ docker run \
--env-file ./.env \
-v "$(pwd)"/data.json:/data.json \
theminator
```

Alternatively, if you are running it persistently (as intended), use the following command.

```bash
$ docker run \
-d \
--restart always \
--env-file ./.env \
-v "$(pwd)"/data.json:/data.json \
theminator
```
