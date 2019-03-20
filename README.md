# dAdvisor
A docker container to inspect inter-container traffic.

Suppose you have a large project with many docker containers, and you don't know which container interacts with each other. This repository helps you to inspect the traffic between those.

## A small demo
An example docker-compose can be found in the root folder of this project.
It'll boot up a web-service (*web*) and a request-maker (*req*). Use the following command for starting those containers:

	docker-compose up -d

## Find out the network traffic
In order to find out the traffic, you'll need two new containers:
1. A container inside the network to perform a DNS translation from container-ID to IP-address.
2. A container to inspect the network traffic.

For 1. you'll need the following commands:

Note: change `--net` to the network in which you want to find out the traffic

	docker run \
	  --net=dadvisor_default \
	  --publish=5001:5001 \
	  --name=dns \
	  --detach=true \
	  dadvisor/dns:latest 

For 2. you'll need the following commands:

	docker run \
	  --name=dadvisor \
	  --net=host \
	  --volume=/:/rootfs:ro \
	  --volume=/var/run:/var/run:ro \
	  --volume=/sys:/sys:ro \
	  --volume=/var/lib/docker/:/var/lib/docker:ro \
	  --volume=/dev/disk/:/dev/disk:ro \
	  --detach=true \
	  dadvisor/dadvisor:latest
