"""
Страница детальной информации о проверке
"""
import dash
from dash import html, dcc, callback, Input, Output, State, ctx
import dash_bootstrap_components as dbc
import dash_ag_grid as dag
import dash_cytoscape as cyto
import plotly.express as px
import plotly.graph_objects as go
from mock_data import get_check_by_id, get_check_results, get_check_versions, get_lineage, MOCK_CHECKS

dash.register_page(__name__, path_template="/check/<check_id>", name="Детали проверки")


def layout(check_id=None):
    if check_id is None:
        check_id = 1
    
    check_id = int(check_id)
    check = get_check_by_id(check_id)
    
    if check is None:
        return dbc.Container([
            dbc.Alert([
                html.I(className="fas fa-exclamation-triangle me-2"),
                "Проверка не найдена. ",
                html.A("Вернуться к списку проверок", href="/checks"),
            ], color="danger")
        ])
    
    results = get_check_results(check_id, limit=30)
    versions = get_check_versions(check_id)
    lineage_elements = get_lineage(check["table_name"])
    
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
            ], width=7),
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
                        html.I(className="fas fa-bug me-1"),
                        "Ошибка"
                    ], id="btn-report-incorrect", color="warning", outline=True,
                       title="Сообщить о некорректной проверке"),
                    dbc.Button([
                        html.I(className="fas fa-trash me-1"),
                    ], id="btn-delete-check", color="danger", outline=True),
                ]),
            ], width=5, className="text-end"),
        ], className="mb-4"),
        
        # Табы
        dbc.Tabs([
            # Таб: Обзор
            dbc.Tab([
                dbc.Row([
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
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader("История запусков"),
                            dbc.CardBody([
                                dcc.Graph(
                                    figure=create_history_chart(results),
                                    style={"height": "250px"},
                                    config={"displayModeBar": False},
                                )
                            ])
                        ])
                    ], width=8),
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader("Информация"),
                            dbc.CardBody([
                                html.Div([
                                    html.Strong("Тип: "), html.Span(check["check_type_name"]),
                                ], className="mb-2"),
                                html.Div([
                                    html.Strong("Домен: "), html.Span(check["domain"]),
                                ], className="mb-2"),
                                html.Div([
                                    html.Strong("Threshold: "), html.Span(f"{check['threshold']*100}%"),
                                ], className="mb-2"),
                                html.Div([
                                    html.Strong("Активна: "),
                                    dbc.Badge("Да" if check["is_active"] else "Нет",
                                              color="success" if check["is_active"] else "secondary"),
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
                            dbc.Col(html.H5("SQL-скрипт проверки"), width=8),
                            dbc.Col([
                                dbc.Button([
                                    html.I(className="fas fa-copy me-1"), "Копировать"
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
            
            # Таб: Предыдущие версии
            dbc.Tab([
                dbc.Card([
                    dbc.CardBody([
                        html.H5("История изменений конфигурации", className="mb-3"),
                        html.P("Все изменения проверки фиксируются и доступны для просмотра.", className="text-muted small"),
                        dag.AgGrid(
                            id="versions-grid",
                            rowData=versions.to_dict("records") if not versions.empty else [],
                            columnDefs=[
                                {"field": "version", "headerName": "Версия", "width": 90,
                                 "cellRenderer": {"function": """params => {
                                    const isCurrent = params.data.is_current;
                                    return isCurrent ? `<span class="badge bg-primary">v${params.value} (текущая)</span>` : `v${params.value}`;
                                 }"""}},
                                {"field": "change_type", "headerName": "Тип изменения", "width": 200},
                                {"field": "changed_by", "headerName": "Автор", "width": 130},
                                {"field": "changed_at", "headerName": "Дата изменения", "width": 180,
                                 "valueFormatter": {"function": "d3.timeFormat('%d.%m.%Y %H:%M')(new Date(params.value))"}},
                                {"field": "threshold", "headerName": "Threshold", "width": 100,
                                 "valueFormatter": {"function": "params.value != null ? (params.value * 100).toFixed(1) + '%' : '-'"}},
                                {"field": "schedule", "headerName": "Расписание", "width": 120},
                            ],
                            defaultColDef={"sortable": True, "resizable": True},
                            dashGridOptions={"pagination": True, "paginationPageSize": 10},
                            style={"height": "350px"},
                            className="ag-theme-alpine",
                        ),
                    ])
                ], className="mt-3")
            ], label="Предыдущие версии", tab_id="tab-versions"),
            
            # Таб: Lineage
            dbc.Tab([
                dbc.Card([
                    dbc.CardBody([
                        html.H5([
                            "Lineage таблицы ",
                            dbc.Badge(check["table_name"], color="info"),
                        ], className="mb-3"),
                        html.P("Граф зависимостей: источники данных слева, потребители справа.", className="text-muted small"),
                        cyto.Cytoscape(
                            id="lineage-graph",
                            elements=lineage_elements,
                            layout={"name": "breadthfirst", "directed": True, "spacingFactor": 1.5},
                            style={"width": "100%", "height": "400px", "border": "1px solid #dee2e6", "borderRadius": "8px"},
                            stylesheet=[
                                {
                                    "selector": "node",
                                    "style": {
                                        "label": "data(label)",
                                        "text-valign": "center",
                                        "text-halign": "center",
                                        "background-color": "#6c757d",
                                        "color": "#fff",
                                        "font-size": "11px",
                                        "width": "120px",
                                        "height": "35px",
                                        "shape": "round-rectangle",
                                        "text-wrap": "wrap",
                                        "text-max-width": "110px",
                                        "padding": "8px",
                                    }
                                },
                                {
                                    "selector": 'node[layer = "center"]',
                                    "style": {
                                        "background-color": "#0d6efd",
                                        "border-width": "3px",
                                        "border-color": "#0a58ca",
                                        "font-weight": "bold",
                                        "width": "140px",
                                        "height": "40px",
                                    }
                                },
                                {
                                    "selector": 'node[layer = "source"]',
                                    "style": {"background-color": "#198754"}
                                },
                                {
                                    "selector": 'node[layer = "target"]',
                                    "style": {"background-color": "#fd7e14"}
                                },
                                {
                                    "selector": "edge",
                                    "style": {
                                        "curve-style": "bezier",
                                        "target-arrow-shape": "triangle",
                                        "target-arrow-color": "#adb5bd",
                                        "line-color": "#adb5bd",
                                        "width": 2,
                                    }
                                },
                            ],
                        ),
                        html.Div([
                            dbc.Badge("Центральная таблица", color="primary", className="me-2"),
                            dbc.Badge("Источники", color="success", className="me-2"),
                            dbc.Badge("Потребители", color="warning", className="me-2"),
                        ], className="mt-2"),
                    ])
                ], className="mt-3")
            ], label="Lineage", tab_id="tab-lineage"),
            
            # Таб: Алерты
            dbc.Tab([
                dbc.Card([
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col(html.H5("Настройки оповещений"), width=8),
                            dbc.Col([
                                dbc.Button([
                                    html.I(className="fas fa-plus me-1"), "Добавить"
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
                html.P("Вы собираетесь запустить проверку:"),
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
                    html.I(className="fas fa-play me-1"), "Запустить"
                ], id="btn-confirm-run", color="success"),
            ]),
        ], id="modal-run-check", is_open=False),
        
        # Модальное окно «Сообщить о некорректной проверке»
        dbc.Modal([
            dbc.ModalHeader(dbc.ModalTitle("Сообщить о некорректной проверке")),
            dbc.ModalBody([
                html.P("Если вы считаете, что проверка работает некорректно, опишите проблему:"),
                dbc.Form([
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Категория проблемы"),
                            dcc.Dropdown(
                                id="report-category",
                                options=[
                                    {"label": "Ложное срабатывание (False Positive)", "value": "false_positive"},
                                    {"label": "Пропуск ошибки (False Negative)", "value": "false_negative"},
                                    {"label": "Некорректный SQL", "value": "bad_sql"},
                                    {"label": "Неверный threshold", "value": "bad_threshold"},
                                    {"label": "Другое", "value": "other"},
                                ],
                                placeholder="Выберите категорию...",
                                searchable=True,
                                clearable=True,
                                style={"fontSize": "0.9em"},
                            ),
                        ]),
                    ], className="mb-3"),
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Описание проблемы"),
                            dbc.Textarea(
                                id="report-description",
                                placeholder="Подробно опишите, что именно некорректно...",
                                rows=4,
                            ),
                        ]),
                    ], className="mb-3"),
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Ваш email (для обратной связи)"),
                            dbc.Input(id="report-email", type="email", placeholder="user@company.com"),
                        ]),
                    ]),
                ]),
            ]),
            dbc.ModalFooter([
                dbc.Button("Отмена", id="btn-cancel-report", color="secondary", outline=True),
                dbc.Button([
                    html.I(className="fas fa-paper-plane me-2"), "Отправить"
                ], id="btn-send-report", color="warning"),
            ]),
        ], id="modal-report-check", size="lg", is_open=False),
        
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
            "OK": "#28a745", "FAIL": "#dc3545",
            "ERROR": "#fd7e14", "SKIP": "#6c757d"
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


