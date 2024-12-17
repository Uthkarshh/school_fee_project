import dash
from dash import html, dcc, callback, Input, Output, State, ALL
from styles import APP_STYLE, HEADER_STYLE, NAV_BAR_STYLE,SUB_HEADER_STYLE, NAV_LINK_STYLE, SECTION_STYLE, BUTTON_STYLE, INPUT_STYLE, OUTPUT_STYLE, DROPDOWN_STYLE, DATE_STYLE, DATE_INPUT_STYLE
from db import get_db_connection
from datetime import date

dash.register_page(__name__)

def generate_input(id, placeholder, input_type='text'):
    return dcc.Input(id=id, type=input_type, placeholder=placeholder, style=INPUT_STYLE)

# Page 3: Fee Details Layout
layout = html.Div([
        html.H1("Fee Details Entry", style=HEADER_STYLE),
        html.Div([
            dcc.Input(id='admission_number', type='number', placeholder='Admission Number', style=INPUT_STYLE),
            dcc.Input(id='year', type='number', placeholder='Year', style=INPUT_STYLE),
            dcc.Input(id='school_fee', type='number', placeholder='School Fee', style=INPUT_STYLE),
            dcc.Dropdown(
                id='school_fee_concession_reason',
                options=[
                    {'label': reason, 'value': reason} for reason in [
                        'Staff', 'Sibling', 'OTP', 'TF', 'FP', 'EC', 'SC', 'General'
                    ]
                ],
                placeholder="School Fee Concession Reason",
                style=DROPDOWN_STYLE
            ),
            dcc.Dropdown(
                id='transport_used',
                options=[
                    {'label': 'Yes', 'value': 'Yes'},
                    {'label': 'No', 'value': 'No'}
                ],
                placeholder="Transport Used",
                style=DROPDOWN_STYLE
            ),
            dcc.Input(id='transport_route', type='number', placeholder='Route Number', style=INPUT_STYLE, disabled=True),
            dcc.Input(id='transport_fee', type='number', placeholder='Transport Fee', style=INPUT_STYLE, disabled=True),
            dcc.Input(id='transport_fee_concession', type='text', placeholder='Transport Fee Concession', style=INPUT_STYLE, disabled=True),
            dcc.Input(id='application_fee', type='number', placeholder='Application Fee', style=INPUT_STYLE),
            html.Button('Submit', id='fee-details-submit-button', n_clicks=0, style=BUTTON_STYLE),
            ], style=SECTION_STYLE),
        html.A("Back to Home", href='/', style={**NAV_LINK_STYLE, 'display': 'inline-block', 'margin-top': '20px'})
    ], style=APP_STYLE)

@callback(
    [
        Output('transport_fee', 'disabled'),
        Output('transport_fee_concession', 'disabled'),
        Output('transport_route', 'disabled'), 
    ],
    Input('transport_used', 'value')
)
def toggle_transport_inputs(transport_used):
    if transport_used == 'No':
        return True, True, True  # Disable fields
    return False, False, False  # Enable fields


# Define the callback to handle Fee Details form submission
@callback(
    Output('fee-details-submit-button', 'children'),
    inputs=[
        Input('fee-details-submit-button', 'n_clicks')
    ],
    state=[
        State('admission_number', 'value'),
        State('year', 'value'),
        State('school_fee', 'value'),
        State('school_fee_concession_reason', 'value'),
        State('transport_used', 'value'),
        State('transport_route', 'value'),
        State('transport_fee', 'value'),
        State('transport_fee_concession', 'value'),
        State('application_fee', 'value')
    ]
)
def fee_details(n_clicks, admission_number, year, school_fee, school_fee_concession_reason, transport_used, transport_route, transport_fee, transport_fee_concession, application_fee):
    if n_clicks > 0:
        try:
            # Validate inputs
            if not all([admission_number, year, school_fee, application_fee]):
                return "Error: Required fields are missing."

            # Convert transport_used to boolean
            transport_used_boolean = True if transport_used == 'Yes' else False

            # Set transport-related fields to 0 if transport is not used
            if not transport_used_boolean:
                transport_fee = 0
                transport_fee_concession = 0
                transport_id = 0
            else:
                # Establish a database connection
                conn = get_db_connection()
                cursor = conn.cursor()

                # Check and get transport_id if transport is used
                transport_id = None
                if transport_route:
                    cursor.execute("SELECT transport_id FROM Transport WHERE route_number = %s", (transport_route,))
                    result = cursor.fetchone()
                    if result:
                        transport_id = result[0]
                    else:
                        return f"Error: No transport found for route number {transport_route}."

                # Close the cursor (will be reopened for the next query)
                cursor.close()
                conn.close()

            # Re-establish a database connection for inserting data
            conn = get_db_connection()
            cursor = conn.cursor()

            # Insert or update data into the Fee table
            insert_fee_query = """
                INSERT INTO Fee (
                    admission_number, year, school_fee, concession_reason, application_fee, transport_fee, transport_fee_concession, transport_used, transport_id
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (admission_number, year) DO UPDATE
                SET school_fee = EXCLUDED.school_fee,
                    concession_reason = EXCLUDED.concession_reason,
                    application_fee = EXCLUDED.application_fee,
                    transport_fee = EXCLUDED.transport_fee,
                    transport_fee_concession = EXCLUDED.transport_fee_concession,
                    transport_used = EXCLUDED.transport_used,
                    transport_id = EXCLUDED.transport_id;
            """

            cursor.execute(insert_fee_query, (
                admission_number, year, school_fee, school_fee_concession_reason, application_fee, transport_fee, transport_fee_concession, transport_used_boolean, transport_id
            ))

            # Commit the transaction and close the connection
            conn.commit()
            cursor.close()
            conn.close()

            return "Fee details successfully uploaded!"

        except Exception as e:
            return f"Error: {str(e)}"

    return "Submit"

