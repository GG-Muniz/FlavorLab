#!/usr/bin/env python3
"""
Main entry point for FooDB nutrient scraping
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.scraper.nutrient_scraper import NutrientScraper
from src.utils.logger import setup_logger
from config.settings import LOG_LEVEL

def main():
    logger = setup_logger('foodb_scraper', LOG_LEVEL)
    
    try:
        logger.info("Starting FooDB nutrient scraping process")
        scraper = NutrientScraper()
        scraper.scrape_all_nutrients()
        logger.info("Scraping process completed successfully")
    except Exception as e:
        logger.error(f"Scraping process failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
