import datetime as dt
import csv
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.plotly as py
import plotly.graph_objs as go
from dash.dependencies import Input, Output, State
from plotly import tools
import time
import pandas as pd
from threading import Timer
import pathlib
from plotly import tools
import dateparser
import re

from backtest.strategies.pullback_entry import PullbackEntry
from backtest.util.api_ftx import FtxClient

backtest = PullbackEntry()
app = dash.Dash(title='Backtest',update_title= None)

ftx = FtxClient()
market_name = 'BTC-PERP'
resolution = 900 # TimeFrame in seconds.
limit = 10000
start_time = (dt.datetime.fromisoformat('2020-07-05 00:00:00') - dt.timedelta(seconds=resolution*100))
end_time = (dt.datetime.now().timestamp())

ohlcv = pd.DataFrame(data=ftx.get_historical_data(market_name,resolution,limit,start_time.timestamp(),end_time))
ohlcv.columns = ["close", "high", "low", "open","time", 'time_float', "Volume"]
ohlcv.index = ohlcv.time.apply(lambda x: dateparser.parse(x[:18]))
# ohlcv = backtest.get_data()


# Needed for single main.py file
THREADED_RUN = True
# Make 80 for AWS EC2, default is 5000
PORT = 80
# Make 0.0.0.0 to IP redirect, default is 127.0.0.1
HOST = '0.0.0.0'

# # Base layout
# layout = dict(
#     autosize=True,
#     automargin=True,
#     margin=dict(
#         l=30,
#         r=30,
#         b=20,
#         t=40
#     ),
#     hovermode="closest",
#     plot_bgcolor="#F9F9F9",
#     paper_bgcolor="#F9F9F9",
#     legend=dict(font=dict(size=10), orientation='h'),
#     title='Pryno Dashboard',
# )


# -----------------------------------------------------------------------------------------
# ----------------------Data Load Functions------------------------------------------------
# -----------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------

####### STUDIES TRACES ######

# Moving average
def moving_average_trace(df, fig):
    df2 = df.rolling(window=5).mean()
    trace = go.Scatter(
        x=df2.index, y=df2["close"], mode="lines", showlegend=False, name="MA"
    )
    fig.append_trace(trace, 1, 1)  # plot in first row
    return fig

# Exponential moving average
def e_moving_average_trace(df, fig):
    df2 = df.rolling(window=20).mean()
    trace = go.Scatter(
        x=df2.index, y=df2["close"], mode="lines", showlegend=False, name="EMA"
    )
    fig.append_trace(trace, 1, 1)  # plot in first row
    return fig


# Bollinger Bands
def bollinger_trace(df, fig, window_size=10, num_of_std=5):
    price = df["close"]
    rolling_mean = price.rolling(window=window_size).mean()
    rolling_std = price.rolling(window=window_size).std()
    upper_band = rolling_mean + (rolling_std * num_of_std)
    lower_band = rolling_mean - (rolling_std * num_of_std)

    trace = go.Scatter(
        x=df.index, y=upper_band, mode="lines", showlegend=False, name="BB_upper"
    )

    trace2 = go.Scatter(
        x=df.index, y=rolling_mean, mode="lines", showlegend=False, name="BB_mean"
    )

    trace3 = go.Scatter(
        x=df.index, y=lower_band, mode="lines", showlegend=False, name="BB_lower"
    )

    fig.append_trace(trace, 1, 1)  # plot in first row
    fig.append_trace(trace2, 1, 1)  # plot in first row
    fig.append_trace(trace3, 1, 1)  # plot in first row
    return fig


# Accumulation Distribution
def accumulation_trace(df):
    df["volume"] = ((df["close"] - df["low"]) - (df["high"] - df["close"])) / (
        df["high"] - df["low"]
    )
    trace = go.Scatter(
        x=df.index, y=df["volume"], mode="lines", showlegend=False, name="Accumulation"
    )
    return trace


# Commodity Channel Index
def cci_trace(df, ndays=5):
    TP = (df["high"] + df["low"] + df["close"]) / 3
    CCI = pd.Series(
        (TP - TP.rolling(window=10, center=False).mean())
        / (0.015 * TP.rolling(window=10, center=False).std()),
        name="cci",
    )
    trace = go.Scatter(x=df.index, y=CCI, mode="lines", showlegend=False, name="CCI")
    return trace


