import discord
from discord.ext import commands,tasks
from config import settings
from subprocess import Popen
from mcstatus import JavaServer
from numdeclination import NumDeclination
from asyncio import sleep


intents = discord.Intents.default()
intents.message_content = True


server = JavaServer.lookup("127.0.0.1:25565")
bot = commands.Bot(command_prefix=settings['prefix'], intents=intents, help_command=None)
nd = NumDeclination()

cooldown = False


def isServerOnline():
  try:
    JavaServer.lookup("127.0.0.1:25565").status()
    return True
  except:
    return False

@bot.event
async def on_ready():
    change_status.start()

@tasks.loop(seconds=15)
async def change_status():
    if not isServerOnline():
        activity = discord.Game(name="Оффлайн", type=3)
        await bot.change_presence(status=discord.Status.dnd, activity=activity)
    else:
        status = server.status()
        activity = discord.Game(name=f"Онлайн: {status.players.online} {nd.declinate(status.players.online,["игрок", "игрока", "игроков" ]).word}", type=3)
        await bot.change_presence(status=discord.Status.online, activity=activity)

@bot.command()
async def status(ctx):
    if isServerOnline():
        status = server.status()
        embed = discord.Embed(colour=discord.Color.green())
        embed.add_field(name="Сервер включён.", value=f"В данный момент на сервере {status.players.online} {nd.declinate(status.players.online,["игрок", "игрока", "игроков" ]).word} онлайн.")
        await ctx.send(embed=embed)
        #await ctx.message.delete()
    else:
        embed = discord.Embed(colour=discord.Color.red())
        embed.add_field(name="Сервер выключен.", value="Для запуска используй команду !start")
        await ctx.send(embed=embed)
        #await ctx.message.delete()

@bot.command()
async def list(ctx):
    if not isServerOnline():
        embed = discord.Embed(colour=discord.Color.red())
        embed.add_field(name="Сервер выключен.", value="Для запуска используй команду !start")
        await ctx.send(embed=embed)
        #await ctx.message.delete()
        return
    query = server.query()
    if query.players.names:
        embed = discord.Embed(colour=discord.Color.green())
        embed.add_field(name="Игроки онлайн:", value=f"{", " .join(query.players.names)}.")
        await ctx.send(embed=embed)
        #await ctx.message.delete()
    else:
        status = server.status()

        if not status.players.sample:
            embed = discord.Embed(colour=discord.Color.yellow())
            embed.add_field(name="Нет игроков на сервере.", value="Зайди первым!")
            await ctx.send(embed=embed)
            #await ctx.message.delete()
        else:
            a = ("Игроки онлайн: "+", ".join([player.name for player in status.players.sample]))
            await ctx.send(a)
            #await ctx.message.delete()

@bot.command()
async def help(ctx):
    embed = discord.Embed(title="Команды бота", colour=discord.Color.blue())
    embed.add_field(name="!start или !run", value="Запускает сервер, если он выключен.")
    embed.add_field(name="!status", value="Отображает статус сервера. Если сервер запущен, отображает количество игроков на нём.")
    embed.add_field(name="!list", value="Отображает список игроков на сервере на текущий момент.")
    await ctx.send(embed=embed)
    #await ctx.message.delete()

@bot.command(aliases=['run'])
async def start(ctx):
    global cooldown
    serverOnline = isServerOnline()
    if not serverOnline and not cooldown:
        cooldown = True
        embed = discord.Embed(colour=discord.Color.green())
        embed.add_field(name="Сервер", value="Сервер запускается. Примерное время запуска 15-20 секунд.")
        await ctx.send(embed=embed)
        #await ctx.message.delete()
        Popen("start run.bat", shell=True)
        await sleep(30)
        cooldown = False
    elif not serverOnline and cooldown:
        embed = discord.Embed(colour=discord.Color.yellow())
        embed.add_field(name="Сервер", value="Команда запуска сервера уже запущена. Ожидайте 30 секунд.")
        await ctx.send(embed=embed)
        #await ctx.message.delete()
    elif serverOnline:
        embed = discord.Embed(colour=discord.Color.red())
        embed.add_field(name="Сервер", value="Сервер уже запущен.")
        await ctx.send(embed=embed)
        #await ctx.message.delete()


bot.run(settings['token'])
