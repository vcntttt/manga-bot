import requests
import discord
import re
import csv
from discord.ext import commands, tasks
from bs4 import BeautifulSoup
from env import BOT_TOKEN, CHANNEL_ID

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="&", intents=intents)
headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
patron = r'Capítulo (\d+)'

def loadCSV():
  mangas = []
  with open ('mangas.csv','r',encoding='utf-8') as file:
    reader = csv.DictReader(file)
    for row in reader:
      mangas.append({
        'manga': row['manga'],
        'url': row['url'],
        'lastCapRegistered': int(row['lastCapRegistered']),
      })
  return mangas

async def checkCap(manga):
  response = requests.get(manga['url'], headers=headers)
  soup = BeautifulSoup(response.text, 'html.parser')
  lastCapElement = soup.find('a', class_='btn-collapse')
  if lastCapElement and lastCapElement.text:
    lastCap = lastCapElement.text
    match = re.search(patron, lastCap)
    return int(match.group(1)) if match else None
  
def updateCSV(mangas):
  with open('mangas.csv', 'w', newline='', encoding='utf-8') as file:
    fieldnames = ['manga', 'url', 'lastCapRegistered']
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()
    for manga in mangas:
      writer.writerow(manga)

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    scheduledCheck.start()

@tasks.loop(minutes=1)
async def scheduledCheck():
  channel = bot.get_channel(int(CHANNEL_ID))
  if channel:
    print('Checking...')
    await channel.send('Checking...')
    mangas = loadCSV()
    for manga in mangas:
      lastCap = await checkCap(manga)
      if lastCap and lastCap > manga['lastCapRegistered']:
        await channel.send(f'Nuevo capitulo de {manga["manga"]}: {lastCap}')
        manga['lastCapRegistered'] = lastCap
      updateCSV(mangas)



bot.run(BOT_TOKEN)