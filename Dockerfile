FROM python:alpine
RUN pip install paho-mqtt
COPY main.py /
CMD ["python", "-u", "main.py"]
