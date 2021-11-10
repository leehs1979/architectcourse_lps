import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import time, uuid, re, csv, io

def parse(file_name, log_format):
    print('call def parse')
    
    log_line_header = ['id','log_line','fhour','fminute','fsecond','fip','freferer','fuser_agent',
                           'fstatus','ftime_taken','freserve1','freserve2','freserve3','created',
                           'frequest','fday','fmonth','fyear','fdate','ftime','fdatetime','fbyte', 'fextension']
    
    
    format_index = get_logformat_index(log_format, "apache")
    
    df_logs = None
    df_logs_all = None
    
    try:
            
        df_logs_all = pd.read_csv(file_name, encoding="utf-8", header=None, comment='#', delimiter="\0", error_bad_lines=False, na_filter=False)            
            
    except UnicodeDecodeError as ude:
        
        print('UnicodeDecodeError Occured! Trying again with another encoding = cp1252 : %s' % ude)    
        
        try:
            df_logs_all = pd.read_csv(file_name, encoding="cp1252", header=None, comment='#', delimiter="\0", error_bad_lines=False, na_filter=False)
        except Exception as uex:
            print('UnicodeDecodeError Occured AGAIN!')
            raise uex            
        
    except Exception as ex: 
        print('Error Occured while creating logdetail read_csv#2 whole lines : %s' % ex)            
        raise ex   
    
    try:           

            df_logs = pd.read_csv(file_name, encoding="utf-8", error_bad_lines=False, header=None, comment='#', delimiter="\s+", escapechar="\\", na_filter=False, quotechar='"')
            
    except UnicodeDecodeError as ude:
        
        print('UnicodeDecodeError Occured! Trying again with another encoding = cp1252 : %s' % ude)
        
        try:
            df_logs = pd.read_csv(file_name, encoding="cp1252", error_bad_lines=False, header=None, comment='#', delimiter="\s+", escapechar="\\", na_filter=False, quotechar='"')
        except Exception as uex:
            print('UnicodeDecodeError Occured AGAIN!')
            raise uex            
        
    except Exception as ex: 
        print('Error Occured while creating logdetail read_csv#1  : %s' % ex)
        raise ex                      
                
    df_logs['log_line'] = df_logs_all
    df_logs = setColumn(df_logs, "apache", log_format, format_index)
    
    #'freserve1', 'freserve2', 'freserve3'        
    df_logs['freserve1'] = ''
    df_logs['freserve2'] = ''
    df_logs['freserve3'] = ''
    
     #'created'
    datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')
    df_logs['created'] = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S.%f')
    
    df_time = pd.DataFrame()
    
    column_names = ['dummy','fday','fmonth','fyear','fhour','fminute','fsecond']

    time_index = format_index['t']
    df_datetime = df_logs[time_index].str.replace(pat='[\:\/\[-]', repl= r' ', regex=True)
    series = df_datetime.str.split(' ')
    df_time = pd.DataFrame(series.tolist(), columns=column_names)
    
    # 보완로직1 - 결측치 제거 : None있으면 해당 row 제거
    df_time.dropna(axis=0, inplace=True)

    # Time Adjust 적용하면 불필요    
    month_map = {
        'Jan' : '01', 'Feb' : '02', 'Mar' : '03', 'Apr' : '04', 'May' : '05', 'Jun' : '06',
        'Jul' : '07', 'Aug' : '08', 'Sep' : '09', 'Oct' : '10', 'Nov' : '11', 'Dec' : '12',
    }

    df_time['fmonth'] = df_time['fmonth'].apply(lambda x : month_map[x])
    
    # Add Columns : fdate YYYYMMDD(fyear+fmonth+fday), ftime hhmmss(fhour+fminute+fsecond), fdatetime(YYYYMMDDhhmmss)
    df_time['fdate'] = df_time['fyear'] + df_time['fmonth'] + df_time['fday']
    df_time['ftime'] = df_time['fhour'] + df_time['fminute'] + df_time['fsecond']
    df_time['fdatetime'] = df_time['fdate']+df_time['ftime']
        
    
    # fbyte 처리 : - 를 0으로 처리
    df_logs['fbyte'] = df_logs['fbyte'].apply(lambda x : 0 if x == '-' else x )      
    
    # fextension 처리 : frequest로부터 처리한다.
    # 정적파일 추출 : js, html, ico, jpg, png, bmp, otf, css
    p = re.compile('(.js|.html|.ico|.jpg|.png|.bmp|.otf|.css)\s', re.DOTALL )
    df_logs['fextension'] = df_logs['frequest'].apply(lambda x: p.findall(x)[0][1:] if len(p.findall(x)) > 0 else '-')
    
    df_logs = df_logs.rename_axis('id').reset_index()
    
    df_logs = pd.concat([df_logs, df_time], axis=1)    
    df_logs.dropna(axis=0, inplace=True)
    
    result_file_name = file_name+'.csv'
    
    df_logs[log_line_header].to_csv(result_file_name, index=False)
    
    return result_file_name
    
