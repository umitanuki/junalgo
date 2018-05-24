import backtrader as bt
import pandas as pd
import talib
import sys


class PandasSignalData(bt.feeds.PandasData):
    params = (
        ('datetime', None),

        # Possible values below:
        #  None : column not present
        #  -1 : autodetect position or case-wise equal name
        #  >= 0 : numeric index to the colum in the pandas dataframe
        #  string : column name (as index) in the pandas dataframe
        ('open', -1),
        ('high', -1),
        ('low', -1),
        ('close', -1),
        ('volume', -1),
        ('signal', -1),
    )
    lines = ('signal',)


class SignalStrategy(bt.Strategy):
    def next(self):
        if self.position.size == 0 and self.data.signal[0] == 1:
            size = (self.broker.getcash() * 0.95) // self.data.close[0]
            self.buy(data=self.data, size=size)
        elif self.position.size > 0 and self.data.signal[0] == -1:
            self.sell(data=self.data, size=self.position.size)


class Signal(object):

    def __repr__(self):
        return self.name


class RSISignal(Signal):
    def __init__(self, period1, period2):
        self.period1 = period1
        self.period2 = period2
        self.name = f'RSI_{period1}_{period2}'

    def calc(self, df):
        rsi1 = talib.RSI(df.close, timeperiod=self.period1)
        rsi2 = talib.RSI(df.close, timeperiod=self.period2)
        rsi1_prev = rsi1.shift(1)
        rsi2_prev = rsi2.shift(1)
        out = df.copy()
        out['signal'] = 0
        out.loc[(rsi1_prev < 30) & (rsi1 >= 30), 'signal'] = 1
        out.loc[(rsi2_prev > 70) & (rsi2 <= 70), 'signal'] = -1
        return out


class MACDSignal(Signal):
    def __init__(self, fast, slow, signal):
        self.fast = fast
        self.slow = slow
        self.signal = signal
        self.name = f'MACD_{fast}_{slow}_{signal}'

    def calc(self, df):
        macd, signal, hist = talib.MACD(
            df.close, fastperiod=self.fast,
            slowperiod=self.slow, signalperiod=self.signal)
        hist_prev = hist.shift(1)
        out = df.copy()
        out['signal'] = 0
        out.loc[(hist_prev < 0) & (hist >= 0), 'signal'] = 1
        out.loc[(hist_prev > 0) & (hist <= 0), 'signal'] = -1
        return out


class CCISignal(Signal):
    def __init__(self, period1, period2):
        self.period1 = period1
        self.period2 = period2
        self.name = f'CCI_{period1}_{period2}'

    def calc(self, df):
        cci1 = talib.CCI(
            df.high, df.low, df.close, timeperiod=self.period1)
        cci2 = talib.CCI(
            df.high, df.low, df.close, timeperiod=self.period2)
        cci1_prev = cci1.shift(1)
        cci2_prev = cci2.shift(1)
        out = df.copy()
        out['signal'] = 0
        out.loc[(cci1_prev < 30) & (cci1 >= 30), 'signal'] = 1
        out.loc[(cci2_prev > 70) & (cci2 <= 70), 'signal'] = -1
        return out


class StochFSignal(Signal):
    def __init__(self, fastk, fastd):
        self.fastk = fastk
        self.fastd = fastd
        self.name = f'STOCKF_{fastk}_{fastd}'

    def calc(self, df):
        fastk, fastd = talib.STOCHF(
            df.high, df.low, df.close,
            fastk_period=self.fastk, fastd_period=self.fastd)
        fastk_prev = fastk.shift(1)
        out = df.copy()
        out['signal'] = 0
        out.loc[(fastk_prev < 20) & (fastk >= 20), 'signal'] = 1
        out.loc[(fastk_prev > 80) & (fastk <= 80), 'signal'] = -1
        return out


