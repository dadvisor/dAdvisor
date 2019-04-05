#!/bin/sh
set -e

tor &
./prometheus-*/prometheus &

if [[ "$(stat -c "%U:%G" /grafana/data)" != grafana:grafana ]]; then
	chown grafana:grafana /grafana/data
fi

su-exec grafana grafana-server --homepath=/grafana &


python main.py