# Price Rate of Change
def roc_trace(df, ndays=5):
    N = df["close"].diff(ndays)
    D = df["close"].shift(ndays)
    ROC = pd.Series(N / D, name="roc")
    trace = go.Scatter(x=df.index, y=ROC, mode="lines", showlegend=False, name="ROC")
    return trace


# Stochastic oscillator %K
def stoc_trace(df):
    SOk = pd.Series((df["close"] - df["low"]) / (df["high"] - df["low"]), name="SO%k")
    trace = go.Scatter(x=df.index, y=SOk, mode="lines", showlegend=False, name="SO%k")
    return trace


# Momentum
def mom_trace(df, n=5):
    M = pd.Series(df["close"].diff(n), name="Momentum_" + str(n))
    trace = go.Scatter(x=df.index, y=M, mode="lines", showlegend=False, name="MOM")
    return trace


# Pivot points
def pp_trace(df, fig):
    PP = pd.Series((df["high"] + df["low"] + df["close"]) / 3)
    R1 = pd.Series(2 * PP - df["low"])
    S1 = pd.Series(2 * PP - df["high"])
    R2 = pd.Series(PP + df["high"] - df["low"])
    S2 = pd.Series(PP - df["high"] + df["low"])
    R3 = pd.Series(df["high"] + 2 * (PP - df["low"]))
    S3 = pd.Series(df["low"] - 2 * (df["high"] - PP))
    trace = go.Scatter(x=df.index, y=PP, mode="lines", showlegend=False, name="PP")
    trace1 = go.Scatter(x=df.index, y=R1, mode="lines", showlegend=False, name="R1")
    trace2 = go.Scatter(x=df.index, y=S1, mode="lines", showlegend=False, name="S1")
    trace3 = go.Scatter(x=df.index, y=R2, mode="lines", showlegend=False, name="R2")
    trace4 = go.Scatter(x=df.index, y=S2, mode="lines", showlegend=False, name="S2")
    trace5 = go.Scatter(x=df.index, y=R3, mode="lines", showlegend=False, name="R3")
    trace6 = go.Scatter(x=df.index, y=S3, mode="lines", showlegend=False, name="S3")
    fig.append_trace(trace, 1, 1)
    fig.append_trace(trace1, 1, 1)
    fig.append_trace(trace2, 1, 1)
    fig.append_trace(trace3, 1, 1)
    fig.append_trace(trace4, 1, 1)
    fig.append_trace(trace5, 1, 1)
    fig.append_trace(trace6, 1, 1)
    return fig


# MAIN CHART TRACES (STYLE tab)
def line_trace(df):
    trace = go.Scatter(
        x=df.index, y=df["close"], mode="lines", showlegend=False, name="line"
    )
    return trace


def area_trace(df):
    trace = go.Scatter(
        x=df.index, y=df["close"], showlegend=False, fill="toself", name="area"
    )
    return trace


def colored_bar_trace(df):
    return go.Ohlc(
        x=df.index,
        open=df["open"],
        high=df["high"],
        low=df["low"],
        close=df["close"],
        showlegend=False,
        name="colored bar",
    )


def candlestick_trace(df):
    return go.Candlestick(
        x=df.index,
        open=df["open"],
        high=df["high"],
        low=df["low"],
        close=df["close"],
        increasing=dict(line=dict(color="lime")),
        decreasing=dict(line=dict(color="tomato")),
        showlegend=False,
        name="candlestick",
    )


