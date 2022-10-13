
FROM ubuntu:18.04

WORKDIR stream2gym-docker

COPY requirements.txt requirements.txt
RUN apt-get update
RUN apt-get install -y \
	git \ 
	python3-pip \
	default-jdk \
	ifupdown \
	iproute2 \ 
	iptables \
	iputils-ping \
	mininet \
	net-tools \
	openvswitch-switch \ 
	openvswitch-testcontroller \
	tcpdump \
	xterm \
	netcat
RUN cp /usr/bin/ovs-testcontroller /usr/bin/ovs-controller
RUN rm -rf /var/lib/apt/lists/* 
RUN touch /etc/network/interfaces 
RUN python3 -m pip install --upgrade pip setuptools wheel
RUN pip3 install -r requirements.txt 

COPY . .

ENTRYPOINT service openvswitch-switch start && /bin/bash







