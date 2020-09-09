import os

import discord
from discord.ext import commands

import random
from xml.dom import minidom
import urllib.request, urllib.error, urllib.parse
from dotenv import load_dotenv
import re

def loadGameDictionary(dictionaryPath):
	dictionaryFile = open(dictionaryPath, 'r')
	Lines = dictionaryFile.readlines()
	
	for line in Lines:
		line = line.strip()
		
		searchId = re.search('(?<=\{)(.*?)(?=\})', line)
		
		gameName = line[0:searchId.span()[0] - 2]
		gameId = re.sub('-', '', searchId.group())
		
		g_gameDictionary[gameId] = gameName;

g_gameDictionary={}

load_dotenv()

loadGameDictionary('psp-game-ids.txt')

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
		
		prometheus = webXML.getElementsByTagName('prometheus')
		
		gameList = webXML.getElementsByTagName('game')
			
		response = formatOnlineEmbed(gameList)

		totalPlayers = prometheus[0].attributes['usercount'].value

		await ctx.send('Total Players Online: ' + totalPlayers, embed=response)

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
		
		gameName = game.attributes['name'].value
		
		if re.search('^[A-Za-z]{4}(?:|[0-9_]{5})$', gameName) != None:
			gameName = g_gameDictionary[gameName]
		
		embedVar.add_field(name=gameName, value='Players Online: ' + game.attributes['usercount'].value + '\n' + playerString, inline=False)
		
		
	return embedVar
	
def parseGameId(gameId):
	pass

#bot.add_command(online)

bot.run(bot_token)