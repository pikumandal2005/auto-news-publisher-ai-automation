"""
Main Automation Script
Runs the complete news automation workflow
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
import logging

class NewsAutomation:
    def __init__(self, config_file='config.json'):
        # Load configuration
        with open(config_file, 'r') as f:
            self.config = json.load(f)
        
        # Setup logging
        self._setup_logging()
        
        # Initialize modules
        self.news_fetcher = NewsFetcher(self.config)
        self.article_writer = ArticleWriter(self.config)
        self.image_scraper = ImageScraper(self.config)
        self.blogger_publisher = BloggerPublisher(self.config)
        
        # Published articles tracker
        self.published_file = 'data/published_articles.json'
        self.published_articles = self._load_published_articles()
    
    def _setup_logging(self):
        """Setup logging"""
        log_file = f"logs/automation_{datetime.now().strftime('%Y%m%d')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger(__name__)
    
    def run_once(self, category='general', num_articles=3):
        """Run automation once - fetch, write, and publish articles"""
        
        self.logger.info("="*60)
        self.logger.info("🚀 STARTING NEWS AUTOMATION")
        self.logger.info("="*60)
        
        # Test Blogger connection first
        if not self.blogger_publisher.test_connection():
            self.logger.error("Blogger connection failed. Check your config!")
            return
        
        # Fetch trending news
        self.logger.info(f"📰 Fetching trending news ({category})...")
        articles = self.news_fetcher.fetch_trending_news(
            category=category,
            country=self.config.get('country', 'us'),
            limit=num_articles * 2  # Get more than needed
        )
        
        self.logger.info(f"   Found {len(articles)} articles")
        
        if not articles:
            self.logger.warning("No articles found!")
            return
        
        # Filter out already published
        new_articles = [a for a in articles if not self._is_published(a['title'])]
        new_articles = new_articles[:num_articles]
        
        self.logger.info(f"   {len(new_articles)} new articles to process")
        
        # Process each article
        published_count = 0
        for i, news_data in enumerate(new_articles, 1):
            try:
                self.logger.info(f"\n--- Processing Article {i}/{len(new_articles)} ---")
                self.logger.info(f"   Title: {news_data['title']}")
                
                # Generate article
                article = self.article_writer.write_article(
                    news_data,
                    word_count=self.config.get('article_word_count', 800)
                )
                
                if not article or not article['content']:
                    self.logger.warning("   ⚠️  Article generation failed, skipping...")
                    continue
                
                self.logger.info(f"   ✅ Article generated ({article['word_count']} words)")
                
                # Download image
                image_path = self.image_scraper.download_image_for_article(news_data)
                
                if image_path:
                    self.logger.info(f"   ✅ Image downloaded")
                else:
                    self.logger.warning("   ⚠️  No image found")
                
                # Publish to Blogger
                result = self.blogger_publisher.publish_article(
                    article,
                    image_path=image_path,
                    status=self.config.get('publish_status', 'publish')
                )
                
                if result['success']:
                    published_count += 1
                    self._mark_as_published(news_data['title'], result)
                    
                    self.logger.info(f"   ✅ Published: {result['url']}")
                else:
                    self.logger.error(f"   ❌ Publishing failed: {result.get('error', 'Unknown')}")
                
                # Delay between articles
                if i < len(new_articles):
                    delay = self.config.get('delay_between_posts', 30)
                    self.logger.info(f"   ⏳ Waiting {delay} seconds...")
                    time.sleep(delay)
                
            except Exception as e:
                self.logger.error(f"   ❌ Error processing article: {e}")
                continue
        
        # Summary
        self.logger.info("\n" + "="*60)
        self.logger.info(f"✅ AUTOMATION COMPLETE")
        self.logger.info(f"   Published: {published_count}/{len(new_articles)} articles")
        self.logger.info("="*60)
    
    def run_continuous(self, interval_hours=6):
        """Run automation continuously"""
        
        self.logger.info(f"🔄 Running in continuous mode (every {interval_hours} hours)")
        
        while True:
            try:
                # Get categories to cover
                categories = self.config.get('categories', ['general', 'technology', 'business'])
                
                for category in categories:
                    self.logger.info(f"\n📂 Processing category: {category.upper()}")
                    
                    self.run_once(
                        category=category,
                        num_articles=self.config.get('articles_per_run', 2)
                    )
                    
                    # Delay between categories
                    time.sleep(60)
                
                # Wait for next run
                wait_seconds = interval_hours * 3600
                self.logger.info(f"\n⏰ Next run in {interval_hours} hours...")
                time.sleep(wait_seconds)
                
            except KeyboardInterrupt:
                self.logger.info("\n🛑 Stopped by user")
                break
            except Exception as e:
                self.logger.error(f"❌ Error in continuous mode: {e}")
                self.logger.info("   Retrying in 5 minutes...")
                time.sleep(300)
    
    def _is_published(self, title):
        """Check if article was already published"""
        return title.lower() in [p['title'].lower() for p in self.published_articles]
    
    def _mark_as_published(self, title, result):
        """Mark article as published"""
        self.published_articles.append({
            'title': title,
            'post_id': result.get('post_id'),
            'url': result.get('url'),
            'published_at': datetime.now().isoformat()
        })
        
        # Save to file
        os.makedirs(os.path.dirname(self.published_file), exist_ok=True)
        with open(self.published_file, 'w') as f:
            json.dump(self.published_articles, f, indent=2)
    
    def _load_published_articles(self):
        """Load published articles from file"""
        try:
            if os.path.exists(self.published_file):
                with open(self.published_file, 'r') as f:
                    return json.load(f)
        except:
            pass
        
        return []

# Command line interface
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Automated News Website Generator')
    parser.add_argument('--mode', choices=['once', 'continuous'], default='once',
                        help='Run once or continuously')
    parser.add_argument('--category', default='general',
                        help='News category (general, technology, business, etc.)')
    parser.add_argument('--articles', type=int, default=3,
                        help='Number of articles to generate')
    parser.add_argument('--interval', type=int, default=6,
                        help='Hours between runs (continuous mode)')
    
    args = parser.parse_args()
    
    try:
        automation = NewsAutomation()
        
        if args.mode == 'once':
            automation.run_once(category=args.category, num_articles=args.articles)
        else:
            automation.run_continuous(interval_hours=args.interval)
            
    except FileNotFoundError:
        print("❌ Error: config.json not found!")
        print("   Please create config.json with your API keys and settings")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
