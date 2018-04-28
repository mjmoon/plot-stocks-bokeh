# pylint: disable=C0103, C0413, E0611, E0401
"""A sample bokeh server applicationb."""
from os import getcwd, chdir
from os.path import join
if '/app/app' not in getcwd():
    chdir(join(getcwd(), 'app'))
from bokeh.themes import Theme
from bokeh.embed import components
from bokeh.plotting import curdoc
from stockprices import StockPrices
from helpers import plot, get_data
from bokeh.io import output_notebook
from bokeh.io import show

PLOT_WIDTH = 600
PLOT_HEIGHT = 600
SELECTED = ['FB', 'AAPL', 'MSFT']

def create_plot(doc):
    """Create a static plot."""
    doc.clear()
    # doc.theme = Theme(filename=join(getcwd(), 'theme.yaml'))
    sp = StockPrices()

    figure = plot(
        5,
        PLOT_WIDTH, PLOT_HEIGHT,
        get_data(sp, SELECTED, 5)
    )

    doc.add_root(figure)

create_plot(curdoc())
script, div = components(curdoc())

with open('bokeh-script.html', 'w') as f:
    f.write(script)

with open('bokeh-div.html', 'w') as f:
    f.write(div)
