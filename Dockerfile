FROM google/cadvisor:latest

# Install inspector
RUN apk add --update tcpdump curl git python3 nginx
RUN python3 -m ensurepip --upgrade
RUN mv /usr/sbin/tcpdump /usr/bin/tcpdump

# Install prometheus
RUN wget -qO- https://github.com/prometheus/prometheus/releases/download/v2.8.1/prometheus-2.8.1.linux-amd64.tar.gz | tar -xz
RUN mv prometheus-2.8.1.linux-amd64 prometheus

# Install grafana
RUN set -ex
RUN addgroup -S grafana
RUN adduser -S -G grafana grafana
RUN apk add --no-cache ca-certificates su-exec
RUN mkdir /tmp/setup
RUN wget -q -P /tmp/setup http://s3-us-west-2.amazonaws.com/grafana-releases/release/grafana-6.1.0.linux-amd64.tar.gz
RUN tar -xzf /tmp/setup/grafana-6.1.0.linux-amd64.tar.gz -C /tmp/setup --strip-components=1
RUN install -m 755 /tmp/setup/bin/grafana-server /usr/local/bin/
RUN install -m 755 /tmp/setup/bin/grafana-cli /usr/local/bin/
RUN mkdir -p /grafana/datasources /grafana/dashboards /grafana/data /grafana/logs /grafana/plugins /var/lib/grafana
RUN cp -r /tmp/setup/public /grafana/public
RUN chown -R grafana:grafana /grafana
RUN ln -s /grafana/plugins /var/lib/grafana/plugins
RUN grafana-cli plugins update-all
RUN rm -rf /tmp/setup



# Configuration
RUN git clone https://github.com/dAdvisor/containers-panel /grafana/plugins/containers-panel

COPY ./nginx.conf /etc/nginx/nginx.conf
COPY ./grafana/dashboard.json /grafana/dashboards
COPY ./grafana/dashboard.yaml /grafana/dashboards
COPY ./grafana/defaults.ini /grafana/conf/
COPY ./grafana/datasource.yaml /grafana/datasources/

COPY . .
RUN pip3 install --upgrade pip3
RUN pip3 install -r src/requirements.txt

EXPOSE 5000

ENTRYPOINT ["sh", "start.sh"]