# Callback для модального окна отчёта о некорректной проверке
@callback(
    Output("modal-report-check", "is_open"),
    [Input("btn-report-incorrect", "n_clicks"),
     Input("btn-cancel-report", "n_clicks"),
     Input("btn-send-report", "n_clicks")],
    State("modal-report-check", "is_open"),
    prevent_initial_call=True
)
def toggle_report_modal(n_report, n_cancel, n_send, is_open):
    return not is_open


@callback(
    [Output("toast-check-action", "is_open"),
     Output("toast-check-action", "children"),
     Output("toast-check-action", "header"),
     Output("toast-check-action", "icon")],
    [Input("btn-confirm-run", "n_clicks"),
     Input("btn-send-report", "n_clicks")],
    [State("report-category", "value"),
     State("report-description", "value")],
    prevent_initial_call=True
)
def handle_check_actions(n_run, n_report, report_cat, report_desc):
    triggered = ctx.triggered_id
    
    if triggered == "btn-confirm-run" and n_run:
        return True, "Проверка отправлена в Airflow для выполнения", "Запуск проверки", "success"
    
    if triggered == "btn-send-report" and n_report:
        if not report_cat or not report_desc:
            return True, "Заполните категорию и описание проблемы", "Ошибка", "danger"
        return True, "Спасибо! Ваше сообщение отправлено команде DQ. Мы свяжемся с вами.", "Отчёт отправлен", "success"
    
    return False, "", "", ""
