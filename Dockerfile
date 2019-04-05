FROM python:3.7-alpine

# Install inspector
RUN apk add --update tcpdump curl tor
RUN wget https://github.com/prometheus/prometheus/releases/download/v2.8.1/prometheus-2.8.1.linux-amd64.tar.gz -O - | tar -xz
RUN echo "ControlPort 9051" > /etc/tor/torrc
RUN echo "CookieAuthentication 1" >> /etc/tor/torrc

RUN set -ex \
 && addgroup -S grafana \
 && adduser -S -G grafana grafana \
 && apk add --no-cache libc6-compat ca-certificates su-exec \
 && mkdir /tmp/setup \
 && wget -P /tmp/setup http://s3-us-west-2.amazonaws.com/grafana-releases/release/grafana-6.1.0.linux-amd64.tar.gz \
 && tar -xzf /tmp/setup/grafana-6.1.0.linux-amd64.tar.gz -C /tmp/setup --strip-components=1 \
 && install -m 755 /tmp/setup/bin/grafana-server /usr/local/bin/ \
 && install -m 755 /tmp/setup/bin/grafana-cli /usr/local/bin/ \
 && mkdir -p /grafana/datasources /grafana/dashboards /grafana/data /grafana/logs /grafana/plugins /var/lib/grafana \
 && cp -r /tmp/setup/public /grafana/public \
 && chown -R grafana:grafana /grafana \
 && ln -s /grafana/plugins /var/lib/grafana/plugins \
 && grafana-cli plugins update-all \
 && rm -rf /tmp/setup

VOLUME /grafana/data

COPY ./defaults.ini /grafana/conf/

RUN mv /usr/sbin/tcpdump /usr/bin/tcpdump
COPY . .
RUN pip install -r requirements.txt

EXPOSE 8800, 3000

CMD ["./start.sh"]