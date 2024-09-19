import discord
from discord.ext import commands,tasks
from config import settings
from subprocess import Popen
from mcstatus import JavaServer
from numdeclination import NumDeclination


def isServerOnline():
  try:
    JavaServer.lookup("127.0.0.1:25565").status()
    return True
  except:
    return False

nd = NumDeclination()

intents = discord.Intents.default()
intents.message_content = True


server = JavaServer.lookup("127.0.0.1:25565")
bot = commands.Bot(command_prefix=settings['prefix'], intents=intents)

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
        embed.add_field(name="Сервер включён", value=f"В данный момент на сервере {status.players.online} {nd.declinate(status.players.online,["игрок", "игрока", "игроков" ]).word} онлайн")
        await ctx.send(embed=embed)
        await ctx.message.delete()
    else:
        embed = discord.Embed(colour=discord.Color.red())
        embed.add_field(name="Сервер выключен", value="=(")
        await ctx.send(embed=embed)
        await ctx.message.delete()

@bot.command()
async def list(ctx):
    if not isServerOnline():
        embed = discord.Embed(colour=discord.Color.red())
        embed.add_field(name="Сервер выключен", value="=(")
        await ctx.send(embed=embed)
        await ctx.message.delete()
        return
    query = server.query()
    if query.players.names:
        embed = discord.Embed(colour=discord.Color.green())
        embed.add_field(name="Игроки онлайн:", value=f"{", " .join(query.players.names)}")
        await ctx.send(embed=embed)
        await ctx.message.delete()
        print("Игроки онлайн:", ", ".join(query.players.names))
    else:
        status = server.status()

        if not status.players.sample:
            embed = discord.Embed(colour=discord.Color.yellow())  # ,color=Hex code
            embed.add_field(name="Нет игроков на сервере", value="=/")
            await ctx.send(embed=embed)
            await ctx.message.delete()
        else:
            a = ("Игроки онлайн: "+", ".join([player.name for player in status.players.sample]))
            await ctx.send(a)
            await ctx.message.delete()

@bot.command()
async def start(ctx):
    Popen("start run.bat", shell=True)


bot.run(settings['token'])
