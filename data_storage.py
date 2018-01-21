# read from the kafka broker
# write to cassandra
import argparse
import logging
import json
import atexit
from cassandra.cluster import Cluster
from kafka import KafkaConsumer

topic_name = ''
kafka_broker = ''
cassandra_broker = ''
key_space = ''
table = ''

logging.basicConfig()
logger = logging.getLogger('data-storage')
logger.setLevel(logging.DEBUG)

def save_data(stock_data, cassandra_session):
	#todo: avoid sql injection
	#prepare statement
    try:
        logger.debug('start to persist data %s', stock_data)
        parsed = json.loads(stock_data)
        currency = parsed.get('currency')
        timestamp = parsed.get('timestamp')
        price = float(parsed.get('price'))
        sentiment = float(parsed.get('sentiment'))

        logger.info('%s\t %s\t %f\t %f'%(timestamp, currency, price, sentiment))
        statement = "INSERT INTO %s (timestamp, currency, price, sentiment) VALUES ('%s', '%s', %f)" %(timestamp, currency, price, sentiment)
        cassandra_session.execute(statement)
        logger.info('succeed to save data to cassandra')
    except Exception:
        logger.error('failed to save to cassandra %s', stock_data)

def shutdown_hook(consumer, session):
	#implement try catch to avoid error
	consumer.close()
	session.shutdown()
	logger.info('release all the resources')



if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('topic_name', help='the kafka topic to subscribe from')
	parser.add_argument('kafka_broker', help='the kafka broker address')
	parser.add_argument('cassandra_broker', help='the location of the cassandra broker')
	parser.add_argument('key_space', help='the keyspace in the cassandra')
	parser.add_argument('table', help='the data table in cassandra')

	args = parser.parse_args()
	topic_name = args.topic_name
	kafka_broker = args.kafka_broker
	cassandra_broker = args.cassandra_broker
	key_space = args.key_space
	table = args.table

	# initialize a kafaka consumer
	consumer = KafkaConsumer(
		topic_name,
		bootstrap_servers=kafka_broker
	)

	# initialize a cassandra session
	cassandra_cluster = Cluster(
		contact_points=cassandra_broker.split(',')
	)
	session = cassandra_cluster.connect()

	session.execute("CREATE KEYSPACE IF NOT EXISTS %s WITH replication = {'class':'SimpleStrategy', 'replication_factor':1} AND durable_writes='true'"%key_space)
	session.set_keyspace(key_space)
	session.execute("CREATE TABLE IF NOT EXISTS %s (timestamp timestamp, currency text, price float, sentiment float, PRIMARY KEY (currency, timestamp))" % table)



	atexit.register(shutdown_hook, consumer, session)

	for msg in consumer:
		logger.debug(msg)
		save_data(msg.value, session)