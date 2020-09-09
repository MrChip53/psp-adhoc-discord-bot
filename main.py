import os

import discord
from discord.ext import commands, tasks

import random
from xml.dom import minidom
import urllib.request, urllib.error, urllib.parse
from dotenv import load_dotenv
import re

def getGamePlayers(webXML, gameName):
	gameList = webXML.getElementsByTagName('game')
	
	for game in gameList:
		if re.search(gameName, game.attributes['name'].value) != None:
			return game.attributes['usercount'].value
	
	return None
		

def getWebXML():
	webpageResponse = urllib.request.urlopen('https://www.socomftb2.com/status.xml')
	webpageContent = webpageResponse.read()
		
	webXML = minidom.parseString(webpageContent.decode("utf-8"))
	return webXML

def loadGameDictionary(dictionaryPath):
	dictionaryFile = open(dictionaryPath, 'r')
	Lines = dictionaryFile.readlines()
	
	for line in Lines:
		line = line.strip()
		
		searchId = re.search('(?<=\{)(.*?)(?=\})', line)
		
		gameName = line[0:searchId.span()[0] - 2]
		gameId = re.sub('-', '', searchId.group())
		
		g_gameDictionary[gameId] = gameName;
		
load_dotenv('ftb_discord.env')
load_dotenv()

g_gameDictionary={}

g_TEST_CHANNEL = int(os.getenv('CHAN_DISCORDBOTS'))

loadGameDictionary('psp-game-ids.txt')

bot_token = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='!')

@tasks.loop(minutes=10.0)
async def monitor_ftbb():
	webXML = getWebXML()
	
	players = getGamePlayers(webXML, 'Fireteam Bravo 2')
	
	if players is not None:
		channel = bot.get_channel(g_TEST_CHANNEL)
		await channel.send(players + ' player(s) are on FTB2! Come join in on the fun!')

@bot.event
async def on_ready():
	print(f'{bot.user} has connected to Discord!')
	await monitor_ftbb.start()
	
@bot.event	
async def on_member_join(member):
	pass
	
@bot.command(pass_context=True, aliases=['who', 'wo'])
async def online(ctx):
	async with ctx.typing():
	
		print('Online command received')
		webXML = getWebXML()
		
		prometheus = webXML.getElementsByTagName('prometheus')
		
		gameList = webXML.getElementsByTagName('game')
			
		response = formatOnlineEmbed(gameList)

		totalPlayers = prometheus[0].attributes['usercount'].value

		if int(totalPlayers) == 1:
			totalPlayersStr = ' player connected'
		else:
			totalPlayersStr = ' players connected'
		
		await ctx.send(totalPlayers + totalPlayersStr, embed=response)

def formatOnlineEmbed(gameList):
	embedVar = discord.Embed()
	if len(gameList) < 1:
		embedVar.add_field(name='No games!', value='No players online!')
		return embedVar
		
	gameNum = 0
	for game in gameList:
		gameNum += 1
		playerList = game.getElementsByTagName('user')
		playerString = '```\n'
		
		for player in playerList:
			playerString = playerString + player.firstChild.nodeValue + '\n'
		
		playerString = playerString + '```'
		
		if len(gameList) > 1 and gameNum < len(gameList):
			playerString += '\n\u200B'
		
		gameName = game.attributes['name'].value
		
		if re.search('^[A-Za-z]{4}(?:|[0-9_]{5})$', gameName) != None:
			gameName = g_gameDictionary[gameName]
		
		onlinePlayers = game.attributes['usercount'].value
		
		if int(onlinePlayers) == 1:
			onlinePlayersStr = ' player'
		else:
			onlinePlayersStr = ' players'
		
		embedVar.add_field(name=gameName, value=onlinePlayers + onlinePlayersStr + '\n' + playerString, inline=False)
		
		
	return embedVar
	
def isNotTestChannel(id):
	if id is not g_TEST_CHANNEL:
		return True
	else:
		return False

bot.run(bot_token)