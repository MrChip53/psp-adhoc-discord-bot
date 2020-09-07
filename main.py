import os

import discord

import random
from xml.dom import minidom
import urllib.request, urllib.error, urllib.parse
from dotenv import load_dotenv

load_dotenv()
bot_token = os.getenv('DISCORD_TOKEN')

client = discord.Client()

@client.event
async def on_ready():
	print(f'{client.user} has connected to Discord!')
	
@client.event
async def on_message(message):
	if message.author == client.user:
		return

	webpageResponse = urllib.request.urlopen('https://www.socomftb2.com/status.xml')
	webpageContent = webpageResponse.read()
	
	webXML = minidom.parseString(webpageContent.decode("utf-8")) #See if we can change to .parse(url)
	
	gameList = webXML.getElementsByTagName('game')

	response = formatOnlineEmbed(gameList)

	if message.content == '!online':
		await message.channel.send('Online Players', embed=response)

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
		
		embedVar.add_field(name=game.attributes['name'].value, value='Players Online: ' + game.attributes['usercount'].value + '\n' + playerString, inline=True)
		
		
	return embedVar

client.run(bot_token)