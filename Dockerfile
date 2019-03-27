FROM python:3.7-alpine

# Install inspector
RUN apk add --update tcpdump
RUN apk add curl

RUN mv /usr/sbin/tcpdump /usr/bin/tcpdump
COPY . .
RUN pip install -r requirements.txt

EXPOSE 8800

CMD ["python", "start.py"]