import os

import discord
from discord.ext import commands

import random
from xml.dom import minidom
import urllib.request, urllib.error, urllib.parse
from dotenv import load_dotenv

load_dotenv()
bot_token = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='!')

@bot.event
async def on_ready():
	print(f'{bot.user} has connected to Discord!')
	
@bot.event	
async def on_member_join(member):
	pass
	
@bot.command()
async def online(ctx):
	async with ctx.typing():
	
		print('Online command received')
		webpageResponse = urllib.request.urlopen('https://www.socomftb2.com/status.xml')
		webpageContent = webpageResponse.read()
		
		webXML = minidom.parseString(webpageContent.decode("utf-8"))
		
		gameList = webXML.getElementsByTagName('game')
			
		response = formatOnlineEmbed(gameList)

		await ctx.send('Online Players', embed=response)

def formatOnlineEmbed(gameList):
	embedVar = discord.Embed()
	if len(gameList) < 1:
		embedVar.add_field(name='No games!', value='No players online!')
		return embedVar
		
	
	for game in gameList:
	
		playerList = game.getElementsByTagName('user')
		playerString = '```\n'
		
		for player in playerList:
			playerString = playerString + player.firstChild.nodeValue + '\n'
		
		playerString = playerString + '```'
		
		embedVar.add_field(name=game.attributes['name'].value, value='Players Online: ' + game.attributes['usercount'].value + '\n' + playerString, inline=False)
		
		
	return embedVar


#bot.add_command(online)

bot.run(bot_token)