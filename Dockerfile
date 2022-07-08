FROM python:3.8.5

RUN apt-get update
RUN apt-get install ffmpeg libsm6 libxext6  -y

COPY requirements.txt /sprite_detection/requirements.txt
RUN pip3 install -r /sprite_detection/requirements.txt

COPY ./sprite_detection /sprite_detection

CMD [ "python", "sprite_detection/run.py"]
