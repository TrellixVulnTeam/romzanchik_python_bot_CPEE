
from twitch_api_checker import get_stream_data
import os
from dotenv import load_dotenv
import asyncio
from discord.ext import commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='!')
date = ''
flag = False


@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')


@bot.command(name='FollowTwitch')
async def FollowTwitch(ctx, streamer):
    global flag
    await ctx.channel.send(f'Начато отслеживание канала: {streamer}')
    flag = False
    print(f'Начато отслеживание канала: {streamer}')
    global date
    try:
        loop_streamer = asyncio.get_event_loop()
        #print(f'loop: {loop_streamer},\ntask: {task_stream}')
        while flag == False:
            task_stream = await loop_streamer.create_task(get_stream_data(streamer))
            if task_stream and task_stream['Online'] and date != task_stream['StartTime']:
                game = task_stream['GameName']
                title = task_stream['StreamTitle']
                start_date = task_stream['StartTime']
                date = start_date
                print(f'{streamer} запустил(а) трансляцию: "{title}".\nИграем в {game}.\nВремя начала стрима: {start_date}.\nСсылка на трансляцию: https://www.twitch.tv/{streamer}')
                await ctx.channel.send(f'_ @everyone @here {title}.\nИграем в {game}.\nВремя начала стрима: {start_date}.\nСсылка на трансляцию:_ https://www.twitch.tv/{streamer}')
            else:
                await asyncio.sleep(15)
    except Exception as exc:
        print("Error: ", exc)


@bot.command(name='StopFollowingTwitch')
async def StopFollowingTwitch(ctx):
    global flag
    flag = True
    await ctx.channel.send(f'Останавлено отслеживание канала')
    print(f'Останавлено отслеживание канала')
    
bot.run(TOKEN)
