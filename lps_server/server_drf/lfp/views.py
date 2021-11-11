from django.shortcuts import render
import time, uuid, re, csv, io

from lfp.models import LogFileProcessor
from lfp.serializers import LogFileProcessorSerializer

from rest_framework.response import Response
from rest_framework import renderers
from rest_framework import viewsets, status

#from postgres_copy import CopyManager
#import copy
import numpy as np
import pandas as pd

from django.conf import settings
import logging

from comm import parser

logger = logging.getLogger(__name__)

# Create your views here.
class LogFileProcessorViewSet(viewsets.ModelViewSet):

    queryset = LogFileProcessor.objects.all()
    serializer_class = LogFileProcessorSerializer

    #filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    #filterset_fields = ['creator']
    #search_fields = ['creator']

    # Parsing 로직
    def create(self, request, *args, **kwargs):
            
        if settings.DEBUG:
    	    logger.debug("LogFileProcessorViewSet : %s !!" % "create" ) # 여기먼저 확인

        start = time.time()
        response = {}
        
        try:
            # 대용량 파일 파싱 테스트
            file_path = "/home/app/"
            #file_name = file_path + "HOM1-W-F11_SampleForTest.log"
            file_name = file_path + "HOM1-W-F11_1GB.log"
            log_format = "%h %{X-Forwarded-For}i %l %u %v %t %r %>s %B %{Referer}i %{User-Agent}i %{JSESSIONID}C %a %{env}e %f %p %D"
            
             # 파싱
            print('[START] PARSE')            
            result_filen_name = parser.parse(file_name, log_format)
            print("[END] PARSE result: ", result_filen_name)
           
            # DB 저장 (Options)
            # postgresql copy 실행                
            #LogDetail_dynamic.objects.model.objects = CopyManager()
            #LogDetail_dynamic.objects.model = ModelSchema.objects.get(name=model_name).as_model()
            
            #for filename in resultFiles:
            #    LogDetail_dynamic.objects.from_csv(filename, delimiter=',', encoding="utf-8")

            print("Total Processing Time : %s sec" % (time.time() - start))
            
            if settings.DEBUG:
                logger.debug("To DB, Total Duration : %s sec" % (time.time() - start))
            
            response = {'message': 'logdetail created successfully.', 'processing_time': round(time.time() - start, 3) }
                
            return Response(response, status = status.HTTP_200_OK)
        
        except Exception as ex: 
            logger.error('Error Occured while creating : %s' % ex)
            
            response = {'message': 'creation failed.'}            
            return Response(response, status = status.HTTP_500_INTERNAL_SERVER_ERROR)