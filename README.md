# dAdvisor
A docker container to inspect inter-container traffic.

Suppose you have a large project with many docker containers, and you don't know which container interacts with each other. This repository helps you to inspect the traffic between those.

## A small demo
An example docker-compose can be found in the root folder of this project.
It'll boot up a web-service (*web*) and a request-maker (*req*). Use the following command for starting those containers:

	docker-compose up -d

## Find out the network traffic
In order to find out the traffic, you'll need the use the following command:

	docker run \
	  --name=dadvisor \
	  --net=host \
	  --volume=/:/rootfs:ro \
	  --volume=/var/run:/var/run:ro \
	  --volume=/sys:/sys:ro \
	  --volume=/var/run/docker.sock:/var/run/docker.sock \
	  --volume=/var/lib/docker/:/var/lib/docker:ro \
	  --volume=/dev/disk/:/dev/disk:ro \
	  --detach=true \
	  dadvisor/dadvisor:latest

## Output
When the containers are up and running, it generates a graph that can be visualized on: [localhost:8800/graph](localhost:8800/graph).

A possible graph for two contains that produces requests and one web-service is shown below.

