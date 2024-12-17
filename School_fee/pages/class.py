import dash
from dash import html, dcc, callback, Input, Output, State, ALL
from styles import APP_STYLE, HEADER_STYLE, NAV_BAR_STYLE,SUB_HEADER_STYLE, NAV_LINK_STYLE, SECTION_STYLE, BUTTON_STYLE, INPUT_STYLE, OUTPUT_STYLE, DROPDOWN_STYLE, DATE_STYLE, DATE_INPUT_STYLE
from db import get_db_connection
from datetime import date

dash.register_page(__name__)

def get_db_connection():
    return psycopg2.connect(
        host="localhost",
        dbname = "school_fee_db",
        user = "uthkarsh",
        password = "Ruthwik081@")

APP_STYLE = {
    'font-family': 'Arial, sans-serif',
    'margin': '0 auto',
    'padding': '20px',
    'max-width': '800px',
    'background-color': '#ffffff',  # Softer white background
    'box-shadow': '0 4px 8px rgba(0, 0, 0, 0.1)',
    'border-radius': '10px',
    'padding-bottom': '30px',
}

HEADER_STYLE = {
    'text-align': 'center',
    'padding': '15px 0',
    'background-color': '#0066cc',  # Calming blue header
    'color': 'white',
    'border-radius': '10px 10px 0 0',
    'font-size': '24px',
    'font-weight': 'bold'
}

SUB_HEADER_STYLE = {
    'text-align': 'center',
    'font-size': '24px',
    'font-weight': 'bold'    
}

NAV_BAR_STYLE = {
    'text-align': 'center',
    'margin': '15px 0',
}

NAV_LINK_STYLE = {
    'margin': '0 10px',
    'padding': '10px 20px',
    'background-color': '#0066cc',  # Matches header
    'color': 'white',
    'border-radius': '5px',
    'text-decoration': 'none',
    'font-weight': 'bold',
    'box-shadow': '0 2px 4px rgba(0, 0, 0, 0.2)',  # Adds depth
}

SECTION_STYLE = {
    'padding': '15px 20px',
    'display': 'flex',
    'flex-direction': 'column',
    'align-items': 'center',
}

BUTTON_STYLE = {
    'background-color': '#0066cc',  # Matches header and nav
    'color': 'white',
    'border': 'none',
    'padding': '10px 30px',
    'border-radius': '5px',
    'cursor': 'pointer',
    'font-size': '16px',
    'margin-top': '15px',
    'box-shadow': '0 2px 4px rgba(0, 0, 0, 0.2)',  # Subtle shadow for depth
}

INPUT_STYLE = {
    'margin': '10px 0',
    'padding': '12px 15px',
    'width': '100%',
    'border': '1px solid #ccc',
    'border-radius': '5px',
    'font-size': '14px',
    'box-shadow': 'inset 0 1px 3px rgba(0, 0, 0, 0.1)',  # Adds dimension
}

OUTPUT_STYLE = {
    "marginTop": "20px",
    "padding": "10px",
    "border": "1px solid #ccc",
    "borderRadius": "5px",
    "backgroundColor": "#f9f9f9",
    "fontSize": "16px"
}

DROPDOWN_STYLE = {
    'margin': '10px 0',
    'padding': '12px 15px',
    'width': '100%',
    'height': '50%',
    'border': '1px solid #ccc',
    'border-radius': '1px',
    'font-size': '14px',
    'background-color': '#f9f9f9',  # Softer background to match input
    'box-shadow': 'inset 0 1px 3px rgba(0, 0, 0, 0.1)',  # Same as input
}

DATE_STYLE = {
    'display': 'flex',
    'justify-content': 'space-between',
    'gap': '15px',  # Balanced spacing between date fields
    'width': '100%',
}

DATE_INPUT_STYLE = {
    'padding': '12px 15px',
    'flex': '1',  # Ensures even width for both date inputs
    'border': '1px solid #ccc',
    'border-radius': '5px',
    'font-size': '14px',
    'box-shadow': 'inset 0 1px 3px rgba(0, 0, 0, 0.1)',
}

def generate_input(id, placeholder, input_type='text'):
    return dcc.Input(id=id, type=input_type, placeholder=placeholder, style=INPUT_STYLE)