# Returns graph figure
def get_fig(currency_pair, type_trace, studies, period):
    # Get OHLC data

    df = (ohlcv.resample(period)
               .agg({'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last'}))

    subplot_traces = [  # first row traces
        "accumulation_trace",
        "cci_trace",
        "roc_trace",
        "stoc_trace",
        "mom_trace",
    ]
    selected_subplots_studies = []
    selected_first_row_studies = []
    row = 1  # number of subplots

    if studies:
        for study in studies:
            if study in subplot_traces:
                row += 1  # increment number of rows only if the study needs a subplot
                selected_subplots_studies.append(study)
            else:
                selected_first_row_studies.append(study)

    fig = tools.make_subplots(
        rows=row,
        shared_xaxes=True,
        shared_yaxes=True,
        cols=1,
        print_grid=False,
        vertical_spacing=0.12,
    )

    # Add main trace (style) to figure
    fig.append_trace(eval(type_trace)(df), 1, 1)

    # Add trace(s) on fig's first row
    for study in selected_first_row_studies:
        fig = eval(study)(df, fig)

    row = 1
    # Plot trace on new row
    for study in selected_subplots_studies:
        row += 1
        fig.append_trace(eval(study)(df), row, 1)

    fig["layout"][
        "uirevision"
    ] = "The User is always right"  # Ensures zoom on graph is the same on update
    fig["layout"]["margin"] = {"t": 50, "l": 50, "b": 50, "r": 25}
    fig["layout"]["autosize"] = True
    fig["layout"]["height"] = 400
    fig["layout"]['dragmode'] = 'pan'
    fig["layout"]["xaxis"]["rangeslider"]["visible"] = False
    fig["layout"]["xaxis"]["tickformat"] = '%y/%m/%d %H:%M:%S'
    fig["layout"]["xaxis"]['color'] = '#F9F9F9'
    fig["layout"]["yaxis"]["showgrid"] = True
    fig["layout"]["yaxis"]["gridcolor"] = "#3E3F40"
    fig["layout"]["yaxis"]["gridwidth"] = 1
    fig["layout"]["yaxis"]['color'] = '#F9F9F9'
    fig["layout"].update(paper_bgcolor="#21252C", plot_bgcolor="#21252C")

    return fig

# returns chart div
def chart_div():
    return html.Div(
        id= "graph_div",
        className="chart-style u-full-width",
        children=[
            # Menu for Currency Graph
            html.Div(
                id="menu",
                className="u-full-width",
                children=[
                    # stores current menu tab
                    html.Div(
                        id="menu_tab",
                        children=["Studies"],
                        style={"display": "none"},
                    ),
                    html.Span(
                        "Style",
                        id="style_header",
                        className="span-menu",
                        n_clicks_timestamp=2,
                    ),
                    html.Span(
                        "Studies",
                        id="studies_header",
                        className="span-menu",
                        n_clicks_timestamp=1,
                    ),
                    # Studies Checklist
                    html.Div(
                        id="studies_tab",
                        children=[
                            dcc.Checklist(
                                id= "studies",
                                options=[
                                    {
                                        "label": "Accumulation/D",
                                        "value": "accumulation_trace",
                                    },
                                    {
                                        "label": "Bollinger bands",
                                        "value": "bollinger_trace",
                                    },
                                    {"label": "MA", "value": "moving_average_trace"},
                                    {"label": "EMA", "value": "e_moving_average_trace"},
                                    {"label": "CCI", "value": "cci_trace"},
                                    {"label": "ROC", "value": "roc_trace"},
                                    {"label": "Pivot points", "value": "pp_trace"},
                                    {
                                        "label": "Stochastic oscillator",
                                        "value": "stoc_trace",
                                    },
                                    {
                                        "label": "Momentum indicator",
                                        "value": "mom_trace",
                                    },
                                ],
                                value=[],
                            )
                        ],
                        className= 'pretty_container',
                        style={"display": "none"},
                    ),
                    # Styles checklist
                    html.Div(
                        id= "style_tab",
                        children=[
                            dcc.RadioItems(
                                id= "chart_type",
                                options=[
                                    {
                                        "label": "candlestick",
                                        "value": "candlestick_trace",
                                    },
                                    {   "label": "line",
                                        "value": "line_trace"
                                    },
                                    {   "label": "mountain", 
                                        "value": "area_trace"
                                    },
                                    {   "label": "colored bar",
                                        "value": "colored_bar_trace",
                                    },
                                ],
                                value="candlestick_trace",
                                className= 'pretty_container',
                            )
                        ],
                    ),
                ],
            ),
            # Chart Top Bar
            html.Div(
                className="row chart-top-bar",
                children=[
                    html.Span(
                        id= "menu_button",
                        className="inline-block chart-title",
                        children=f"{market_name} ☰",
                        n_clicks=0,
                    ),
                    # Dropdown and close button float right
                    html.Div(
                        className="graph-top-right inline-block",
                        children=[
                            html.Div(
                                className="inline-block",
                                children=[
                                    dcc.Dropdown(
                                        className="dropdown-period",
                                        id= "dropdown_period",
                                        options=[
                                            {"label": "M15", "value": "15Min"},
                                            {"label": "M30", "value": "30Min"},
                                            {"label": "H1", "value": "1H"},
                                            {"label": "H4", "value": "4H"},
                                            {"label": "D1", "value": "1D"},
                                        ],
                                        value="15Min",
                                        clearable=False,
                                    )
                                ],
                            ),
                        ],
                    ),
                ],
            ),
            # Graph div
            html.Div(
                dcc.Graph(
                    id= "chart",
                    className="chart-graph",
                    config={"displayModeBar": False, "scrollZoom": True},
                    
                )
            ),
        ],
    )

