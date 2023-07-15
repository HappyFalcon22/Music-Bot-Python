import asyncio
import discord
from discord.ext import commands, tasks
import os
from dotenv import load_dotenv
import youtube_dl
from private_info import *

command_prefix = ">> "

ytdl_format_options = {
    'format': 'bestaudio/best',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'extractor_retries': 'auto',
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

load_dotenv()
DISCORD_TOKEN = os.getenv(BOT_TOKEN)
intents = discord.Intents().all()
client = discord.Client(intents = intents)
bot = commands.Bot(command_prefix = command_prefix, intents = intents)

youtube_dl.utils.bug_reports_message = lambda: ''

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = ""

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]
        filename = data['title'] if stream else ytdl.prepare_filename(data)
        return filename

@bot.command(name = "join")
async def join(ctx):
    if not ctx.message.author.voice:
        await ctx.send("***{}*** is not connected to a voice channel.".format(ctx.message.author.name))
        return
    else:
        channel = ctx.message.author.voice.channel
        await channel.connect()
        await ctx.send("***Ready for service.***")

@bot.command(name = "play")
async def play(ctx, url, title):
    server = ctx.message.guild
    voice_channel = server.voice_client
    async with ctx.typing():
        filename = await YTDLSource.from_url(url, loop=bot.loop)
        voice_channel.play(discord.FFmpegPCMAudio(executable = "C:\\Users\\admin\\Desktop\\My Lair\\Discord Bot Python\\Music-Bot-Python\\ffmpeg\\bin\\ffmpeg.exe", source=filename))
    await ctx.send(f'***Now playing :*** {title}')

@bot.command(name='pause', help='This command pauses the song')
async def pause(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        await voice_client.pause()
        await ctx.send("***Paused.***")
    else:
        await ctx.send("***The bot is not playing anything at the moment.***")

@bot.command(name='resume', help='Resumes the song')
async def resume(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_paused():
        await voice_client.resume()
        await ctx.send("Resumed. Enjoy !")
    else:
        await ctx.send("The bot was not playing anything before this. Use play_song command")

@bot.command(name='leave', help='To make the bot leave the voice channel')
async def leave(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_connected():
        await voice_client.disconnect()
        await ctx.send("***Goodbye***")
    else:
        await ctx.send("The bot is not connected to a voice channel.")

@bot.command(name='stop', help='Stops the song')
async def stop(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        await voice_client.stop()
        await ctx.send("***Stopped.***")
    else:
        await ctx.send("The bot is not playing anything at the moment.")

if __name__ == "__main__" :
    bot.run(BOT_TOKEN)
