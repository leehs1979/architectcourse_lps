import faust
import json
import websockets
from datetime import datetime, timedelta
from influxdb import InfluxDBClient
from dataclasses import asdict, dataclass

######################################################################
database_name = 'lps_test'
host = '172.16.1.109'
port = 8086
user = 'admin'
passwd = "citec!00"

client = InfluxDBClient(host, port, user, passwd)
client.switch_database(database_name)

print("db list : ", client.get_list_database())
print("measurement list : ", client.get_list_measurements())

######################################################################
app = faust.App(
    'StreamLogProcessor',
    broker='kafka://172.16.1.113:9092',
    topic_partitions=3,
    value_serializer='json'
)

# Parsed Record Template
# {'@timestamp': 1636502374.0, 'host': '172.16.1.101', 'user': '-', 'time': '10/Nov/2021:08:59:34 +0900', 
#  'method': 'GET', 'path': '/index.html', 'code': '200', 'size': '18'}
@dataclass
class StreamLog(faust.Record):
    time : str
    host : str
    user : str
    method : str
    #path : str
    code : str
    size : str

stream_log_topic = app.topic('lps_web1_apache', value_type=StreamLog)
stream_log_count = app.Table('stream_log_count', default=int).tumbling(timedelta(seconds=3))

######################################################################
# By default the changelog topic for a given Table has the format <app_id>-<table_name>-changelogs 
@app.agent(stream_log_topic)
async def count_stream_log_views(logs):
    async for log in logs.group_by(StreamLog.time):
    #async for log in logs:
        stream_log_count[log.time] += 1
        
        print(log)        
                
        #print(stream_log_views)
        #print(stream_log_count[log.time])
        #print(stream_log_count[log.time].value())
        
        # Time conversion for influxDB
        #tmp = '10/Nov/2021:08:59:34 +0900'
        tmp = log.time
        dt_datetime = datetime.strptime(tmp.split()[0],'%d/%b/%Y:%H:%M:%S')
        dt_datetime = dt_datetime.strftime("%Y-%m-%d %H:%M:%S")        
        
        # Making point for influxDB
        point = [
            {
                'measurement': 'access',
                'tags': {'server_id': log.host}, 
                'fields': {'host': log.host, 'user': user, 'method': log.method, 
                        #'path': log.path, 
                        'code': log.code, 'size': log.size},
                'time': dt_datetime
            },
        ]
        
        # InfluxDB insert
        client.write_points(points=point, protocol='json')
        
        # Websocket send
        async with websockets.connect("ws://172.16.1.106:9080/ws/chat/100/") as websocket:
            
            send_json = {                
                'message': log.time+','+ str(stream_log_count[log.time].value())
            }
            await websocket.send(json.dumps(send_json))
            result = await websocket.recv()
            print("received data : ", result)

# faust -A StreamLogProcessor worker -l info --web-port 6068
# pipe and filter도 추가되어야 한다.