# Dash App Layout
app.layout =  html.Div(
    className="u-full-width",
    children=[
        
        # Interval component for graph updates
        dcc.Interval(id="i_tris", interval=1 * 5000, n_intervals=0),

        html.Img(
            src="assets/logo-light.png",
            className='two columns',
            style={'align': 'left'}
            ),

        # Right Panel Div
        html.Div(
            className="div-right-panel u-full-width",
            children=[

                # First info row
            html.Div(
                [
                    html.Div(
                        [
                            html.P(
                                children="Profit",
                                className="info_text2",
                            ),
                            html.H6(
                                children="Profit",
                                style= {'text-align': 'center'},
                                id="profit",
                                className="info_text"
                            )
                        ],
                        id="",
                        className="pretty_container"
                    ),

                    html.Div(
                        [
                            html.P(
                                children="Order Num",
                                className="info_text2"
                            ),
                            html.H6(
                                children="Order Num",
                                style= {'text-align': 'center'},
                                id="order_num",
                                className="info_text"
                            )
                        ],
                        id="",
                        className="pretty_container"
                    ),

                    html.Div(
                        [
                            html.P(
                                children="Position",
                                className="info_text2"
                                ),
                            html.H6(
                                children="Position",
                                style= {'text-align': 'center'},
                                id="position",
                                className="info_text"
                            )
                        ],
                        id="",
                        className="pretty_container"
                    ),

                    html.Div(
                        [
                            html.P(
                                children="Stop",
                                className="info_text2"
                            ),
                            html.H6(
                                children="Stop",
                                style= {'text-align': 'center'},
                                id="stop",
                                className="info_text"
                            )
                        ],
                        id="",
                        className="pretty_container"
                    ),

                    html.Div(
                        [
                            html.P(
                                children="Liquidation",
                                className="info_text2"
                            ),
                            html.H6(
                                children="Liquidation",
                                style= {'text-align': 'center'},
                                id="liquidation",
                                className="info_text"
                            )
                        ],
                        id="",
                        className="pretty_container"
                    ),

                    html.Div(
                        [
                            html.P(
                                children="Break Even",
                                className="info_text2"
                            ),
                            html.H6(
                                children="Break Even",
                                style= {'text-align': 'center'},
                                id="beven",
                                className="info_text"
                            )
                        ],
                        id="",
                        className="pretty_container"
                    ),
                        html.Div(
                        [
                            html.P(
                                children="Price",
                                className="info_text2"
                            ),
                            html.H6(
                                children="Price",
                                style= {'text-align': 'center'},
                                id="price",
                                className="info_text"
                            )
                        ],
                        id="",
                        className="pretty_container"
                    ),

                ],
                id="info",
                className="row2"
            ),

                # Charts Div
                html.Div(
                    id="charts",
                    className="u-full-width",
                    children=[chart_div()],
                ),
                html.Div([
                    dcc.DatePickerRange(
                        id='my-date-picker-range',
                        min_date_allowed=start_time,
                        max_date_allowed=dt.datetime.now() + dt.timedelta(days=1),
                        # initial_visible_month=dt.datetime.now() - dt.timedelta(days=1),
                        end_date=dt.datetime.now().date()
                    ),
                html.Div(id='output-container-date-picker-range')
                    ]   
                )
            ],

        ),
        
    ],
)

