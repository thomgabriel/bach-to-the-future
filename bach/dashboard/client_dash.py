import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import datetime as dt
import bach.util.settings as SETTINGS

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
                                'background':'#ffc000',
                                'font-family' : 'Ubuntu',
                            }
                        ),
                        html.Div(
                            id='output-container-date-picker-range',
                            style={
                                'color':'#ffc000',
                                'font-family' : 'Ubuntu',
                            }
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
                                children="Stop Losses",
                                className="info_text2"
                                ),
                            html.H6(
                                children="Stop Losses",
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
                                children="Profit Targets",
                                className="info_text2"
                            ),
                            html.H6(
                                children="Profit Targets",
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
                                children="Partial Target",
                                className="info_text2"
                            ),
                            html.H6(
                                children="Partial Target",
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
                                className= "not_visible",
                                style= {'box-shadow': '0px 0.5px 2px 1px lightgrey',
                                        'margin-left' : '10px',
                                        'margin-top' : '1px',
                                        'width': 'auto',
                                        'height': 'auto',
                                    },
                                children=[
                                    # stores current menu tab
                                    html.Div(
                                        id="menu_tab",
                                        children=["Studies"],
                                        style={"display": "none",}
                                        ),

                                    html.Div(
                                        style= {'box-shadow': '0px 0px 2px 1px lightgrey',
                                                'background-color': '#21252C',
                                                'padding':'12px'
                                            },
                                        children=[
                                            html.Div(
                                                style= {
                                                    'display': 'flex'
                                                    },
                                                children=[
                                                    html.Div(
                                                        className="pretty_container_buttons",
                                                        children=[
                                                            html.Span(
                                                                children="Style",
                                                                id="style_header",
                                                                className="inline-block chart-title",
                                                                n_clicks_timestamp=2,
                                                                style= {'font-size': '15px',
                                                                        'color': '#F9F9F9',
                                                                        'font-family' : 'Ubuntu',
                                                                    },
                                                                )
                                                            ]
                                                        ),
                                                    html.Div(
                                                        className="pretty_container_buttons",
                                                        children=[
                                                            html.Span(
                                                                children="Studies",
                                                                id="studies_header",
                                                                className="inline-block chart-title",
                                                                n_clicks_timestamp=1,
                                                                style= {'font-size': '15px',
                                                                        'color': '#F9F9F9',
                                                                        'font-family' : 'Ubuntu',
                                                                    },
                                                                ),
                                                            ]
                                                        ),
                                                    ]
                                                ),
                                            ],
                                        ),


                                    # Studies Checklist
                                    html.Div(
                                        id="studies_tab",
                                        children=[
                                            dcc.Checklist(
                                                id= "studies",
                                                options=[
                                                    {
                                                        "label": " Bollinger bands",
                                                        "value": "bollinger_trace",
                                                    },
                                                    {
                                                        "label": " MA7", 
                                                        "value": "moving_average_trace7"
                                                    },
                                                    {
                                                        "label": " MA20", 
                                                        "value": "moving_average_trace20"
                                                    },
                                                    {
                                                        "label": " MA50", 
                                                        "value": "moving_average_trace50"
                                                    },
                                                    {
                                                        "label": " LinReg", 
                                                        "value": "linear_regression_trace"
                                                    },
                                                    {
                                                        "label": " Pivot points", 
                                                        "value": "pp_trace"
                                                    },
                                                    
                                            
                                                ],
                                                value=[],
                                                labelStyle={
                                                    'font-size': '18px',
                                                    'font-family' : 'Ubuntu',
                                                },
                                            )
                                        ],
                                        className= 'pretty_container_checklist',
                                        style={"display": "none"},
                                    ),
                                    # Styles checklist
                                    html.Div(
                                        id= "style_tab",
                                        className= 'pretty_container_checklist',
                                        children=[
                                            dcc.RadioItems(
                                                id= "chart_type",
                                                options=[
                                                    {
                                                        "label": " Candlestick",
                                                        "value": "candlestick_trace",
                                                    },
                                                    {   "label": " Line",
                                                        "value": "line_trace"
                                                    },
                                                    {   "label": " Mountain", 
                                                        "value": "area_trace"
                                                    },
                                                    {   "label": " Colored Bar",
                                                        "value": "colored_bar_trace",
                                                    },
                                                ],
                                                value="candlestick_trace",
                                                labelStyle={
                                                    'font-size': '18px',
                                                    'font-family' : 'Ubuntu',
                                                },
                                                
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
                                        style= {
                                            'font-size': '20px',
                                            # 'color': '#F9F9F9',
                                            'color': '#ffc000',
                                            'font-family' : 'Ubuntu',
                                            },
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
                                                        ],
                                                        value="15Min",
                                                        clearable=False,
                                                        style={
                                                            'font-size': '18px',
                                                            'font-family' : 'Ubuntu',
                                                            'color': '#F9F9F9',
                                                        }
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

                            # Footer
                            html.Div(
                                className="u-full-width",
                                # style = {'display' : 'flex'},
                                children=[
                                    html.P(
                                        children = 'Bach to the Future Dashboard  v{0} - © Quan Digital 2020'.format(SETTINGS.VERSION),
                                        className = 'footer1',
                                        ),
                                    html.P(
                                        children ='Designed by thomgabriel',
                                        className = 'footer1',
                                        ),
                                    ], 
                                ),
                            ],
                        ), 
                    ],
                ),    
            ],
        ),
    ],
)