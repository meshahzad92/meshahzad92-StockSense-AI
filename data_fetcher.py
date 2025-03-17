import os
import requests
from datetime import datetime, timedelta
import pandas as pd
from typing import List, Dict, Any
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# Load environment variables
load_dotenv()

class DataFetcher:
    def __init__(self):
        self.alpha_vantage_key = os.getenv('ALPHA_VANTAGE_API_KEY')
        self.news_api_key = os.getenv('NEWS_API_KEY')
        self.logger = logging.getLogger(__name__)
        
        # Validate API keys
        if not self.alpha_vantage_key:
            self.logger.error("Alpha Vantage API key not found in .env file")
            raise ValueError("Alpha Vantage API key is required")
        if not self.news_api_key:
            self.logger.error("News API key not found in .env file")
            raise ValueError("News API key is required")
        
    def fetch_stock_data(self, symbol: str, period: str = '1d') -> pd.DataFrame:
        """
        Fetch real-time stock data using Alpha Vantage API.
        
        Args:
            symbol (str): Stock symbol (e.g., 'AAPL')
            period (str): Time period for data
            
        Returns:
            pd.DataFrame: Stock data
        """
        try:
            self.logger.info(f"Fetching stock data for {symbol}")
            
            # Alpha Vantage API endpoint
            url = f'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=5min&apikey={self.alpha_vantage_key}'
            
            self.logger.info(f"Making request to: {url}")
            response = requests.get(url)
            
            # Check response status
            if response.status_code != 200:
                self.logger.error(f"API request failed with status code {response.status_code}")
                self.logger.error(f"Response content: {response.text}")
                raise ValueError(f"API request failed: {response.text}")
            
            data = response.json()
            
            # Log the response structure
            self.logger.info(f"API Response keys: {data.keys()}")
            
            # Check for API error messages
            if 'Error Message' in data:
                self.logger.error(f"API Error: {data['Error Message']}")
                raise ValueError(f"Alpha Vantage API Error: {data['Error Message']}")
            
            if 'Time Series (5min)' not in data:
                self.logger.error(f"Unexpected API response format. Available keys: {data.keys()}")
                raise ValueError(f"No data found for symbol {symbol}")
            
            # Convert to DataFrame
            df = pd.DataFrame.from_dict(data['Time Series (5min)'], orient='index')
            
            # Rename columns
            df.columns = ['open', 'high', 'low', 'close', 'volume']
            
            # Convert string values to float
            for col in df.columns:
                df[col] = pd.to_numeric(df[col].str.replace(r'[^\d.]', ''), errors='coerce')
            
            # Add date index
            df.index = pd.to_datetime(df.index)
            
            # Sort by date
            df = df.sort_index()
            
            self.logger.info(f"Successfully fetched data for {symbol}. Shape: {df.shape}")
            return df
            
        except Exception as e:
            self.logger.error(f"Error fetching stock data for {symbol}: {str(e)}")
            raise
    
    def fetch_news(self, symbol: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Fetch real-time news using News API.
        
        Args:
            symbol (str): Stock symbol
            limit (int): Number of articles to fetch
        
        Returns:
            List[Dict]: List of news articles
        """
        try:
            self.logger.info(f"Fetching news for {symbol}")
            
            # News API endpoint
            url = f'https://newsapi.org/v2/everything'
            params = {
                'q': f"{symbol} stock",  # Add 'stock' to get more relevant results
                'language': 'en',
                'sortBy': 'publishedAt',
                'apiKey': self.news_api_key,
                'pageSize': limit,
                'from': (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')  # Last 7 days
            }
            
            self.logger.info(f"Making request to News API with params: {params}")
            response = requests.get(url, params=params)
            
            # Check response status
            if response.status_code != 200:
                self.logger.error(f"News API request failed with status code {response.status_code}")
                self.logger.error(f"Response content: {response.text}")
                raise ValueError(f"News API request failed: {response.text}")
            
            data = response.json()
            
            if data.get('status') != 'ok':
                self.logger.error(f"News API error: {data.get('message', 'Unknown error')}")
                raise ValueError(f"News API error: {data.get('message', 'Unknown error')}")
            
            if 'articles' not in data:
                self.logger.error("No articles found in API response")
                return []
            
            # Format news articles
            news = []
            for article in data['articles']:
                if not article['description']:
                    continue
                    
                news_item = {
                    'title': article['title'],
                    'content': article['description'],
                    'source': article['source']['name'],
                    'date': datetime.strptime(article['publishedAt'], '%Y-%m-%dT%H:%M:%SZ'),
                    'url': article['url']
                }
                news.append(news_item)
            
            self.logger.info(f"Successfully fetched {len(news)} news articles for {symbol}")
            return news
            
        except Exception as e:
            self.logger.error(f"Error fetching news for {symbol}: {str(e)}")
            raise
    
    def get_market_status(self) -> bool:
        """
        Check if the market is open based on current time.
        
        Returns:
            bool: True if market is open, False otherwise
        """
        now = datetime.now()
        # Market is open 9:30 AM to 4:00 PM EST, Monday to Friday
        # Simplified check (can be made more accurate with timezone handling)
        return (9 <= now.hour < 16) and (now.weekday() < 5)
    
    def get_company_info(self, symbol: str) -> Dict[str, Any]:
        """
        Fetch company information using Finnhub API.
        
        Args:
            symbol (str): Stock symbol
            
        Returns:
            Dict: Company information
        """
        try:
            # Finnhub API endpoint
            url = f'https://finnhub.io/api/v1/stock/profile2?symbol={symbol}&token={self.finnhub_key}'
            response = requests.get(url)
            return response.json()
            
        except Exception as e:
            self.logger.error(f"Error fetching company info for {symbol}: {str(e)}")
            raise 