# -----------------------------------------------------------------------------------------
# --------------------Dash Callback Functions----------------------------------------------
# -----------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------

# Function to update Graph Figure
def generate_figure_callback(pair):
    def chart_fig_callback(i_tris, period, type_trace, studies):

        return get_fig(pair, type_trace, studies, period)

    return chart_fig_callback

def update_date_button():
    def update_output(start_date, end_date):
        string_prefix = 'You have selected: '
        if start_date is not None:
            start_date = dt.datetime.strptime(re.split('T| ', start_date)[0], '%Y-%m-%d')
            start_date_string = start_date.strftime('%B %d, %Y')
            string_prefix = string_prefix + 'Start Date: ' + start_date_string + ' | '
        if end_date is not None:
            end_date = dt.datetime.strptime(re.split('T| ', end_date)[0], '%Y-%m-%d')
            end_date_string = end_date.strftime('%B %d, %Y')
            string_prefix = string_prefix + 'End Date: ' + end_date_string
        if len(string_prefix) == len('You have selected: '):
            return 'Select a date to see it displayed here'
        else:
            return string_prefix
    return update_output

app.callback(
    Output('output-container-date-picker-range', 'children'),
    [Input('my-date-picker-range', 'start_date'),
     Input('my-date-picker-range', 'end_date')]
)(update_date_button())


# Function to open or close STYLE or STUDIES menu
def generate_open_close_menu_callback():
    def open_close_menu(n, className):
        if n == 0:
            return "not_visible"
        if className == "visible":
            return "not_visible"
        else:
            return "visible"

    return open_close_menu


# Function for hidden div that stores the last clicked menu tab
# Also updates style and studies menu headers
def generate_active_menu_tab_callback():
    def update_current_tab_name(n_style, n_studies):
        if n_style >= n_studies:
            return "Style", "span-menu selected", "span-menu"
        return "Studies", "span-menu", "span-menu selected"

    return update_current_tab_name


# Function show or hide studies menu for chart
def generate_studies_content_tab_callback():
    def studies_tab(current_tab):
        if current_tab == "Studies":
            return {"display": "block", "textAlign": "left", "marginTop": "30"}
        return {"display": "none"}

    return studies_tab


# Function show or hide style menu for chart
def generate_style_content_tab_callback():
    def style_tab(current_tab):
        if current_tab == "Style":
            return {"display": "block", "textAlign": "left", "marginTop": "30"}
        return {"display": "none"}

    return style_tab

# Callback to update the actual graph
app.callback(
    Output("chart", "figure"),
    [
        Input("i_tris", "n_intervals"),
        Input("dropdown_period", "value"),
        Input("chart_type", "value"),
        Input("studies", "value"),
    ],
)(generate_figure_callback(market_name))


# show or hide graph menu
app.callback(
    Output("menu", "className"),
    [Input("menu_button", "n_clicks")],
    [State("menu", "className")],
)(generate_open_close_menu_callback())


# stores in hidden div name of clicked tab name
app.callback(
    [
        Output("menu_tab", "children"),
        Output("style_header", "className"),
        Output("studies_header", "className"),
    ],
    [
        Input("style_header", "n_clicks_timestamp"),
        Input("studies_header", "n_clicks_timestamp"),
    ],
)(generate_active_menu_tab_callback())


# # hide/show STYLE tab content if clicked or not
app.callback(
    Output("style_tab", "style"), [Input("menu_tab", "children")]
)(generate_style_content_tab_callback())


# hide/show MENU tab content if clicked or not
app.callback(
    Output("studies_tab", "style"), [Input("menu_tab", "children")]
)(generate_studies_content_tab_callback())


def run_server():
    print("Dashboard app server started running.")
    app.server.run(host=HOST, port=PORT, debug=True, threaded=THREADED_RUN)


if __name__ == "__main__":
    run_server()
