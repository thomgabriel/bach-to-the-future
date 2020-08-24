import datetime as dt
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
from dash.dependencies import Input, Output, State
from plotly import tools
import pandas as pd
import dateparser
import re
import talib as tb

from bach.strategies.pullback_entry import PullbackEntry
from bach.dashboard.client_dash import clients_dash


app = dash.Dash(title='Bach to the Future',update_title= 'Loading...')

from bach.util.api_ftx import FtxClient
ftx = FtxClient()
market_name = 'BTC-PERP'
resolution = 900 # TimeFrame in seconds.
limit = 10000
start_time = (dt.datetime.fromisoformat('2020-07-05 00:00:00'))
end_time = (dt.datetime.now().timestamp())

ohlcv = pd.DataFrame(data=ftx.get_historical_data(market_name,resolution,limit,start_time.timestamp(),end_time))
ohlcv.columns = ["Close", "High", "Low", "Open","datetime", 'time', "Volume"]
ohlcv.index = ohlcv.datetime.apply(lambda x: dateparser.parse(x[:18]))


# Needed for single main.py file
THREADED_RUN = True
# Make 80 for AWS EC2, default is 5000
PORT = 80
# Make 0.0.0.0 to IP redirect, default is 127.0.0.1
HOST = '0.0.0.0'


# -----------------------------------------------------------------------------------------
# ----------------------Data Load Functions------------------------------------------------
# -----------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------

####### STUDIES TRACES ######

# Moving average
def moving_average_trace7(df, fig):
    df2 = tb.SMA(df.Close,7)
    trace = go.Scatter(
        x=df2.index, y=df2, mode="lines", showlegend=False, name="MA7"
    )
    fig.append_trace(trace, 1, 1)  # plot in first row
    return fig

def moving_average_trace20(df, fig):
    df2 = tb.SMA(df.Close,20)
    trace = go.Scatter(
        x=df2.index, y=df2, mode="lines", showlegend=False, name="MA20"
    )
    fig.append_trace(trace, 1, 1)  # plot in first row
    return fig

def moving_average_trace50(df, fig):
    df2 = tb.SMA(df.Close,50)
    trace = go.Scatter(
        x=df2.index, y=df2, mode="lines", showlegend=False, name="MA50"
    )
    fig.append_trace(trace, 1, 1)  # plot in first row
    return fig

# LINEAR REGRESSION
def linear_regression_trace(df, fig):
    df2 = tb.LINEARREG(tb.SMA(df.Close,50),10)
    trace = go.Scatter(
        x=df2.index, y=df2, mode="lines", showlegend=False, name="LinReg"
    )
    fig.append_trace(trace, 1, 1)  # plot in first row
    return fig


# Bollinger Bands
def bollinger_trace(df, fig, window_size=20, num_of_std=2):
    price = df["Close"]
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

# Pivot points
def pp_trace(df, fig):
    PP = pd.Series((df["High"] + df["Low"] + df["Close"]) / 3)
    R1 = pd.Series(2 * PP - df["Low"])
    S1 = pd.Series(2 * PP - df["High"])
    R2 = pd.Series(PP + df["High"] - df["Low"])
    S2 = pd.Series(PP - df["High"] + df["Low"])
    R3 = pd.Series(df["High"] + 2 * (PP - df["Low"]))
    S3 = pd.Series(df["Low"] - 2 * (df["High"] - PP))
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
        x=df.index, y=df["Close"], mode="lines", showlegend=False, name="line"
    )
    return trace

def area_trace(df):
    trace = go.Scatter(
        x=df.index, y=df["Close"], showlegend=False, fill="toself", name="area"
    )
    return trace

def colored_bar_trace(df):
    return go.Ohlc(
        x=df.index,
        open=df["Open"],
        high=df["High"],
        low=df["Low"],
        close=df["Close"],
        showlegend=False,
        name="colored bar",
    )

def candlestick_trace(df):
    return go.Candlestick(
        x=df.index,
        open=df["Open"],
        high=df["High"],
        low=df["Low"],
        close=df["Close"],
        increasing=dict(line=dict(color="lime")),
        decreasing=dict(line=dict(color="tomato")),
        showlegend=False,
        name="candlestick",
    )

# Returns graph figure
def get_fig(currency_pair, type_trace, studies, period, start_date, end_date):
    # Get OHLC data

    df = (ohlcv[start_date:end_date].resample(period)
               .agg({'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last'}))

    init_date = start_time
    backtest = PullbackEntry()
    backtest.run_backtest(df)
    statistics = backtest.calc_statistics(df)
    fm = statistics['Final Margin']
    pl = statistics['Profit/loss']
    sr = statistics["Stops Reached"]
    pr = statistics['Target Reached']
    pt = statistics['Partial Target Reached']
    wr = statistics['Winrate']
    mp = statistics['Median Position Time']
 
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
    fig["layout"]["margin"] = {"t": 30, "l": 70, "b": 40, "r": 30}
    fig["layout"]["autosize"] = True
    fig["layout"]["height"] = 500
    fig["layout"]['dragmode'] = 'pan'
    fig["layout"]["xaxis"]["rangeslider"]["visible"] = False
    fig["layout"]["xaxis"]["tickformat"] = '%y/%m/%d %H:%M:%S'
    fig["layout"]["xaxis"]['color'] = '#F9F9F9'
    fig["layout"]["xaxis"]['tickfont']['size'] = 13
    fig["layout"]["yaxis"]["showgrid"] = True
    fig["layout"]["yaxis"]["gridcolor"] = "#3E3F40"
    fig["layout"]["yaxis"]["gridwidth"] = 1
    fig["layout"]["yaxis"]['color'] = '#F9F9F9'
    fig["layout"].update(paper_bgcolor="#21252C", plot_bgcolor="#21252C")
    fig["layout"]["yaxis"]['tickfont']['size'] = 15

    fig["layout"]["xaxis"]['tickfont']['family'] = 'Ubuntu'
    fig["layout"]["yaxis"]['tickfont']['family'] = 'Ubuntu' #'Noto Mono'

    return fig, fm, pl, sr, pr, pt, wr, mp, f"{currency_pair} ☰", init_date

# Dash App Layout
app.layout =  clients_dash

# -----------------------------------------------------------------------------------------
# --------------------Dash Callback Functions----------------------------------------------
# -----------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------

# Function to update Graph Figure
def generate_figure_callback(pair):
    def chart_fig_callback(period, type_trace, studies, start_date, end_date): 

        return get_fig(pair, type_trace, studies, period, start_date, end_date)

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
    [
        Output("chart", "figure"),
        Output('final_margin', 'children'),
        Output('profit_loss', 'children'),
        Output('stops_reached', 'children'),
        Output('target_reached', 'children'),
        Output('partial_target', 'children'),
        Output('winrate', 'children'),
        Output('median_time', 'children'),
        Output("menu_button", 'children'),
        Output('my-date-picker-range', 'min_date_allowed'),
        
    ],
    [  
        Input("dropdown_period", "value"),
        Input("chart_type", "value"),
        Input("studies", "value"),
        Input('my-date-picker-range', 'start_date'),
        Input('my-date-picker-range', 'end_date'),
        
    ],
)(generate_figure_callback(pair= market_name))


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
