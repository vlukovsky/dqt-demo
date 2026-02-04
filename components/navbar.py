"""
Навигационная панель DQT
"""
import dash_bootstrap_components as dbc
from dash import html


def create_navbar():
    """Создание верхней навигационной панели"""
    return dbc.Navbar(
        dbc.Container([
            # Логотип и название
            dbc.Row([
                dbc.Col(html.I(className="fas fa-shield-alt fa-lg me-2")),
                dbc.Col(dbc.NavbarBrand("DQT - Data Quality Tool", className="ms-2 fw-bold")),
            ], align="center", className="g-0"),
            
            # Правая часть navbar
            dbc.Nav([
                dbc.NavItem(dbc.NavLink([
                    html.I(className="fas fa-bell me-1"),
                    dbc.Badge("3", color="danger", pill=True, className="position-absolute top-0 start-100 translate-middle"),
                ], href="#", className="position-relative")),
                dbc.NavItem(dbc.NavLink([
                    html.I(className="fas fa-user me-1"),
                    "demo_user"
                ], href="#")),
            ], className="ms-auto", navbar=True),
        ], fluid=True),
        color="primary",
        dark=True,
        className="mb-0",
        style={"height": "56px"}
    )
