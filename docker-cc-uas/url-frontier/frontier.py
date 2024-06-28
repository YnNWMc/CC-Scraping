from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import sys, os
import asyncio
import aiohttp
import logging

# from scrapy.crawler import crawler

app = Flask(__name__)
CORS(app)  # Enable CORS for all origins on all routes
# Set up logging
log_filename = '/logs/frontier.log'  # Define the log file path

logging.basicConfig(
    filename=log_filename,
    level=logging.DEBUG,  # Log all messages from DEBUG level and higher
    format='%(asctime)s %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logging.info('Frontier URL application started')

"""
api : /urlqueue
"""
arr_url= []
scraping_status = "on"
async def send_data_async( url):
    if scraping_status == "on":
        async with aiohttp.ClientSession() as session:
            data = {'url': arr_url[0]}
            arr_url.pop(0)
            async with session.post(url, json=data) as response:
                return await response.json()
    return
            
@app.route('/urlqueue', methods=['POST'])
def urlqueue():
    data = request.get_json()  # Get JSON data from POST request
    if not data:
        logging.error('No JSON data received in /urlqueue')
        return jsonify({'error': 'No JSON data received'}), 400
    url = data.get('url')
    arr_url.append(url)
    logging.info(f'URL added to queue: {url}')
    asyncio.run(send_data_async("http://proxy:3001"))  # Ganti dengan URL API tujuan
    print(arr_url)
    return jsonify({'message': 'GOOD FRONTIER'}), 200
"""
http://localhost:5002/geturlqueue
"""
@app.route('/geturlqueue', methods=['GET'])
def geturlqueue():
    logging.info('Current URL queue retrieved')
    return jsonify({'URL_QUEUE': arr_url,'scraping_status':scraping_status}), 200
"""
http://localhost:5002/changestatus
{
    "status":"off"
}
"""
@app.route('/changestatus', methods=['PUT'])
def changestatus():
    global scraping_status
    data = request.get_json()  # Get JSON data from POST request
    if not data:
        logging.error('No JSON data received in /changestatus')
        return jsonify({'error': 'No JSON data received'}), 400
    status = data.get('status')
    scraping_status = status
    logging.info(f'Scraping status changed to: {status}')
    asyncio.run(send_data_async("http://api-downloader:5000/scrape"))  # Ganti dengan URL API tujuan
    return jsonify({'message': ' Status Changed'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5002,debug=True)
