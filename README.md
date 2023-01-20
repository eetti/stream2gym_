# stream2gym

Tool for fast prototyping of distributed stream processing applications.

The tool was tested on Ubuntu 20.04.4 and is based on Python 3.8.10, Kafka 2.13-2.8.0, PySpark 3.2.1 and MySQL 8.0.30.

## Getting started

1. Clone the repository, then enter into it.

```git clone https://github.com/PINetDalhousie/stream2gym.git```

```cd stream2gym```

2. Install dependencies. Our tool depends on the following software:

  - pip3
  - Mininet 2.3.0
  - Networkx 2.5.1
  - Java 11
  - Xterm
  - Kafka-python 2.0.2
  - Matplotlib 3.3.4
  - Seaborn 0.12.1
  - PyYAML 5.3.1

  Most dependencies can be installed using `apt install` and `pip3 install`:
  
  ```bash
  $ sudo apt install python3-pip mininet default-jdk xterm netcat
  
  $ sudo pip3 install mininet networkx kafka-python matplotlib python-snappy lz4 seaborn pyyaml seaborn
  ```
  3. You are ready to go! Should be able to get help using:

  ```sudo python3 main.py -h```
  
  ## Sample command lines
  
  1) Navigate through the ```use-cases/``` directory to explore the diverse applications we tested using stream2gym.  Details of the applications including the exact data processing pipeline, topology, executed queries, and platform configurations can be found inside respective application directory. Example command to test a streaming data analytics application in a small network: 
  
  ```sudo python3 main.py use-cases/app-testing/word-count/input.graphml```
  
  2) Log  production, consumption history and metrics of interest (e.g., bandwidth consumption) automatically for STANDARD producer and consumer. Look over the logs in `logs/output/` directory once the simulation ends.
    
  3) Set a duration for the simulation (OBS.: this is the time the workload will run, not the total simulation time.)

  ```sudo python3 main.py use-cases/app-testing/millitary-coordination/input.graphml --time 300```

  4) Capture the traffic of all the hosts while testing your application.

  ```sudo python3 main.py use-cases/app-testing/millitary-coordination/input.graphml --capture-all```

  5) Run event streaming and stream processing engine jointly or individually. Default setup is running event streaming (Apache Kafka) and stream processing engine (Apache Spark) as a sequential pipeline.

  ```sudo python3 main.py use-cases/reproducibility/input.graphml --only-spark 1```

  6) Explore the stream2gym supported configuration parameters in ```config-parameters.pdf```. Setup parameters as you need and quickly test your prototype in a distributed emulated environment.