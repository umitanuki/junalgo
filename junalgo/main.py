import logging
import json
import pandas as pd
import time
from junalgo.common import NY, api
from junalgo.signals import find_instance, find_best_strategies
from junalgo import bars

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

state_file = '.state.json'


def load_state():
    try:
        with open(state_file) as fp:
            return json.load(fp)
    except BaseException:
        return {}


def save_state(state):
    with open(state_file, 'w') as fp:
        json.dump(state, fp)


def get_current_strategies():
    state = load_state()
    if 'current_strategies' in state:
        return [find_instance(name) for name in state['current_strategies']]


def set_current_strategies(strategies):
    state = load_state()
    names = [s.name for s in strategies]
    state['current_strategies'] = names
    save_state(state)
    return strategies


def reset_strategies(bt_df):
    '''Find the best 3 strategies in bt_df and save them'''
    results = find_best_strategies(bt_df)
    best3 = [st for st, _ in results[:3]]
    logger.info('reset to {}'.format(best3))
    return set_current_strategies(best3)


def run():
    current_df = bars.get('SPY')
    current_strategies = get_current_strategies()
    if not current_strategies:
        current_strategies = reset_strategies()
    try:
        position = api.get_position('SPY')
    except BaseException:
        position = None
    account = api.get_account()

    for st in current_strategies:
        out_df = st.calc(current_df)
        sig = out_df['signal'].values[-1]
        if position is not None and sig == 1:
            qty = (account.cash * 0.95) // current_df.close.values[-1]
            api.submit_order(
                symbol='SPY',
                qty=qty,
                side='buy',
                type='market',
                time_in_force='day',
            )
            logger.info('buy with {}'.format(st))
            set_current_strategies([st])
            break
        elif position is not None and sig == -1:
            qty = position.qty
            api.submit_order(
                symbol='SPY',
                qty=qty,
                side='sell',
                type='market',
                time_in_force='day',
            )
            logger.info('sell')
            reset_strategies(current_df)
            break


def main():
    logging.info('start running')
    done = None
    while True:
        now = pd.Timestamp.now(tz=NY)
        if 0 <= now.dayofweek <= 4 and done != now.strftime('%Y-%m-%d'):
            if now.time() >= pd.Timestamp('09:30', tz=NY).time():
                run()
                done = now.strftime('%Y-%m-%d')
                logger.info(f'done for {done}')

        time.sleep(1)


if __name__ == '__main__':
    main()
