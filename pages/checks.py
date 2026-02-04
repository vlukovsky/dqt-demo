"""
Страница списка проверок
"""
import dash
from dash import html, dcc, callback, Input, Output, State, ctx
import dash_bootstrap_components as dbc
import dash_ag_grid as dag
from mock_data import MOCK_CHECKS, MOCK_CHECK_TYPES, DOMAINS, OWNERS

dash.register_page(__name__, path="/checks", name="Проверки")


def layout():
    return dbc.Container([
        # Заголовок
        dbc.Row([
            dbc.Col([
                html.H2("Проверки качества данных", className="mb-0"),
                html.P("Управление проверками DQT", className="text-muted"),
            ], width=8),
            dbc.Col([
                dbc.Button([
                    html.I(className="fas fa-plus me-2"),
                    "Создать проверку"
                ], id="btn-create-check", color="primary"),
            ], width=4, className="text-end"),
        ], className="mb-4 align-items-center"),
        
        # Фильтры
        dbc.Card([
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        dbc.InputGroup([
                            dbc.InputGroupText(html.I(className="fas fa-search")),
                            dbc.Input(
                                id="search-checks",
                                placeholder="Поиск по названию, таблице...",
                                debounce=True,
                            ),
                        ]),
                    ], width=4),
                    dbc.Col([
                        dbc.Select(
                            id="filter-status",
                            options=[
                                {"label": "Все статусы", "value": ""},
                                {"label": "✅ OK", "value": "OK"},
                                {"label": "❌ FAIL", "value": "FAIL"},
                                {"label": "⚠️ ERROR", "value": "ERROR"},
                            ],
                            value="",
                        ),
                    ], width=2),
                    dbc.Col([
                        dbc.Select(
                            id="filter-type",
                            options=[{"label": "Все типы", "value": ""}] + [
                                {"label": ct["check_type_name"], "value": ct["check_type_name"]}
                                for ct in MOCK_CHECK_TYPES.to_dict("records")
                            ],
                            value="",
                        ),
                    ], width=2),
                    dbc.Col([
                        dbc.Select(
                            id="filter-domain",
                            options=[{"label": "Все домены", "value": ""}] + [
                                {"label": d, "value": d} for d in DOMAINS
                            ],
                            value="",
                        ),
                    ], width=2),
                    dbc.Col([
                        dbc.Button([
                            html.I(className="fas fa-filter-circle-xmark me-1"),
                            "Сбросить"
                        ], id="btn-reset-filters", color="outline-secondary", size="sm"),
                    ], width=2, className="text-end"),
                ], className="g-2"),
            ]),
        ], className="mb-3 shadow-sm"),
        
        # Статистика
        dbc.Row([
            dbc.Col([
                html.Span(id="checks-count", className="text-muted"),
            ]),
        ], className="mb-2"),
        
        # Таблица с AG Grid
        dag.AgGrid(
            id="checks-grid",
            columnDefs=[
                {
                    "field": "check_id", 
                    "headerName": "ID", 
                    "width": 80,
                    "pinned": "left",
                },
                {
                    "field": "check_name", 
                    "headerName": "Название",
                    "width": 250,
                    "cellRenderer": "CheckNameRenderer",
                },
                {
                    "field": "table_name", 
                    "headerName": "Таблица",
                    "width": 200,
                    "filter": True,
                },
                {
                    "field": "check_type_name", 
                    "headerName": "Тип",
                    "width": 150,
                    "filter": True,
                },
                {
                    "field": "domain", 
                    "headerName": "Домен",
                    "width": 120,
                    "filter": True,
                },
                {
                    "field": "owner", 
                    "headerName": "Владелец",
                    "width": 120,
                },
                {
                    "field": "schedule_main_value", 
                    "headerName": "Расписание",
                    "width": 100,
                    "cellRenderer": "ScheduleRenderer",
                },
                {
                    "field": "last_status", 
                    "headerName": "Статус",
                    "width": 100,
                    "cellRenderer": "StatusRenderer",
                },
                {
                    "field": "is_active", 
                    "headerName": "Активна",
                    "width": 90,
                    "cellRenderer": "ActiveRenderer",
                },
                {
                    "field": "priority", 
                    "headerName": "Приоритет",
                    "width": 100,
                    "cellRenderer": "PriorityRenderer",
                },
                {
                    "field": "actions", 
                    "headerName": "Действия",
                    "width": 150,
                    "cellRenderer": "ActionsRenderer",
                    "pinned": "right",
                },
            ],
            defaultColDef={
                "sortable": True, 
                "resizable": True,
                "filter": True,
            },
            dashGridOptions={
                "pagination": True, 
                "paginationPageSize": 15,
                "rowSelection": "multiple",
                "animateRows": True,
            },
            style={"height": "600px"},
            className="ag-theme-alpine",
        ),
        
        # Модальное окно создания проверки
        dbc.Modal([
            dbc.ModalHeader(dbc.ModalTitle("Создание новой проверки")),
            dbc.ModalBody([
                dbc.Form([
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Название проверки"),
                            dbc.Input(id="new-check-name", placeholder="check_table_name_type"),
                        ], width=6),
                        dbc.Col([
                            dbc.Label("Тип проверки"),
                            dbc.Select(
                                id="new-check-type",
                                options=[
                                    {"label": ct["check_type_name"], "value": ct["check_type_id"]}
                                    for ct in MOCK_CHECK_TYPES.to_dict("records")
                                ],
                            ),
                        ], width=6),
                    ], className="mb-3"),
                    
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Схема.Таблица"),
                            dbc.Input(id="new-check-table", placeholder="dwh.f_transactions"),
                        ], width=6),
                        dbc.Col([
                            dbc.Label("Домен"),
                            dbc.Select(
                                id="new-check-domain",
                                options=[{"label": d, "value": d} for d in DOMAINS],
                            ),
                        ], width=6),
                    ], className="mb-3"),
                    
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Расписание"),
                            dbc.Select(
                                id="new-check-schedule",
                                options=[
                                    {"label": "Ежедневно", "value": "daily"},
                                    {"label": "Ежечасно", "value": "hourly"},
                                    {"label": "Еженедельно", "value": "weekly"},
                                    {"label": "Ежемесячно", "value": "monthly"},
                                ],
                            ),
                        ], width=4),
                        dbc.Col([
                            dbc.Label("Приоритет"),
                            dbc.Select(
                                id="new-check-priority",
                                options=[
                                    {"label": "Высокий", "value": "HIGH"},
                                    {"label": "Средний", "value": "MEDIUM"},
                                    {"label": "Низкий", "value": "LOW"},
                                ],
                            ),
                        ], width=4),
                        dbc.Col([
                            dbc.Label("Владелец"),
                            dbc.Select(
                                id="new-check-owner",
                                options=[{"label": o, "value": o} for o in OWNERS],
                            ),
                        ], width=4),
                    ], className="mb-3"),
                    
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Описание"),
                            dbc.Textarea(
                                id="new-check-description",
                                placeholder="Описание проверки...",
                                rows=2,
                            ),
                        ]),
                    ], className="mb-3"),
                    
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("SQL-скрипт проверки"),
                            dbc.Textarea(
                                id="new-check-sql",
                                placeholder="SELECT COUNT(*) FROM ...",
                                rows=6,
                                style={"fontFamily": "monospace", "fontSize": "0.9em"},
                            ),
                        ]),
                    ], className="mb-3"),
                ]),
            ]),
            dbc.ModalFooter([
                dbc.Button("Отмена", id="btn-cancel-create", color="secondary", outline=True),
                dbc.Button([
                    html.I(className="fas fa-save me-2"),
                    "Сохранить"
                ], id="btn-save-check", color="primary"),
            ]),
        ], id="modal-create-check", size="lg", is_open=False),
        
        # Toast для уведомлений
        dbc.Toast(
            id="toast-notification",
            header="Уведомление",
            is_open=False,
            dismissable=True,
            duration=4000,
            icon="success",
            style={"position": "fixed", "top": 66, "right": 10, "width": 350},
        ),
        
    ], fluid=True, className="py-3")


