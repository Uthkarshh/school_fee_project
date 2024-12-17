import dash
from dash import html, dcc, callback, Input, Output, State, ALL
from styles import APP_STYLE, HEADER_STYLE, NAV_BAR_STYLE,SUB_HEADER_STYLE, NAV_LINK_STYLE, SECTION_STYLE, BUTTON_STYLE, INPUT_STYLE, OUTPUT_STYLE, DROPDOWN_STYLE, DATE_STYLE, DATE_INPUT_STYLE
from db import get_db_connection
from datetime import date

dash.register_page(__name__)

layout = html.Div([
        html.H1("Class Details", style=HEADER_STYLE),
        html.Div([
            dcc.Dropdown(
                id='class-dropdown',
                options=[{'label': f'Class {i}', 'value': str(i)} for i in range(1, 13)],
                placeholder="Select Class",
                style=DROPDOWN_STYLE
            ),
            dcc.Dropdown(
                id='year-dropdown',
                options=[{'label': str(year), 'value': year} for year in range(2020, 2025)],
                placeholder="Select Year",
                style=DROPDOWN_STYLE
            ),
            html.Button("Fetch Details", id='fetch-class-details', style=BUTTON_STYLE),
            html.Div(id='class-details-output', style=OUTPUT_STYLE)
        ], style=SECTION_STYLE),
        html.A("Back to Home", href='/', style={**NAV_LINK_STYLE, 'display': 'inline-block', 'margin-top': '20px'})
    ], style=APP_STYLE)


@callback(
    Output('class-details-output', 'children'),
    [Input('fetch-class-details', 'n_clicks')],
    [State('class-dropdown', 'value'), State('year-dropdown', 'value')]
)
def fetch_class_details(n_clicks, selected_class, selected_year):
    if not n_clicks:
        return dash.no_update

    conn = None  # Ensure connection is initialized
    try:
        # Establish a database connection
        conn = get_db_connection()
        cursor = conn.cursor()

        # Parameterized query to prevent SQL injection
        query = """
            WITH class_data AS (
                SELECT
                    cd.class,
                    cd.section,
                    s.gender,
                    yr.total_fee_paid,
                    yr.total_fee_due
                FROM classdetails cd
                LEFT JOIN Student s ON cd.admission_number = s.admission_number
                LEFT JOIN YearlyRecord yr ON cd.admission_number = yr.admission_number AND cd.year = yr.year
                WHERE cd.class = %s AND cd.year = %s
            )
            SELECT
                COUNT(*) AS total_students,
                SUM(CASE WHEN section = 'A' THEN 1 ELSE 0 END) AS Sec_A,
                SUM(CASE WHEN section = 'B' THEN 1 ELSE 0 END) AS Sec_B,
                SUM(CASE WHEN section = 'C' THEN 1 ELSE 0 END) AS Sec_C,
                SUM(CASE WHEN gender = 'Boy' THEN 1 ELSE 0 END) AS total_male,
                SUM(CASE WHEN gender = 'Girl' THEN 1 ELSE 0 END) AS total_female,
                SUM(total_fee_paid) AS total_fee_paid,
                SUM(total_fee_due) AS total_fee_due
            FROM class_data;
        """
        cursor.execute(query, (selected_class, selected_year))
        result = cursor.fetchone()

        if not result:
            return "No data found for the selected class and year."

        # Unpack results and handle None values
        total_students, sec_a, sec_b, sec_c, total_male, total_female, total_fee_paid, total_fee_due = result
        total_fee_paid = total_fee_paid or 0  # Default to 0 if None
        total_fee_due = total_fee_due or 0    # Default to 0 if None

        # Calculate total sections
        total_sections = sum([bool(sec_a), bool(sec_b), bool(sec_c)])

        # Return data as a Div
        return html.Div([
            html.P(f"Total Students: {total_students}"),
            html.P(f"Sec A: {sec_a}"),
            html.P(f"Sec B: {sec_b}"),
            html.P(f"Sec C: {sec_c}"),
            html.P(f"Male Students: {total_male}"),
            html.P(f"Female Students: {total_female}"),
            html.P(f"Total Fee Paid: ₹{total_fee_paid:.2f}"),
            html.P(f"Total Fee Due: ₹{total_fee_due:.2f}")
        ])

    except Exception as e:
        if conn and not conn.closed:  # Rollback only if the connection is open
            conn.rollback()
        return f"An error occurred: {str(e)}"

    finally:
        if conn and not conn.closed:  # Close connection if it's open
            conn.close()

