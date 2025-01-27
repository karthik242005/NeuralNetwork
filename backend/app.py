import os
import json
import logging
from flask import Flask, jsonify, render_template
from flask_cors import CORS
from newsapi import NewsApiClient
from datetime import datetime, timedelta

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Flask Web Application
app = Flask(__name__, 
            static_folder='../frontend', 
            template_folder='../frontend')
CORS(app)  # Enable CORS for all routes

def fetch_ml_news(api_key, days_back=7, max_articles=20):
    """
    Fetch ML and AI related news with advanced filtering
    """
    newsapi = NewsApiClient(api_key=api_key)
    to_date = datetime.now()
    from_date = to_date - timedelta(days=days_back)
    
    ml_articles_with_content = []
    
    # More specific and targeted keywords
    keywords = [
        '"machine learning" AND (technology OR innovation OR research)',
        '"artificial intelligence" AND (breakthrough OR development OR future)',
        '"deep learning" AND (neural OR algorithm OR model)',
        '"AI research" AND (scientific OR academic OR cutting-edge)',
        '"data science" AND (analysis OR prediction OR insights)'
    ]

    # Trusted sources for AI and ML news
    trusted_sources = [
        'techcrunch', 
        'wired', 
        'mit-technology-review', 
        'ars-technica', 
        'science-daily', 
        'verge'
    ]

    for keyword in keywords:
        try:
            # Advanced search with multiple parameters
            articles = newsapi.get_everything(
                q=keyword,
                language='en',
                sources=','.join(trusted_sources),
                sort_by='relevancy',  # Sort by relevance instead of publish date
                from_param=from_date.strftime('%Y-%m-%d'),
                to=to_date.strftime('%Y-%m-%d'),
                page_size=max_articles
            )
            
            # Process and filter articles
            for article in articles['articles']:
                # Additional filtering to ensure relevance
                if (article['title'] and article['description'] and 
                    any(tech_term in article['title'].lower() or 
                        tech_term in article['description'].lower() 
                        for tech_term in ['ai', 'machine learning', 'deep learning', 'data science'])):
                    
                    # Avoid duplicates
                    if not any(existing['url'] == article['url'] for existing in ml_articles_with_content):
                        processed_article = {
                            'title': article['title'],
                            'source_name': article['source']['name'],
                            'description': article['description'],
                            'url': article['url'],
                            'publishedAt': article['publishedAt'],
                            # Additional metadata
                            'keywords': keyword
                        }
                        
                        ml_articles_with_content.append(processed_article)
                
                # Stop if we've reached max articles
                if len(ml_articles_with_content) >= max_articles:
                    break

        except Exception as e:
            logger.error(f"Error fetching news for keyword {keyword}: {e}")
    
    # Final filtering and sorting
    ml_articles_with_content = sorted(
        ml_articles_with_content, 
        key=lambda x: x['publishedAt'], 
        reverse=True
    )[:max_articles]

    return ml_articles_with_content

@app.route('/')
def index():
    """
    Render the main index page with fetched news
    """
    try:
        API_KEY = '714c12d6ab174ecf881357114426a92f'  # Replace with your actual NewsAPI key
        news_articles = fetch_ml_news(API_KEY)
        
        # Log the number of articles fetched
        logger.info(f"Fetched {len(news_articles)} ML and AI related articles")
        
        return render_template('index.html', news_articles=news_articles)
    
    except Exception as e:
        logger.error(f"Error rendering index page: {e}")
        return render_template('error.html', error_message="Unable to fetch news articles")

@app.route('/refresh-news')
def refresh_news():
    """
    Endpoint to manually refresh news articles
    """
    try:
        API_KEY = '714c12d6ab174ecf881357114426a92f'
        news_articles = fetch_ml_news(API_KEY)
        return jsonify(news_articles)
    except Exception as e:
        logger.error(f"Error refreshing news: {e}")
        return jsonify({"error": "Unable to refresh news articles"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)