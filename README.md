# dAdvisor
A Docker container to inspect your existing Docker Container Distribution.

Suppose you have a large project with many Docker containers, and you don't know which containers interact with each other. Then, this repository helps you to visualize the docker container distribution by monitoring the internet traffic that is being send between those containers. It also retrieves specific metrics about the price of hosting your machines, and the amount of money that you're wasting, because you are not using all resources.

If you use multiple machines, then it even works across multiple virtual machines, but then you need to deploy this container on every host.

## Implementation
dAdvisor is implemented in a P2P System. In order to find the peers, you have to specify a unique info hash, such that is doesn't mesh up deployments of other users.

## Internally
Internally, the following programs are installed that are all configured together and work out of the box:
- [cAdvisor](https://github.com/google/cadvisor): for monitoring host metrics, and the containers that are deployed.
- [Prometheus](https://github.com/prometheus/prometheus): for storing these information
- dAdvisor: for finding out the internet traffic between hosts. Internally dAdvisor uses [TCPDUMP](https://www.tcpdump.org/manpages/tcpdump.1.html).
- [Grafana](https://github.com/grafana/grafana): for displaying the obtained results.
- [Nginx](https://www.nginx.com/): for allowing a reverse proxy between Prometheus, dAdvisor and Grafana.

## Find out the network traffic
In order to find out the traffic, you'll need the use the following command:

	docker run \
	  --name=dadvisor \
	  --net=host \
	  --volume=/:/rootfs:ro \
      --volume=/var/run:/var/run:ro \
      --volume=/sys:/sys:ro \
      --volume=/var/lib/docker/:/var/lib/docker:ro \
      --volume=/dev/disk/:/dev/disk:ro \
      --volume=/prometheus:/prometheus \
      --volume=/grafana/data:/grafana:data \
      --detach=true \
      --env INFO_HASH=abc1234567890 \
      dadvisor/dadvisor

## Output
When the containers are up and running, it generates the output on one of the Grafana dashboard.
Visit the following link for redirecting to this dashboard: [localhost:14100/dadvisor/dashboard](localhost:14100/dadvisor/dashboard).

## Dashboard example
![Figure 1](docs/fig1.png)
![Figure 2](docs/fig1.png)