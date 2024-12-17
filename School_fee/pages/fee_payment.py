import dash
from dash import html, dcc, callback, Input, Output, State, ALL
from styles import APP_STYLE, HEADER_STYLE, NAV_BAR_STYLE,SUB_HEADER_STYLE, NAV_LINK_STYLE, SECTION_STYLE, BUTTON_STYLE, INPUT_STYLE, OUTPUT_STYLE, DROPDOWN_STYLE, DATE_STYLE, DATE_INPUT_STYLE
from db import get_db_connection
from datetime import date

dash.register_page(__name__)

input_fields = [
        {'id': 'paid', 'type': 'number', 'placeholder': 'Fee Paid'},
        {'id': 'due', 'type': 'number', 'placeholder': 'Fee Due'},
        {'id': 'receipt_number', 'type': 'number', 'placeholder': 'Receipt Number'}
    ]

layout = html.Div([
        html.H1("Fee Payment Details Entry", style=HEADER_STYLE),
        html.Div([
            dcc.Input(id='admission_number', type='number', placeholder='Admission Number', style=INPUT_STYLE),
            dcc.Input(id='year', type='number', placeholder='Year', style=INPUT_STYLE),
            dcc.Dropdown(
                id='fee_type',
                options=[
                    {'label': 'School Fee', 'value': 'school_fee'},
                    {'label': 'Transport Fee', 'value': 'transport_fee'},
                    {'label': 'Application Fee', 'value': 'application_fee'}
                ],
                value=None,  # Default to None
                placeholder="Select Fee Type",
                style=DROPDOWN_STYLE
            ),
            dcc.Dropdown(
                id='fee_term',
                options=[
                    {'label': 'Term 1', 'value': 'term_1'},
                    {'label': 'Term 2', 'value': 'term_2'},
                    {'label': 'Term 3', 'value': 'term_3'}
                ],
                value=None,  # Default to None
                placeholder="Select Fee Term",
                style=DROPDOWN_STYLE
            ),
            *[dcc.Input(id = field['id'], type = field['type'], placeholder = field['placeholder'], style=INPUT_STYLE) for field in input_fields],
            html.H2("Date paid", style= SUB_HEADER_STYLE),
            dcc.DatePickerSingle(
                id='paid_date',
                display_format='DD/MM/YYYY',
                placeholder="Date Paid",
                date=date.today(),  # Set the default date to today
                style={'margin-top': '10px'}
            ),
            html.Button('Submit', id='feepayment-details-submit-button', n_clicks=0, style=BUTTON_STYLE)
        ], style=SECTION_STYLE),
        html.Div(id='fee-content'),
        html.A("Back to Home", href='/', style={**NAV_LINK_STYLE, 'display': 'inline-block', 'margin-top': '20px'})
    ], style=APP_STYLE)

# Define the callback to handle Fee Payment Details form submission
@callback(
    Output('fee-content', 'children'),
    inputs=[
        Input('feepayment-details-submit-button', 'n_clicks')
    ],
    state=[
        State('admission_number', 'value'),
        State('year', 'value'),
        State('fee_type', 'value'),
        State('fee_term', 'value'),
        State('paid', 'value'),
        State('due', 'value'),
        State('receipt_number', 'value'),
        State('paid_date', 'date')
    ]
)
def fee_payment_details(n_clicks, admission_number, year, fee_type, fee_term, paid, due, receipt_no, paid_date):
    if n_clicks > 0:
        try:
            # Validate required fields
            if not all([admission_number, year, fee_type, fee_term, paid, due, receipt_no, paid_date]):
                return "Error: All fields are required."

            # Establish a database connection
            conn = get_db_connection()
            cursor = conn.cursor()

            # Insert or update data into the FeeBreakdown table
            insert_fee_breakdown_query = """
                INSERT INTO FeeBreakdown (
                    admission_number, year, fee_type, term, paid, due, receipt_no, fee_paid_date
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (admission_number, year, fee_type) DO UPDATE
                SET term = EXCLUDED.term,
                    paid = EXCLUDED.paid,
                    due = EXCLUDED.due,
                    receipt_no = EXCLUDED.receipt_no,
                    fee_paid_date = EXCLUDED.fee_paid_date;
            """

            cursor.execute(insert_fee_breakdown_query, (
                admission_number, year, fee_type, fee_term, paid, due, receipt_no, paid_date
            ))

            # Commit the transaction and close the connection
            conn.commit()
            cursor.close()
            conn.close()

            return "Fee payment details successfully uploaded!"

        except Exception as e:
            return f"Error: {str(e)}"

    return ""

