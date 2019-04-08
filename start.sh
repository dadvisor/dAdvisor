#!/bin/sh
set -e

mkdir /prometheus
./prometheus-*/prometheus &
tor &

if [[ "$(stat -c "%U:%G" /grafana/data)" != grafana:grafana ]]; then
	chown grafana:grafana /grafana/data
fi

su-exec grafana grafana-server --homepath=/grafana &

python -m dadvisor