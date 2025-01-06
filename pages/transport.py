import dash
from dash import html, dcc, callback, Input, Output, State, ALL
from styles import APP_STYLE, HEADER_STYLE, NAV_BAR_STYLE,SUB_HEADER_STYLE, NAV_LINK_STYLE, SECTION_STYLE, BUTTON_STYLE, INPUT_STYLE, OUTPUT_STYLE, DROPDOWN_STYLE, DATE_STYLE, DATE_INPUT_STYLE
from db import get_db_connection
from datetime import date

dash.register_page(__name__)

layout = html.Div([
        html.H1("Transport Details Entry", style=HEADER_STYLE),
        html.Div([
            dcc.Input(id='pickup_point', type='text', placeholder='Pick-Up Point', style=INPUT_STYLE),
            dcc.Input(id='transport_route', type='number', placeholder='Route Number', style=INPUT_STYLE),
           html.Button('Submit', id='transport-details-submit-button', n_clicks=0, style=BUTTON_STYLE),
            ], style=SECTION_STYLE),
        html.A("Back to Home", href='/', style={**NAV_LINK_STYLE, 'display': 'inline-block', 'margin-top': '20px'})
    ], style=APP_STYLE)

@callback(
    Output('transport-details-submit-button', 'children'),
    inputs=[
        Input('transport-details-submit-button', 'n_clicks'),
        State('pickup_point', 'value'),
        State('transport_route', 'value'),
    ]
)
def transport_details(n_clicks, pick_up_point, route_number):
    if n_clicks > 0:
        try:
            # Validate required fields
            if not all([pick_up_point, route_number]):
                return "Please fill all required fields"

            # Connect to the database
            conn = get_db_connection()
            cursor = conn.cursor()

            # Check if admission number already exists
            check_query = "SELECT COUNT(*) FROM Transport WHERE route_number = %s"
            cursor.execute(check_query, (route_number,))
            count = cursor.fetchone()[0]

            if count > 0:
                return "Route Number already exists. Please use unique values."

            # SQL query to insert data
            insert_query = """
                INSERT INTO Transport (
                    pick_up_point, route_number
                )
                VALUES (%s, %s)
            """

            # Execute query with the submitted data
            cursor.execute(insert_query, (
                pick_up_point, route_number
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
