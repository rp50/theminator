import hikari
import arc
import random
from json import dump, load
from typing import Optional
from dotenv import load_dotenv
from os import getenv

load_dotenv()

BOT_TOKEN = getenv("DISCORDAPITOKEN")

bot = hikari.GatewayBot(token=BOT_TOKEN)

client = arc.GatewayClient(bot)

cron_str: str = "0 10 * * 0"

active = []  # List containing user_ids of people in the rotation
inactive = []  # List containing user_ids of people in the rotation who have already been picked

running = False  # Whether or not the rotation cronloop is already running
is_first_run = True  # Used to ensure the rotation loop doesn't run on invocation
channel_id = -1  # Channel to send the rotation cronloop message in


def write_data() -> None:
    """
    Function to write variables out to data.json.
    """
    with open("data.json", "w") as file:
        dump(
            {
                "active": active,
                "inactive": inactive,
                "running": running,
                "channel_id": channel_id,
            },
            file,
        )


@client.include
@arc.slash_command("register", "Register to the theme rotation.")
async def register(ctx: arc.GatewayContext) -> None:
    """
    Add a user to the Rotation
    """
    if ctx.author.id in active or ctx.author.id in inactive:
        await ctx.respond(f"Stop it {ctx.author.mention}.")
        return
    active.append(ctx.author.id)
    await ctx.respond(f"{ctx.author.mention} added.")
    write_data()


@client.include
@arc.slash_command("deregister", "Deregister from the theme rotation.")
async def deregister(ctx: arc.GatewayContext) -> None:
    """
    Remove a user from the Rotation
    """
    if ctx.author.id in active:
        active.remove(ctx.author.id)
    elif ctx.author.id in inactive:
        inactive.remove(ctx.author.id)
    else:
        await ctx.respond(f"{ctx.author.mention} not registered.")
        return
    await ctx.respond(f"{ctx.author.mention} removed.")
    write_data()


async def choose_user() -> Optional[hikari.User]:
    """
    Chooses a user and returns it.
    """
    global active, inactive
    if not active:
        if not inactive:
            return None
        active = inactive
        inactive = []

    user_id = random.choice(active)
    active.remove(user_id)
    inactive.append(user_id)
    write_data()
    return await bot.rest.fetch_user(user_id)


@arc.utils.cron_loop(cron_str)
async def rotation() -> None:
    """
    Cronlooped function that manages the theme rotation.
    """
    global is_first_run
    if is_first_run:
        is_first_run = False
        return
    global running
    user = await choose_user()
    if not user:
        rotation.stop()
        running = False
        await bot.rest.create_message(
            channel=channel_id, content="No users found, ending rotation."
        )
        write_data()
        return
    await bot.rest.create_message(
        channel=channel_id, content=f"{user.mention}'s turn to choose the theme!"
    )


@client.include
@arc.slash_command("begin", "Begin the theme rotation.")
async def begin(ctx: arc.GatewayContext) -> None:
    """
    Starts the rotation cronloop
    """
    global running, channel_id
    channel_id = ctx.channel_id
    if running:
        await ctx.respond(
            f"Theme rotation already active, changing channel to {ctx.get_channel().mention}."
        )
        return
    running = True
    write_data()
    rotation.start()
    await ctx.respond("Beginning theme rotation.")


@client.include
@arc.slash_command("end", "End the theme rotation.")
async def end(ctx: arc.GatewayContext) -> None:
    global running, channel_id, is_first_run
    channel_id = ctx.channel_id
    running = False
    is_first_run = True
    write_data()
    rotation.stop()
    await ctx.respond("Stopping theme rotation.")


@client.set_startup_hook
async def startup(client: arc.GatewayClient) -> None:
    try:
        with open("data.json") as file:
            data = load(file)
            global active, inactive, running, channel_id
            active = data["active"]
            inactive = data["inactive"]
            running = data["running"]
            channel_id = data["channel_id"]
    except FileNotFoundError:
        pass
    if running and channel_id != -1:
        rotation.start()


bot.run()