@callback(
    [Output("checks-grid", "rowData"),
     Output("checks-count", "children")],
    [Input("search-checks", "value"),
     Input("filter-status", "value"),
     Input("filter-type", "value"),
     Input("filter-domain", "value")]
)
def update_checks_table(search, status, check_type, domain):
    df = MOCK_CHECKS.copy()
    
    # Применяем фильтры
    if search:
        search = search.lower()
        df = df[
            df["check_name"].str.lower().str.contains(search, na=False) |
            df["table_name"].str.lower().str.contains(search, na=False)
        ]
    
    if status:
        df = df[df["last_status"] == status]
    
    if check_type:
        df = df[df["check_type_name"] == check_type]
    
    if domain:
        df = df[df["domain"] == domain]
    
    count_text = f"Найдено проверок: {len(df)}"
    
    return df.to_dict("records"), count_text


@callback(
    [Output("search-checks", "value"),
     Output("filter-status", "value", allow_duplicate=True),
     Output("filter-type", "value", allow_duplicate=True),
     Output("filter-domain", "value", allow_duplicate=True)],
    Input("btn-reset-filters", "n_clicks"),
    prevent_initial_call=True
)
def reset_filters(n_clicks):
    return "", "", "", ""


@callback(
    Output("modal-create-check", "is_open"),
    [Input("btn-create-check", "n_clicks"),
     Input("btn-cancel-create", "n_clicks"),
     Input("btn-save-check", "n_clicks")],
    State("modal-create-check", "is_open"),
    prevent_initial_call=True
)
def toggle_modal(n_create, n_cancel, n_save, is_open):
    return not is_open


@callback(
    [Output("toast-notification", "is_open"),
     Output("toast-notification", "children"),
     Output("toast-notification", "header"),
     Output("toast-notification", "icon")],
    Input("btn-save-check", "n_clicks"),
    [State("new-check-name", "value"),
     State("new-check-table", "value")],
    prevent_initial_call=True
)
def save_check(n_clicks, name, table):
    if n_clicks:
        if name and table:
            return True, f"Проверка '{name}' успешно создана!", "Успех", "success"
        else:
            return True, "Заполните обязательные поля", "Ошибка", "danger"
    return False, "", "", ""
