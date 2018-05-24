import pandas as pd
from junalgo.common import NY, api


def get(symbols):
    singular = not isinstance(symbols, (list, tuple, set))
    if singular:
        symbols = [symbols]
    dfs = {}
    now = pd.Timestamp.now(tz=NY)
    end_dt = now
    if now.time() >= pd.Timestamp('09:30', tz=NY).time():
        end_dt = now - \
            pd.Timedelta(now.strftime('%H:%M:%S')) - pd.Timedelta('1 minute')
    result = api.list_bars(symbols, '1D', end_dt=end_dt.isoformat())
    for asset_bar in result:
        symbol = asset_bar.symbol
        bars = asset_bar.bars
        index = []
        d = {
            'open': [],
            'high': [],
            'low': [],
            'close': [],
            'volume': [],
        }
        for bar in bars:
            index.append(pd.Timestamp(bar.time))
            d['open'].append(float(bar.open))
            d['high'].append(float(bar.high))
            d['low'].append(float(bar.low))
            d['close'].append(float(bar.close))
            d['volume'].append(int(bar.volume))
        dfs[symbol] = pd.DataFrame(d, index=index)
    if singular:
        return dfs[symbol]
    return dfs
