import discord
import threading
import asyncio
from discord.ext import commands
from time import sleep

tokenfile = "../API-KEYS/Whamageddon.txt"
token = "API-KEY"
with open(tokenfile) as tf:
    token = tf.readline()
intents = discord.Intents.default()
intents.message_content = True
cli = False

client = commands.Bot(command_prefix = "", intents = intents)
"""
https://discord.com/oauth2/authorize?client_id=1440842599521845309&permissions=2252263737645120&integration_type=0&scope=bot+applications.commands invite 
"""

class CLI_Commands:
    help = "help"
    exit = "exit"
    

cmds = f"""
    {CLI_Commands.help} - List all commands
    {CLI_Commands.exit} - Exit the program and shut down the bot
"""
rulesmes = """```
Whamageddon is a game where you have to go from the 1st to the 25th of December without hearing Last Christmas by Wham!
Other covers of Last Christmas are completely fine!
```"""
def cli_loop():
    sleep(5)
    while True: #not working but will find a way
            cmd = input("Enter a command: ")
            match cmd:
                case CLI_Commands.help:
                    print(cmds)
                case CLI_Commands.exit:
                    asyncio.run_coroutine_threadsafe(client.close(), client.loop)
                    exit()
                case unknown_command:
                    print("Unknown command, try 'help'\n\n") 

@client.event
async def on_ready():
    print("We have logged in as {0.user} ".format(client)) 
    activity = discord.Activity(name="Not listening to hit christmas song 'Last Christmas' by Wham!", type=3)               # this is to writing prefix in playing a game.(optional)
    await client.change_presence(status=discord.Status.online, activity=activity) # this is for making the status as an online and writing prefix in playing a game.(optional)  
    try:
        synced = await client.tree.sync(guild=None)
        print(f"Synced {len(synced)} slash commands.")
        cli = True
    except Exception as e:
        print(e)                   

@client.tree.command(name="rules", description="Show the rules of Whamageddon")
async def rules(interaction: discord.Interaction):
    await interaction.response.send_message(rulesmes)

@client.tree.command(name="join", description="Join this years Whamageddon")
async def join(interaction: discord.Interaction):
    await interaction.response.send_message("This dont do nothing yet")

@client.tree.command(name="out", description="Declare yourself as having lost this years Whamageddon")
async def out(interaction: discord.Interaction):
    await interaction.response.send_message("This dont do nothing yet")

@client.tree.command(name="blacklist", description="Blacklist a channel for Whamagededdon")
async def out(interaction: discord.Interaction):
    await interaction.response.send_message("This dont do nothing yet")

@client.tree.command(name="whitelist", description="Whitelist a channel for Whamagededdon")
async def out(interaction: discord.Interaction):
    await interaction.response.send_message("This dont do nothing yet")

@client.tree.command(name="chart", description="Show a chart of the current state of Whamageddon in your Guild")
async def out(interaction: discord.Interaction):
    await interaction.response.send_message("This dont do nothing yet")

threading.Thread(target=cli_loop, daemon=True).start()

client.run(token)
