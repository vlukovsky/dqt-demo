"""
Страница таблиц (заглушка)
"""
import dash
from dash import html
import dash_bootstrap_components as dbc

dash.register_page(__name__, path="/tables", name="Таблицы")


def layout():
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H2("Таблицы", className="mb-4"),
                
                dbc.Alert([
                    html.I(className="fas fa-info-circle me-2"),
                    "Страница в разработке. Здесь будет реестр таблиц с проверками качества данных."
                ], color="info"),
                
                dbc.Card([
                    dbc.CardHeader("Планируемый функционал"),
                    dbc.CardBody([
                        html.Ul([
                            html.Li("Список всех таблиц в DWH с покрытием проверками"),
                            html.Li("Фильтрация по схеме, домену, владельцу"),
                            html.Li("Статистика качества данных по таблице"),
                            html.Li("Связь с Data Catalog"),
                            html.Li("Lineage визуализация"),
                        ])
                    ])
                ])
            ])
        ])
    ], fluid=True, className="py-3")
