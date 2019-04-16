FROM python:3.7-alpine

# Install inspector
RUN apk add --update tcpdump curl git
RUN mv /usr/sbin/tcpdump /usr/bin/tcpdump

# Install prometheus
RUN wget https://github.com/prometheus/prometheus/releases/download/v2.8.1/prometheus-2.8.1.linux-amd64.tar.gz -O - | tar -xz

# Install grafana
RUN set -ex
RUN addgroup -S grafana
RUN adduser -S -G grafana grafana
RUN apk add --no-cache ca-certificates libc6-compat su-exec
RUN mkdir /tmp/setup
RUN wget -P /tmp/setup http://s3-us-west-2.amazonaws.com/grafana-releases/release/grafana-6.1.0.linux-amd64.tar.gz
RUN tar -xzf /tmp/setup/grafana-6.1.0.linux-amd64.tar.gz -C /tmp/setup --strip-components=1
RUN install -m 755 /tmp/setup/bin/grafana-server /usr/local/bin/
RUN install -m 755 /tmp/setup/bin/grafana-cli /usr/local/bin/
RUN mkdir -p /grafana/datasources /grafana/dashboards /grafana/data /grafana/logs /grafana/plugins /var/lib/grafana
RUN cp -r /tmp/setup/public /grafana/public
RUN chown -R grafana:grafana /grafana
RUN ln -s /grafana/plugins /var/lib/grafana/plugins
RUN grafana-cli plugins update-all
RUN rm -rf /tmp/setup

# Install cAdvisor
RUN apk --no-cache add device-mapper findutils \
 && apk --no-cache add zfs --repository http://dl-3.alpinelinux.org/alpine/edge/main/ \
 && apk --no-cache add thin-provisioning-tools --repository http://dl-3.alpinelinux.org/alpine/edge/main/ \
 && curl -f -L -o  /etc/apk/keys/sgerrand.rsa.pub https://alpine-pkgs.sgerrand.com/sgerrand.rsa.pub \
 && curl -f -L -o  glibc-2.28-r0.apk https://github.com/sgerrand/alpine-pkg-glibc/releases/download/2.28-r0/glibc-2.28-r0.apk \ 
 && curl -f -L -o  glibc-bin-2.28-r0.apk https://github.com/sgerrand/alpine-pkg-glibc/releases/download/2.28-r0/glibc-bin-2.28-r0.apk \
 && apk add glibc-2.28-r0.apk glibc-bin-2.28-r0.apk \
 && /usr/glibc-compat/sbin/ldconfig /lib /usr/glibc-compat/lib \
 && rm glibc-2.28-r0.apk glibc-bin-2.28-r0.apk \
 && echo 'hosts: files mdns4_minimal [NOTFOUND=return] dns mdns4' >> /etc/nsswitch.conf \
 && rm -rf /var/cache/apk/*



# Grafana configuration
VOLUME /grafana/data

RUN grafana-cli plugins install simpod-json-datasource
RUN git clone https://github.com/dAdvisor/containers-panel /grafana/plugins/containers-panel

COPY ./grafana/dashboard.json /grafana/dashboards
COPY ./grafana/dashboard.yaml /grafana/dashboards
COPY ./grafana/defaults.ini /grafana/conf/
COPY ./grafana/datasource.yaml /grafana/datasources/

COPY . .
RUN pip install -r src/requirements.txt

EXPOSE 8800
EXPOSE 3000

CMD ["./start.sh"]