import scrapy
from searchIndexing.items import SearchindexingItem
import sys, os
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from bs4 import BeautifulSoup  # Import BeautifulSoup
import re
from collections import Counter  # Import Counter for counting unique elements
from scrapy.selector import Selector
from datetime import datetime
import random
import string

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
# # import custom_logger as CustomLogger

# log_folder = 'C:\\Users\\wardyweird\\Desktop\\search-indexing-main\\logs\\'
# logger = CustomLogger(log_folder)

def generate_unique_id():
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')  # Current timestamp in a specific format
    random_str = ''.join(random.choices(string.ascii_letters + string.digits, k=6))  # Random string of 6 characters
    unique_id = f"{timestamp}_{random_str}"
    return unique_id

class SearchspiderSpider(scrapy.Spider):
    name = "searchspider"
    # start_urls = ["https://market.bisnis.com/read/20240529/7/1769261/saham-bren-prajogo-pangestu-langsung-arb-10-akibat-ppk-full-call-auction"]
    custom_settings ={
            'FEEDS' :{
                'booksdata.json' : {'format':'json' , 'overwrite':True}
            },
        }
    

    def __init__(self, *args, **kwargs): 
        super(SearchspiderSpider, self).__init__(*args, **kwargs) 
        self.start_urls = [kwargs.get('start_url')] 
        self.allowed_domains = kwargs.get('allowed_domains', [])  # Default to empty list
        self.rules = (
            Rule(LinkExtractor(allow=self.allowed_domains), callback='parse', follow=True),
            )
        # logger.info_log(f"Spider initialized with start URL: {self.start_urls[0]}", 'searchspider.py')

    def parse(self, response):
        try:
            book_item = SearchindexingItem()
            book_item['webId'] = generate_unique_id()

            res = response.body
            book_item['name'] = response.url
            title = response.css('title::text').get()
            book_item['title'] = title

            # COMPLETELY HTML FILE===================================
            # Clean HTML text using BeautifulSoup
            soup = BeautifulSoup(res, 'html.parser')
            formatted_html = soup.prettify(formatter='html')  # Indent with HTML formatting
            book_item['body'] = formatted_html

            # GET ALL CLEAN CONTENT WITHOUT HTML ELEMENT =============================
            # Option 1: Basic cleaning (remove all HTML tags and extra spaces)
            text = soup.get_text(separator=' ')  # Get text with spaces as separator
            clean_text = re.sub(r'\s+', ' ', text).strip()  # Replace multiple spaces with single space and strip whitespace
            book_item['content'] = clean_text  # Option 1 result

            # EXTRACT ALL LINKS IN CURRENT PAGES ===============================
            extracted_links = [link.url for link in LinkExtractor(allow=self.allowed_domains).extract_links(response)]
            book_item['set_url'] = extracted_links

            # Get HTML tags -------------------------------
            # Extract and count unique tags (excluding text and self-closing tags)
            all_tags = set(sorted(tag.name for tag in soup.find_all() if tag.name not in ('script')))
            book_item['html_tags'] = list(all_tags)

            # CSS tags------------------------------------------------------------------
            # Extract and build element hierarchy
            extracted_data = []
            indent = 0  # Track indentation level

            def build_hierarchy(element):
                nonlocal indent  # Access and modify the indent variable
                tag_name = element.name
                if 'class' in element.attrs:  # Check for class attribute
                    classes = element['class']
                    class_str = ' '.join(classes)  # Combine classes into a string
                else:
                    class_str = ''

                entry = ""
                entry += indent * '  ' + "<"
                entry += tag_name

                if class_str:
                    entry += ' class="' + class_str + '">'

                extracted_data.append(entry)
                indent += 1  # Increase indentation for child elements

                for child in element.children:
                    if not isinstance(child, str):  # Skip text nodes
                        build_hierarchy(child)

                indent -= 1  # Decrease indentation for closing tag

                # Add closing tag entry
                closing_entry = indent * '  ' + '<' + tag_name + "/>"
                extracted_data.append(closing_entry)

            build_hierarchy(soup)  # Start building hierarchy from the root element
            # Add tuple (tag, class)
            book_item['class_tags'] = list(extracted_data)

            # logger.info_log(f"Parsed URL: {response.url}", 'searchspider.py')
            yield book_item

        except Exception as e:
            print(e)
            # logger.error_log(f"Error parsing URL {response.url}: {e}", 'searchspider.py')
        
        print('-----------------', self.allowed_domains)

        yield book_item