class EMASignal(Signal):
    def __init__(self, period1, period2):
        self.period1 = period1
        self.period2 = period2
        self.name = f'EMA_{period1}_{period2}'

    def calc(self, df):
        ema1 = talib.EMA(df.close, timeperiod=self.period1)
        ema2 = talib.EMA(df.close, timeperiod=self.period2)
        ema1_prev = ema1.shift(1)
        ema2_prev = ema2.shift(1)
        close = df.close
        close_prev = df.close.shift(1)
        out = df.copy()
        out['signal'] = 0
        out.loc[(ema1_prev > close_prev) & (ema1 <= close), 'signal'] = 1
        out.loc[(ema2_prev < close_prev) & (ema2 >= close), 'signal'] = -1
        return out


class SARSignal(Signal):
    def __init__(self, acceleration, maximum):
        self.acceleration = acceleration
        self.maximum = maximum
        self.name = f'SAR_{acceleration}_{maximum}'

    def calc(self, df):
        sar = talib.SAR(
            df.high,
            df.low,
            acceleration=self.acceleration,
            maximum=self.maximum)
        sar_prev = sar.shift(1)
        low = df.low
        low_prev = df.low.shift(1)
        high = df.high
        high_prev = df.high.shift(1)
        out = df.copy()
        out['signal'] = 0
        out.loc[(sar_prev < low_prev) & (sar > high), 'signal'] = 1
        out.loc[(sar_prev > high_prev) & (sar < low), 'signal'] = -1
        return out


class SignalGroup(object):
    def __init__(self, name, signalers):
        self.name = name
        self.signalers = signalers

    def find_best(self, df, duration=pd.Timedelta('180 days')):
        all = rank_signals(self.signalers, df, duration=duration)
        return all[0]


signalGroups = [
    SignalGroup('RSI',
                [RSISignal(period1, period2)
                 for period1 in range(2, 15, 2)
                 for period2 in range(2, 15, 2)]),
    SignalGroup('MACD',
                [MACDSignal(fast, slow, signal)
                 for fast in range(8, 16, 2)
                 for slow in range(12, 26, 2)
                 for signal in range(2, 20, 2) if signal < fast < slow]),
    SignalGroup('CCI',
                [CCISignal(period1, period2)
                 for period1 in range(2, 15, 2)
                 for period2 in range(4, 15, 2)]),
    SignalGroup('STOCHF',
                [StochFSignal(fastk, fastd)
                 for fastk in range(1, 10, 2)
                 for fastd in range(1, 10, 2) if fastk > fastd]),
    SignalGroup('EMA',
                [EMASignal(period1, period2)
                 for period1 in range(3, 20, 3)
                 for period2 in range(3, 20, 3)]),
    SignalGroup('SAR',
                [SARSignal(acceleration * 0.01, maximum * 0.1)
                 for acceleration in range(1, 10, 2)
                 for maximum in range(1, 10, 2)]),
]


def find_instance(name):
    for sg in signalGroups:
        for s in sg.signalers:
            if s.name == name:
                return s


def rank_signals(signalers, ohlcv_df, duration=pd.Timedelta('180 days')):
    results = []
    for signaler in signalers:
        df = signaler.calc(ohlcv_df)
        df = df[df.index[-1] - duration:]
        profit_ratio = eval_strategy(SignalStrategy, df)
        sys.stdout.write(f'{signaler.name} {profit_ratio}\r')
        results.append((signaler, profit_ratio))

    return sorted(results, key=lambda x: -x[1])


def eval_strategy(st, df):
    cerebro = bt.Cerebro(cheat_on_open=True)
    cerebro.addstrategy(st)
    cerebro.adddata(PandasSignalData(dataname=df))
    principal = cerebro.broker.getvalue()
    cerebro.run()
    final = cerebro.broker.getvalue()
    return (final - principal) / principal


def find_best_strategies(df):
    results = []
    for sg in signalGroups:
        signaler, pl = sg.find_best(df)
        results.append((signaler, pl))

    return sorted(results, key=lambda x: -x[1])
