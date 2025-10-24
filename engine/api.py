from flask import Flask, request, jsonify
from backtrader import Cerebro
import backtrader as bt
import yfinance as yf
import pandas as pd
from strategies.momentum import MomentumStrategy
from utils.metrics import compute_metrics
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api/backtest', methods=['POST'])
def backtest():
    data = request.get_json()

    ticker = data.get('ticker', 'AAPL')
    start = data.get('start_date', '2022-01-01')
    end = data.get('end_date', '2023-01-01')
    strategy_name = data.get('strategy', 'momentum')
    params = data.get('params', {})

    df = yf.download(ticker, start=start, end=end)

    df = df[['Open', 'High', 'Low', 'Close', 'Volume']].copy()
    df.columns = ['open', 'high', 'low', 'close', 'volume']

    data_feed = bt.feeds.PandasData(dataname=df)
    cerebro = bt.Cerebro()
    cerebro.adddata(data_feed)

    if strategy_name == 'momentum':
        cerebro.addstrategy(MomentumStrategy, **params)
    else:
        return jsonify({'error': 'Unknown strategy'}), 400


    results = cerebro.run()
    strat = results[0]

    portfolio_value = cerebro.broker.getvalue()
    equity_curve = pd.Series(strat.value_series, index=pd.to_datetime(strat.date_series))

    # Compute metrics
    metrics = compute_metrics(strat.value_series)

    # Collect trades
    trades = strat.trade_log

    equity_curve_json = [
        {"date": str(d.date()), "value": float(v)}
        for d, v in equity_curve.items()
    ]

    print("Backtest completed. Portfolio Value: ", portfolio_value)

    return jsonify({
        'metrics': metrics,
        'equity_curve': equity_curve_json,
        'trades': trades
    })

if __name__ == '__main__':
    app.run(debug=True)
