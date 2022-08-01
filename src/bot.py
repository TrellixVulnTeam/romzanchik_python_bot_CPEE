
from twitch_api_checker import get_stream_data
import os
from dotenv import load_dotenv
import asyncio
from discord.ext import commands
import dill

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='!')
date = {}
try:
    with open('cache/cached_data.pkl', 'rb') as f:
        cache_data = dill.load(f)
except Exception as e:
    cache_data = []
    print(f'Dill load failed: {e}')
print(cache_data)
tasks = {}

@bot.event
async def on_ready():
    global tasks
    global cache_data
    print(f'{bot.user.name} has connected to Discord and ready for work!')
    
    try:
        if cache_data:
            for i in cache_data:
                channel = bot.get_channel(i[0])
                tw_name = i[1]
                tasks[tw_name + str(i[0])] = asyncio.create_task(track_stream_and_send_message(channel, tw_name))
                await channel.send(f'Возобновлена работа по отслеживанию канала: {tw_name}')
    except Exception as e:
        print(f'Send failed: {e}')

async def track_stream_and_send_message(ctx, streamer):
    global date
    
    try:
        while True:
            task_stream = await get_stream_data(streamer)
            if task_stream and task_stream['Online'] and date.get(streamer, '') != task_stream['StartTime']:
                game = task_stream['GameName']
                title = task_stream['StreamTitle']
                start_date = task_stream['StartTime']
                date[streamer] = start_date
                #print(f'{streamer} запустил(а) трансляцию: "{title}".\nИграем в {game}.\nВремя начала стрима: {start_date}.\nСсылка на трансляцию: https://www.twitch.tv/{streamer}')
                await ctx.send(f'_ @everyone @here {title}.\nИграем в {game}.\nВремя начала стрима: {start_date}.\nСсылка на трансляцию:_ https://www.twitch.tv/{streamer}')
            else:
                await asyncio.sleep(15)
    except Exception as exc:
        print("Error: ", exc)


@bot.command(name='TrackStreamer', aliases=['TS', 'FollowTwitch', 'TrackOnline', 'TO'], help='Отслеживание онлайна twitch канала.')
async def TrackStreamer(ctx, tw_name):
    global cache_data
    global tasks
    if (ctx.channel.id, tw_name) not in cache_data:
        cache_data.append((ctx.channel.id, tw_name))
        try:
            with open('cache/cached_data.pkl', 'wb') as f:
                dill.dump(cache_data, f)
        except Exception as e:
            print(f'Dill dump failed: {e}')

        channel = bot.get_channel(ctx.channel.id)
        tasks[tw_name + str(ctx.channel.id)] = asyncio.create_task(track_stream_and_send_message(channel, tw_name))
        await ctx.channel.send(f'Начато отслеживание канала: {tw_name}')
        #print(f'Начато отслеживание канала: {tw_name}')
    else:
        await ctx.channel.send(f'{tw_name} уже отслеживается в данном канале!')
    
@bot.command(name='StopTracking', aliases=['ST', 'StopFollowTwitch'], help='Остановить отслеживание онлайна twitch канала.')
async def StopTracking(ctx, tw_name):
    global tasks
    global cache_data
    tasks[tw_name + str(ctx.channel.id)].cancel()

    try:
        del cache_data[cache_data.index((ctx.channel.id, tw_name))]
        with open('cache/cached_data.pkl', 'wb') as f:
            dill.dump(cache_data, f)

        tasks.pop(tw_name + str(ctx.channel.id))
        await ctx.channel.send(f'Остановлено отслеживание канала : {tw_name}')
    except Exception as e:
        print(f'Update dump failed: {e}')

@bot.command(name='ShowFollowedChannels', aliases=['SFC', 'DisplayTrackList', 'DTL'], help='Показать отслеживаемые каналы в данном чате.')
async def ShowFollowedChannels(ctx):
    global tasks
    for key in tasks.keys():
        if key.endswith(f'{ctx.channel.id}'):
            channel = key.replace(f'{ctx.channel.id}', '')
            await ctx.channel.send(f'Отслеживаемый канал в данном чате: {channel}')
    
    

bot.run(TOKEN)