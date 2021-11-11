import faust
import json
from datetime import datetime, timedelta
import aiofiles
import asyncio

######################################################################
app = faust.App(
    'StreamLogProcessor',
    broker='kafka://172.16.1.113:9092',
    topic_partitions=3,
    value_serializer='raw'
)

stream_log_topic = app.topic('lps_web1_apache')
######################################################################
@app.agent(stream_log_topic)
async def log_to_file(logs):
    async for log in logs:   
        
        print(log)
        async with aiofiles.open('logsForValidation.txt', mode='a') as f:
            await f.write(str(log)+"\n")
  

# faust -A StreamLogFileForValidation worker -l info --web-port 6068