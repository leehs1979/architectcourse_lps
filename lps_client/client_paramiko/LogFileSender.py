import paramiko
import time
import psutil

print("paramiko")

# Set properties : LPSClient에서 실행해야 함
# LPS 서버정보
host = "172.16.1.106"
port = 22

id = 'app'
#id = 'root'
pwd = 'citec!00'

localpath = "/home/app/"
remotepath = "/home/app/"

filename = "HOM1-W-F11_1GB.log"
#filename = "HOM1-W-F11.log.gz"

paramiko.util.log_to_file(localpath+'sftp.log')

# TODO: System Check
psutil.cpu_percent()

#psutil.virtual_memory().percent
#psutil.virtual_memory().available * 100 / psutil.virtual_memory().total

print('memory % used:', psutil.virtual_memory()[2])

try:
    
    start = time.time()
    
    transport = paramiko.transport.Transport(host, port)
    
    print(transport.getpeername())
    
    # Connect
    transport.connect(username=id, password=pwd)
    
    sftp = paramiko.SFTPClient.from_transport(transport)    
    
    # Upload
    sftp.put(localpath + filename, remotepath + filename)
    
    # Download
    #sftp.get(remotepath + filename, localpath + filename)
    
    print("Duration : %s" % (time.time() - start))
    
    # TODO: 업로드 완료 후 LPS Parsing Logic 호출 by REST API
     
    
except Exception as ex:
    print('Error Occured', ex)
      
finally:
    sftp.close()
    transport.close()