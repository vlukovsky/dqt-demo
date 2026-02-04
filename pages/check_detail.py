"""
Страница детальной информации о проверке
"""
import dash
from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
import dash_ag_grid as dag
import plotly.express as px
import plotly.graph_objects as go
from mock_data import get_check_by_id, get_check_results, MOCK_CHECKS

dash.register_page(__name__, path_template="/check/<check_id>", name="Детали проверки")


def layout(check_id=None):
    if check_id is None:
        check_id = 1
    
    check_id = int(check_id)
    check = get_check_by_id(check_id)
    
    if check is None:
        return dbc.Container([
            dbc.Alert("Проверка не найдена", color="danger")
        ])
    
    results = get_check_results(check_id, limit=30)
    
    # Статистика за последние 30 дней
    total_runs = len(results)
    success_runs = len(results[results["check_status_name"] == "OK"])
    success_rate = round(success_runs / total_runs * 100, 1) if total_runs > 0 else 0
    avg_time = results["execution_time_sec"].mean() if not results.empty else 0
    
    return dbc.Container([
        # Хлебные крошки
        dbc.Breadcrumb(
            items=[
                {"label": "Проверки", "href": "/checks"},
                {"label": check["check_name"], "active": True},
            ],
            className="mb-3"
        ),
        
        # Заголовок с действиями
        dbc.Row([
            dbc.Col([
                html.H2([
                    check["check_name"],
                    dbc.Badge(
                        check["last_status"],
                        color="success" if check["last_status"] == "OK" else "danger",
                        className="ms-2"
                    ),
                ], className="mb-1"),
                html.P([
                    html.I(className="fas fa-table me-1"),
                    check["table_name"],
                    html.Span(" | ", className="text-muted"),
                    html.I(className="fas fa-user me-1"),
                    check["owner"],
                    html.Span(" | ", className="text-muted"),
                    html.I(className="fas fa-clock me-1"),
                    check["schedule_main_value"],
                ], className="text-muted"),
            ], width=8),
            dbc.Col([
                dbc.ButtonGroup([
                    dbc.Button([
                        html.I(className="fas fa-play me-1"),
                        "Запустить"
                    ], id="btn-run-check", color="success", outline=True),
                    dbc.Button([
                        html.I(className="fas fa-edit me-1"),
                        "Изменить"
                    ], id="btn-edit-check", color="primary", outline=True),
                    dbc.Button([
                        html.I(className="fas fa-trash me-1"),
                    ], id="btn-delete-check", color="danger", outline=True),
                ]),
            ], width=4, className="text-end"),
        ], className="mb-4"),
        
        # Табы
        dbc.Tabs([
            # Таб: Обзор
            dbc.Tab([
                dbc.Row([
                    # KPI карточки
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.H4(f"{total_runs}", className="mb-0 text-primary"),
                                html.Small("Запусков за 30 дней", className="text-muted"),
                            ])
                        ], className="text-center")
                    ], width=3),
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.H4(f"{success_rate}%", className="mb-0 text-success"),
                                html.Small("Успешность", className="text-muted"),
                            ])
                        ], className="text-center")
                    ], width=3),
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.H4(f"{avg_time:.1f}s", className="mb-0 text-info"),
                                html.Small("Среднее время", className="text-muted"),
                            ])
                        ], className="text-center")
                    ], width=3),
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.H4(
                                    check["priority"],
                                    className=f"mb-0 text-{'danger' if check['priority'] == 'HIGH' else 'warning' if check['priority'] == 'MEDIUM' else 'secondary'}"
                                ),
                                html.Small("Приоритет", className="text-muted"),
                            ])
                        ], className="text-center")
                    ], width=3),
                ], className="mb-4 mt-3"),
                
                dbc.Row([
                    # График истории
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader("История запусков"),
                            dbc.CardBody([
                                dcc.Graph(
                                    figure=create_history_chart(results),
                                    style={"height": "250px"}
                                )
                            ])
                        ])
                    ], width=8),
                    
                    # Информация о проверке
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader("Информация"),
                            dbc.CardBody([
                                html.Div([
                                    html.Strong("Тип: "),
                                    html.Span(check["check_type_name"]),
                                ], className="mb-2"),
                                html.Div([
                                    html.Strong("Домен: "),
                                    html.Span(check["domain"]),
                                ], className="mb-2"),
                                html.Div([
                                    html.Strong("Threshold: "),
                                    html.Span(f"{check['threshold']*100}%"),
                                ], className="mb-2"),
                                html.Div([
                                    html.Strong("Активна: "),
                                    dbc.Badge(
                                        "Да" if check["is_active"] else "Нет",
                                        color="success" if check["is_active"] else "secondary"
                                    ),
                                ], className="mb-2"),
                                html.Div([
                                    html.Strong("Описание: "),
                                    html.P(check["description"], className="text-muted small mb-0"),
                                ]),
                            ])
                        ])
                    ], width=4),
                ]),
            ], label="Обзор", tab_id="tab-overview"),
            
            # Таб: SQL
            dbc.Tab([
                dbc.Card([
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                html.H5("SQL-скрипт проверки"),
                            ], width=8),
                            dbc.Col([
                                dbc.Button([
                                    html.I(className="fas fa-copy me-1"),
                                    "Копировать"
                                ], id="btn-copy-sql", size="sm", color="outline-secondary"),
                            ], width=4, className="text-end"),
                        ], className="mb-3"),
                        
                        dcc.Markdown(
                            f"```sql\n{check['sql_script']}\n```",
                            className="border rounded p-3 bg-light",
                            style={"fontSize": "0.9em"}
                        ),
                    ])
                ], className="mt-3")
            ], label="SQL-скрипт", tab_id="tab-sql"),
            
            # Таб: История
            dbc.Tab([
                dbc.Card([
                    dbc.CardBody([
                        dag.AgGrid(
                            id="history-grid",
                            rowData=results.to_dict("records"),
                            columnDefs=[
                                {"field": "run_datetime", "headerName": "Время запуска", "width": 180,
                                 "valueFormatter": {"function": "d3.timeFormat('%d.%m.%Y %H:%M')(new Date(params.value))"}},
                                {"field": "check_status_name", "headerName": "Статус", "width": 100,
                                 "cellRenderer": "StatusRenderer"},
                                {"field": "execution_time_sec", "headerName": "Время (сек)", "width": 120},
                                {"field": "rows_checked", "headerName": "Строк проверено", "width": 140,
                                 "valueFormatter": {"function": "params.value ? params.value.toLocaleString() : '-'"}},
                                {"field": "rows_failed", "headerName": "Строк с ошибками", "width": 150},
                                {"field": "error_message", "headerName": "Сообщение об ошибке", "width": 250},
                            ],
                            defaultColDef={"sortable": True, "resizable": True},
                            dashGridOptions={"pagination": True, "paginationPageSize": 10},
                            style={"height": "400px"},
                            className="ag-theme-alpine",
                        )
                    ])
                ], className="mt-3")
            ], label="История запусков", tab_id="tab-history"),
            
            # Таб: Алерты
            dbc.Tab([
                dbc.Card([
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                html.H5("Настройки оповещений"),
                            ], width=8),
                            dbc.Col([
                                dbc.Button([
                                    html.I(className="fas fa-plus me-1"),
                                    "Добавить"
                                ], size="sm", color="primary"),
                            ], width=4, className="text-end"),
                        ], className="mb-3"),
                        
                        dbc.ListGroup([
                            dbc.ListGroupItem([
                                dbc.Row([
                                    dbc.Col([
                                        html.I(className="fab fa-telegram text-info me-2"),
                                        html.Strong("Telegram"),
                                        html.Span(" - @dq_alerts_channel", className="text-muted ms-2"),
                                    ], width=8),
                                    dbc.Col([
                                        dbc.Badge("При FAIL", color="danger", className="me-2"),
                                        dbc.Switch(id="alert-tg-switch", value=True, className="d-inline"),
                                    ], width=4, className="text-end"),
                                ]),
                            ]),
                            dbc.ListGroupItem([
                                dbc.Row([
                                    dbc.Col([
                                        html.I(className="fas fa-envelope text-primary me-2"),
                                        html.Strong("Email"),
                                        html.Span(" - team@company.com", className="text-muted ms-2"),
                                    ], width=8),
                                    dbc.Col([
                                        dbc.Badge("При ERROR", color="warning", className="me-2"),
                                        dbc.Switch(id="alert-email-switch", value=False, className="d-inline"),
                                    ], width=4, className="text-end"),
                                ]),
                            ]),
                        ]),
                    ])
                ], className="mt-3")
            ], label="Алерты", tab_id="tab-alerts"),
            
        ], id="check-tabs", active_tab="tab-overview"),
        
        # Модальное окно запуска
        dbc.Modal([
            dbc.ModalHeader(dbc.ModalTitle("Запуск проверки")),
            dbc.ModalBody([
                html.P(f"Вы собираетесь запустить проверку:"),
                html.H5(check["check_name"]),
                html.Hr(),
                dbc.Form([
                    dbc.Label("Дата проверки (опционально)"),
                    dbc.Input(type="date", id="run-date-input"),
                    dbc.FormText("Оставьте пустым для проверки за вчера"),
                ]),
            ]),
            dbc.ModalFooter([
                dbc.Button("Отмена", id="btn-cancel-run", color="secondary", outline=True),
                dbc.Button([
                    html.I(className="fas fa-play me-1"),
                    "Запустить"
                ], id="btn-confirm-run", color="success"),
            ]),
        ], id="modal-run-check", is_open=False),
        
        # Toast
        dbc.Toast(
            id="toast-check-action",
            header="Уведомление",
            is_open=False,
            dismissable=True,
            duration=4000,
            style={"position": "fixed", "top": 66, "right": 10, "width": 350},
        ),
        
    ], fluid=True, className="py-3")


