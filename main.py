import discord
from discord import app_commands
from discord.ext import commands
import requests

token = "API KEY"
prefix = "."
intents = discord.Intents.default()
intents.message_content = True

client = commands.Bot(command_prefix = prefix, intents = intents)
"""
https://discord.com/oauth2/authorize?client_id=1440842599521845309&permissions=2252263737645120&integration_type=0&scope=bot+applications.commands invite 
"""

@client.event
async def on_ready():
    print("We have logged in as {0.user} ".format(client)) 
    activity = discord.Activity(name="Not listening to hit christmas song 'Last Christmas' by Wham!", type=3)               # this is to writing prefix in playing a game.(optional)
    await client.change_presence(status=discord.Status.online, activity=activity) # this is for making the status as an online and writing prefix in playing a game.(optional)  
    try:
        synced = await client.tree.sync(guild=None)
        print(f"Synced {len(synced)} slash commands.")
    except Exception as e:
        print(e)                      

@client.tree.command(name="rules", description="Show the rules of Whamageddon")
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message("Hello! 👋")
                       
                            

                      
client.run(token)    
                            
                            
                            
