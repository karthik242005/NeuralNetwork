import logging
from datetime import datetime, timedelta
import json
import nltk
from newspaper import Article
from newsapi import NewsApiClient

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Download necessary NLTK data
nltk.download('punkt', quiet=True)

class MLNewsContentAggregator:
    def __init__(self, api_key):
        """
        Initialize the ML News Content Aggregator
        
        Args:
            api_key (str): NewsAPI key
        """
        self.newsapi = NewsApiClient(api_key=api_key)
        
        # ML and AI related keywords
        self.ml_keywords = [
            'machine learning', 
            'artificial intelligence', 
            'deep learning', 
            'neural networks', 
            'AI research', 
            'data science'
        ]

    def extract_article_content(self, url):
        """
        Extract full content from a news article URL
        """
        try:
            # Download and parse the article
            article = Article(url)
            article.download()
            article.parse()
            article.nlp()
            
            # Return structured article data
            return {
                'title': article.title or 'No Title',
                'authors': article.authors or [],
                'publish_date': str(article.publish_date) if article.publish_date else 'Unknown',
                'summary': article.summary or '',
                'keywords': article.keywords or [],
                'text': article.text or '',
                'top_image': article.top_image or '',
                'url': url
            }
        except Exception as e:
            logger.error(f"Error extracting content from {url}: {e}")
            return None

    def get_ml_news_with_content(self, days_back=7, max_articles=20):
        """
        Fetch ML and AI related news with full content
        """
        # Calculate date range
        to_date = datetime.now()
        from_date = to_date - timedelta(days=days_back)
        
        # Prepare results list
        ml_articles_with_content = []
        
        # Search through different keywords
        for keyword in self.ml_keywords:
            try:
                # Fetch articles
                articles = self.newsapi.get_everything(
                    q=keyword,
                    language='en',
                    sort_by='publishedAt',
                    from_param=from_date.strftime('%Y-%m-%d'),
                    to=to_date.strftime('%Y-%m-%d'),
                    page_size=max_articles
                )
                
                # Process and extract content for each article
                for article in articles['articles']:
                    # Extract full article content
                    full_article = self.extract_article_content(article['url'])
                    
                    if full_article:
                        # Add source metadata
                        full_article.update({
                            'source_name': article['source']['name'],
                            'original_description': article['description'] or '',
                            'keyword_matched': keyword
                        })
                        
                        # Avoid duplicates
                        if not any(a['url'] == full_article['url'] for a in ml_articles_with_content):
                            ml_articles_with_content.append(full_article)
                    
                    # Break if we've reached max articles
                    if len(ml_articles_with_content) >= max_articles:
                        break
            
            except Exception as e:
                logger.error(f"Error fetching news for {keyword}: {e}")
        
        return ml_articles_with_content

    def save_to_json(self, articles, filename='ml_news_content.json'):
        """
        Save articles to JSON
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(articles, f, ensure_ascii=False, indent=4)
            logger.info(f"Saved {len(articles)} articles to {filename}")
        except Exception as e:
            logger.error(f"Error saving JSON: {e}")