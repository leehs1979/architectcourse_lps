# pull official base image
FROM python:3.7.10-buster

# set work directory
WORKDIR /code

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt /code/
RUN pip install -r requirements.txt

# copy project
#COPY . /code/
COPY ./StreamLogProcessorForPod.py /code/

#CMD ["python", "app.py"]
CMD ["faust","-A","StreamLogProcessorForPod","worker","-l","info","--web-port","6068"]