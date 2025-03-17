import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
from datetime import datetime, timedelta
import time
from data_fetcher import DataFetcher
from sentiment_analyzer import SentimentAnalyzer
from trading_signals import TradingSignalGenerator

# Set page config
st.set_page_config(
    page_title="Financial Sentiment Trading Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        padding: 2rem;
    }
    .stMetric {
        background-color: #1E1E1E;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .error-box {
        background-color: #FF4B4B;
        color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .success-box {
        background-color: #00CC00;
        color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1E1E1E;
        color: #00FF00;
    }
    .stButton>button {
        width: 100%;
        background-color: #1E1E1E;
        color: #00FF00;
        border: 1px solid #00FF00;
        border-radius: 0.5rem;
        padding: 0.5rem;
        margin: 0.5rem 0;
    }
    .stButton>button:hover {
        background-color: #2D2D2D;
    }
</style>
""", unsafe_allow_html=True)

# Initialize components
@st.cache_resource
def init_components():
    try:
        return {
            'data_fetcher': DataFetcher(),
            'sentiment_analyzer': SentimentAnalyzer(),
            'signal_generator': TradingSignalGenerator()
        }
    except Exception as e:
        st.error(f"Error initializing components: {str(e)}")
        return None

# Main title and description
st.title("📈 Financial Sentiment Trading Dashboard")
st.markdown("""
<div style='text-align: center; margin-bottom: 2rem;'>
    <p style='font-size: 1.2rem; color: #888;'>
        Real-time sentiment analysis and trading signals based on news and market data
    </p>
</div>
""", unsafe_allow_html=True)

# Initialize components
components = init_components()

if not components:
    st.error("Failed to initialize the application. Please check your API keys in the .env file.")
    st.stop()

# Sidebar configuration
with st.sidebar:
    st.header("Configuration")
    
    # Stock symbols input
    symbols = st.text_input(
        "Stock Symbols",
        value="AAPL,GOOGL,MSFT",
        help="Enter stock symbols separated by commas"
    ).split(",")
    
    # Convert to list and clean up
    symbols = [s.strip().upper() for s in symbols if s.strip()]
    
    if not symbols:
        st.error("Please enter at least one stock symbol")
        st.stop()
    
    # Analysis parameters
    st.subheader("Analysis Parameters")
    sentiment_threshold = st.slider(
        "Sentiment Threshold",
        min_value=0.0,
        max_value=1.0,
        value=0.2,
        step=0.1
    )
    
    # Refresh interval
    refresh_interval = st.selectbox(
        "Refresh Interval",
        options=["1 minute", "5 minutes", "15 minutes", "30 minutes", "1 hour"],
        index=1
    )
    
    # Auto-refresh toggle
    auto_refresh = st.checkbox("Enable Auto-refresh", value=True)
    
    # Market status
    market_status = components['data_fetcher'].get_market_status()
    status_color = '#00CC00' if market_status else '#FF4B4B'
    status_text = 'OPEN' if market_status else 'CLOSED'
    
    st.markdown(f"""
    <div style='background-color: {status_color}; 
                color: white; 
                padding: 0.5rem; 
                border-radius: 0.5rem; 
                text-align: center; 
                margin: 1rem 0;'>
        Market Status: {status_text}
    </div>
    """, unsafe_allow_html=True)

# Main content area
tab1, tab2, tab3, tab4 = st.tabs([
    "Trading Signals", 
    "Sentiment Analysis", 
    "Price Charts",
    "News Feed"
])

with tab1:
    st.subheader("Trading Signals")
    
    # Create columns for each symbol
    cols = st.columns(len(symbols))
    
    if st.button("Refresh Signals", type="primary"):
        with st.spinner("Updating signals..."):
            for idx, symbol in enumerate(symbols):
                try:
                    with cols[idx]:
                        st.markdown(f"""
                        <div style='background-color: #1E1E1E; 
                                    padding: 1rem; 
                                    border-radius: 0.5rem; 
                                    text-align: center;'>
                            <h3>{symbol}</h3>
                            <div>Fetching data...</div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Fetch data
                        stock_data = components['data_fetcher'].fetch_stock_data(symbol)
                        news_data = components['data_fetcher'].fetch_news(symbol)
                        
                        if stock_data.empty:
                            raise ValueError("No stock data available")
                        
                        # Analyze sentiment
                        sentiment_results = components['sentiment_analyzer'].analyze_news_batch(news_data)
                        
                        # Generate signal
                        signal = components['signal_generator'].generate_signal(
                            sentiment_data=sentiment_results,
                            price_data=stock_data
                        )
                        
                        # Update signal display
                        color = {
                            'BUY': '#00CC00',
                            'SELL': '#FF4B4B',
                            'HOLD': '#FFA500'
                        }.get(signal['action'], '#888888')
                        
                        st.markdown(f"""
                        <div style='background-color: #1E1E1E; 
                                    padding: 1rem; 
                                    border-radius: 0.5rem; 
                                    text-align: center;'>
                            <h3>{symbol}</h3>
                            <div style='color: {color}; font-size: 1.5rem; font-weight: bold;'>
                                {signal['action']}
                            </div>
                            <div style='color: #888;'>
                                Confidence: {signal['confidence']:.1%}
                            </div>
                            <div style='margin-top: 1rem;'>
                                <small>Last Price: ${stock_data['close'].iloc[-1]:.2f}</small>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Display reasoning
                        with st.expander(f"{symbol} Signal Reasoning"):
                            for reason in signal['reasoning']:
                                st.write(f"• {reason}")
                                
                except Exception as e:
                    cols[idx].error(f"Error processing {symbol}: {str(e)}")
    else:
        st.info("Click 'Refresh Signals' to fetch real-time trading signals")

with tab2:
    st.subheader("Sentiment Analysis")
    
    # Select symbol for detailed sentiment analysis
    selected_symbol = st.selectbox("Select Symbol", symbols)
    
    if st.button("Analyze Sentiment", type="primary"):
        with st.spinner("Analyzing sentiment..."):
            try:
                # Fetch and analyze news
                news_data = components['data_fetcher'].fetch_news(selected_symbol)
                sentiment_results = components['sentiment_analyzer'].analyze_news_batch(news_data)
                
                if not news_data:
                    st.warning(f"No recent news found for {selected_symbol}")
                else:
                    # Create sentiment gauge chart
                    fig = go.Figure(go.Indicator(
                        mode="gauge+number",
                        value=sentiment_results['average_sentiment']['compound'],
                        title={'text': "Overall Sentiment"},
                        gauge={
                            'axis': {'range': [-1, 1]},
                            'bar': {'color': "darkblue"},
                            'steps': [
                                {'range': [-1, -0.3], 'color': "#FF4B4B"},
                                {'range': [-0.3, 0.3], 'color': "#FFA500"},
                                {'range': [0.3, 1], 'color': "#00CC00"}
                            ],
                            'threshold': {
                                'line': {'color': "white", 'width': 4},
                                'thickness': 0.75,
                                'value': sentiment_results['average_sentiment']['compound']
                            }
                        }
                    ))
                    
                    fig.update_layout(height=300, margin={'l': 0, 'r': 0, 't': 30, 'b': 0})
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Display sentiment metrics
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric(
                            "Compound Score",
                            f"{sentiment_results['average_sentiment']['compound']:.2f}"
                        )
                    with col2:
                        st.metric(
                            "Positive",
                            f"{sentiment_results['average_sentiment']['positive']:.2f}"
                        )
                    with col3:
                        st.metric(
                            "Negative",
                            f"{sentiment_results['average_sentiment']['negative']:.2f}"
                        )
                    with col4:
                        st.metric(
                            "Neutral",
                            f"{sentiment_results['average_sentiment']['neutral']:.2f}"
                        )
                    
                    # Display recent news
                    st.subheader("Recent News Analysis")
                    for article in news_data:
                        with st.expander(article['title']):
                            st.write(article['content'])
                            st.caption(f"Source: {article['source']} | {article['date'].strftime('%Y-%m-%d %H:%M')}")
                            st.markdown(f"[Read More]({article['url']})")
                
            except Exception as e:
                st.error(f"Error analyzing sentiment: {str(e)}")

with tab3:
    st.subheader("Price Charts")
    
    # Select symbol for price chart
    chart_symbol = st.selectbox("Select Symbol for Chart", symbols, key="chart_symbol")
    
    if st.button("Update Chart", type="primary"):
        with st.spinner("Updating chart..."):
            try:
                # Fetch price data
                stock_data = components['data_fetcher'].fetch_stock_data(chart_symbol)
                
                if stock_data.empty:
                    st.warning(f"No price data available for {chart_symbol}")
                else:
                    # Create candlestick chart with volume
                    fig = make_subplots(
                        rows=2, cols=1,
                        shared_xaxes=True,
                        vertical_spacing=0.03,
                        subplot_titles=(f'{chart_symbol} Price', 'Volume'),
                        row_width=[0.7, 0.3]
                    )
                    
                    # Add candlestick chart
                    fig.add_trace(
                        go.Candlestick(
                            x=stock_data.index,
                            open=stock_data['open'],
                            high=stock_data['high'],
                            low=stock_data['low'],
                            close=stock_data['close'],
                            name='OHLC'
                        ),
                        row=1, col=1
                    )
                    
                    # Add volume bars
                    fig.add_trace(
                        go.Bar(
                            x=stock_data.index,
                            y=stock_data['volume'],
                            name='Volume'
                        ),
                        row=2, col=1
                    )
                    
                    # Update layout
                    fig.update_layout(
                        height=800,
                        xaxis_rangeslider_visible=False,
                        template="plotly_dark"
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Display summary statistics
                    st.subheader("Price Summary")
                    latest_price = stock_data['close'].iloc[-1]
                    price_change = (latest_price - stock_data['close'].iloc[-2]) / stock_data['close'].iloc[-2]
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Latest Price", f"${latest_price:.2f}")
                    with col2:
                        st.metric("Change", f"{price_change:.2%}")
                    with col3:
                        st.metric("Volume", f"{stock_data['volume'].iloc[-1]:,.0f}")
                
            except Exception as e:
                st.error(f"Error creating chart: {str(e)}")

with tab4:
    st.subheader("News Feed")
    
    # Select symbol for news
    news_symbol = st.selectbox("Select Symbol for News", symbols)
    
    if st.button("Update News"):
        with st.spinner("Fetching news..."):
            try:
                # Fetch news
                news_data = components['data_fetcher'].fetch_news(news_symbol)
                
                # Display news articles
                for news in news_data:
                    with st.expander(news['title']):
                        st.write(news['content'])
                        col1, col2 = st.columns([1, 2])
                        with col1:
                            st.caption(f"Source: {news['source']}")
                        with col2:
                            st.caption(f"Date: {news['date'].strftime('%Y-%m-%d %H:%M')}")
                        st.markdown(f"[Read More]({news['url']})")
                
            except Exception as e:
                st.error(f"Error fetching news: {str(e)}")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center'>
    <p>Built with ❤️ using Streamlit</p>
    <p>Data provided by Alpha Vantage and News API</p>
</div>
""", unsafe_allow_html=True)

# Auto-refresh functionality
if auto_refresh:
    refresh_seconds = {
        "1 minute": 60,
        "5 minutes": 300,
        "15 minutes": 900,
        "30 minutes": 1800,
        "1 hour": 3600
    }[refresh_interval]
    
    st.empty()
    time.sleep(refresh_seconds)
    st.experimental_rerun() 