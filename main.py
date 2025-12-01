import discord
import threading
import asyncio
import dbAccess as db
import pandas as pd
import aiohttp
import os
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
from discord.ext import commands
from discord import app_commands
from time import sleep
from json import dumps, loads
from io import BytesIO
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from PIL import Image
from dotenv import load_dotenv
load_dotenv()

token = os.getenv("API_KEY") # Set intents and api key
intents = discord.Intents.default()
intents.guilds = True
intents.message_content = True
intents.members = True

client = commands.Bot(command_prefix = "nevergettingused", intents = intents) # Initialise bot

"""
Link for bot invite.
https://discord.com/oauth2/authorize?client_id=1440842599521845309&permissions=2252263737645120&integration_type=0&scope=bot+applications.commands invite 
"""

def help(): # Print all server cli commands
    for key in commands.keys():
        print(key)

CLI_Commands = { # Dictionary of commands and their function
    "help": lambda: help(),
    "db_t": lambda: db.test(),
    "exit": lambda: (
        db.closeConnection(),
        asyncio.run_coroutine_threadsafe(client.close(), client.loop),
        os._exit(0)
    )
}

# Some simple response strings which may be removed in future
rulesmes = """```
Whamageddon is a game where you have to go from the 1st to the 25th of December without hearing Last Christmas by Wham!
Other covers of Last Christmas are completely fine!
```"""
nowhitelist = "This channel is not whitelisted for use"

# Time related variables
today = datetime.now()
currentYear = int(today.year)

# Checks the current year has an entry in the DB and checks if it should be active
if db.getYears(currentYear) is None:
    db.insertYear(currentYear)
if today.month == 12 and today.day < 26:
    db.setYears(currentYear, True)


def cli_loop():
    sleep(5)
    while True: # Server Terminal Command loop
            cmd = input("Enter a command: ")
            try:
                CLI_Commands[cmd]()
            except:
                print("Command not found, try 'help'")

def checkWhitelist(GuildID, ChannelID): # Check if the given channel is in the whitelist and check if it is enabled
    if not db.getToggle(GuildID):
        return True
    else:
        channels = db.getChannels(GuildID)[0]
        return str(ChannelID) in channels

class WhamBot(commands.Bot): # Sync commands to discord
    async def setup_hook(self):
        synced = await self.tree.sync()
        print(f"Synced {len(synced)} commands.")

client = WhamBot(command_prefix="yellglelelle", intents=intents)


@client.event
async def on_ready():
    print("We have logged in as {0.user} ".format(client)) 
    activity = discord.Activity(name="Not listening to hit christmas song 'Last Christmas' by Wham!", type=3)               # this is to writing prefix in playing a game.(optional)
    await client.change_presence(status=discord.Status.online, activity=activity) # this is for making the status as an online and writing prefix in playing a game.(optional)                   



@client.tree.command(name="rules", description="Show the rules of Whamageddon")
async def rules(interaction: discord.Interaction):
    if checkWhitelist(interaction.guild.id, interaction.channel_id):
        await interaction.response.send_message(rulesmes)
    else:
        await interaction.response.send_message(nowhitelist)

@client.tree.command(name="join", description="Join this years Whamageddon")
async def join(interaction: discord.Interaction):
    GuildID = interaction.guild.id
    UserID = interaction.user.id
    if not db.checkGuild(GuildID): # If there is no guild entry for the current guild then create one
            db.insertGuild(GuildID)
    if checkWhitelist(interaction.guild.id, interaction.channel_id): 
        if not db.checkUser(UserID): # If the user doesn't have an entry then create one
            db.insertUser(UserID)
        if not db.checkAttempt(currentYear, UserID): # If the user doesnt have an attempt entry for this year create one
            db.insertAttempt(currentYear, UserID)
        else:
            await interaction.response.send_message(f"You have already joined Whamageddon {currentYear}!")
            return
        await interaction.response.send_message("You have successfully joined Whamageddon!")
    else:
        await interaction.response.send_message(nowhitelist)

@client.tree.command(
    name="out",
    description="Declare yourself as having lost this year's Whamageddon"
)

@app_commands.describe(loss_reason="How did you lose?")
async def out(
    interaction: discord.Interaction,
    loss_reason: str
):
    if checkWhitelist(interaction.guild.id, interaction.channel_id):
        # Limit length manually
        if len(loss_reason) > 200:  # max 200 characters
            await interaction.response.send_message("Your loss reason is too long! Max 200 characters.")
            return
        GuildID = interaction.guild.id
        UserID = interaction.user.id

        if not db.checkGuild(GuildID): # If there is no guild entry for the current guild then create one
            db.insertGuild(GuildID)

        if not db.checkAttempt(currentYear, UserID): # If there is no attempt entry inform the user
            await interaction.response.send_message("You haven't done /join yet!")
            return

        db.addLoss(currentYear, today, loss_reason, UserID) # Record the loss in the users attempt entry
        await interaction.response.send_message(f"Loss recorded: {loss_reason}")
    else:
        await interaction.response.send_message(nowhitelist)

