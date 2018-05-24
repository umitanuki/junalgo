import backtrader as bt
import pandas as pd
from junalgo.signals import *
from junalgo import bars


class TestStrategy(bt.Strategy):
    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        self.current_strategies = None

    def current_df(self):
        full = self.data.p.dataname
        return full[:self.data.datetime.date(0)]

    def set_strategies(self):
        bt_df = self.current_df()
        strategies = find_best_strategies(bt_df)
        self.current_strategies = strategies[:3]
        self.log('chose 3: {}'.format(self.current_strategies))

    def next(self):
        if len(self.data.close) < 100:
            return

        if self.current_strategies is None:
            try:
                self.set_strategies()
            except BaseException:
                return

        # self.log('Close {}'.format(self.data.close[0]))

        current_df = self.current_df()
        for st, pl in self.current_strategies:
            out_df = st.calc(current_df)
            sig = out_df['signal'].values[-1]
            if self.position.size == 0 and sig == 1:
                size = (self.broker.getcash() * 0.95) // self.data.close[0]
                self.buy(data=self.data, size=size)
                self.current_strategies = [(st, pl)]
                self.log('buy -> chose: {}'.format(st))
                break
            elif self.position.size > 0 and sig == -1:
                self.sell(data=self.data, size=self.position.size)
                self.log('sell')
                self.set_strategies()
                break


def main():
    df = bars.get('SH')
    # df = pd.read_csv('spy.csv', index_col=0, parse_dates=True)
    data = bt.feeds.PandasData(dataname=df)
    cerebro = bt.Cerebro(cheat_on_open=True)
    cerebro.addstrategy(TestStrategy)
    cerebro.adddata(data)
    cerebro.broker.setcash(100000.0)

    # Print out the starting conditions
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # Run over everything
    cerebro.run()

    # Print out the final result
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

    cerebro.plot()


if __name__ == '__main__':
    main()
