# pylint: disable=C0103
"""A sample bokeh server applicationb."""
from os.path import dirname, join
from datetime import datetime
from bokeh.layouts import row, column, widgetbox
from bokeh.themes import Theme
from bokeh.models import Div, AutocompleteInput, RadioButtonGroup
from bokeh.plotting import curdoc
from stockprices import StockPrices
from helpers import plot, get_data

def create_plot(doc):
    """Creat a bokeh plot."""
    # create a plot and style its properties
    # doc = curdoc()
    doc.theme = Theme(filename=join(dirname(__file__), 'theme.yaml'))
    doc.title = 'Sample bokeh plot'
    sp = StockPrices()

    plot_width = 600
    plot_height = 600

    # elements
    symbol_selector = AutocompleteInput(
        completions=list(sp.get_symbols()),
        width=150
    )
    period_selector = RadioButtonGroup(
        labels=[
            "Today" if datetime.today().weekday() < 5
            else "Friday",
            "5 days",
            "1 month",
            "6 months",
            "1 year",
            "5 years"
        ],
        active=5,
        width=400
    )
    selected = ['GOOGL', 'AMZN']
    spinner = Div(text='')
    overlay = Div(text='')
    layout = column(
        Div(
            text='<header><h1>Stock Closing Prices</h1></header>',
            width=plot_width
        ),
        row(
            column(widgetbox(
                Div(text='<h3>Period</h3>'),
                period_selector,
                width=400
            )),
            column(widgetbox(
                Div(text='<h3>Symbols</h3>'),
                symbol_selector,
                width=plot_width-400
            ))

        ),
        plot(
            period_selector.active,
            plot_width, plot_height,
            get_data(sp, selected, period_selector.active)
        ),
        spinner,
        overlay,
        width=plot_width+20
    )
    # layout.css_classes = ['wrapper']

    doc.add_root(layout)

    # Set up callbacks
    # symbol selector
    def update_symbol_list(attr, old, new):
        """Update selected symobls."""
        spinner.css_classes = ['loader-spinner']
        overlay.css_classes = ['loader-overlay']

        if symbol_selector.value is None:
            return
        if symbol_selector.value in selected:
            selected.remove(symbol_selector.value)
        else:
            selected.append(symbol_selector.value)
        if selected is None:
            _data = None
        else:
            _data = get_data(sp, selected, period_selector.active)

        layout.children[2] = plot(
            period_selector.active, plot_width, plot_height, _data)

        symbol_selector.value = None
        spinner.css_classes = []
        overlay.css_classes = []

    symbol_selector.on_change('value', update_symbol_list)
    # period selector
    def update_period(attr, old, new):
        """Update selected period."""
        spinner.css_classes = ['loader-spinner']
        overlay.css_classes = ['loader-overlay']

        _data = get_data(sp, selected, period_selector.active)

        layout.children[2] = plot(
            period_selector.active, plot_width, plot_height, _data)

        spinner.css_classes = []
        overlay.css_classes = []

    period_selector.on_change('active', update_period)

create_plot(curdoc())
