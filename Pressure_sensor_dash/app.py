import json
import numpy as np
from dash import Dash, html, dcc, Input, Output, State
import dash_bootstrap_components as dbc

# Params
mu = 100
std_dev = 200
previous_data = np.random.normal(mu, std_dev, (8, 6))
def generate_data():
    global previous_data
    alpha = 1  # Controls Variability
    new_data = np.random.normal(mu, std_dev, (8, 6))
    
    blended_data = alpha * new_data + (1 - alpha) * previous_data
    previous_data = blended_data
    
    return blended_data.tolist()

def count_cells(data):
    return np.sum(np.array(data) > 0).tolist()

def create_figures(store_data):
    if not store_data:
        return Dash.no_update, Dash.no_update
    payload = json.loads(store_data)
    data = payload['data']
    counts = payload['counts']

    line_color = '#2D708EFF'

    heatmap_figure = {
        'data': [{
            'z': data, 
            'type': 'heatmap', 
            'colorscale': 'Viridis', 
            'showscale': False}],
        'layout': {
            'margin': {'l': 40, 'r': 40, 't': 40, 'b': 40},
            'autosize': True}
    }
    
    lineplot_figure = {
        'data': [{
            'x': [i for i in range(len(counts))],
            'y': counts,
            'type': 'scatter',
            'mode': 'lines',
            'line': {'color': line_color}
        }],
        'layout': {
            'title': 'Count of Active Cells',
            'xaxis': {'title': 'Row'},
            'yaxis': {'title': 'Count'},
            'margin': {'l': 40, 'r': 40, 't': 120, 'b': 20}
        }
    }
    return heatmap_figure, lineplot_figure

def create_metrics(store_data, threshold):
    if not store_data:
        return Dash.no_update
    
    payload = json.loads(store_data)

    counts_avg = payload['average']
    percent_avg = 100 * counts_avg / 48
    font_color = 'red' if percent_avg <= threshold else 'green' # We need do decide what threshold = 'bad' 

    return [
        html.P('Total Cells: {}'.format(48)),
        html.P(['Percent of Cells Active: ',
               html.Span('{:.2f}%'.format(percent_avg),
        style={'color': font_color})
        ])
    ]

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])  
app.layout = dbc.Container([
    dbc.Container([
        dbc.Row([
            dbc.Col([
                dcc.Markdown('Pressure Map Dashboard', 
                             style={'textAlign': 'center', 'fontSize': 30, 'fontWeight': 'bold'})
            ], width=12)
        ]),
        dbc.Row([
            dbc.Col([
                html.H4('Pressure Map 1', style={'textAlign': 'center', 
                                                 'marginTop': '50px', 
                                                 'color': '#481567FF'}),
                dcc.Graph(id='heatmap1', 
                          style={'height': '80vh'})
            ], width=6),
            dbc.Col([
                html.H4('Pressure Map 2', style={'textAlign': 'center', 
                                                 'marginTop': '50px',
                                                 'color': '#481567FF'}),
                dcc.Graph(id='heatmap2', 
                        style={'height': '80vh'})
            ], width=6)
        ]),
        dbc.Row([
            dbc.Col([
                dcc.Graph(id="lineplot1"),
                html.Div(id='live-update-text1', 
                         style={'textAlign': 'left', 'fontSize': 16}),
                dcc.Slider(0, 100, 10, value=50, id='slider1')
            ], width=6),
            dbc.Col([
                dcc.Graph(id="lineplot2"),
                html.Div(id='live-update-text2', 
                         style={'textAlign': 'left', 'fontSize': 16}),
                dcc.Slider(0, 100, 10, value=50, id='slider2')
            ], width=6)
        ]),
        dcc.Interval(id="interval-component", 
                     interval=1*50, # in milliseconds
                     n_intervals=0)
    ]),
    dcc.Store(id='store-data1'),
    dcc.Store(id='store-data2')
])

counts1 = []
counts2 = []
@app.callback(
    Output('store-data1', 'data'),
    Output('store-data2', 'data'),
    [Input('interval-component', 'n_intervals')],
    [State('store-data1', 'data')] ,[State('store-data2', 'data')]
)
def update_data(n_intervals, store_data1, store_data2):
    data1 = generate_data()
    data2 = generate_data()

    cell_count1 = count_cells(data1)
    cell_count2 = count_cells(data2)

    if store_data1:
        store1 = json.loads(store_data1)
        counts1 = store1.get('counts', [])
    else:
        counts1 = []

    if store_data2:
        store2 = json.loads(store_data2)
        counts2 = store2.get('counts', [])
    else:
        counts2 = []

    counts1.append(cell_count1)
    counts2.append(cell_count2)
    counts_avg1 = np.mean(counts1).tolist()
    counts_avg2 = np.mean(counts2).tolist()
    return json.dumps({'data': data1, 'counts': counts1, 'average': counts_avg1}), json.dumps(
        {'data': data2, 'counts': counts2, 'average': counts_avg2})

@app.callback(
    Output(component_id='heatmap1', component_property='figure'),
    Output(component_id='lineplot1', component_property='figure'),
    [Input(component_id='store-data1', component_property='data')]
)
def update_graphs(store_data):
    return create_figures(store_data)

@app.callback(
    Output(component_id='heatmap2', component_property='figure'),
    Output(component_id='lineplot2', component_property='figure'),
    [Input(component_id='store-data2', component_property='data')]
)
def update_graphs(store_data):
    return create_figures(store_data)

@app.callback(
    Output('live-update-text1', 'children'),
    [Input('store-data1', 'data')],
    [Input('slider1', 'value')]
)
def update_metrics(store_data, threshold):
    return create_metrics(store_data, threshold)

@app.callback(
    Output('live-update-text2', 'children'),
    [Input('store-data2', 'data')],
    [Input('slider2', 'value')]
)
def update_metrics(store_data, threshold):
    return create_metrics(store_data, threshold)

if __name__ == '__main__':
    app.run_server(debug=True, port=8051)
