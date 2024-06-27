import pika,sys,pickle
import json
import sqlite3
import os
import mysql.connector
import requests
import re
from datetime import datetime, timedelta
import logging

def is_valid_url(url):
    # Regular expression for validating a URL
    regex = re.compile(
        r'^(https?:\/\/)?'  # http:// or https://
        r'(([A-Za-z0-9-]+\.)+[A-Za-z]{2,})'  # domain
        r'(\/\S*)?$'  # path
    )
    return re.match(regex, url) is not None

def check_url_status(url):
    try:
        response = requests.head(url, allow_redirects=True, timeout=5)  # HEAD request for efficiency
        if response.status_code < 400:
            return True
    except requests.RequestException as e:
        print(f"Error checking URL {url}: {e}")
    return False

log_filename = '/logs/consumer-url.log'  # Define the log file path

logging.basicConfig(
    filename=log_filename,
    level=logging.INFO,  # Log all messages from DEBUG level and higher
    format='%(asctime)s %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logging.info('Consumer SEEN URL Started')

def main():

    conn = mysql.connector.connect(
        host="db",
        user="root",
        password="example",
        database="example"
    )
    cursor = conn.cursor()
    # Create the table if it doesn't exist

    creds = pika.PlainCredentials("user","user")
    connection = pika.BlockingConnection(
        pika.ConnectionParameters('rabbitmq',credentials=creds)
    )

    channel  = connection.channel()
    channel.queue_declare(queue='logs')
    def callback(ch,method,props,body):
        payload = json.loads(body)
        webId = payload.get("webId")  # Access the "name" property
        urls  = payload.get("urls")  # Access the "name" property
        logging.debug(f"Received payload: {payload}")
        new_urls = []
        for url in urls:
            status = "valid"
            if not is_valid_url(url):
                status = "not valid"
                logging.warning(f"URL {url} is not valid.")
            if not check_url_status(url):
                status = "not valid"
                logging.warning(f"URL {url} is not reachable.")

            cursor.execute("SELECT COUNT(*) FROM urls WHERE url = %s", (url,))
            exists = cursor.fetchone()

            if exists[0] == 0:
                query = "INSERT INTO urls (url, status, web_id) VALUES (%s, %s, %s)"
                cursor.execute(query, (url, status, webId))
                conn.commit()
                logging.info(f"Inserted new URL into database: {url}")
                if status == "valid":
                    payload = {'url': url}
                    response = requests.post("http://urlfrontier:5002/urlqueue", json=payload)
                    print('Sent to Frontier')
                    logging.info(f'URL Send to queue: {url}')
                    response.raise_for_status()
                new_urls.append(url)
                print(f"[X] Received {url}")
                ch.basic_ack(delivery_tag=method.delivery_tag)
            else:
                logging.debug(f"URL {url} already exists in the database.")

        if new_urls:
            logging.info(f'New URLs inserted: {new_urls}')
            # return jsonify({'message': 'New URLs inserted successfully', 'urls': new_urls}), 200
        else:
            logging.info('No new URLs to insert; all URLs already exist.')

            # return jsonify({'message': 'No new URLs to insert; all URLs already exist'}), 200
        

    channel.basic_consume(queue='logs',on_message_callback=callback,auto_ack=True)
    print('[*] Waiting for messages to exit press CTRL+C')
    try:
        channel.start_consuming()
    except Exception as e:
        logging.error(f"Error occurred: {e}")
        connection.close()
        sys.exit(1)
        
if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os.exit(0)