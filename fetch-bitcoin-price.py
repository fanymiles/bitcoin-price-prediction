# fetch current bitcoin price from coindesk api
# send to any kafka cluster
# send to any kafka topic 

import requests
import schedule
import argparse
from datetime import datetime
import logging
import json
import time
import atexit
from kafka import KafkaProducer

coindeskAPI = "http://api.coindesk.com/v1/bpi/"
logging.basicConfig()
logger = logging.getLogger('fetch-bitcoin-price')
logger.setLevel(logging.DEBUG)


def shutdown_hock(producer):
	logger.info('closing kafka producer')
	producer.flush(10)
	producer.close(10)
	logger.info('kafka producer closed')

def fetch_price_and_send(producer):
	logger.debug('about to fetch price')
	price, time = get_current_price(currency)
	data = {
		'price': price,
		'last_trade_time': time
	}
	data = json.dumps(data)
	logger.debug('retrieved bitcoin price %s', data)
	try:
		producer.send(topic = topic_name, value = data)
		logger.debug('send to kafka %s', data)
	except Exception as e:
		logger.warn('fail to send price to kafka: %s', e)


def get_current_price(currency):
	response = requests.get(coindeskAPI + "currentprice/" + currency + ".json")
	price = response.json()['bpi'][currency]['rate_float']
	time = str(datetime.now())
	return price, time


if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('topic_name', help ='the name of kafka topic')
	parser.add_argument('kafka_broker', help = 'the location of kafka')
	parser.add_argument('currency', nargs='?', default='USD', help = 'currency of the bitcoin price, default is USD')

	args = parser.parse_args()
	topic_name = args.topic_name
	kafka_broker = args.kafka_broker
	currency = args.currency

	producer = KafkaProducer(
		bootstrap_servers = kafka_broker
	)

	schedule.every(1).second.do(fetch_price_and_send, producer)
	atexit.register(shutdown_hock, producer)

	while True:
		schedule.run_pending()
		time.sleep(1)