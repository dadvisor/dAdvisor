#!/bin/sh
set -e

./prometheus/prometheus --web.external-url http://localhost:14102/prometheus/ &

if [[ "$(stat -c "%U:%G" /grafana/data)" != grafana:grafana ]]; then
	chown grafana:grafana /grafana/data
fi

# debug command
cd /grafana/plugins/containers-panel && git pull && cd /

/usr/bin/cadvisor --port 14104 &
su-exec grafana grafana-server --homepath=/grafana &

nginx
python3 -u src/main.py