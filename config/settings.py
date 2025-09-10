import os
from dotenv import load_dotenv

load_dotenv()

# FooDB Settings
BASE_URL = os.getenv('BASE_URL', 'https://foodb.ca/nutrients')
SCRAPE_DELAY = int(os.getenv('SCRAPE_DELAY', 1))
MAX_RETRIES = int(os.getenv('MAX_RETRIES', 3))
HEADLESS_MODE = os.getenv('HEADLESS_MODE', 'true').lower() == 'true'

# File Paths
DATA_DIR = 'data'
RAW_DATA_DIR = os.path.join(DATA_DIR, 'raw')
PROCESSED_DATA_DIR = os.path.join(DATA_DIR, 'processed')
NUTRIENTS_DIR = os.path.join(PROCESSED_DATA_DIR, 'nutrients')
LOGS_DIR = os.path.join(DATA_DIR, 'logs')

# Logging
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE_PATH = os.getenv('LOG_FILE_PATH', os.path.join(LOGS_DIR, 'scraper.log'))

# Data Processing
VALIDATE_DATA = os.getenv('VALIDATE_DATA', 'true').lower() == 'true'
OUTPUT_FORMAT = os.getenv('OUTPUT_FORMAT', 'json')

# Nutrient Categories
NUTRIENT_CATEGORIES = {
    'macronutrient': 'macronutrients.json',
    'micronutrient': 'micronutrients.json', 
    'mineral': 'minerals.json',
    'vitamin': 'vitamins.json',
    'other': 'other_nutrients.json'
}
