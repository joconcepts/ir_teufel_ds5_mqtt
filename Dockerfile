FROM python:alpine
RUN python -m pip install --upgrade pip
RUN pip3 install paho-mqtt
COPY main.py /
CMD ["python", "-u", "main.py"]
