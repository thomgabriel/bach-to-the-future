import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import datetime as dt

clients_dash = html.Div(
    className="u-full-width",
    children=[
        
    
        html.Div(
            className="u-full-width",
            children=[
                html.Img(
                    src="assets/rino.png",
                    className='two columns',
                    style= {
                        'height':'10%', 
                        'width':'10%',
                        'padding-top': '0.5rem',
                        'padding-bot' : '-1rem'}
                    
                    ),
                html.Img(
                    src="assets/logo.png",
                    className='two columns',
                    style= {
                        'height':'10%', 
                        'width':'10%',
                        'padding-top': '1.5rem',
                        'padding-bot' : '-1rem',
                        'margin-left': '-2rem',
                        }
                    ),
                html.Div(
                    style= {
                        'padding-top': '5rem',
                        'padding-right': '12rem',
                        'text-align': 'right',
                        'font-size': 18,
                        },
                    children=[
                        dcc.DatePickerRange(
                            id='my-date-picker-range',
                            max_date_allowed=dt.datetime.now(),
                            end_date=dt.datetime.now(),  
                            display_format = 'YYYY/MM/DD',
                            className='ui-datepicker',
                            style= 
                                {
                                'color': '#ffc000',
                                'background':'#ffc000'
                            }
                        ),
                        html.Div(
                            id='output-container-date-picker-range',
                            style={'color':'#ffc000'}
                        )
                    ],
                ),
            ],
        ),

        # Right Panel Div
        html.Div(
            className="u-full-width",
            children=[

                # First info row
            html.Div(
                [
                    html.Div(
                        [
                            html.P(
                                children="Final Margin",
                                className="info_text2",
                            ),
                            html.H6(
                                children="Final Margin",
                                style= {'text-align': 'center'},
                                id="final_margin",
                                className="info_text"
                            )
                        ],
                        id="",
                        className="pretty_container"
                    ),

                    html.Div(
                        [
                            html.P(
                                children="Profit/loss",
                                className="info_text2"
                            ),
                            html.H6(
                                children="Profit/loss",
                                style= {'text-align': 'center'},
                                id="profit_loss",
                                className="info_text"
                            )
                        ],
                        id="",
                        className="pretty_container"
                    ),

                    html.Div(
                        [
                            html.P(
                                children="Stops Reached",
                                className="info_text2"
                                ),
                            html.H6(
                                children="Stops Reached",
                                style= {'text-align': 'center'},
                                id="stops_reached",
                                className="info_text"
                            )
                        ],
                        id="",
                        className="pretty_container"
                    ),

                    html.Div(
                        [
                            html.P(
                                children="Target Reached",
                                className="info_text2"
                            ),
                            html.H6(
                                children="Target Reached",
                                style= {'text-align': 'center'},
                                id="target_reached",
                                className="info_text"
                            )
                        ],
                        id="",
                        className="pretty_container"
                    ),

                    html.Div(
                        [
                            html.P(
                                children="Partial Target Reached",
                                className="info_text2"
                            ),
                            html.H6(
                                children="Partial Target Reached",
                                style= {'text-align': 'center'},
                                id="partial_target",
                                className="info_text"
                            )
                        ],
                        id="",
                        className="pretty_container"
                    ),

                    html.Div(
                        [
                            html.P(
                                children="Winrate",
                                className="info_text2"
                            ),
                            html.H6(
                                children="Winrate",
                                style= {'text-align': 'center'},
                                id="winrate",
                                className="info_text"
                            )
                        ],
                        id="",
                        className="pretty_container"
                    ),
                        html.Div(
                        [
                            html.P(
                                children="Median Position Time",
                                className="info_text2"
                            ),
                            html.H6(
                                children="Median Position Time",
                                style= {'text-align': 'center'},
                                id="median_time",
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
                className="row",
                children=[
                    html.Div(
                        id= "graph_div",
                        className= "chart-style u-full-width",
                        children=[
                            # Menu for Currency Graph
                            html.Div(
                                id="menu",
                                className= "row",
                                style= {'box-shadow': '0px 0.5px 2px 1px lightgrey'},
                                children=[
                                    # stores current menu tab
                                    html.Div(
                                        id="menu_tab",
                                        children=["Studies"],
                                        style={"display": "none",}
                                        ),
                                    html.Span(
                                        "Style",
                                        id="style_header",
                                        className="span-menu",
                                        n_clicks_timestamp=2,
                                        style={
                                            'width': '100%',
                                            'box-shadow': '2px 2px 2px lightgrey',
                                            }
                                        ),
                                    html.Span(
                                        "Studies",
                                        id="studies_header",
                                        className="span-menu",
                                        n_clicks_timestamp=1,
                                        style={
                                            'width': '100%',
                                            'box-shadow': '2px 2px 2px lightgrey',
                                            }
                                        ),
                                    # Studies Checklist
                                    html.Div(
                                        id="studies_tab",
                                        children=[
                                            dcc.Checklist(
                                                id= "studies",
                                                options=[
                                                    {
                                                        "label": "Bollinger bands",
                                                        "value": "bollinger_trace",
                                                    },
                                                    {
                                                        "label": "MA7", 
                                                        "value": "moving_average_trace7"
                                                    },
                                                    {
                                                        "label": "MA20", 
                                                        "value": "moving_average_trace20"
                                                    },
                                                    {
                                                        "label": "MA50", 
                                                        "value": "moving_average_trace50"
                                                    },
                                                    {
                                                        "label": "LinReg", 
                                                        "value": "linear_regression_trace"
                                                    },
                                                    {
                                                        "label": "Pivot points", 
                                                        "value": "pp_trace"
                                                    },
                                                    
                                            
                                                ],
                                                value=[],
                                                className= 'pretty_container',
                                            )
                                        ],
                                        # className= 'pretty_container',
                                        style={"display": "none"},
                                    ),
                                    # Styles checklist
                                    html.Div(
                                        id= "style_tab",
                                        className= 'pretty_container',
                                        children=[
                                            dcc.RadioItems(
                                                id= "chart_type",
                                                options=[
                                                    {
                                                        "label": "Candlestick",
                                                        "value": "candlestick_trace",
                                                    },
                                                    {   "label": "Line",
                                                        "value": "line_trace"
                                                    },
                                                    {   "label": "Mountain", 
                                                        "value": "area_trace"
                                                    },
                                                    {   "label": "Colored Bar",
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
                                className= 'u-full-width chart-top-bar', #"row chart-top-bar",
                                style= {'box-shadow': '0px 0px 2px 1px lightgrey'},
                                children=[
                                    html.Span(
                                        id= "menu_button",
                                        className="inline-block chart-title",
                                        children= "☰",
                                        style= {'font-size': '20px',
                                                'color': '#F9F9F9'},
                                        n_clicks=0,
                                        
                                    ),
                                    # Dropdown and close button float right
                                    html.Div(
                                        className="graph-top-right inline-block",
                                        # style= {'font-size': '17px',
                                        #         'color': '#F9F9F9'},
                                        children=[
                                            html.Div(
                                                className="inline-block",
                                                style= {'font-size': '17px',
                                                        'color': '#F9F9F9'},
                                                children=[
                                                    dcc.Dropdown(
                                                        className="dropdown-period",
                                                        id= "dropdown_period",
                                                        options=[
                                                            {"label": "M15", "value": "15Min"},
                                                            {"label": "M30", "value": "30Min"},
                                                            {"label": "H1", "value": "1H"},
                                                            {"label": "H4", "value": "4H"},
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
                                    className="row u-full-width",
                                    style= {'box-shadow': '0px -0.5px 2px 0px lightgrey'},
                                    config={"scrollZoom": True},
                                    ),
                                ),
                            ],
                        ), 
                    ],
                ),    
            ],
        ),
    ],
)