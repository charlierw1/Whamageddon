import discord
import threading
import asyncio
import dbAccess as db
from datetime import datetime
from datetime import date 
from discord.ext import commands
from discord import app_commands
from time import sleep
from json import dumps, loads

tokenfile = "../API-KEYS/Whamageddon.txt"
token = "API-KEY"
with open(tokenfile) as tf:
    token = tf.readline()
intents = discord.Intents.default()
intents.guilds = True
intents.message_content = True

client = commands.Bot(command_prefix = "yellglelelle", intents = intents)
"""
https://discord.com/oauth2/authorize?client_id=1440842599521845309&permissions=2252263737645120&integration_type=0&scope=bot+applications.commands invite 
"""

class CLI_Commands: #customise as needed
    help = "help"
    db_test = "dbtest"
    nuke_tables = "nuke" #only for table changes really
    exit = "exit"

cmds = f"""
    {CLI_Commands.help} - List all commands
    {CLI_Commands.db_test} - Test database access
    {CLI_Commands.exit} - Exit the program and shut down the bot
"""
rulesmes = """```
Whamageddon is a game where you have to go from the 1st to the 25th of December without hearing Last Christmas by Wham!
Other covers of Last Christmas are completely fine!
```"""

nowhitelist = "This channel is not whitelisted for use"

today = datetime.now()
currentYear = int(today.year)

if db.getYears(currentYear) is None:
    db.insertYear(currentYear)

if today.month == 12 and today.day < 26:
    db.setYears(currentYear, True)


def cli_loop():
    sleep(5)
    while True: #not working but will find a way
            cmd = input("Enter a command: ")
            match cmd:
                case CLI_Commands.help:
                    print(cmds)
                case CLI_Commands.db_test:
                    db.test()
                case CLI_Commands.exit:
                    db.closeConnection()
                    asyncio.run_coroutine_threadsafe(client.close(), client.loop)
                    exit()
                case _:
                    print("Unknown command, try 'help'\n\n")

def checkWhitelist(GuildID, ChannelID):
    if not db.getToggle(GuildID):
        return True
    else:
        channels = db.getChannels(GuildID)[0]
        return str(ChannelID) in channels

class WhamBot(commands.Bot):
    async def setup_hook(self):
        guild = discord.Object(id=1132340472363368570)

        # Sync guild-only commands
        synced = await self.tree.sync(guild=guild)
        print(f"Synced {len(synced)} guild commands.")

client = WhamBot(command_prefix="yellglelelle", intents=intents)


@client.event
async def on_ready():
    print("We have logged in as {0.user} ".format(client)) 
    activity = discord.Activity(name="Not listening to hit christmas song 'Last Christmas' by Wham!", type=3)               # this is to writing prefix in playing a game.(optional)
    await client.change_presence(status=discord.Status.online, activity=activity) # this is for making the status as an online and writing prefix in playing a game.(optional)                   



@client.tree.command(name="rules", description="Show the rules of Whamageddon")
@app_commands.guilds(1132340472363368570)
async def rules(interaction: discord.Interaction):
    if checkWhitelist(interaction.guild.id, interaction.channel_id):
        await interaction.response.send_message(rulesmes)
    else:
        await interaction.response.send_message(nowhitelist)

