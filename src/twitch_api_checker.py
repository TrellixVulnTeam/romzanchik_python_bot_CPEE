# %%
import asyncio
from datetime import datetime
from dateutil import tz

async def get_stream_data(ChannelName: str):
   '''
   Check Twich stream online or not
   This is one of the route where Twich expose data, 
   They have many more: https://dev.twitch.tv/docs
   '''
   import requests
   import os
   from dotenv import load_dotenv

   load_dotenv()
   twitch_token = os.getenv('TWITCH_TOKEN')
   twitch_client_id = os.getenv('TWITCH_CLIENT_ID')

   endpoint = "https://api.twitch.tv/helix/streams?"

   headers = {'Authorization': f'Bearer {twitch_token}', 'Client-ID': twitch_client_id}

   params = {"user_login": ChannelName}
   try:
      response = (requests.get(endpoint, params=params, headers=headers)).json()
      #print(response)
      if 'data' in response:
         if response['data'] != [] and response['data'][0]['type'] == 'live':
            data = response['data'][0]
            start_time = data['started_at']
            from_zone = tz.gettz('UTC')
            to_zone = tz.gettz('Europe/Moscow')
            utc = datetime.strptime(start_time, '%Y-%m-%dT%H:%M:%SZ')
            utc = utc.replace(tzinfo=from_zone)
            msk = utc.astimezone(to_zone)

            return {'Online': True, 'UserName': ChannelName, 'GameName': data['game_name'], 'StreamTitle': data['title'], 'StartTime': msk.ctime()}
   except Exception as e:
      print("Error checking user: ", e)
   return False
#print(IsTwitchLive('yakutyan_'))
# %%