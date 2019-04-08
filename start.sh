#!/bin/sh
set -e

./prometheus-*/prometheus &
tor &

if [[ "$(stat -c "%U:%G" /grafana/data)" != grafana:grafana ]]; then
	chown grafana:grafana /grafana/data
fi

su-exec grafana grafana-server --homepath=/grafana &

cd dadvisor
python main.py