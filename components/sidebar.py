"""
Боковая панель навигации DQT
"""
import dash_bootstrap_components as dbc
from dash import html


def create_sidebar():
    """Создание боковой панели навигации"""
    return html.Div([
        dbc.Nav([
            dbc.NavLink([
                html.I(className="fas fa-chart-line me-2"),
                "Дашборд"
            ], href="/", active="exact", className="sidebar-link"),
            
            dbc.NavLink([
                html.I(className="fas fa-tasks me-2"),
                "Проверки"
            ], href="/checks", active="exact", className="sidebar-link"),
            
            dbc.NavLink([
                html.I(className="fas fa-history me-2"),
                "История"
            ], href="/results", active="exact", className="sidebar-link"),
            
            dbc.NavLink([
                html.I(className="fas fa-bell me-2"),
                "Алерты"
            ], href="/alerts", active="exact", className="sidebar-link"),
            
            dbc.NavLink([
                html.I(className="fas fa-table me-2"),
                "Таблицы"
            ], href="/tables", active="exact", className="sidebar-link"),
            
            html.Hr(className="my-3"),
            
            dbc.NavLink([
                html.I(className="fas fa-cog me-2"),
                "Настройки"
            ], href="/settings", active="exact", className="sidebar-link"),
            
            dbc.NavLink([
                html.I(className="fas fa-question-circle me-2"),
                "Справка"
            ], href="/help", active="exact", className="sidebar-link"),
        ], vertical=True, pills=True, className="flex-column"),
        
        # Статус системы внизу
        html.Div([
            html.Hr(),
            html.Div([
                html.Span("Статус: ", className="text-muted small"),
                html.Span("●", className="text-success me-1"),
                html.Span("Online", className="text-success small"),
            ], className="mb-2"),
            html.Div([
                html.Span("Версия: ", className="text-muted small"),
                html.Span("1.0.0-demo", className="small"),
            ]),
        ], className="mt-auto pt-3"),
    ], className="sidebar d-flex flex-column", style={"height": "calc(100vh - 56px)"})
