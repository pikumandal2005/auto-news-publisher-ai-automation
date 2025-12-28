"""
Auto-Post Every 1 Minute
Continuously generates and posts articles to Blogger
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.news_fetcher import NewsFetcher
from modules.article_writer import ArticleWriter
from modules.image_scraper import ImageScraper
from modules.blogger_publisher import BloggerPublisher

import json
import time
from datetime import datetime

def load_config():
    with open('config.json', 'r') as f:
        return json.load(f)

def log(message):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] {message}")

# Global counter for language rotation and duplicate tracking
post_counter = 0
posted_titles = set()  # Track posted article titles to avoid duplicates

def generate_and_post():
    """Generate one article and post it"""
    global post_counter, posted_titles
    post_counter += 1
    
    config = load_config()
    
    # Initialize modules
    news_fetcher = NewsFetcher(config)
    article_writer = ArticleWriter(config)
    image_scraper = ImageScraper(config)
    blogger_publisher = BloggerPublisher(config)
    
    # Determine language (every 3rd post is Bengali)
    language = 'bengali' if post_counter % 3 == 0 else 'english'
    
    log(f"Starting article generation... (Post #{post_counter}, Language: {language})")
    
    # Rotate or randomize news categories for diversity
    categories = config.get('news_settings', {}).get('categories', ['general'])
    import random
    chosen_category = random.choice(categories)
    log(f"Fetching news for category: {chosen_category} (India)...")
    articles = news_fetcher.fetch_trending_news(
        category=chosen_category,
        country='in',  # India
        limit=20  # Fetch more to find unique ones
    )
    
    if not articles:
        log("ERROR: No articles found")
        return False
    
    # Find an article we haven't posted yet
    news_data = None
    for article in articles:
        if article['title'] not in posted_titles:
            news_data = article
            posted_titles.add(article['title'])
            break
    
    # If all articles were posted, clear history and start fresh
    if not news_data:
        log("All fetched articles already posted, clearing history...")
        posted_titles.clear()
        news_data = articles[0]
        posted_titles.add(articles[0]['title'])
    
    log(f"Topic: {news_data['title'][:60]}...")
    
    # Generate article with language support
    log(f"Generating article with AI ({language})...")
    try:
        article = article_writer.write_article(news_data, word_count=1000, language=language)
    except Exception as e:
        log(f"ERROR generating article: {e}")
        return False
    
    if not article or not article.get('content'):
        log("ERROR: Article generation failed")
        return False
    
    log(f"Article generated ({article['word_count']} words)")
    
    # Download image
    log("Downloading image...")
    try:
        image_path = image_scraper.download_image_for_article(news_data)
        if image_path:
            log("Image downloaded")
        else:
            log("No image found (will post without image)")
    except Exception as e:
        log(f"Image download failed: {e}")
        image_path = None
    
    # Publish
    log("Publishing to Blogger...")
    try:
        result = blogger_publisher.publish_article(
            article,
            image_path=image_path,
            status='publish'
        )
        
        if result['success']:
            log(f"SUCCESS! Published: {result['url']}")
            log(f"Post ID: {result['post_id']}")
            return True
        else:
            log(f"FAILED: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        log(f"ERROR publishing: {e}")
        return False

def main():
    log("="*60)
    log("BLOGGER AUTO-POSTER - Every 1 Minute")
    log("="*60)
    log("Press Ctrl+C to stop")
    log("")
    
    post_count = 0
    error_count = 0
    
    while True:
        try:
            log("")
            log(f"--- Post #{post_count + 1} ---")
            
            success = generate_and_post()
            
            if success:
                post_count += 1
                log(f"Total posts published: {post_count}")
            else:
                error_count += 1
                log(f"Total errors: {error_count}")
            
            # Wait 1 minute
            log("Waiting 1 minute until next post...")
            time.sleep(60)
            
        except KeyboardInterrupt:
            log("")
            log("="*60)
            log(f"Stopped by user")
            log(f"Total posts published: {post_count}")
            log(f"Total errors: {error_count}")
            log("="*60)
            break
            
        except Exception as e:
            error_count += 1
            log(f"UNEXPECTED ERROR: {e}")
            log("Waiting 1 minute before retry...")
            time.sleep(60)

if __name__ == "__main__":
    main()
