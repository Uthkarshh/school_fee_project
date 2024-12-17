import dash
from dash import Dash, html, dcc
import dash_bootstrap_components as dbc

# Initialize the Dash app
app = Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Create the navigation bar
navbar = dbc.Navbar(
    dbc.Container(
        [
            dbc.NavbarBrand("School App", href="/"),
            dbc.Nav(
                [
                    dbc.NavLink(page["name"], href=page["relative_path"], active="exact")
                    for page in dash.page_registry.values()
                ],
                navbar=True,
                pills=True,
            ),
        ]
    ),
    color="dark",
    dark=True,
    className="mb-4",
)

# Define the app layout
app.layout = html.Div([
    navbar,  # Add the navbar here
    dash.page_container  # This displays the content of the selected page
])

if __name__ == '__main__':
    app.run(debug=True)
