# Financial News Sentiment Analysis & Trading Signals

A real-time financial dashboard that combines stock market data with news sentiment analysis to generate trading signals. This application uses machine learning and natural language processing to analyze market sentiment and provide trading recommendations.

## Features

- Real-time stock price monitoring
- News sentiment analysis using NLP
- Automated trading signals generation
- Interactive data visualization
- Multi-stock tracking (AAPL, GOOGL, MSFT)
- Historical price data analysis
- Sentiment-based market insights

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Virtual Environment
- API Keys:
  - Alpha Vantage API key (for stock data)
  - News API key (for news articles)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd NLP_Project
```

2. Create and activate a virtual environment:

For Windows:
```bash
python -m venv venv
.\venv\Scripts\activate
```

For Unix/MacOS:
```bash
python -m venv venv
source venv/bin/activate
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

## Configuration

1. Create a `.env` file in the project root directory
2. Add your API keys:
```
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key
NEWS_API_KEY=your_news_api_key
```

## Usage

1. Ensure your virtual environment is activated:

For Windows:
```bash
.\venv\Scripts\activate
```

For Unix/MacOS:
```bash
source venv/bin/activate
```

2. Run the Streamlit application:
```bash
streamlit run app.py
```

3. Open your web browser and navigate to `http://localhost:8501`

## Dashboard Features

- **Stock Price Monitor**: Real-time price tracking for selected stocks
- **News Feed**: Latest financial news with sentiment analysis
- **Trading Signals**: AI-generated buy/sell recommendations
- **Sentiment Analysis**: Overall market sentiment indicators
- **Technical Indicators**: Price trends and volume analysis
- **Interactive Charts**: Visual representation of price movements

## Project Structure

```
NLP_Project/
├── app.py                  # Main Streamlit application
├── data_fetcher.py        # Data retrieval module
├── sentiment_analyzer.py   # News sentiment analysis
├── trading_signals.py     # Trading signal generation
├── alert_system.py        # Alert system module
├── requirements.txt       # Project dependencies
├── .env                   # Environment variables
└── README.md             # Project documentation
```

## Dependencies

Main packages used:
- streamlit==1.32.0
- pandas==2.2.1
- numpy==1.26.4
- requests==2.31.0
- python-dotenv==1.0.1
- nltk==3.8.1
- scikit-learn==1.3.2
- textblob>=0.15.3
- vaderSentiment>=3.3.2
- plotly>=5.3.0

## Error Handling

If you encounter any issues:

1. Check if your virtual environment is activated
2. Verify API keys in the `.env` file
3. Ensure all dependencies are installed correctly
4. Check internet connectivity for real-time data
5. Verify Python version compatibility

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Alpha Vantage API for stock data
- News API for financial news
- NLTK and TextBlob for sentiment analysis
- Streamlit for the web interface

## Support

For support, please open an issue in the repository or contact the maintainers.

## Results:
This is the sample output attached below.
![image](https://github.com/user-attachments/assets/a5a35d7d-019b-41a7-b754-3bd2d842b18b)
![image](https://github.com/user-attachments/assets/4bae9bde-df7a-4808-b85a-f82ba7d613b1)
![image](https://github.com/user-attachments/assets/f731d265-1711-4eb2-9497-9292a2b994d2)




