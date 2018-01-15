Bitcoin Price Prediction
================

Introduction
------------

A data pipeline predicting the Bitcoin price and sending the alert to subscribers.

Data Source
-----------

-   [Bitcoin API](https://api.coinmarketcap.com/v1/ticker/bitcoin/)
-   [Twitter API](https://github.com/tweepy/tweepy/)

Data Ingestion
--------------

-   Kafka
    real time (good scalability, robustness)

Data Storage
------------

-   Cassandra

Data Computation
----------------

-   Spark

Cluster Scheduling Layer
------------------------

-   Mesos

Reference
---------

[Bitcoin Price Prediction using Sentiment Analysis](http://www.ee.columbia.edu/~cylin/course/bigdata/projects/)