@client.tree.command(name="join", description="Join this years Whamageddon")
@app_commands.guilds(1132340472363368570)
@app_commands.choices(timezone = [
    app_commands.Choice(name="UTC-11", value="-11"),
    app_commands.Choice(name="UTC-10 (Hawaii)", value="-10"),
    app_commands.Choice(name="UTC-9 (Alaska)", value="-9"),
    app_commands.Choice(name="UTC-8 (Pacific)", value="-8"),
    app_commands.Choice(name="UTC-7 (Mountain)", value="-7"),
    app_commands.Choice(name="UTC-6 (Central)", value="-6"),
    app_commands.Choice(name="UTC-5 (Eastern)", value="-5"),
    app_commands.Choice(name="UTC-4 (Atlantic)", value="-4"),
    app_commands.Choice(name="UTC-3", value="-3"),
    app_commands.Choice(name="UTC-2", value="-2"),
    app_commands.Choice(name="UTC-1", value="-1"),

    app_commands.Choice(name="UTC±0 (UK / Portugal)", value="0"),

    app_commands.Choice(name="UTC+1 (CET)", value="1"),
    app_commands.Choice(name="UTC+2 (EET)", value="2"),
    app_commands.Choice(name="UTC+3 (Moscow / Turkey)", value="3"),
    app_commands.Choice(name="UTC+4 (UAE)", value="4"),
    app_commands.Choice(name="UTC+5 (Pakistan)", value="5"),
    app_commands.Choice(name="UTC+5:30 (India)", value="5.5"),
    app_commands.Choice(name="UTC+6 (Bangladesh)", value="6"),
    app_commands.Choice(name="UTC+7 (Thailand / Vietnam)", value="7"),
    app_commands.Choice(name="UTC+8 (China / Singapore)", value="8"),
    app_commands.Choice(name="UTC+9 (Japan / Korea)", value="9"),
    app_commands.Choice(name="UTC+10 (AEST)", value="10"),
    app_commands.Choice(name="UTC+11", value="11"),
    app_commands.Choice(name="UTC+12 (New Zealand)", value="12")
]
)
async def join(interaction: discord.Interaction, timezone: app_commands.Choice[str]):
    if checkWhitelist(interaction.guild.id, interaction.channel_id):
        GuildID = interaction.guild.id
        UserID = interaction.user.id
        if not db.checkGuild(GuildID):
            db.insertGuild(GuildID)
        if not db.checkUser(UserID):
            db.insertUser(UserID, timezone.value)
        if not db.checkAttempt(currentYear, UserID):
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
@app_commands.guilds(1132340472363368570)
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

        if not db.checkGuild(GuildID):
            db.insertGuild(GuildID)

        if not db.checkAttempt(currentYear, UserID):
            await interaction.response.send_message("You haven't done /join yet!")
            return

        db.addLoss(currentYear, date.today(), loss_reason, UserID)
        await interaction.response.send_message(f"Loss recorded: {loss_reason}")
    else:
        await interaction.response.send_message(nowhitelist)

@client.tree.command(name="toggle", description="Toggle the whitelist for allowed channels (limited to 5)")
@app_commands.checks.has_permissions(administrator=True)
@app_commands.guilds(1132340472363368570)
async def toggle(interaction: discord.Interaction):
    GuildID = interaction.guild.id
    await interaction.response.send_message(f"Whitelist enabled: {db.toggleWhitelist(GuildID)}")

@client.tree.command(name="whitelistadd", description="Whitelist a channel for Whamagededdon")
@app_commands.checks.has_permissions(administrator=True)
@app_commands.guilds(1132340472363368570)
@app_commands.describe(channel_id="Channel ID of Whitelisted Channel")
async def whitelistAdd(interaction: discord.Interaction, channel_id: str):
    GuildID = interaction.guild.id
    if client.get_channel(int(channel_id)) is None:
        print("FUUUUUUUUUUUUUUUUUUUUCK")
        return await interaction.response.send_message("Invalid Channel ID (channel doesn't exist)")
    channels = loads(db.getChannels(GuildID)[0])
    if channel_id in channels:
        await interaction.response.send_message("Channel already whitelisted.")
        return
    if len(channels) > 9:
        await interaction.response.send_message("Max whitelisted channels reached.")
        return
    else:
        channels.append(channel_id)
        db.setChannels(GuildID, dumps(channels))
        await interaction.response.send_message(f"Channel {channel_id} added to the whitelist.")
        return

@client.tree.command(name="whitelistremove", description="UnWhitelist a channel for Whamagededdon")
@app_commands.checks.has_permissions(administrator=True)
@app_commands.guilds(1132340472363368570)
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
@app_commands.guilds(1132340472363368570)
async def chart(interaction: discord.Interaction):
    if checkWhitelist(interaction.guild.id, interaction.channel_id):
        await interaction.response.send_message("This dont do nothing yet")
    else:
        await interaction.response.send_message(nowhitelist)

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
