"""Helper functions."""
from datetime import datetime
from dateutil.relativedelta import relativedelta
import numpy as np
from bokeh.models import HoverTool
from bokeh.plotting import figure
# from bokeh.palettes import Colorblind
from bokeh.palettes import Dark2

"""
plotting helpers
"""
def plot(period, width=800, height=600, data=None):
    """Return a plot figure."""
    plt = figure(
        x_axis_type='datetime',
        output_backend='webgl',
        tools=['box_zoom'],
        plot_width=width,
        plot_height=height
    )
    plt.toolbar_location = None

    _day_of_week = datetime.today().weekday()

    _start = (datetime.today() - relativedelta(
        hours=9, days=max(_day_of_week - 4, 0))
             ).replace(
                 hour=8, minute=30, second=0, microsecond=0
             ) - _get_periods()[int(period)]

    data = data[data.index.get_level_values(1) > _start]

    if data is not None:
        # remove missing period if period is < 1 year
        if period == 0:
            for ind, (sym, dat) in enumerate(data.groupby(level=0)):
                # map dataframe indices to date strings and use as label overrides
                plt.xaxis.major_label_overrides = {
                    i: date.strftime('%H:%M')
                    for i, date
                    in enumerate(dat.index.get_level_values(1))
                }
                _add_line(ind, sym, dat, plt, period)
        elif period < 4:
            for ind, (sym, dat) in enumerate(data.groupby(level=0)):
                # map dataframe indices to date strings and use as label overrides
                plt.xaxis.major_label_overrides = {
                    i: date.strftime('%b %d')
                    for i, date
                    in enumerate(dat.index.get_level_values(1))
                }
                _add_line(ind, sym, dat, plt, period)
        else:
            for ind, (sym, dat) in enumerate(data.groupby(level=0)):
                _add_line(ind, sym, dat, plt, period)
    return plt

def get_data(sp, selected, period):
    """Get data based on period and symbols."""
    if period > 1:
        return sp.get_history(selected).loc[selected]
    else:
        return sp.get_recent(selected).loc[selected]

def _to_date(date_time):
    return date_time.strftime('%b %d, %Y')
def _to_date_time(date_time):
    return date_time.strftime('%b %d %H:%M')
def _to_time(date_time):
    return date_time.strftime('%H:%M')

def _add_line(ind, sym, dat, plt, period):
    xlab = 'Time' if period == 0 else 'Date'
    if period < 4:
        line = plt.line(
            x=dat.reset_index().index,
            y=dat['close'],
            legend=sym,
            name=sym,
            line_color=Dark2[8][np.mod((ind), 8)]
        )
    else:
        line = plt.line(
            x=dat.index.get_level_values(1),
            y=dat['close'],
            legend=sym,
            name=sym,
            line_color=Dark2[8][np.mod((ind), 8)]
        )
    if period == 0:
        line.data_source.data['date_str'] =\
            dat.index.get_level_values(1).map(_to_time)
    elif period == 1:
        line.data_source.data['date_str'] =\
            dat.index.get_level_values(1).map(_to_date_time)
    else:
        line.data_source.data['date_str'] =\
            dat.index.get_level_values(1).map(_to_date)

    plt.add_tools(HoverTool(renderers=[line], tooltips=[
        ('Ticker', sym),
        (xlab, "@date_str"),
        ('Value', "@y{($ 0.00)}")
    ]))

def _get_periods():
    """Return a list of relativedelta objects."""
    return [
        relativedelta(),
        relativedelta(days=6),
        relativedelta(months=1, days=1),
        relativedelta(months=6, days=1),
        relativedelta(years=1),
        relativedelta(years=5)
        ]
