# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import sys, os

# PATHNYA AGAK GAK JELAS BUAT IMPORT
# relative_path = "requirements.txt"
# absolute_path = os.path.abspath(relative_path)
# path_components = absolute_path.split(os.path.sep)

# path_components.pop()
# full_path = os.path.join(*path_components,"logger")
# full_path_with_drive = str(os.path.join(path_components[0], os.path.sep, full_path))

# sys.path.insert(1, str(full_path_with_drive))

# print(full_path_with_drive)

# import custom_logger as CustomLogger
import os
import logging
import json
# import logstash

# class JsonFormatter(logging.Formatter):
#     def format(self, record):
#         log_record = {
#             'timestamp': self.formatTime(record, self.datefmt),
#             'where': record.__dict__.get('where', os.path.basename(record.pathname)),
#             'level': record.levelname,
#             'message': record.getMessage(),
#             'logger': record.name,
#             'filename': record.filename,
#             'funcName': record.funcName,
#             'lineno': record.lineno,
#         }
#         return json.dumps(log_record)

# class CustomLogger:
#     def __init__(self, log_folder, log_file='application.log', logstash_host='localhost', logstash_port=5044):
#         self.logger = logging.getLogger()
#         self.logger.setLevel(logging.DEBUG)

#         self.log_folder = log_folder
#         self.log_file = log_file

#         if not os.path.exists(self.log_folder):
#             os.makedirs(self.log_folder)

#         self.file_handler = self._get_file_handler(self.log_file)
#         self.logger.addHandler(self.file_handler)

#         self.logstash_handler = self._get_logstash_handler(logstash_host, logstash_port)
#         self.logger.addHandler(self.logstash_handler)

#     def _get_file_handler(self, filename):
#         file_path = os.path.join(self.log_folder, filename)
#         handler = logging.FileHandler(file_path)
#         handler.setLevel(logging.DEBUG)
#         formatter = JsonFormatter()
#         handler.setFormatter(formatter)
#         return handler

#     def _get_logstash_handler(self, host, port):
#         handler = logstash.LogstashHandler(host, port, version=1)
#         handler.setLevel(logging.DEBUG)
#         return handler

#     def error_log(self, message, where="Unknown"):
#         self.logger.error(message, extra={'where': where})

#     def info_log(self, message, where="Unknown"):
#         self.logger.info(message, extra={'where': where})

#     def debug_log(self, message, where="Unknown"):
#         self.logger.debug(message, extra={'where': where})

#     def warning_log(self, message, where="Unknown"):
#         self.logger.warning(message, extra={'where': where})

#     def trace_log(self, message, where="Unknown"):
#         self.logger.log(logging.NOTSET, message, extra={'where': where})

#     def critical_log(self, message, where="Unknown"):
#         self.logger.critical(message, extra={'where': where})
# log_folder = 'C:\\Users\\wardyweird\\Desktop\\search-indexing-main\\logs\\'
# logger = CustomLogger(log_folder)

class SearchindexingPipeline:
    def process_item(self, item, spider):
        # logger.debug_log(f"Processing item in Pipeline: {item}", 'pipelines.py')
        return item

from pymongo import MongoClient

class SaveToMongoDBPipeline:
  def __init__(self):
    # Connect to MongoDB
    uri = f"mongodb://user:pass@mongodb:27017/"
    self.client = MongoClient(uri)
    self.db = self.client["cc-webcrawl"]  # Replace "books" with your database name

  def process_item(self, item, spider):
    # Get collection (table equivalent)
    collection = self.db["webcrawl"]  # Replace "books" with your collection name
    exists = collection.find_one({"content": item["content"]})
    title_exists = collection.find_one({"title": item["title"]})

    if not title_exists:
            # self.db[spider.name].insert_one(dict(item))
            collection.insert_one(item)
            # logger.debug_log("Article added to MongoDB", 'pipelines.py')
    # Insert data into collection
    # collection.insert_one(item)

    return item

  def close_spider(self,spider):
    # Close connection
    self.client.close()
import pika,sys,pickle
import requests
import json
from scrapy.exceptions import DropItem
import pika
import json

class SendURLToAPIPipeline:
    def __init__(self,  rabbitmq_host, rabbitmq_user, rabbitmq_pass, rabbitmq_queue):
        # self.api_url = api_url
        self.rabbitmq_host = rabbitmq_host
        self.rabbitmq_user = rabbitmq_user
        self.rabbitmq_pass = rabbitmq_pass
        self.rabbitmq_queue = rabbitmq_queue
        self.connection = None
        self.channel = None

    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings
        # api_url = settings.get('API_URL', 'default_api_url')
        rabbitmq_host = settings.get('RABBITMQ_HOST', 'rabbitmq')
        rabbitmq_user = settings.get('RABBITMQ_USER', 'user')
        rabbitmq_pass = settings.get('RABBITMQ_PASS', 'user')
        rabbitmq_queue = settings.get('RABBITMQ_QUEUE', 'logs')

        return cls( rabbitmq_host, rabbitmq_user, rabbitmq_pass, rabbitmq_queue)

    def open_spider(self, spider):
        creds = pika.PlainCredentials(self.rabbitmq_user, self.rabbitmq_pass)
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(self.rabbitmq_host, credentials=creds)
        )
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=self.rabbitmq_queue)

    def close_spider(self, spider):
        if self.connection:
            self.connection.close()

    def process_item(self, item, spider):
        set_urls = item['set_url']
        payload = {'webId': item['webId'], 'urls': set_urls}

        try:
            self.channel.basic_publish(
                exchange='',
                routing_key=self.rabbitmq_queue,
                body=json.dumps(payload)
            )
            # spider.logger.info(f"Sent item {item['webId']} to RabbitMQ")
        except pika.exceptions.AMQPError as err:
            # spider.logger.error(f"Failed to send item {item['webId']}: {err}")
            raise

        return item

# class SendURLToAPIPipeline:
    # def __init__(self, api_url):
    #     self.api_url = api_url

    # @classmethod
    # def from_crawler(cls, crawler):
    #     return cls(
    #         api_url=crawler.settings.get('API_URL')
    #     )

    # def process_item(self, item, spider):
    #     if 'set_url' not in item:
    #         raise DropItem("Missing 'set_url' field in item")

    #     set_urls = item['set_url']
    #     payload = {'webId': item['webId'], 'urls': set_urls}

    #     try:
    #         response = requests.post("http://localhost:5001/api/post_url", json=payload)
    #         response.raise_for_status()
    #         # logger.info_log(f"URLs sent to API: {set_urls}", 'pipelines.py')
    #     except requests.RequestException as e:
    #         print(e)
    #         # logger.error_log(f"Failed to send URLs to API: {e}", 'pipelines.py')

    #     return item