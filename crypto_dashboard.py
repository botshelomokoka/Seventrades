import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd
import json
import datetime

from seven_bot import get_total_portfolio_value_usdt, quarterly_data, coins_to_trade, exchange, rebalance_portfolio, start_trading, stop_trading  # Import necessary functions and data from your bot


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Helper function to generate report table data
def generate_report_data(period):
    filename = f"{period}_report.csv"
    try:
        df = pd.read_csv(filename)
        return df.to_dict('records')
    except FileNotFoundError:
        return []


# Define app layout
app.layout = html.Div(
    [
        html.H1("Crypto Trading Bot Dashboard", style={"textAlign": "center"}),
        dcc.Interval(id='interval-component', interval=60*1000, n_intervals=0),

        # Portfolio Overview
        html.H2("Portfolio Overview", style={"textAlign": "center"}),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H3("Portfolio Value (USDT)", style={"textAlign": "center"}),
                        html.Div(id="portfolio-value", style={"textAlign": "center", 'fontSize': 24}),
                        dcc.Graph(id="portfolio-pie-chart"),
                    ],
                    width=6,
                ),
                dbc.Col(
                    [
                        html.H3("Active Coins", style={"textAlign": "center"}),
                        html.Ul(id="active-coins-list"),
                    ],
                    width=6,
                ),
            ]
        ),

        # Performance Reports
        html.H2("Performance Reports", style={"textAlign": "center"}),
        dbc.Tabs(
            [
                dbc.Tab(label="Monthly", children=[
                    dash_table.DataTable(
                        id="monthly-report-table",
                        columns=[{"name": i, "id": i} for i in ["Date", "Start Value", "End Value", "Change (%)"]],
                        data=[]  # Will be populated by callback
                    ),
                ]),
                dbc.Tab(label="Quarterly", children=[
                    dash_table.DataTable(
                        id="quarterly-report-table",
                        columns=[{"name": i, "id": i} for i in ["Quarter", "Start Value", "End Value", "Change (%)"]],
                        data=[]  # Will be populated by callback
                    ),
                ]),
                dbc.Tab(label="Half-Yearly", children=[
                    dash_table.DataTable(
                        id="half-yearly-report-table",
                        columns=[{"name": i, "id": i} for i in ["Half-Year", "Start Value", "End Value", "Change (%)"]],
                        data=[]  # Will be populated by callback
                    ),
                ]),
                dbc.Tab(label="Yearly", children=[
                    dash_table.DataTable(
                        id="yearly-report-table",
                        columns=[{"name": i, "id": i} for i in ["Year", "Start Value", "End Value", "Change (%)"]],
                        data=[]  # Will be populated by callback
                    ),
                ]),
                # ... (Add tabs for weekly reports as needed)
            ]
        ),

        # Projections
        html.H2("Portfolio Projections", style={"textAlign": "center"}),
        dcc.Graph(id="projection-graph"),  # Graph to display portfolio projections

        # Bot Controls
        html.H2("Bot Controls", style={"textAlign": "center"}),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Button("Start Bot", id="start-button", color="success", className="me-2", n_clicks=0),
                        dbc.Button("Stop Bot", id="stop-button", color="danger", className="me-2", n_clicks=0, disabled=True),
                        dbc.Button("Rebalance Portfolio", id="rebalance-button", color="primary", n_clicks=0),
                    ],
                    width=12,  # Full width for buttons
                ),
            ]
        ),

    ]
)


# --- DASHBOARD CALLBACKS ---

@app.callback(Output('portfolio-pie-chart', 'figure'),
              Output('portfolio-value', 'children'),
              Output('active-coins-list', 'children'),
              [Input('interval-component', 'n_intervals')])
def update_portfolio_overview(n):
    labels = []
    values = []
    balance = exchange.fetch_balance()
    for symbol, data in balance.items():
        if data['total'] > 0 and symbol != 'USDT':  # Exclude USDT
            labels.append(symbol)
            values.append(data['total'] * get_token_price(symbol))

    fig = go.Figure(data=[go.Pie(labels=labels, values=values)])
    fig.update_layout(title='Portfolio Asset Allocation')

    value = get_total_portfolio_value_usdt()
    return fig, f"USDT {value:.2f}", [html.Li(x) for x in coins_to_trade]


@app.callback(
    Output("monthly-report-table", "data"),
    Input("interval-component", "n_intervals"),
)
def update_monthly_report(n):
    return generate_report_data("monthly")

@app.callback(
    Output("quarterly-report-table", "data"),
    Input("interval-component", "n_intervals"),
)
def update_quarterly_report(n):
    return generate_report_data("quarterly")


@app.callback(
    Output("half-yearly-report-table", "data"),
    Input("interval-component", "n_intervals"),
)
def update_half_yearly_report(n):
    return generate_report_data("half-yearly")

@app.callback(
    Output("yearly-report-table", "data"),
    Input("interval-component", "n_intervals"),
)
def update_yearly_report(n):
    return generate_report_data("yearly")

# Callback for projection graph (implement based on `project_portfolio_value` logic)
@app.callback(
    Output('projection-graph', 'figure'),
    Input('interval-component', 'n_intervals')
)
def update_projection_graph(n):
    fig = go.Figure()

    current_value = get_total_portfolio_value_usdt()
    monthly_investment = 3000  
    annual_growth_rates = [0.10, 0.15, 0.20]  
    projection_years = [8, 18]  
    withdrawal_scenarios = {
        50: {"withdrawal": 30000, "label": "Optimistic"}, 
        60: {"withdrawal": 30000, "label": "Realistic"}, 
    }

    for rate in annual_growth_rates:
        for years, scenario in withdrawal_scenarios.items():
            future_values = []
            for year in range(1, years + 1):
                future_value = calculate_future_value(current_value, monthly_investment, rate, year, scenario["withdrawal"], years)
                future_values.append(future_value)

            fig.add_trace(go.Scatter(x=list(range(1, years + 1)), y=future_values, mode='lines+markers', name=f"{scenario['label']} ({rate * 100:.0f}%)"))
    fig.update_layout(title="Portfolio Projections", xaxis_title="Years", yaxis_title="Portfolio Value (USDT)")
    return fig
        
#Callbacks to handle button clicks
@app.callback(
    [Output("start-button", "disabled"), Output("stop-button", "disabled")],
    [Input("start-button", "n_clicks"), Input("stop-button", "n_clicks")],
)
def start_stop_bot(start_clicks, stop_clicks):
    if start_clicks > stop_clicks:  # Start button was clicked last
        start_trading()
        return True, False  # Disable start, enable stop
    else:  # Stop button was clicked last
