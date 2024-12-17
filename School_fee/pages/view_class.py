import dash
from dash import html, dcc, callback, Input, Output, State, ALL
from styles import APP_STYLE, HEADER_STYLE, NAV_BAR_STYLE,SUB_HEADER_STYLE, NAV_LINK_STYLE, SECTION_STYLE, BUTTON_STYLE, INPUT_STYLE, OUTPUT_STYLE, DROPDOWN_STYLE, DATE_STYLE, DATE_INPUT_STYLE
from db import get_db_connection
from datetime import date

dash.register_page(__name__)

layout = html.Div([
        html.H1("Student Details", style=HEADER_STYLE),
        html.Div([
            dcc.Input(
                id='admission-number',
                type='number',
                placeholder="Enter Admission Number",
                style=INPUT_STYLE
            ),
            dcc.Dropdown(
                id='student-year-dropdown',
                options=[{'label': str(year), 'value': year} for year in range(2020, 2025)],
                placeholder="Select Year",
                style=DROPDOWN_STYLE
            ),
            html.Button("Fetch Details", id='fetch-student-details', style=BUTTON_STYLE),
            html.Div(id='student-details-output', style=OUTPUT_STYLE)
        ], style=SECTION_STYLE),
        html.A("Back to Home", href='/', style={**NAV_LINK_STYLE, 'display': 'inline-block', 'margin-top': '20px'})
    ], style=APP_STYLE)

@callback(
    Output('student-details-output', 'children'),
    [Input('fetch-student-details', 'n_clicks')],
    [State('admission-number', 'value'), State('student-year-dropdown', 'value')]
)
def fetch_student_details(n_clicks, admission_number, selected_year):
    if not n_clicks:
        return dash.no_update

    if not admission_number or not selected_year:
        return "Please provide both Admission Number and Year."

    try:
        # Establish a database connection
        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
            SELECT
                s.admission_number,
                s.aadhar_number,
                s.student_name,
                s.guardian_name,
                s.gender,
                s.date_of_birth,
                s.date_of_joining,
                s.contact_number,
                s.village,
                yr.year,
                SUM(fb.paid) FILTER (WHERE fb.fee_type = 'school_fee') AS total_school_fee_paid,
                SUM(fb.paid) FILTER (WHERE fb.fee_type = 'transport_fee') AS total_transport_fee_paid,
                SUM(fb.paid) FILTER (WHERE fb.fee_type = 'application_fee') AS total_application_fee_paid,
                SUM(fb.paid) AS total_fee_paid,
                SUM(fb.due) FILTER (WHERE fb.fee_type = 'school_fee') AS total_school_fee_due,
                SUM(fb.due) FILTER (WHERE fb.fee_type = 'transport_fee') AS total_transport_fee_due,
                SUM(fb.due) FILTER (WHERE fb.fee_type = 'application_fee') AS total_application_fee_due,
                SUM(fb.due) AS total_fee_due
            FROM Student s
            LEFT JOIN FeeBreakdown fb ON s.admission_number = fb.admission_number
            LEFT JOIN YearlyRecord yr ON s.admission_number = yr.admission_number AND fb.year = yr.year
            WHERE fb.admission_number = %s AND fb.year = %s
            GROUP BY s.admission_number, s.aadhar_number, s.student_name, s.guardian_name, s.gender,
                     s.date_of_birth, s.date_of_joining, s.contact_number, s.village, yr.year;
        """
        cursor.execute(query, (admission_number, selected_year))
        records = cursor.fetchall()

        if not records:
            return "No data found for the selected admission number and year."

        record = records[0]
        fields = [
            "Admission Number", "Aadhar Number", "Student Name", "Guardian Name", "Gender",
            "Date of Birth", "Date of Joining", "Contact Number", "Village", "Year",
            "Total School Fee Paid", "Total Transport Fee Paid", "Total Application Fee Paid",
            "Total Fee Paid", "Total School Fee Due", "Total Transport Fee Due",
            "Total Application Fee Due", "Total Fee Due"
        ]
        return html.Div([html.P(f"{field}: {value}") for field, value in zip(fields, record)])
    except Exception as e:
        return f"An error occurred: {str(e)}"
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

