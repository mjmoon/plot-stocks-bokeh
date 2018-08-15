# pylint: disable=E1101
"""This module provides a class for getting stock prices."""
import re
from os.path import dirname, join
from datetime import date
from dateutil.relativedelta import relativedelta
import yaml
import pandas as pd
pd.core.common.is_list_like = pd.api.types.is_list_like
from alpha_vantage.timeseries import TimeSeries
from pandas_datareader import data as web

class StockPrices(object):
    """Get up-to-date stock price data."""

    def __init__(self):
        self._datareader = web
        with open(join(dirname(__file__), '_access.yml'), 'r') as config:
            api_key = yaml.load(config)['AV_API_KEY']
        self._alphavantage = TimeSeries(
            api_key, output_format='pandas')
        self._iex_symbols = self._datareader.get_iex_symbols()
        self._history = None
        self._recent = None

    def get_symbols(self):
        """Get available symbols from IEX."""
        return self._iex_symbols['symbol']

    def get_metadata(self, symbols):
        """Get metadat from IEX."""
        if isinstance(symbols, str):
            symbols = [symbols]
        return self._iex_symbols[self._iex_symbols['symbol'].isin(symbols)]

    def get_history(self, symbols):
        """Return 5 years of data."""
        start = date.today() - relativedelta(years=5)
        end = date.today()
        if isinstance(symbols, str):
            symbols = [symbols]
        if self._history is not None:
            new_symbols =\
                set(symbols) - set(self._history.index.levels[0])
            if new_symbols:
                self._history =\
                    pd.concat([
                        self._history,
                        self._retreive_history(new_symbols, start, end)
                    ])
        else:
            self._history = self._retreive_history(symbols, start, end)
        return self._history

    def get_recent(self, symbols):
        """Return 15 min interval data."""
        if isinstance(symbols, str):
            symbols = [symbols]
        if self._recent is not None:
            new_symbols =\
                set(symbols) - set(self._recent.index.levels[0])
            if new_symbols:
                self._recent =\
                    pd.concat([
                        self._recent,
                        self._retreive_recent(new_symbols)
                        ])
        else:
            self._recent = self._retreive_recent(symbols)
        return self._recent

    def _retreive_history(
            self, symbols, start_date, end_date):
        """Retrieve daily stock prices."""
        data_list = []
        try:
            for sym in symbols:
                datum = self._datareader.DataReader(
                    sym, 'iex', start_date, end_date
                )
                datum['symbol'] = sym
                data_list.append(datum)
            data = pd.concat(data_list)
            data.rename(columns=lambda x: x.lower(), inplace=True)
            data.index = pd.to_datetime(data.index)
            return data.reset_index().set_index(['symbol', 'date'])
        except:
            print("Error retreiving data for " + sym)
            return pd.DataFrame()

    def _retreive_recent(
            self, symbols, interval=1, output_size='full'):
        """Retrieve intra-day stock prices using Alpha Vantage API."""
        data_list = []
        try:
            for sym in symbols:
                datum = self._alphavantage.get_intraday(
                    sym,
                    str(interval)+'min',
                    output_size)[0]
                datum['symbol'] = sym
                data_list.append(datum)
            data = pd.concat(data_list)
            data.rename(
                columns=lambda x: re.sub(r'[^a-zA-Z_]', '', x),
                inplace=True)

            data.index = pd.to_datetime(data.index)
            return data.reset_index().set_index(['symbol', 'date'])
        except:
            print("Error retreiving data for " + sym)
            return pd.DataFrame()
