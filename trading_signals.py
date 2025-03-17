from typing import Dict, Any, List
import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta

class TradingSignalGenerator:
    def __init__(self):
        """Initialize the trading signal generator."""
        self.logger = logging.getLogger(__name__)
        
        # Define signal thresholds
        self.sentiment_threshold = 0.2
        self.price_change_threshold = 0.02
        self.volume_threshold = 1.5
        
        # Define signal weights
        self.weights = {
            'sentiment': 0.4,
            'price_trend': 0.3,
            'volume': 0.2,
            'volatility': 0.1
        }
    
    def generate_signal(self, 
                       sentiment_data: Dict[str, Any],
                       price_data: pd.DataFrame) -> Dict[str, Any]:
        """
        Generate trading signal based on sentiment and price data.
        
        Args:
            sentiment_data (Dict): Sentiment analysis results
            price_data (pd.DataFrame): Price data
            
        Returns:
            Dict: Trading signal with confidence and reasoning
        """
        try:
            # Calculate price metrics
            price_metrics = self._calculate_price_metrics(price_data)
            
            # Calculate sentiment metrics
            sentiment_metrics = self._calculate_sentiment_metrics(sentiment_data)
            
            # Calculate volume metrics
            volume_metrics = self._calculate_volume_metrics(price_data)
            
            # Calculate volatility metrics
            volatility_metrics = self._calculate_volatility_metrics(price_data)
            
            # Combine all metrics
            metrics = {
                'price_trend': price_metrics,
                'sentiment': sentiment_metrics,
                'volume': volume_metrics,
                'volatility': volatility_metrics
            }
            
            # Generate signal
            signal = self._generate_signal_from_metrics(metrics)
            
            # Add reasoning
            signal['reasoning'] = self._generate_reasoning(metrics, signal)
            
            return signal
            
        except Exception as e:
            self.logger.error(f"Error generating trading signal: {str(e)}")
            raise
    
    def _calculate_price_metrics(self, price_data: pd.DataFrame) -> Dict[str, float]:
        """Calculate price trend metrics."""
        try:
            # Calculate price changes
            current_price = price_data['close'].iloc[-1]
            prev_price = price_data['close'].iloc[-2]
            price_change = (current_price - prev_price) / prev_price
            
            # Calculate moving averages
            ma5 = price_data['close'].rolling(window=5).mean().iloc[-1]
            ma20 = price_data['close'].rolling(window=20).mean().iloc[-1]
            
            # Calculate trend strength
            trend_strength = (ma5 - ma20) / ma20
            
            return {
                'current_price': current_price,
                'price_change': price_change,
                'ma5': ma5,
                'ma20': ma20,
                'trend_strength': trend_strength
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating price metrics: {str(e)}")
            raise
    
    def _calculate_sentiment_metrics(self, sentiment_data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate sentiment metrics."""
        try:
            avg_sentiment = sentiment_data['average_sentiment']
            
            # Calculate sentiment strength
            sentiment_strength = abs(avg_sentiment['compound'])
            
            # Calculate sentiment bias
            sentiment_bias = avg_sentiment['positive'] - avg_sentiment['negative']
            
            return {
                'compound': avg_sentiment['compound'],
                'positive': avg_sentiment['positive'],
                'negative': avg_sentiment['negative'],
                'neutral': avg_sentiment['neutral'],
                'strength': sentiment_strength,
                'bias': sentiment_bias
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating sentiment metrics: {str(e)}")
            raise
    
    def _calculate_volume_metrics(self, price_data: pd.DataFrame) -> Dict[str, float]:
        """Calculate volume metrics."""
        try:
            current_volume = price_data['volume'].iloc[-1]
            avg_volume = price_data['volume'].rolling(window=20).mean().iloc[-1]
            volume_ratio = current_volume / avg_volume
            
            return {
                'current_volume': current_volume,
                'avg_volume': avg_volume,
                'volume_ratio': volume_ratio
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating volume metrics: {str(e)}")
            raise
    
    def _calculate_volatility_metrics(self, price_data: pd.DataFrame) -> Dict[str, float]:
        """Calculate volatility metrics."""
        try:
            # Calculate daily returns
            returns = price_data['close'].pct_change()
            
            # Calculate volatility (standard deviation of returns)
            volatility = returns.std()
            
            # Calculate recent volatility (last 5 days)
            recent_volatility = returns.tail(5).std()
            
            return {
                'volatility': volatility,
                'recent_volatility': recent_volatility,
                'volatility_trend': recent_volatility / volatility if volatility > 0 else 0
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating volatility metrics: {str(e)}")
            raise
    
    def _generate_signal_from_metrics(self, metrics: Dict[str, Dict[str, float]]) -> Dict[str, Any]:
        """Generate trading signal from combined metrics."""
        try:
            # Calculate weighted score
            score = 0
            
            # Sentiment component
            sentiment_score = metrics['sentiment']['bias'] * metrics['sentiment']['strength']
            score += sentiment_score * self.weights['sentiment']
            
            # Price trend component
            price_score = metrics['price_trend']['trend_strength']
            score += price_score * self.weights['price_trend']
            
            # Volume component
            volume_score = (metrics['volume']['volume_ratio'] - 1) / 2
            score += volume_score * self.weights['volume']
            
            # Volatility component
            volatility_score = -metrics['volatility']['volatility_trend']
            score += volatility_score * self.weights['volatility']
            
            # Determine signal
            if score > self.sentiment_threshold:
                action = 'BUY'
            elif score < -self.sentiment_threshold:
                action = 'SELL'
            else:
                action = 'HOLD'
            
            # Calculate confidence
            confidence = min(abs(score), 1.0)
            
            return {
                'action': action,
                'confidence': confidence,
                'score': score
            }
            
        except Exception as e:
            self.logger.error(f"Error generating signal from metrics: {str(e)}")
            raise
    
    def _generate_reasoning(self, metrics: Dict[str, Dict[str, float]], signal: Dict[str, Any]) -> List[str]:
        """Generate reasoning for the trading signal."""
        reasoning = []
        
        # Sentiment reasoning
        sentiment = metrics['sentiment']
        if sentiment['bias'] > 0:
            reasoning.append(f"Positive sentiment bias ({sentiment['bias']:.2f}) with strong sentiment ({sentiment['strength']:.2f})")
        else:
            reasoning.append(f"Negative sentiment bias ({sentiment['bias']:.2f}) with strong sentiment ({sentiment['strength']:.2f})")
        
        # Price trend reasoning
        price = metrics['price_trend']
        if price['trend_strength'] > 0:
            reasoning.append(f"Strong upward price trend (MA5 above MA20)")
        else:
            reasoning.append(f"Strong downward price trend (MA5 below MA20)")
        
        # Volume reasoning
        volume = metrics['volume']
        if volume['volume_ratio'] > self.volume_threshold:
            reasoning.append(f"High trading volume ({volume['volume_ratio']:.1f}x average)")
        
        # Volatility reasoning
        volatility = metrics['volatility']
        if volatility['volatility_trend'] > 1.5:
            reasoning.append(f"Increasing market volatility")
        
        return reasoning 