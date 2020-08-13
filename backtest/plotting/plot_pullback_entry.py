import pandas as pd
import statistics

from bokeh.io import output_file, show
from bokeh.plotting import figure
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, HoverTool
from bokeh.models.widgets import DataTable, DateFormatter, TableColumn

from bokeh.colors.named import (
    lime as BULL_COLOR,
    tomato as BEAR_COLOR)
from bokeh.transform import factor_cmap

def plot(data,statistics):

    ohlcv = data['ohlcv']
    stops_reached = data['stops_reached']
    targets_reached = data['targets_reached']
    partial_reached = data['partial_reached']
    long_signals = data['long_signals']
    short_signals = data['short_signals']
    all_exec = data['all_exec']
    margin_returns = data['margin_returns']
    statistics = statistics


    w = 10*60*1000 # candle size in ms
    bull = ColumnDataSource(ohlcv[ohlcv.Close > ohlcv.Open])
    bear = ColumnDataSource(ohlcv[ohlcv.Open > ohlcv.Close])

    TOOLS = "pan,wheel_zoom,box_zoom,reset,save,crosshair"
    p = figure(x_axis_type="datetime", tools=[TOOLS], plot_width=1800, plot_height=700,active_drag='pan', active_scroll='wheel_zoom')

    p.add_tools(HoverTool(
        names=["hover"],
        tooltips=[
            ("Date", "@datetime{%Y-%m-%d %H:%M:%S}"),
            ("Open", "$@Open{0,0.0}"),
            ("High", "$@High{0,0.0}"),
            ("Low", "$@Low{0,0.0}"),
            ("Close", "$@Close{0,0.0}"),
        ],
        formatters={
            '@datetime' : 'datetime',                       
            }
        ))

    p.segment('datetime', 'High', 'datetime', 'Low', source=bull, color="black")
    p.segment('datetime', 'High', 'datetime', 'Low', source=bear, color="black")

    p.vbar('datetime', w, 'Open', 'Close', source=bull, fill_color=BULL_COLOR, line_color="black", name='hover')
    p.vbar('datetime', w, 'Open', 'Close', source=bear, fill_color=BEAR_COLOR, line_color="black", name='hover')

    p.circle([x[0] for x in stops_reached], [x[2] for x in stops_reached], legend_label="Stop Loss Reached", fill_color="coral", size=8, muted_alpha=0.2)
    p.circle([x[0] for x in targets_reached], [x[2] for x in targets_reached], legend_label="Profit Target Reached", fill_color="lime", size=8, muted_alpha=0.2)
    p.hex([x[0] for x in partial_reached], [x[2] for x in partial_reached], legend_label="Partial 2 Target Reached", fill_color="pink", size=10, muted_alpha=0.2)
    # p.hex([x[0] for x in partial2_reached], [x[2] for x in partial2_reached], legend_label="Partial Target Reached", fill_color="yellow", size=10, muted_alpha=0.2)

    p.triangle([x[0] for x in long_signals], [x[1] for x in long_signals], legend_label="Long Signal", fill_color="green", size=12, muted_alpha=0.2)
    p.inverted_triangle([x[0] for x in short_signals], [x[1] for x in short_signals], legend_label="Short Signal", fill_color="red", size=12, muted_alpha=0.2)

    p.legend.location = "top_left"
    p.legend.click_policy="mute"

    result = pd.DataFrame(data=all_exec,columns = ["datetime", 'Price', 'Type'])
    Columns = [TableColumn(field="datetime", title='Date', formatter=DateFormatter(format='%Y-%m-%d %H:%M:%S')),
                TableColumn(field="Price", title='Price'),
                TableColumn(field="Type", title='Type'),    
                ] # bokeh columns
    data_table = DataTable(columns=Columns, source=ColumnDataSource(result), width=1100, height=300, background='red',index_width= 0) # bokeh table

    stats = pd.DataFrame(data = [(x,y) for x,y in zip([x for x in statistics],[statistics[x] for x in statistics])], columns = ['parameters','values'])
    Columns = [TableColumn(field='parameters', title='Parameters'),
                TableColumn(field='values', title='Values')
                ] # bokeh columns
    data_table2 = DataTable(columns=Columns, source=ColumnDataSource(stats), width=700,height=300, index_width= 0) # bokeh table

    m = figure(x_axis_type="datetime", tools=[TOOLS], plot_width=1800, plot_height=400, active_scroll='wheel_zoom')
    m.line('datetime','data', source =margin_returns, line_width=2, line_color="black",legend_label="Margin Returns")
    m.hex('datetime','data', source =margin_returns, fill_color="black", size=15, muted_alpha=0.2, name='hover', legend_label="Executions")
    m.legend.location = "top_left"
    m.add_tools(HoverTool(
        names=["hover"],
        tooltips=[
            ("Date: ", "@datetime{%Y-%m-%d %H:%M:%S}"),
            ("Change: ", "@pct{0.00}%"),
            ("Type: ", "@type"),
        ],
        formatters={
            '@datetime' : 'datetime',                       
            }
        ))

    return show(column([p,row(data_table2,data_table),m]))
