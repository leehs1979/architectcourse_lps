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
# {'timestamp': 1636502374.0, 'host': '172.16.1.101', 'user': '-', 'time': '10/Nov/2021:08:59:34 +0900', 
#  'method': 'GET', 'path': '/index.html', 'code': '200', 'size': '18'}
@dataclass
class StreamLog(faust.Record):
    timestamp : str
    time : str
    host : str
    user : str
    method : str
    #path : str
    code : str
    size : str
    
class StreamLogBuffer:

    def __init__(self):
        self.pending = []
        self.total = 0

    def flush(self):

        self.pending.clear()
        print('TOTAL NOW: %r' % self.total)

    def add(self, coord):
        self.pending.append(coord)
        self.total += 1
        
    def get_last_item(self):
        if len(self.pending) > 0:
            #print(self.pending)
            return self.pending[-1]
        else:
            return None
        
buffer = StreamLogBuffer()    

stream_log_topic = app.topic('lps_web1_apache', value_type=StreamLog)
######################################################################
# By default the changelog topic for a given Table has the format <app_id>-<table_name>-changelogs 
stream_log_count = app.Table('stream_log_count', default=int).tumbling(timedelta(seconds=3))

@app.agent(stream_log_topic)
async def count_stream_log_views(logs):
    async for log in logs.group_by(StreamLog.time):
        stream_log_count[log.time] += 1
        
        print(log)        
        print(stream_log_count[log.time].value())
        
        stream_timestamp = datetime.fromtimestamp(log.timestamp).strftime("%Y-%m-%d %H:%M:%S")
        
        coord_json = {                
            'message': '(x, y) = ('+stream_timestamp+', '+ str(stream_log_count[log.time].value())+' )'
        }
        
        buffer.add(coord_json)        
        
@app.timer(interval=3.0)
async def send_ws():   
    
    print("buffer.get_last_item() : ", buffer.get_last_item())
    send_json = buffer.get_last_item()
    
    if send_json is not None and len(send_json) > 0:
    
        # Websocket send
        async with websockets.connect("ws://172.16.1.106:9080/ws/chat/100/") as websocket:
                        
            await websocket.send(json.dumps(send_json))
            result = await websocket.recv()
            print("received data : ", result)
            
            buffer.flush()

# faust -A StreamLogProcessor worker -l info --web-port 6068
# pipe and filter도 추가되어야 한다.
######################################################################
#@app.agent(stream_log_topic)
#async def log_to_influxdb(logs):
#    async for log in logs:        
#       
#        print("[INFLUXDB] log : ", log)
         # Time conversion for influxDB
         #tmp = '10/Nov/2021:08:59:34 +0900'
         #tmp = log.time
         #dt_datetime = datetime.strptime(tmp.split()[0],'%d/%b/%Y:%H:%M:%S')
         #dt_datetime = dt_datetime.strftime("%Y-%m-%d %H:%M:%S")  
#   
#        # Making point for influxDB
#        point = [
#            {
#                'measurement': 'access',
#                'tags': {'server_id': log.host}, 
#                'fields': {'host': log.host, 'user': user, 'method': log.method, 
#                        #'path': log.path, 
#                        'code': log.code, 'size': log.size},
#                'time': datetime.fromtimestamp(log.timestamp).strftime("%Y-%m-%d %H:%M:%S.%f")
#            },
#        ]
#        
#        # InfluxDB insert
#        client.write_points(points=point, protocol='json')        

# faust -A StreamLogProcessor worker -l info --web-port 6068