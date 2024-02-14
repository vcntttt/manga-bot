import requests
import discord
import re
import csv
from discord.ext import commands, tasks
from bs4 import BeautifulSoup
from env import BOT_TOKEN

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)
headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
patron = r'Capítulo (\d+)'

mangas = []
with open("mangas.csv", "r", encoding="utf-8") as file:
  reader = csv.DictReader(file)
  for row in reader:
     mangas.append({
        'manga': row['manga'],
        'url': row['url'],
        'ultimoCapRegistrado': int(row['ultimoCapRegistrado'])
     })

def checkCap(manga, lastCapRegistered):
    response = requests.get(manga['url'], headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    lastCapElement = soup.find('a', class_='btn-collapse')
    lastCapText = lastCapElement.text
    match = re.search(patron, lastCapText)
    lastCap = match.group(1) if match else "Número de capítulo no encontrado"
    return manga['manga'] + ': ' + lastCap if int(lastCap) != int(lastCapRegistered) else manga['manga'] + ': ' + 'No hay nuevos capítulos'

if __name__ == "__main__":
    for manga in mangas:
        print(checkCap(manga, manga['ultimoCapRegistrado']))

# @tasks.loop(minutes=1)
# async def scheduledCheck(ctx):
#   channel = bot.get_channel(1109648180297089065)
#   if channel:
#     for url in mangas:
#       ultimoCapRegistrado = ultimocap[url]
#       lastCapText = checkCap(url, ultimoCapRegistrado)
#       await channel.send(f'Último capítulo de {url}: {lastCapText}, registrado: {ultimoCapRegistrado}')

# @scheduledCheck.before_loop
# async def before_scheduledCheck():
#     print('Esperando a que el bot esté listo...')
#     await bot.wait_until_ready()

# bot.run(BOT_TOKEN)