def generate_dropdown(id, options, placeholder):
    return dcc.Dropdown(id=id, options=options, placeholder=placeholder, style=DROPDOWN_STYLE)

# Page 2: Student Class Details Layout
layout = html.Div([
        html.H1("Student Class Details Entry", style=HEADER_STYLE),
        html.Div([
            generate_input('admission_number', 'Admission Number', 'number'),
            generate_input('roll_number', 'Roll Number', 'number'),
            generate_input('photo_id', 'Photo ID', 'number'),
            dcc.Dropdown(
                id='class_no', 
                options=[{'label': f'Class {i}', 'value': i} for i in range(1, 13)],
                placeholder="Class",
                style=DROPDOWN_STYLE
            ),
            generate_input('section', 'Section', 'text'),
            generate_input('current_year', 'Year', 'number'),
            dcc.Dropdown(id='enrolled', options=[
                {'label': 'Yes', 'value': 'Yes'},
                {'label': 'No', 'value': 'No'}
            ], placeholder="Currently Enrolled", style=DROPDOWN_STYLE),
            dcc.Dropdown(id='language', options=[
                {'label': 'Telugu', 'value': 'Telugu'},
                {'label': 'Hindi', 'value': 'Hindi'},
                {'label': 'Sanskrit', 'value': 'Sanskrit'}
            ], placeholder="Language", style=DROPDOWN_STYLE),
            dcc.Dropdown(id='vocational', options=[
                {'label': 'Agriculture', 'value': 'Agriculture'},
                {'label': 'Artificial Intelligence', 'value': 'AI'},
                {'label': 'Physical Activity Trainer', 'value': 'PAT'},
                {'label': 'Tourism', 'value': 'Tourism'}
            ], placeholder="Vocational", style=DROPDOWN_STYLE),
            html.Button('Submit', id='student-class-submit-button', n_clicks=0, style=BUTTON_STYLE),
        ], style=SECTION_STYLE),
        html.A("Back to Home", href='/', style={**NAV_LINK_STYLE, 'display': 'inline-block', 'margin-top': '20px'})
    ], style=APP_STYLE)



@callback(
    Output('student-class-submit-button', 'children'),
    inputs=[
        Input('student-class-submit-button', 'n_clicks'),
        State('admission_number', 'value'),
        State('roll_number', 'value'),
        State('photo_id', 'value'),
        State('class_no', 'value'),
        State('section', 'value'),
        State('current_year', 'value'),
        State('enrolled', 'value'),
        State('language', 'value'),
        State('vocational', 'value'),
    ]
)
def upload_student__class_data(n_clicks, admission_number, roll_number, photo_id, class_no, section, current_year, enrolled,language,vocational):
    if n_clicks > 0:
        try:
            # Validate required fields
            if not all([admission_number, roll_number, photo_id, class_no, section, current_year, enrolled]):
                return "Please fill all required fields"
            
            # Convert enrolled to boolean
            currently_enrolled = True if enrolled == 'Yes' else False
            
            # Connect to the database
            conn = get_db_connection()
            cursor = conn.cursor()

            # Check if admission number already exists
            check_query = "SELECT COUNT(*) FROM ClassDetails WHERE admission_number = %s and year = %s"
            cursor.execute(check_query, (admission_number, current_year))
            count = cursor.fetchone()[0]

            if count > 0:
                return "Admission number or Aadhar number already exists. Please use unique values."

            # SQL query to insert data
            insert_query = """
                INSERT INTO ClassDetails (admission_number, year, class, section, roll_number, photo_id, currently_enrolled,language,vocational)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (admission_number, year) DO UPDATE
                SET roll_number = EXCLUDED.roll_number,
                    photo_id = EXCLUDED.photo_id,
                    currently_enrolled = EXCLUDED.currently_enrolled,
                    language = EXCLUDED.language,
                    vocational = EXCLUDED.vocational
            """

            # Execute query with the submitted data
            cursor.execute(insert_query, (
                admission_number, current_year, class_no, section, roll_number, photo_id, currently_enrolled,language,vocational
            ))

            # Commit changes
            conn.commit()

            # Close connection
            cursor.close()
            conn.close()

            return "Data submitted successfully!"

        except Exception as e:
            return f"Error: {str(e)}"

    return "Submit"


