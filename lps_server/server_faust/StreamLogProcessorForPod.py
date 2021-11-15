import faust
from datetime import datetime, timedelta
from dataclasses import asdict, dataclass
import math

######################################################################
app = faust.App(
    'StreamLogProcessor',
    broker='kafka://my-kafka.default.svc.cluster.local:9092',
    topic_partitions=3,
    value_serializer='json'
)

# Parsed Record Template
# {'timestamp': 1636502374.0, 'host': '172.16.1.101', 'user': '-', 'time': '10/Nov/2021:08:59:34 +0900', 
#  'method': 'GET', 'path': '/index.html', 'code': '200', 'size': '18'}
@dataclass
class StreamLog(faust.Record):
    timestamp : str
    time : str
    host : str
    user : str
    method : str
    code : str
    size : str
 

stream_log_topic = app.topic('lps_web1_apache', value_type=StreamLog)
stream_log_count = app.Table('stream_log_count', default=int).tumbling(timedelta(seconds=3))

@app.agent(stream_log_topic)
async def count_stream_log_views(logs):
    async for log in logs.group_by(StreamLog.time):
        stream_log_count[log.time] += 1
        
        print(log)        
        print(stream_log_count[log.time].value())
        
        # CPU 과부하 연산
        x = 0.0001
        for cnt in (1,1000000,1):
            x += math.sqrt(x)
        
        print("OK!")
        
# faust -A StreamLogProcessorForPod worker -l info --web-port 6068