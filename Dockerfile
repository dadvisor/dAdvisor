FROM python:3.7-alpine

# Install inspector
RUN apk add --update tcpdump curl tor
RUN wget https://github.com/prometheus/prometheus/releases/download/v2.8.1/prometheus-2.8.1.linux-amd64.tar.gz -O - | tar -xz
RUN echo "ControlPort 9051" > /etc/tor/torrc
RUN echo "CookieAuthentication 1" >> /etc/tor/torrc

RUN mv /usr/sbin/tcpdump /usr/bin/tcpdump
COPY . .
RUN pip install -r requirements.txt

EXPOSE 8800

CMD ["./start.sh"]