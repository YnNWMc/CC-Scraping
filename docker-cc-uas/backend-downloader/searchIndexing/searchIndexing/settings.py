# # Elasticsearch configuration
# ELASTICSEARCH_HOST = 'localhost'
# ELASTICSEARCH_PORT = 9200
# ELASTICSEARCH_SCHEME = 'https'  # Use 'https' if your Elasticsearch setup requires HTTPS
# ELASTICSEARCH_USERNAME = 'elastic'
# ELASTICSEARCH_PASSWORD = '+W0exDtj1WDxoyIh1Y+k'
# ELASTICSEARCH_VERIFY_CERTS = False

# # Configure Elasticsearch connection
# ELASTICSEARCH_SETTINGS = {
#     'host': ELASTICSEARCH_HOST,
#     'port': ELASTICSEARCH_PORT,
#     'scheme': ELASTICSEARCH_SCHEME,
#     'http_auth': (ELASTICSEARCH_USERNAME, ELASTICSEARCH_PASSWORD),
#     'verify_certs': False  # Adjust as needed (True/False) based on your Elasticsearch setup
# }

# LOG_FILE_PATH = str("C:\\Users\\wardyweird\\Desktop\\search-indexing-main\\logs\\application.log")  # Path to the log file to be uploaded to Elasticsearch
# Scrapy settings for searchIndexing project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = "searchIndexing"

SPIDER_MODULES = ["searchIndexing.spiders"]
NEWSPIDER_MODULE = "searchIndexing.spiders"


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = "searchIndexing (+http://www.yourdomain.com)"

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
#DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
#    "Accept-Language": "en",
#}

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    "searchIndexing.middlewares.SearchindexingSpiderMiddleware": 543,
#}

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#DOWNLOADER_MIDDLEWARES = {
#    "searchIndexing.middlewares.SearchindexingDownloaderMiddleware": 543,
#}

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    "scrapy.extensions.telnet.TelnetConsole": None,
#}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
#    "searchIndexing.pipelines.SearchindexingPipeline": 300,
    "searchIndexing.pipelines.SaveToMongoDBPipeline": 400,
    "searchIndexing.pipelines.SendURLToAPIPipeline": 500,  # Adjust the priority as needed

}
import os
# uri_api = f"http://localhost:5001/api/post_url"

API_URL = "http://api-url:5001/api/post_url"  # Replace with your API endpoint URL

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = "httpcache"
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = "scrapy.extensions.httpcache.FilesystemCacheStorage"

# Set settings whose default value is deprecated to a future-proof value
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"


def get_elasticsearch_settings():
    return ELASTICSEARCH_SETTINGS

def get_log_file_path():
    return LOG_FILE_PATH