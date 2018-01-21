# Demo 1: 
## create data producer to fetch bitcoin price using coindesk API

- Code can be found in [fetch_bitcoin_price.py](fetch_bitcoin_price.py).
### Step 1: Setup Docker
- Start zookeeper container by `docker run -d -p 2181:2181 -p 2888:2888 -p 3888:3888 --name zookeeper confluent/zookeeper`.
- Start Kafka container by `docker run -d -p 9092:9092 -e KAFKA_ADVERTISED_HOST_NAME=localhost -e KAFKA_ADVERTISED_PORT=9092 --name kafka --link zookeeper:zookeeper confluent/kafka`

### Step 2: Setup Kafka topic and broker
- Run python scritpt [fetch_bitcoin_price.py](fetch_bitcoin_price.py).
- Setup Kafka topic (eg. bitcoin_price), and Kafka Broker (eg. localhost:9092)

### Step 3: Specify Currency
- Specify bitcoin price currency by using currency short name letters. (eg. CNY, USD, EUR)

### Screenshot
![](bitcoin-price-prediction/images/data-producer.png) 
![](bitcoin-price-prediction/images/data-producer-2.png)

