import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer, PorterStemmer
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from typing import List, Dict, Any
import numpy as np
import logging
from collections import defaultdict

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')
    nltk.download('wordnet')

class SentimentAnalyzer:
    def __init__(self):
        """Initialize the sentiment analyzer with required components."""
        self.vader = SentimentIntensityAnalyzer()
        self.stop_words = set(stopwords.words('english'))
        self.lemmatizer = WordNetLemmatizer()
        self.stemmer = PorterStemmer()
        self.logger = logging.getLogger(__name__)
        
        # Financial-specific words to consider
        self.financial_keywords = {
            'positive': ['surge', 'growth', 'profit', 'gain', 'up', 'rise', 'positive', 'strong'],
            'negative': ['decline', 'loss', 'down', 'fall', 'negative', 'weak', 'risk', 'concern']
        }
    
    def analyze_news_batch(self, news_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze sentiment for a batch of news articles.
        
        Args:
            news_data (List[Dict]): List of news articles
            
        Returns:
            Dict: Aggregated sentiment analysis results
        """
        try:
            # Initialize results
            results = {
                'articles': [],
                'average_sentiment': {
                    'compound': 0.0,
                    'positive': 0.0,
                    'negative': 0.0,
                    'neutral': 0.0
                },
                'keyword_analysis': defaultdict(int),
                'sentence_sentiments': []
            }
            
            # Process each article
            for article in news_data:
                article_analysis = self._analyze_single_article(article)
                results['articles'].append(article_analysis)
                
                # Update average sentiment
                for key in results['average_sentiment']:
                    results['average_sentiment'][key] += article_analysis['sentiment'][key]
                
                # Update keyword analysis
                for word, count in article_analysis['keyword_analysis'].items():
                    results['keyword_analysis'][word] += count
                
                # Add sentence sentiments
                results['sentence_sentiments'].extend(article_analysis['sentence_sentiments'])
            
            # Calculate averages
            num_articles = len(news_data)
            for key in results['average_sentiment']:
                results['average_sentiment'][key] /= num_articles
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error analyzing news batch: {str(e)}")
            raise
    
    def _analyze_single_article(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze sentiment for a single article.
        
        Args:
            article (Dict): News article data
            
        Returns:
            Dict: Article analysis results
        """
        # Combine title and content for analysis
        text = f"{article['title']} {article['content']}"
        
        # Tokenize into sentences
        sentences = sent_tokenize(text)
        
        # Analyze each sentence
        sentence_sentiments = []
        for sentence in sentences:
            sentiment = self._analyze_sentence(sentence)
            sentence_sentiments.append({
                'sentence': sentence,
                'sentiment': sentiment
            })
        
        # Get overall sentiment
        vader_sentiment = self.vader.polarity_scores(text)
        textblob_sentiment = TextBlob(text).sentiment
        
        # Combine sentiment scores
        sentiment = {
            'compound': vader_sentiment['compound'],
            'positive': vader_sentiment['pos'],
            'negative': vader_sentiment['neg'],
            'neutral': vader_sentiment['neu'],
            'subjectivity': textblob_sentiment.subjectivity
        }
        
        # Analyze keywords
        keyword_analysis = self._analyze_keywords(text)
        
        return {
            'title': article['title'],
            'sentiment': sentiment,
            'keyword_analysis': keyword_analysis,
            'sentence_sentiments': sentence_sentiments
        }
    
    def _analyze_sentence(self, sentence: str) -> Dict[str, float]:
        """
        Analyze sentiment for a single sentence.
        
        Args:
            sentence (str): Input sentence
            
        Returns:
            Dict: Sentence sentiment scores
        """
        # Get VADER sentiment
        vader_sentiment = self.vader.polarity_scores(sentence)
        
        # Get TextBlob sentiment
        textblob_sentiment = TextBlob(sentence).sentiment
        
        return {
            'compound': vader_sentiment['compound'],
            'subjectivity': textblob_sentiment.subjectivity,
            'polarity': textblob_sentiment.polarity
        }
    
    def _analyze_keywords(self, text: str) -> Dict[str, int]:
        """
        Analyze financial keywords in the text.
        
        Args:
            text (str): Input text
            
        Returns:
            Dict: Keyword frequencies
        """
        # Tokenize and clean text
        tokens = word_tokenize(text.lower())
        tokens = [self.lemmatizer.lemmatize(token) for token in tokens]
        tokens = [token for token in tokens if token not in self.stop_words]
        
        # Count financial keywords
        keyword_counts = defaultdict(int)
        for category, keywords in self.financial_keywords.items():
            for keyword in keywords:
                keyword_counts[f"{category}_{keyword}"] = tokens.count(keyword)
        
        return dict(keyword_counts) 