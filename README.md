Bitcoin Price Prediction Platform
================

Introduction
------------

This is a data pipeline project that predicts the Bitcoin price, visualizes the trend, and proposes the sell/buy decisions. Ideally, we will implement the Lambda architecture using Spark, Mesos, Akka, Cassandra and Kafka (SMACK) stack and the front-end tool Node.js.

Data Source
-----------

-   [CoinDesk API](https://www.coindesk.com/api/)
-   [Twitter API](https://github.com/tweepy/tweepy/)

Architecture
------------

![](images/architecture.png)

Data Ingestion
--------------

### Kafka

-   User can specify currency and fetch bitcoin price by running fetch-bitcoin-price.py.
-   Bitcoin price will be sent to any kafka topic specified by user.
-   Code can be found here: [fetch-bitcoin-price.py](fetch-bitcoin-price.py). Screenshot: ![](images/data-producer.png) ![](images/data-producer-2.png)

![](images/sentiments.png)

Data Storage
------------

### Cassandra

-   schema

| column\_name |    type   |
|:------------:|:---------:|
|   timestamp  | timestamp |
|   currency   |    text   |
|  true\_price |   float   |
|  pred\_price |   float   |
|   sentiment  |   float   |

-   PRIMARY KEY (currency, timestamp)

Data Computation
----------------

### Spark

Cluster Scheduling Layer
------------------------

### Mesos

Reference
---------

[Bitcoin Price Prediction using Sentiment Analysis](http://www.ee.columbia.edu/~cylin/course/bigdata/projects/)