def get_logformat_index(log_format, format_kind):
    format_index = {}
    index = 0
    for tmp in log_format.split(sep=' '):
        
        if format_kind == 'apache' or format_kind == 'tomcat' or format_kind == 'webtob' or format_kind == 'IIS-NCSA':
            if tmp.find('Referer') != -1:
                format_index['Referer'] = index
            elif tmp.find('User-Agent') != -1:
                format_index['User-Agent'] = index
            elif tmp.find('X-Forwarded-For') != -1:
                format_index['X-Forwarded-For'] = index                    
            elif "%h" in tmp:
                format_index['h'] = index
            elif "%t" in tmp:
                format_index['t'] = index
                index = index + 1 # 하나 더 세야 한다.(apache 시간의 경우 [24/Dec/2019:13:54:26 +0900] 이런 형식이기 때문에)
            elif "%r" in tmp:
                format_index['r'] = index
            elif "%s" in tmp or "%>s" in tmp:
                format_index['s'] = index
            elif "%b" in tmp or "%B" in tmp:
                format_index['b'] = index
            elif "%D" in tmp:   # millisecond
                format_index['D'] = index
            elif "%T" in tmp:   # second
                format_index['T'] = index   
            
        index = index + 1 
        
    return format_index    

def setColumn(df_logs, format_kind, log_format, format_index):
    
    # if 'h' in log_format:
    if log_format.find('h') != -1:
        df_logs.rename(columns = {format_index['h'] : 'fip'}, inplace = True)
    else:
        #  %{X-Forwarded-For}i의 맨 앞은 사용자 IP, %h와 같이 사용하지 않을 것임   
        if log_format.find('X-Forwarded-For') != -1:
            df_logs['fip'] = df_logs[format_index['X-Forwarded-For']].str.split(',').str[0]            
        else:
            df_logs['fip'] = 'NA'
        
    # if 'r' in log_format:
    if log_format.find('r') != -1:
        df_logs.rename(columns = {format_index['r'] : 'frequest'}, inplace = True)
    else:           
        df_logs['frequest'] = 'NA'    

    # if 's' in log_format:
    if log_format.find('s') != -1:
        df_logs.rename(columns = {format_index['s'] : 'fstatus'}, inplace = True)
    else:
        df_logs['fstatus'] = 'NA'
        
    # bytes    
    if log_format.find('b') != -1 or log_format.find('B') != -1:
        df_logs.rename(columns = {format_index['b'] : 'fbyte'}, inplace = True)
    else:
        df_logs['fbyte'] = 0

    if log_format.find('Referer') != -1:
        df_logs.rename(columns = {format_index['Referer'] : 'freferer'}, inplace = True)
    else:
        df_logs['freferer'] = 'NA'
        
    if log_format.find('User-Agent') != -1:
        df_logs.rename(columns = {format_index['User-Agent'] : 'fuser_agent'}, inplace = True)
    else:
        df_logs['fuser_agent'] = 'NA'

    if log_format.find('%T') != -1:     # Second
        df_logs.rename(columns = {format_index['T'] : 'ftime_taken'}, inplace = True)

    elif log_format.find('%D') != -1:
        df_logs.rename(columns = {format_index['D'] : 'ftime_taken'}, inplace = True)
        
        # Tomcat, WebtoB의 경우 단위가 ms이므로 *1000 필요 df_logs['ftime_taken']
        if format_kind == 'tomcat' or format_kind == 'webtob':
            df_logs['ftime_taken'] = pd.to_numeric(df_logs['ftime_taken'], errors='coerce').fillna(0).mul(1000).astype(int)
    else:
        df_logs['ftime_taken'] = -1
        
    return df_logs