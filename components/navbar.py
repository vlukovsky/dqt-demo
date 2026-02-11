"""
Навигационная панель DQT
"""
import dash_bootstrap_components as dbc
from dash import html, dcc


def create_navbar():
    """Создание верхней навигационной панели"""
    return dbc.Navbar(
        dbc.Container([
            # Логотип и название
            dbc.Row([
                dbc.Col([
                    # Кнопка-гамбургер для мобильных
                    dbc.Button(
                        html.I(className="fas fa-bars"),
                        id="btn-sidebar-toggle",
                        color="link",
                        className="text-white d-md-none me-2 p-1",
                        style={"fontSize": "1.2rem"},
                    ),
                ], width="auto", className="d-md-none"),
                dbc.Col(html.I(className="fas fa-shield-alt fa-lg me-2")),
                dbc.Col(dbc.NavbarBrand("DQT - Data Quality Tool", className="ms-2 fw-bold")),
            ], align="center", className="g-0"),
            
            # Правая часть navbar
            dbc.Nav([
                # Селектор роли
                dbc.NavItem(
                    html.Div([
                        html.Small("Роль:", className="text-light me-1 d-none d-lg-inline"),
                        dcc.Dropdown(
                            id="role-selector",
                            options=[
                                {"label": "Администратор", "value": "admin"},
                                {"label": "Редактор", "value": "editor"},
                                {"label": "Наблюдатель", "value": "viewer"},
                            ],
                            value="admin",
                            clearable=False,
                            searchable=False,
                            style={"width": "160px", "fontSize": "0.8em"},
                            className="d-inline-block",
                        ),
                    ], className="d-flex align-items-center me-3"),
                ),
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
