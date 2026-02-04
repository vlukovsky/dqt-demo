"""
Страница справки
"""
import dash
from dash import html
import dash_bootstrap_components as dbc

dash.register_page(__name__, path="/help", name="Справка")


def layout():
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H2("Справка", className="mb-4"),
                
                dbc.Card([
                    dbc.CardHeader([
                        html.I(className="fas fa-book me-2"),
                        "О системе DQT"
                    ]),
                    dbc.CardBody([
                        html.P([
                            html.Strong("DQT (Data Quality Tool)"),
                            " — система управления качеством данных для хранилища данных."
                        ]),
                        html.P("Основные возможности:"),
                        html.Ul([
                            html.Li("Создание и управление проверками качества данных"),
                            html.Li("Мониторинг результатов проверок"),
                            html.Li("Оповещения о проблемах через Telegram"),
                            html.Li("Интеграция с Airflow для запуска проверок"),
                        ]),
                    ])
                ], className="mb-4"),
                
                dbc.Card([
                    dbc.CardHeader([
                        html.I(className="fas fa-tasks me-2"),
                        "Типы проверок"
                    ]),
                    dbc.CardBody([
                        dbc.Table([
                            html.Thead([
                                html.Tr([
                                    html.Th("Тип"),
                                    html.Th("Описание"),
                                ])
                            ]),
                            html.Tbody([
                                html.Tr([
                                    html.Td(html.Strong("Полнота данных")),
                                    html.Td("Проверка на отсутствие NULL значений в важных полях"),
                                ]),
                                html.Tr([
                                    html.Td(html.Strong("Уникальность")),
                                    html.Td("Проверка уникальности ключевых полей"),
                                ]),
                                html.Tr([
                                    html.Td(html.Strong("Актуальность")),
                                    html.Td("Проверка своевременности загрузки данных"),
                                ]),
                                html.Tr([
                                    html.Td(html.Strong("Согласованность")),
                                    html.Td("Проверка ссылочной целостности между таблицами"),
                                ]),
                                html.Tr([
                                    html.Td(html.Strong("Корректность формата")),
                                    html.Td("Проверка соответствия форматам (email, телефон и т.д.)"),
                                ]),
                                html.Tr([
                                    html.Td(html.Strong("Бизнес-правило")),
                                    html.Td("Кастомные проверки бизнес-логики"),
                                ]),
                            ])
                        ], bordered=True, hover=True, responsive=True),
                    ])
                ], className="mb-4"),
                
                dbc.Card([
                    dbc.CardHeader([
                        html.I(className="fas fa-user-shield me-2"),
                        "Роли пользователей"
                    ]),
                    dbc.CardBody([
                        dbc.Table([
                            html.Thead([
                                html.Tr([
                                    html.Th("Роль"),
                                    html.Th("Права"),
                                ])
                            ]),
                            html.Tbody([
                                html.Tr([
                                    html.Td(dbc.Badge("admin_dqt", color="danger")),
                                    html.Td("Полный доступ ко всем функциям системы"),
                                ]),
                                html.Tr([
                                    html.Td(dbc.Badge("steward_dq", color="warning")),
                                    html.Td("Управление проверками домена, шаблоны"),
                                ]),
                                html.Tr([
                                    html.Td(dbc.Badge("tech_user", color="info")),
                                    html.Td("Создание и запуск своих проверок"),
                                ]),
                                html.Tr([
                                    html.Td(dbc.Badge("author_check", color="primary")),
                                    html.Td("Создание проверок, просмотр"),
                                ]),
                                html.Tr([
                                    html.Td(dbc.Badge("viewer", color="secondary")),
                                    html.Td("Только просмотр"),
                                ]),
                            ])
                        ], bordered=True, hover=True, responsive=True),
                    ])
                ], className="mb-4"),
                
                dbc.Card([
                    dbc.CardHeader([
                        html.I(className="fas fa-phone me-2"),
                        "Контакты"
                    ]),
                    dbc.CardBody([
                        html.P([
                            html.I(className="fab fa-telegram me-2 text-info"),
                            "Telegram: @dq_support"
                        ]),
                        html.P([
                            html.I(className="fas fa-envelope me-2 text-primary"),
                            "Email: dq-team@company.com"
                        ]),
                        html.P([
                            html.I(className="fab fa-confluence me-2"),
                            "Документация: Confluence / DQT"
                        ]),
                    ])
                ]),
            ])
        ])
    ], fluid=True, className="py-3")
