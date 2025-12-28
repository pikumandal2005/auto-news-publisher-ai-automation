"""
Auto-Post to BOTH Blogger AND Facebook
Posts every 1 minute to both platforms simultaneously
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.news_fetcher import NewsFetcher
from modules.article_writer import ArticleWriter
from modules.image_scraper import ImageScraper
from modules.blogger_publisher import BloggerPublisher
from modules.facebook_publisher import FacebookPublisher

import json
import time
from datetime import datetime

LANGUAGES = ['english', 'bengali', 'hindi']
language_index = 0
trending_topics = []
last_trending_refresh = 0
topic_index = 0
posted_titles = set()

def load_config():
    with open('config.json', 'r') as f:
        return json.load(f)

def log(message):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] {message}")

def generate_and_post():
    global topic_index, posted_titles, trending_topics, last_trending_refresh
    config = load_config()
    news_fetcher = NewsFetcher(config)
    article_writer = ArticleWriter(config)
    image_scraper = ImageScraper(config)
    blogger_publisher = BloggerPublisher(config)
    facebook_publisher = FacebookPublisher(config)
    # Refresh trending topics every 30 minutes
    now = time.time()
    if not trending_topics or now - last_trending_refresh > 60 * 30:
        trending_topics = news_fetcher.get_trending_topics()
        last_trending_refresh = now
        topic_index = 0
        log(f"[Trending] Refreshed trending topics: {trending_topics}")
    if not trending_topics:
        log("❌ No trending topics found. Skipping post.")
        return False
    topic = trending_topics[topic_index % len(trending_topics)]
    topic_lower = topic.lower()
    if any(word in topic_lower for word in ['bengal', 'bangladesh', 'kolkata', 'bengali']):
        language = 'bengali'
    elif any(word in topic_lower for word in ['india', 'indian', 'hindi', 'delhi', 'uttar pradesh', 'mumbai', 'maharashtra', 'gujarat', 'punjab', 'bihar', 'jharkhand', 'chhattisgarh', 'rajasthan', 'uttarakhand', 'haryana', 'himachal', 'goa', 'kerala', 'karnataka', 'tamil', 'andhra', 'telangana', 'odisha', 'assam', 'tripura', 'manipur', 'nagaland', 'mizoram', 'sikkim', 'meghalaya', 'arunachal']):
        language = 'hindi'
    else:
        language = 'english'
    log(f"Starting article generation... (Trending Topic: {topic}, Language: {language})")
    articles = news_fetcher.fetch_trending_news(
        category=topic,
        country='in',
        limit=20
    )
    topic_articles = articles
    news_data = None
    for article in topic_articles:
        if article['title'] not in posted_titles:
            news_data = article
            posted_titles.add(article['title'])
            break
    if not news_data:
        if topic_articles:
            log("All articles posted for this topic, clearing history...")
            posted_titles.clear()
            news_data = topic_articles[0]
            posted_titles.add(news_data['title'])
        else:
            log(f"❌ No articles found for topic: {topic}. Skipping post.")
            return False
    import random
    word_count = random.randint(1000, 1500)
    try:
        article = article_writer.write_article(news_data, word_count=word_count, language=language)
        log(f"📝 Article generated with {word_count} words (target) in {language}")
    except Exception as e:
        log(f"❌ Article generation error: {e}")
        article = None
    try:
        images = image_scraper.download_multiple_images(news_data, count=3)
        if images:
            log(f"✅ Downloaded images: {images}")
        else:
            log("⚠️ No images found for article.")
    except Exception as e:
        log(f"❌ Image download error: {e}")
    try:
        main_image = images[0] if images else None
        blogger_result = blogger_publisher.publish_article(
            article if article else news_data,
            image_path=main_image,
            status='publish'
        )
        if blogger_result and blogger_result.get('success'):
            log(f"✅ Blogger: Post ID {blogger_result.get('post_id')} | URL: {blogger_result.get('url')}")
        else:
            log(f"❌ Blogger: {blogger_result}")
    except Exception as e:
        log(f"❌ Blogger error: {e}")
    try:
        blog_url = blogger_result.get('url') if blogger_result and blogger_result.get('success') else None
        facebook_result = None
        for img in images:
            facebook_result = facebook_publisher.publish_article(
                article if article else news_data,
                image_path=img,
                blog_url=blog_url
            )
            if facebook_result['success']:
                log(f"✅ Facebook: Post ID {facebook_result['post_id']} (image: {img})")
            else:
                log(f"⚠️ Facebook: {facebook_result.get('error')} (image: {img})")
    except Exception as e:
        log(f"❌ Facebook error: {e}")
    blogger_status = "✅" if blogger_result and blogger_result.get('success') else "❌"
    facebook_status = "✅" if facebook_result and facebook_result.get('success') else "❌"
    log(f"Status: Blogger {blogger_status} | Facebook {facebook_status}")
    return True

def main():
    global topic_index, language_index, trending_topics
    """Main loop"""
    log("="*70)
    log("DUAL-PLATFORM AUTO-POSTER - Blogger + Facebook")
    log("="*70)
    log("Press Ctrl+C to stop")
    log("")
    total_posts = 0
    total_errors = 0
    try:
        while True:
            log("")
            log(f"--- Post #{total_posts + 1} ---")
            success = generate_and_post()
            topic_index = (topic_index + 1) % (len(trending_topics) if trending_topics else 1)
            language_index = (language_index + 1) % len(LANGUAGES)
            if success:
                total_posts += 1
                log(f"Total posts published: {total_posts}")
            else:
                total_errors += 1
                log(f"Post failed (total errors: {total_errors})")
            log("Waiting 1 minute until next post...")
            time.sleep(60)
    except KeyboardInterrupt:
        log("")
        log("="*70)
        log("Stopped by user")
        log(f"Total posts published: {total_posts}")
        log(f"Total errors: {total_errors}")
        log("="*70)

if __name__ == "__main__":
    main()
