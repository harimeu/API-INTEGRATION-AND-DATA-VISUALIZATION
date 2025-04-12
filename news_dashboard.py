import os
import time  # For timestamp to prevent image caching
import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
from dash import Dash, html, dcc, dash_table, Input, Output
import dash_bootstrap_components as dbc


API_KEY = '25ed166d4e22434c8752314f66f5c072'  
BASE_URL = 'https://newsapi.org/v2/everything'


PLOT_DIR = "assets/plots"
os.makedirs(PLOT_DIR, exist_ok=True)


app = Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])
app.title = "News Insight Dashboard"
server = app.server


def fetch_news_data(query):
    params = {
        'q': query,
        'language': 'en',
        'pageSize': 100,
        'apiKey': API_KEY
    }
    response = requests.get(BASE_URL, params=params)
    data = response.json()
    if data['status'] != 'ok':
        return pd.DataFrame()
    return pd.DataFrame(data['articles'])


def prepare_data(df):
    if df.empty:
        return df
    df['publishedAt'] = pd.to_datetime(df['publishedAt'])
    df['date'] = df['publishedAt'].dt.date
    df['sourceName'] = df['source'].apply(lambda x: x['name'])
    return df

def generate_plots(df, keyword):
    if df.empty:
        return
    sns.set(style="darkgrid")

    
    time_data = df.groupby('date').size().reset_index(name='Count')
    plt.figure(figsize=(8, 4))
    sns.lineplot(data=time_data, x='date', y='Count', marker='o')
    plt.title(f'Articles Over Time: {keyword.capitalize()}')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(f"{PLOT_DIR}/time_plot.png")
    plt.close()

    
    top_sources = pd.DataFrame(Counter(df['sourceName']).most_common(10),
                               columns=['Source', 'Count'])
    plt.figure(figsize=(8, 4))
    sns.barplot(data=top_sources, x='Count', y='Source', palette='coolwarm')
    plt.title('Top 10 News Sources')
    plt.tight_layout()
    plt.savefig(f"{PLOT_DIR}/sources_plot.png")
    plt.close()


app.layout = dbc.Container([
    html.Div([
        html.H1("📰 News Insight Dashboard", className="display-4 fw-bold text-center mb-2", style={'fontFamily': 'Trebuchet MS', 'textTransform': 'uppercase'}),
        html.P("Explore the latest headlines on Technology, AI, Weather, Cybersecurity, and more.",
               className="lead text-center mb-4", style={'color': '#AAAAAA'})
    ]),

    dbc.Row([
        dbc.Col([
            dcc.Dropdown(
                id='keyword-input',
                options=[
                    {'label': 'Technology', 'value': 'technology'},
                    {'label': 'Artificial Intelligence', 'value': 'AI'},
                    {'label': 'Weather', 'value': 'weather'},
                    {'label': 'Cybersecurity', 'value': 'cybersecurity'},
                    {'label': 'Space', 'value': 'space'},
                    {'label': 'Robotics', 'value': 'robotics'},
                    {'label': 'Energy', 'value': 'renewable energy'},
                ],
                value='technology',
                placeholder='Select a topic',
                clearable=False,
                style={'color': 'black', 'backgroundColor': 'white'}
            )
        ])
    ]),

    dbc.Row([
        dbc.Col(html.Img(id='time-plot', style={'width': '100%', 'borderRadius': '10px'}))
    ], className="my-3"),

    dbc.Row([
        dbc.Col(html.Img(id='sources-plot', style={'width': '100%', 'borderRadius': '10px'}))
    ], className="mb-4"),

    html.H4("Latest Articles", className="mt-4 mb-2", style={'fontFamily': 'Trebuchet MS'}),

    dash_table.DataTable(
        id='articles-table',
        columns=[
            {"name": "Title", "id": "title"},
            {"name": "Source", "id": "sourceName"},
            {"name": "Published", "id": "publishedAt"},
        ],
        style_header={'backgroundColor': '#1a1a1a', 'color': 'white', 'fontWeight': 'bold'},
        style_data={'backgroundColor': '#2c2c2c', 'color': 'white'},
        style_table={'overflowX': 'auto'},
        style_cell={'textAlign': 'left', 'padding': '10px'},
        page_size=10
    )
], fluid=True, style={'overflowY': 'scroll', 'height': '100vh', 'padding': '20px'})


@app.callback(
    [Output('time-plot', 'src'),
     Output('sources-plot', 'src'),
     Output('articles-table', 'data')],
    [Input('keyword-input', 'value')]
)
def update_dashboard(keyword):
    df = fetch_news_data(keyword)
    df = prepare_data(df)

    if not df.empty:
        generate_plots(df, keyword)

    timestamp = int(time.time())
    time_src = f'/assets/plots/time_plot.png?{timestamp}'
    source_src = f'/assets/plots/sources_plot.png?{timestamp}'
    table_data = df[['title', 'sourceName', 'publishedAt']].to_dict('records')

    return time_src, source_src, table_data

if __name__ == '__main__':
    app.run(debug=True)
