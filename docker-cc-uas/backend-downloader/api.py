from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import logging
import sys, os
# from scrapy.crawler import crawler

app = Flask(__name__)
CORS(app)  # Enable CORS for all origins on all routes
log_filename = '/logs/downloader.log'  # Define the log file path

logging.basicConfig(
    filename=log_filename,
    level=logging.INFO,  # Log all messages from DEBUG level and higher
    format='%(asctime)s %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

@app.route('/scrape', methods=['POST'])
def scrape():
    data = request.json  # Receive JSON data from frontend
    
    if not data or 'url' not in data:
        logging.error_log('Invalid request: missing URL', 'api.py')
        return jsonify({'error': 'Invalid request'}), 400
    
    target_url = data['url']
    allowed_domains = data.get('allowed_domains', [])
    # scraping_in_progress = True
    
    logging.info(f"Scraping initiated for URL: {target_url}", 'api.py')
    logging.info(f"Allowed domains: {allowed_domains}", 'api.py')

    # Launch Scrapy spider in background using subprocess
    cmd = f"scrapy crawl searchspider -a start_url={target_url} "
    # command = [
    #     'scrapy crawl searchspider -a ',
    #     'crawl',
    #     'searchspider',
    #     '-a', f'start_url={target_url}',
    #     '-a', f'allowed_domains={",".join(allowed_domains)}'
    # ]

    logging.info(f"Launching spider with command: {' '.join(cmd)}", 'api.py')
    
    try:
        # dir = f"{full_path_with_drive}"
        subprocess.Popen(cmd, cwd=r'./searchIndexing/searchIndexing', shell=True)
    except Exception as e:
        logging.error(f"Error launching spider: {str(e)}", 'api.py')
        return jsonify({'error': str(e)}), 500

    return jsonify({'message': 'Scraping initiated. Please wait for results.'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)