@client.tree.command(name="toggle", description="Toggle the whitelist for allowed channels (limited to 5)")
@app_commands.checks.has_permissions(administrator=True)
async def toggle(interaction: discord.Interaction):
    GuildID = interaction.guild.id
    await interaction.response.send_message(f"Whitelist enabled: {db.toggleWhitelist(GuildID)}")

@client.tree.command(name="whitelistadd", description="Whitelist a channel for Whamagededdon")
@app_commands.checks.has_permissions(administrator=True)
@app_commands.describe(channel_id="Channel ID of Whitelisted Channel")
async def whitelistAdd(interaction: discord.Interaction, channel_id: str):
    GuildID = interaction.guild.id
    if client.get_channel(int(channel_id)) is None: # Check channel ID is valid
        return await interaction.response.send_message("Invalid Channel ID (channel doesn't exist)")
    channels = loads(db.getChannels(GuildID)[0]) # Load the jsonified list of whitelisted channel ids
    if channel_id in channels:
        await interaction.response.send_message("Channel already whitelisted.")
        return
    if len(channels) > 9: # Only 10 channel ids are to be whitelisted at a time
        await interaction.response.send_message("Max whitelisted channels reached.")
        return
    else:
        channels.append(channel_id)
        db.setChannels(GuildID, dumps(channels))
        await interaction.response.send_message(f"Channel {channel_id} added to the whitelist.")
        return

@client.tree.command(name="whitelistremove", description="UnWhitelist a channel for Whamagededdon")
@app_commands.checks.has_permissions(administrator=True)
@app_commands.describe(channel_id="Channel ID of Whitelisted Channel")
async def whitelistRemove(interaction: discord.Interaction, channel_id: str):
    GuildID = interaction.guild.id
    raw_channels = db.getChannels(GuildID)[0]
    if raw_channels is not None:
        channels = loads(raw_channels)
    else:
        channels = []
    if channel_id in channels:
        channels.remove(channel_id)
        db.setChannels(GuildID, dumps(channels))
        await interaction.response.send_message(f"{channel_id} removed from whitelist.", ephemeral=True)
        return
    else:
        await interaction.response.send_message(f"{channel_id} isn't in the whitelist.", ephemeral=True)
        return

@client.tree.command(name="chart", description="Show a chart of the current state of Whamageddon in your Guild")
async def chart(interaction: discord.Interaction):
    guild = interaction.guild

    # Fetch all non-bot members
    members = [member async for member in guild.fetch_members(limit=None) if not member.bot]

    # Prepare data
    data = []
    for member in members:
        if db.checkAttempt(currentYear, member.id):
            loss_info = db.getLoss(member.id)  
            if loss_info[0]: # If user has lost
                data.append({
                    "user": member.display_name,
                    "avatar_url": str(member.display_avatar.url),
                    "date": loss_info[1],
                })

    if not data:
        await interaction.response.send_message("No data to display for this year.", ephemeral=True)
        return

    df = pd.DataFrame(data)
    df['date_num'] = mdates.date2num(df['date'])  # Convert datetime to matplotlib numeric format

    fig, ax = plt.subplots(figsize=(12, 6))

    # Draw scatter points and avatars
    async with aiohttp.ClientSession() as session:
        for idx, row in df.iterrows():
            ax.scatter(row['date_num'], idx, s=50, color='blue')  # If there is no profile picture draw a blue dot

            try:
                async with session.get(row['avatar_url']) as resp:
                    avatar_bytes = await resp.read()
                avatar_img = Image.open(BytesIO(avatar_bytes)).convert("RGBA")
                avatar_img = avatar_img.resize((32, 32))

                imagebox = OffsetImage(avatar_img, zoom=1)
                ab = AnnotationBbox(imagebox, (row['date_num'], idx), frameon=False, pad=0)
                ax.add_artist(ab)
            except Exception as e:
                print(f"Failed to load avatar for {row['user']}: {e}")
                ax.text(row['date_num'], idx, row['user'], fontsize=8, verticalalignment='center')

    # Y-axis
    ax.set_yticks(range(len(df)))
    ax.set_yticklabels(df['user'])

    # X-axis formatting
    ax.set_xlim(datetime(currentYear, 12, 1), datetime(currentYear, 12, 25))
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
    plt.setp(ax.get_xticklabels(), rotation=45, ha='right')

    # Labels and title
    ax.set_xlabel("Date")
    ax.set_title(f"Whamageddon {currentYear} Losses")
    plt.tight_layout()

    # Save figure to BytesIO
    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close(fig)

    await interaction.response.send_message(file=discord.File(fp=buf, filename="whamageddon_chart.png"))

@client.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.CommandNotFound):
        # Handle missing/unsynced commands
        await interaction.response.send_message("This command is not available yet (might be syncing). Please try again later.", ephemeral=True)
        return
    # For other errors, you can log them
    print(f"App command error: {error}")

threading.Thread(target=cli_loop, daemon=True).start()
client.run(token)
