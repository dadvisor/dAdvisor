#!/bin/sh
set -e

mkdir /prometheus
./prometheus-*/prometheus &

if [[ "$(stat -c "%U:%G" /grafana/data)" != grafana:grafana ]]; then
	chown grafana:grafana /grafana/data
fi

cd /grafana/plugins/containers-panel && git pull && cd /
/usr/bin/cadvisor &
su-exec grafana grafana-server --homepath=/grafana &

python3 -u src/main.py