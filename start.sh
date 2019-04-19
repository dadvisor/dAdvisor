#!/bin/sh
set -e

mkdir /prometheus
./prometheus-*/prometheus --web.external-url http://localhost:8800/prometheus/ &

if [[ "$(stat -c "%U:%G" /grafana/data)" != grafana:grafana ]]; then
	chown grafana:grafana /grafana/data
fi

cd /grafana/plugins/containers-panel && git pull && cd /
/usr/bin/cadvisor &
su-exec grafana grafana-server --homepath=/grafana &

cd src


gunicorn dadvisor:run_forever --bind 0.0.0.0:8800 --worker-class aiohttp.GunicornWebWorker