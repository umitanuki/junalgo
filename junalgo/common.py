import alpaca_trade_api as tradeapi
import logging

NY = 'America/New_York'
api = tradeapi.REST()


def _dry_run_submit(*args, **kwargs):
    logging.info(f'submit({args}, {kwargs})')


def set_dry_run():
    api.submit_order = _dry_run_submit
