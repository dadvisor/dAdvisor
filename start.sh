#!/bin/sh
set -ex

if [[ "$DATA_REPLICATION"="1" ]]; then
	echo "Starting Prometheus and Grafana"

	./prometheus/prometheus --web.listen-address=:14102 \
	--web.external-url http://localhost:14100/prometheus/ &

	if [[ "$(stat -c "%U:%G" /grafana/data)" != grafana:grafana ]]; then
		chown grafana:grafana /grafana/data
	fi

	# debug command
	cd /grafana/plugins/containers-panel && git pull && cd /


	su-exec grafana grafana-server --homepath=/grafana &
else
	echo "No prometheus and grafana: $DATA_REPLICATION"
fi

/usr/bin/cadvisor --port 14104 &
nginx
python3 -u src/main.py