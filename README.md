# theminator

Discord bot for choosing users each week to pick a server theme.

## How to run

First, create a file `data.json` with the following contents:

```json
{
    "active": [], 
    "inactive": [], 
    "running": false, 
    "channel_id": -1
}
```

To run this bot you will need `docker` installed. Once you have docker installed build the container.

```bash
docker build theminator .
```

And then run the container using the below command, you will need to have created a `.env` file with a variable `DISCORD_API_TOKEN` containing the token of your bot.

```bash
docker run \
--env-file ./.env \
-v "$(pwd)"/data.json:/data.json \
theminator
```