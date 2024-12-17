import dash
from dash import html, dcc, callback, Input, Output, State, ALL
from styles import APP_STYLE, HEADER_STYLE, NAV_BAR_STYLE,SUB_HEADER_STYLE, NAV_LINK_STYLE, SECTION_STYLE, BUTTON_STYLE, INPUT_STYLE, OUTPUT_STYLE, DROPDOWN_STYLE, DATE_STYLE, DATE_INPUT_STYLE
from db import get_db_connection
from datetime import date
import base64
import io
import pandas as pd

dash.register_page(__name__)

def generate_input(id, placeholder, input_type='text'):
    return dcc.Input(id=id, type=input_type, placeholder=placeholder, style=INPUT_STYLE)


input_fields = [
    {'id': 'admission_number', 'type': 'number', 'placeholder': 'Admission Number', 'value': None},
    {'id': 'aadhar_number', 'type': 'number', 'placeholder': 'Aadhar Number', 'value': None},
    {'id': 'StudentName', 'type': 'text', 'placeholder': 'Student Name', 'value': ''},
    {'id': 'FatherName', 'type': 'text', 'placeholder': "Father's Name", 'value': ''},
    {'id': 'contact_number', 'type': 'tel', 'placeholder': 'Contact Number', 'value': ''},
    {'id': 'village', 'type': 'text', 'placeholder': 'Village', 'value': ''}
]

date_pickers = [
    {'id': 'dob', 'placeholder': 'Date of Birth'},
    {'id': 'doj', 'placeholder': 'Date of Joining'}
]

layout = html.Div([
    html.H1("Student Details Entry", style=HEADER_STYLE),
    html.Div([
        *[generate_input(field['id'], field['placeholder'], input_type=field['type']) for field in input_fields],
        dcc.Dropdown(
            id='gender',
            options=[{'label': label, 'value': label} for label in ['Boy', 'Girl']],
            placeholder="Gender",
            style=DROPDOWN_STYLE
        ),
        html.Div([
            *[dcc.DatePickerSingle(id=date['id'], display_format='DD/MM/YYYY', placeholder=date['placeholder'], style=DATE_INPUT_STYLE) for date in date_pickers]
        ], style=DATE_STYLE),
        html.Button('Submit', id='student-details-submit-button', n_clicks=0, style=BUTTON_STYLE),
        dcc.Upload(
            id='upload-csv',
            children=html.Button('Import from CSV', style=BUTTON_STYLE),
            accept='.csv',
            style={'margin-top': '10px'}
        ),
    ], style=SECTION_STYLE),
    html.A("Back to Home", href='/', style={**NAV_LINK_STYLE, 'display': 'inline-block', 'margin-top': '20px'})
], style=APP_STYLE)

@callback(
    Output('upload-csv', 'children'),
    Input('upload-csv', 'contents')
)
def import_csv(contents):
    if contents:
        try:
            content_type, content_string = contents.split(',')
            decoded = base64.b64decode(content_string)
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))

            # Connect to the database
            conn = get_db_connection()
            cursor = conn.cursor()

            for _, row in df.iterrows():
                admission_number = row['admission_number']
                student_name = row['student_name']
                guardian_name = row['guardian_name']
                gender = row['gender']
                aadhar_number = row['aadhar_number']
                date_of_birth = row['date_of_birth']
                date_of_joining = row['date_of_joining']
                contact_number = row['contact_number']
                village = row['village']

                # SQL query to insert data
                insert_query = """
                    INSERT INTO Student (
                        admission_number, student_name, guardian_name, gender, aadhar_number,
                        date_of_birth, date_of_joining, contact_number, village
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (admission_number) DO NOTHING
                """
                cursor.execute(insert_query, (
                    admission_number, student_name, guardian_name, gender,
                    aadhar_number, date_of_birth, date_of_joining, contact_number, village
                ))

            # Commit changes
            conn.commit()
            cursor.close()
            conn.close()

            return "CSV data imported successfully!"

        except Exception as e:
            return f"Error processing file: {str(e)}"

    return "Import from CSV"

@callback(
    Output('student-details-submit-button', 'children'),
    inputs=[
        Input('student-details-submit-button', 'n_clicks'),
        State('admission_number', 'value'),
        State('StudentName', 'value'),
        State('FatherName', 'value'),
        State('gender', 'value'),
        State('aadhar_number', 'value'),
        State('dob', 'date'),
        State('doj', 'date'),
        State('contact_number', 'value'),
        State('village', 'value'),
    ]
)
def upload_student_data(n_clicks, admission_number, student_name, guardian_name, gender, aadhar_number, date_of_birth, date_of_joining, contact_number, village):
    if n_clicks > 0:
        try:
            # Validate required fields
            if not all([admission_number, student_name, guardian_name, gender, date_of_birth, date_of_joining]):
                return "Please fill all required fields"

            # Connect to the database
            conn = get_db_connection()
            cursor = conn.cursor()

            # Check if admission number already exists
            check_query = "SELECT COUNT(*) FROM Student WHERE admission_number = %s or aadhar_number = %s"
            cursor.execute(check_query, (admission_number, aadhar_number))
            count = cursor.fetchone()[0]

            if count > 0:
                return "Admission number or Aadhar number already exists. Please use unique values."

            # SQL query to insert data
            insert_query = """
                INSERT INTO Student (
                    admission_number, student_name, guardian_name, gender, aadhar_number,
                    date_of_birth, date_of_joining, contact_number, village
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (admission_number) DO NOTHING
            """

            # Execute query with the submitted data
            cursor.execute(insert_query, (
                admission_number, student_name, guardian_name, gender,
                aadhar_number, date_of_birth, date_of_joining, contact_number, village
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