def create_history_chart(results):
    """Создание графика истории запусков"""
    if results.empty:
        return go.Figure()
    
    fig = px.scatter(
        results,
        x="run_datetime",
        y="execution_time_sec",
        color="check_status_name",
        size="rows_checked",
        color_discrete_map={
            "OK": "#28a745",
            "FAIL": "#dc3545",
            "ERROR": "#fd7e14",
            "SKIP": "#6c757d"
        },
        labels={
            "run_datetime": "Дата",
            "execution_time_sec": "Время (сек)",
            "check_status_name": "Статус"
        },
    )
    
    fig.update_layout(
        margin=dict(l=20, r=20, t=20, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hovermode="closest",
    )
    
    return fig


# Callback для модального окна запуска
@callback(
    Output("modal-run-check", "is_open"),
    [Input("btn-run-check", "n_clicks"),
     Input("btn-cancel-run", "n_clicks"),
     Input("btn-confirm-run", "n_clicks")],
    State("modal-run-check", "is_open"),
    prevent_initial_call=True
)
def toggle_run_modal(n_run, n_cancel, n_confirm, is_open):
    return not is_open


@callback(
    [Output("toast-check-action", "is_open"),
     Output("toast-check-action", "children"),
     Output("toast-check-action", "header"),
     Output("toast-check-action", "icon")],
    Input("btn-confirm-run", "n_clicks"),
    prevent_initial_call=True
)
def run_check(n_clicks):
    if n_clicks:
        return True, "Проверка отправлена в Airflow для выполнения", "Запуск проверки", "success"
    return False, "", "", ""
