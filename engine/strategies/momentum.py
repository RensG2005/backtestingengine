import backtrader as bt

class MomentumStrategy(bt.Strategy):
    params = (('sma_period', 20),)

    def __init__(self):
        self.sma = bt.indicators.SimpleMovingAverage(self.data.close, period=self.params.sma_period)
        self.value_series = []
        self.date_series = []
        self.trade_log = []

    def next(self):
        # Track portfolio value each step
        self.value_series.append(self.broker.getvalue())
        self.date_series.append(self.data.datetime.date(0))

        if not self.position:
            if self.data.close[0] > self.sma[0]:
                self.buy(size=10)
                self.trade_log.append({
                    'date': str(self.data.datetime.date(0)),
                    'action': 'BUY',
                    'price': float(self.data.close[0]),
                    'size': 10
                })
        else:
            if self.data.close[0] < self.sma[0]:
                self.sell(size=10)
                self.trade_log.append({
                    'date': str(self.data.datetime.date(0)),
                    'action': 'SELL',
                    'price': float(self.data.close[0]),
                    'size': 10
                })
