import dash
from dash import html, dcc, Input, Output, callback
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime
import psycopg2
from .sidebar import sidebar

# Initialize the app with suppress_callback_exceptions=True
dash.register_page(__name__, name="Home", path="/", suppress_callback_exceptions=True)

def fetch_data(dbname, user, password):
    """Fetch required data from database"""
    try:
        conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host="localhost",
            port="5432"
        )
        
        queries = {
            'class_strength': """
                SELECT cd.class, cd.section, COUNT(*) as student_count 
                FROM ClassDetails cd 
                WHERE cd.currently_enrolled = true 
                GROUP BY cd.class, cd.section
                ORDER BY cd.class, cd.section
            """,
            'gender_distribution': """
                SELECT cd.class, s.gender, COUNT(*) as count
                FROM Student s
                JOIN ClassDetails cd ON s.admission_number = cd.admission_number
                WHERE cd.currently_enrolled = true
                GROUP BY cd.class, s.gender
                ORDER BY cd.class, s.gender
            """,
            'fee_collection': """
                SELECT fb.year, fb.fee_type, SUM(fb.paid) as total_paid
                FROM FeeBreakdown fb
                GROUP BY fb.year, fb.fee_type
                ORDER BY fb.year, fb.fee_type
            """,
            'concession_distribution': """
                SELECT f.concession_reason, COUNT(*) as count
                FROM Fee f
                WHERE f.concession_reason != ''
                GROUP BY f.concession_reason
            """
        }
        
        data = {name: pd.read_sql_query(query, conn) for name, query in queries.items()}
        conn.close()
        return data
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

def create_empty_figures():
    """Create empty figures for initial loading"""
    return {
        'class_distribution': px.bar(title='Student Distribution Across Classes'),
        'gender_distribution': px.bar(title='Gender Distribution by Class'),
        'fee_collection': px.line(title='Fee Collection Trends'),
        'concession_distribution': px.pie(title='Distribution of Fee Concessions')
    }

def layout(**kwargs):
    current_year = datetime.now().year
    
    return html.Div([
        # Main container with center alignment
        html.Div(
            className="container-fluid px-4 py-4",
            children=[
                # Header
                html.Div(
                    className="text-center mb-4",
                    children=[
                        html.H1("School Analytics Dashboard", className="text-primary")
                    ]
                ),
                
                # Filters Row
                dbc.Row(
                    justify="center",
                    className="mb-4",
                    children=[
                        dbc.Col([
                            html.Label("Select Year"),
                            dcc.Dropdown(
                                id='year-filter',
                                options=[{'label': str(year), 'value': year} 
                                        for year in range(current_year-5, current_year+1)],
                                value=current_year,
                                clearable=False
                            )
                        ], xs=12, sm=6, md=3),
                        dbc.Col([
                            html.Label("Select Class"),
                            dcc.Dropdown(
                                id='class-filter',
                                options=[{'label': str(i), 'value': i} for i in range(1, 13)],
                                value=[i for i in range(1, 13)],
                                multi=True
                            )
                        ], xs=12, sm=6, md=3),
                        dbc.Col([
                            html.Div(id='data-source-info', className="text-muted mt-4 text-center")
                        ], xs=12, md=6)
                    ]
                ),
                
                # Graphs Container
                html.Div(
                    className="row justify-content-center",
                    children=[
                        # First Row of Graphs
                        html.Div(
                            className="col-12 mb-4",
                            children=[
                                dbc.Row([
                                    dbc.Col([
                                        dbc.Card([
                                            dbc.CardHeader("Class-wise Student Distribution"),
                                            dbc.CardBody(dcc.Graph(id='class-distribution-graph'))
                                        ])
                                    ], xs=12, md=6, className="mb-4 mb-md-0"),
                                    
                                    dbc.Col([
                                        dbc.Card([
                                            dbc.CardHeader("Gender Distribution by Class"),
                                            dbc.CardBody(dcc.Graph(id='gender-distribution-graph'))
                                        ])
                                    ], xs=12, md=6)
                                ])
                            ]
                        ),
                        
                        # Second Row of Graphs
                        html.Div(
                            className="col-12",
                            children=[
                                dbc.Row([
                                    dbc.Col([
                                        dbc.Card([
                                            dbc.CardHeader("Fee Collection Trends"),
                                            dbc.CardBody(dcc.Graph(id='fee-collection-graph'))
                                        ])
                                    ], xs=12, md=6, className="mb-4 mb-md-0"),
                                    
                                    dbc.Col([
                                        dbc.Card([
                                            dbc.CardHeader("Concession Distribution"),
                                            dbc.CardBody(dcc.Graph(id='concession-distribution-graph'))
                                        ])
                                    ], xs=12, md=6)
                                ])
                            ]
                        )
                    ]
                )
            ]
        )
    ])

@callback(
    [Output('class-distribution-graph', 'figure'),
     Output('gender-distribution-graph', 'figure'),
     Output('fee-collection-graph', 'figure'),
     Output('concession-distribution-graph', 'figure')],
    [Input('year-filter', 'value'),
     Input('class-filter', 'value')]
)
def update_graphs(selected_year, selected_classes):
    # Fetch data
    data = fetch_data(
        dbname="school_fee_db",
        user="username",
        password="password@"
    )
    
    if data is None:
        return [create_empty_figures()[key] for key in [
            'class_distribution', 'gender_distribution',
            'fee_collection', 'concession_distribution'
        ]]

    # Filter data based on selected classes
    class_strength = data['class_strength'][
        data['class_strength']['class'].isin(selected_classes)
    ]
    gender_dist = data['gender_distribution'][
        data['gender_distribution']['class'].isin(selected_classes)
    ]

    # Create figures
    class_fig = px.bar(
        class_strength,
        x='class',
        y='student_count',
        color='section',
        title='Student Distribution Across Classes',
        labels={'student_count': 'Number of Students', 'class': 'Class'}
    )

    gender_fig = px.bar(
        gender_dist,
        x='class',
        y='count',
        color='gender',
        title='Gender Distribution by Class',
        barmode='group',
        labels={'count': 'Number of Students', 'class': 'Class'}
    )

    fee_fig = px.line(
        data['fee_collection'][data['fee_collection']['year'] == selected_year],
        x='fee_type',
        y='total_paid',
        title=f'Fee Collection Trends ({selected_year})',
        labels={'total_paid': 'Amount Collected (₹)', 'fee_type': 'Fee Type'}
    )

    concession_fig = px.pie(
        data['concession_distribution'],
        values='count',
        names='concession_reason',
        title='Distribution of Fee Concessions'
    )

    return class_fig, gender_fig, fee_fig, concession_fig
