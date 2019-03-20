FROM google/cadvisor:latest

# Install inspector
RUN apk add --update tcpdump

# Install pip and python
RUN apk add --no-cache python3
RUN apk add --update py-pip
RUN pip install --upgrade pip
RUN mv /usr/sbin/tcpdump /usr/bin/tcpdump
COPY . .
RUN pip install -r requirements.txt

EXPOSE 8080 8800

ENTRYPOINT ["./start.sh"]