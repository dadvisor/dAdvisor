FROM python:3.7-alpine

# Install inspector
RUN apk add --update tcpdump curl
RUN wget https://github.com/prometheus/prometheus/releases/download/v2.8.1/prometheus-2.8.1.linux-amd64.tar.gz -O - | tar -xz

RUN mv /usr/sbin/tcpdump /usr/bin/tcpdump
COPY . .
RUN pip install -r requirements.txt

EXPOSE 8800

CMD ["python", "main.py"]