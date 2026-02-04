"""
Страница настроек (заглушка)
"""
import dash
from dash import html
import dash_bootstrap_components as dbc

dash.register_page(__name__, path="/settings", name="Настройки")


def layout():
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H2("Настройки", className="mb-4"),
                
                dbc.Alert([
                    html.I(className="fas fa-info-circle me-2"),
                    "Страница в разработке. Здесь будут настройки системы."
                ], color="info"),
                
                dbc.Card([
                    dbc.CardHeader("Планируемые разделы"),
                    dbc.CardBody([
                        dbc.Accordion([
                            dbc.AccordionItem([
                                html.P("Управление пользователями и ролями"),
                                html.Ul([
                                    html.Li("Список пользователей"),
                                    html.Li("Назначение ролей"),
                                    html.Li("Права доступа"),
                                ])
                            ], title="Пользователи и роли"),
                            
                            dbc.AccordionItem([
                                html.P("Настройки подключений"),
                                html.Ul([
                                    html.Li("Greenplum GP100"),
                                    html.Li("PostgreSQL PG226"),
                                    html.Li("Airflow"),
                                ])
                            ], title="Подключения"),
                            
                            dbc.AccordionItem([
                                html.P("Настройки оповещений"),
                                html.Ul([
                                    html.Li("Telegram бот"),
                                    html.Li("Email рассылки"),
                                    html.Li("Шаблоны сообщений"),
                                ])
                            ], title="Оповещения"),
                            
                            dbc.AccordionItem([
                                html.P("Справочники системы"),
                                html.Ul([
                                    html.Li("Типы проверок"),
                                    html.Li("Статусы"),
                                    html.Li("Домены"),
                                ])
                            ], title="Справочники"),
                        ], start_collapsed=True)
                    ])
                ])
            ])
        ])
    ], fluid=True, className="py-3")
