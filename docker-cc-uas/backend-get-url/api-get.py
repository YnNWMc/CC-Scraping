from flask import Flask, request, jsonify
import mysql.connector
import requests
from flask_cors import CORS
import re
from datetime import datetime, timedelta
from pymongo import MongoClient


app = Flask(__name__)
CORS(app)  # Enable CORS for all origins on all routes
client = MongoClient('mongodb://user:pass@54.204.230.86:27017/')
db = client['cc-webcrawl']  # replace with your database name
collection = db['webcrawl']  # replace with your collection name

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

# Connect to MySQL database
conn = mysql.connector.connect(
    host="db",
    user="root",
    password="example",
    database="example"
)
cursor = conn.cursor()

# Create the table if it doesn't exist
cursor.execute("""
CREATE TABLE IF NOT EXISTS urls (
    id INT AUTO_INCREMENT PRIMARY KEY,
    url VARCHAR(255) NOT NULL,
    status VARCHAR(255) NOT NULL,
    web_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

@app.route('/', methods=["GET"])
def posts():
    try:
        cursor.execute("SELECT * FROM urls")
        data = cursor.fetchall()
        return jsonify(data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/post_url', methods=['POST'])
def post_url():
    data = request.get_json()  # Get JSON data from POST request
    if not data:
        return jsonify({'error': 'No JSON data received'}), 400
    webId = data.get('webId')
    urls = data.get('urls')
    if not urls:
        return jsonify({'error': 'No URLs provided'}), 400
    try:
        new_urls = []
        for url in urls:
            status = "valid"
            if not is_valid_url(url):
                status = "not valid"
            if not check_url_status(url):
                status = "not valid"

            cursor.execute("SELECT COUNT(*) FROM urls WHERE url = %s", (url,))
            exists = cursor.fetchone()

            if exists[0] == 0:
                query = "INSERT INTO urls (url, status, web_id) VALUES (%s, %s, %s)"
                cursor.execute(query, (url, status, webId))
                conn.commit()
                
                if status == "valid":
                    payload = {'url': url}
                    response = requests.post("http://urlfrontier:5002/urlqueue", json=payload)
                    print('Sent to Frontier')
                    response.raise_for_status()

                new_urls.append(url)
                print(f"[X] Received {url}")

        if new_urls:
            return jsonify({'message': 'New URLs inserted successfully', 'urls': new_urls}), 200
        else:
            return jsonify({'message': 'No new URLs to insert; all URLs already exist'}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/fetch-data', methods=["GET"])
def fetch_data():
    draw = int(request.args.get('draw', 0))
    start = int(request.args.get('start', 0))
    length = int(request.args.get('length', 10))
    search_value = request.args.get('search[value]', '')
    order_column = request.args.get('order[0][column]', 0)
    order_direction = request.args.get('order[0][dir]', 'asc')

    columns = ['id', 'url', 'status', 'web_id', 'created_at']
    sort_column = columns[int(order_column)]

    try:
        query = "SELECT id, url, status, web_id, created_at FROM urls"

        if search_value:
            query += f" WHERE url LIKE '%{search_value}%'"

        query += f" ORDER BY {sort_column} {order_direction}"
        query += f" LIMIT {length} OFFSET {start}"

        cursor.execute(query)
        data = cursor.fetchall()

        cursor.execute("SELECT COUNT(*) FROM urls")
        total_records = cursor.fetchone()[0]

        urls = [
            {
                'id': row[0],
                'url': row[1],
                'status': row[2],
                'web_id': row[3],
                'created_at': row[4]
            }
            for row in data
        ]

        response = {
            'draw': draw,
            'recordsTotal': total_records,
            'recordsFiltered': total_records,
            'data': urls
        }

        return jsonify(response), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/fetch-recently-scraped', methods=["GET"])
def fetch_recently_created():
    draw = int(request.args.get('draw', 0))
    start = int(request.args.get('start', 0))
    length = int(request.args.get('length', 10))
    search_value = request.args.get('search[value]', '')
    order_column = request.args.get('order[0][column]', 0)
    order_direction = request.args.get('order[0][dir]', 'asc')

    columns = ['id', 'url', 'status', 'web_id', 'created_at']
    sort_column = columns[int(order_column)]

    try:
        query = "SELECT id, url, status, web_id, created_at FROM urls WHERE created_at >= %s"

        if search_value:
            query += f" AND url LIKE '%{search_value}%'"

        query += f" ORDER BY {sort_column} {order_direction}"
        query += f" LIMIT {length} OFFSET {start}"

        cursor = conn.cursor()
        created_after_timestamp = (datetime.utcnow() - timedelta(minutes=5)).strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute(query, (created_after_timestamp,))
        data = cursor.fetchall()

        cursor.execute("SELECT COUNT(*) FROM urls WHERE created_at >= %s", (created_after_timestamp,))
        total_records = cursor.fetchone()[0]

        urls = [
            {
                'id': row[0],
                'url': row[1],
                'status': row[2],
                'web_id': row[3],
                'created_at': row[4]
            }
            for row in data
        ]

        response = {
            'draw': draw,
            'recordsTotal': total_records,
            'recordsFiltered': total_records,
            'data': urls
        }

        return jsonify(response), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    
@app.route('/fetch-search-result', methods=["GET"])
def fetch_search_result():
    query = request.args.get('query', '').strip()
    if not query:
        return jsonify({'error': 'No search query provided'}), 400

    try:
        search_filter = {
            "$or": [
                {"title": {"$regex": query, "$options": "i"}},
                {"content": {"$regex": query, "$options": "i"}}
            ]
        }
        results = collection.find(search_filter, {"title": 1, "content": 1, "set_url": 1})

        search_results = [
            {
                'title': result.get('title'),
                'content': result.get('content'),
                'set_url': result.get('set_url')[0] if 'set_url' in result and result.get('set_url') else ''
            }
            for result in results
        ]

        logging.info(f"Search results fetched for query: {query}")
        return jsonify(search_results), 200

    except Exception as e:
        logging.error(f"Error fetching search results: {e}")
        return jsonify({'error': 'Internal server error'}), 500
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5001)
