#!/bin/sh
set -e

mkdir /prometheus
./prometheus-*/prometheus &

if [[ "$(stat -c "%U:%G" /grafana/data)" != grafana:grafana ]]; then
	chown grafana:grafana /grafana/data
fi

cd /grafana/plugins/containers-panel && git pull && cd /
su-exec grafana grafana-server --homepath=/grafana &

python src/main.py