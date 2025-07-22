from flask import Flask, jsonify, request, render_template
import yfinance as yf
import pandas as pd
import pandas_ta as ta
from prophet import Prophet
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

app = Flask(__name__)
analyzer = SentimentIntensityAnalyzer()

@app.route("/stock/<ticker>")
def get_stock_data(ticker):
    stock = yf.Ticker(ticker)
    hist = stock.history(period="1y")

    # Add technical indicators
    hist.ta.rsi(append=True)
    hist.ta.macd(append=True)
    hist.ta.bbands(append=True)

    return jsonify(hist.reset_index().to_dict(orient="records"))

@app.route("/forecast/<ticker>")
def get_forecast(ticker):
    stock = yf.Ticker(ticker)
    hist = stock.history(period="1y")

    # Prepare data for Prophet
    df = hist.reset_index()[['Date', 'Close']]
    df = df.rename(columns={'Date': 'ds', 'Close': 'y'})

    # Create and fit the model
    m = Prophet()
    m.fit(df)

    # Make future dataframe
    future = m.make_future_dataframe(periods=7)
    forecast = m.predict(future)

    return jsonify(forecast.to_dict(orient="records"))

@app.route("/sentiment/<ticker>")
def get_sentiment(ticker):
    stock = yf.Ticker(ticker)
    news = stock.news

    sentiments = []
    for item in news:
        sentiment = analyzer.polarity_scores(item['title'])
        sentiments.append({
            'title': item['title'],
            'publisher': item['publisher'],
            'link': item['link'],
            'sentiment': sentiment
        })

    return jsonify(sentiments)


@app.route("/")
def index():
    return render_template("index.html")
