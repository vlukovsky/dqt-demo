"""
Страница списка проверок
"""
import dash
from dash import html, dcc, callback, Input, Output, State, ctx
import dash_bootstrap_components as dbc
import dash_ag_grid as dag
from mock_data import MOCK_CHECKS, MOCK_CHECK_TYPES, DOMAINS, OWNERS, TABLES

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
                    ], width=3),
                    dbc.Col([
                        dbc.Select(
                            id="filter-status",
                            options=[
                                {"label": "Все статусы", "value": ""},
                                {"label": "OK", "value": "OK"},
                                {"label": "FAIL", "value": "FAIL"},
                                {"label": "ERROR", "value": "ERROR"},
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
                        dbc.Select(
                            id="filter-owner",
                            options=[{"label": "Все владельцы", "value": ""}] + [
                                {"label": o, "value": o} for o in OWNERS
                            ],
                            value="",
                        ),
                    ], width=2),
                    dbc.Col([
                        dbc.Button([
                            html.I(className="fas fa-filter-circle-xmark me-1"),
                            "Сбросить"
                        ], id="btn-reset-filters", color="outline-secondary", size="sm"),
                    ], width=1, className="text-end"),
                ], className="g-2"),
            ]),
        ], className="mb-3 shadow-sm"),
        
        # Статистика и массовые действия
        dbc.Row([
            dbc.Col([
                html.Span(id="checks-count", className="text-muted"),
            ], width=6),
            dbc.Col([
                # Панель массовых действий (скрыта по умолчанию)
                html.Div([
                    html.Span(id="selected-count", className="text-primary me-3"),
                    dbc.ButtonGroup([
                        dbc.Button([
                            html.I(className="fas fa-play me-1"),
                            "Запустить"
                        ], id="btn-bulk-run", color="success", size="sm", outline=True),
                        dbc.Button([
                            html.I(className="fas fa-toggle-on me-1"),
                            "Включить"
                        ], id="btn-bulk-enable", color="primary", size="sm", outline=True),
                        dbc.Button([
                            html.I(className="fas fa-toggle-off me-1"),
                            "Выключить"
                        ], id="btn-bulk-disable", color="secondary", size="sm", outline=True),
                        dbc.Button([
                            html.I(className="fas fa-trash me-1"),
                            "Удалить"
                        ], id="btn-bulk-delete", color="danger", size="sm", outline=True),
                    ], size="sm"),
                ], id="bulk-actions-panel", style={"display": "none"}),
            ], width=6, className="text-end"),
        ], className="mb-2 align-items-center"),
        
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
                    "width": 100,
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
                "getRowId": {"function": "params => params.data.check_id"},
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
                            dcc.Dropdown(
                                id="new-check-table",
                                options=[{"label": t, "value": t} for t in TABLES],
                                placeholder="Начните вводить название таблицы...",
                                searchable=True,
                                clearable=True,
                                style={"fontSize": "0.9em"},
                            ),
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
                            dbc.Label("Threshold (допустимый % ошибок)"),
                            dbc.InputGroup([
                                dbc.Input(
                                    id="new-check-threshold",
                                    type="number",
                                    min=0,
                                    max=100,
                                    step=0.1,
                                    value=0,
                                ),
                                dbc.InputGroupText("%"),
                            ]),
                        ], width=4),
                        dbc.Col([
                            dbc.Label("Описание"),
                            dbc.Input(
                                id="new-check-description",
                                placeholder="Краткое описание проверки...",
                            ),
                        ], width=8),
                    ], className="mb-3"),
                    
                    dbc.Row([
                        dbc.Col([
                            dbc.Label([
                                "SQL-скрипт проверки",
                                dbc.Button([
                                    html.I(className="fas fa-magic me-1"),
                                    "Сгенерировать"
                                ], id="btn-generate-sql", color="link", size="sm", className="ms-2 p-0"),
                            ]),
                            dbc.Textarea(
                                id="new-check-sql",
                                placeholder="SELECT COUNT(*) FROM ... или нажмите 'Сгенерировать'",
                                rows=8,
                                style={"fontFamily": "monospace", "fontSize": "0.85em"},
                            ),
                        ]),
                    ], className="mb-3"),
                ]),
            ]),
            dbc.ModalFooter([
                dbc.Button("Отмена", id="btn-cancel-create", color="secondary", outline=True),
                dbc.Button([
                    html.I(className="fas fa-play me-2"),
                    "Тест SQL"
                ], id="btn-test-sql", color="outline-info", className="me-2"),
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
     Input("filter-domain", "value"),
     Input("filter-owner", "value")]
)
def update_checks_table(search, status, check_type, domain, owner):
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
    
    if owner:
        df = df[df["owner"] == owner]
    
    count_text = f"Найдено проверок: {len(df)}"
    
    return df.to_dict("records"), count_text


@callback(
    [Output("search-checks", "value"),
     Output("filter-status", "value", allow_duplicate=True),
     Output("filter-type", "value", allow_duplicate=True),
     Output("filter-domain", "value", allow_duplicate=True),
     Output("filter-owner", "value", allow_duplicate=True)],
    Input("btn-reset-filters", "n_clicks"),
    prevent_initial_call=True
)
def reset_filters(n_clicks):
    return "", "", "", "", ""


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
    [Input("btn-save-check", "n_clicks"),
     Input("checks-grid", "cellClicked")],
    [State("new-check-name", "value"),
     State("new-check-table", "value")],
    prevent_initial_call=True
)
def handle_actions(n_clicks, cell_clicked, name, table):
    triggered = ctx.triggered_id
    
    # Обработка сохранения проверки
    if triggered == "btn-save-check" and n_clicks:
        if name and table:
            return True, f"Проверка '{name}' успешно создана!", "Успех", "success"
        else:
            return True, "Заполните обязательные поля", "Ошибка", "danger"
    
    # Обработка клика по ячейке таблицы
    if triggered == "checks-grid" and cell_clicked:
        col_id = cell_clicked.get("colId", "")
        row_data = cell_clicked.get("value", {})
        check_id = cell_clicked.get("rowId", "")
        
        if col_id == "is_active":
            # Toggle active status
            current_status = cell_clicked.get("value", False)
            new_status = "выключена" if current_status else "включена"
            return True, f"Проверка #{check_id} {new_status}", "Статус изменён", "success"
        
        if col_id == "actions":
            # Действия обрабатываются через отдельные кнопки
            return True, f"Действие для проверки #{check_id}", "Действие", "info"
    
    return False, "", "", ""


@callback(
    [Output("bulk-actions-panel", "style"),
     Output("selected-count", "children")],
    Input("checks-grid", "selectedRows"),
    prevent_initial_call=True
)
def toggle_bulk_actions(selected_rows):
    if selected_rows and len(selected_rows) > 0:
        count = len(selected_rows)
        return {"display": "inline-flex", "alignItems": "center"}, f"Выбрано: {count}"
    return {"display": "none"}, ""


@callback(
    [Output("toast-notification", "is_open", allow_duplicate=True),
     Output("toast-notification", "children", allow_duplicate=True),
     Output("toast-notification", "header", allow_duplicate=True),
     Output("toast-notification", "icon", allow_duplicate=True)],
    [Input("btn-bulk-run", "n_clicks"),
     Input("btn-bulk-enable", "n_clicks"),
     Input("btn-bulk-disable", "n_clicks"),
     Input("btn-bulk-delete", "n_clicks")],
    State("checks-grid", "selectedRows"),
    prevent_initial_call=True
)
def handle_bulk_actions(n_run, n_enable, n_disable, n_delete, selected_rows):
    if not selected_rows:
        return False, "", "", ""
    
    triggered = ctx.triggered_id
    count = len(selected_rows)
    check_ids = [row["check_id"] for row in selected_rows]
    
    if triggered == "btn-bulk-run":
        return True, f"Запущено {count} проверок: {check_ids}", "Массовый запуск", "success"
    elif triggered == "btn-bulk-enable":
        return True, f"Включено {count} проверок", "Массовое включение", "success"
    elif triggered == "btn-bulk-disable":
        return True, f"Выключено {count} проверок", "Массовое выключение", "warning"
    elif triggered == "btn-bulk-delete":
        return True, f"Удалено {count} проверок", "Массовое удаление", "danger"
    
    return False, "", "", ""


# Шаблоны SQL для разных типов проверок
SQL_TEMPLATES = {
    1: """-- Проверка полноты данных
SELECT 
    COUNT(*) as total_rows,
    SUM(CASE WHEN important_field IS NULL THEN 1 ELSE 0 END) as null_count,
    ROUND(100.0 * SUM(CASE WHEN important_field IS NULL THEN 1 ELSE 0 END) / NULLIF(COUNT(*), 0), 2) as null_pct
FROM {table}
WHERE load_date = CURRENT_DATE - 1;""",
    
    2: """-- Проверка уникальности
SELECT 
    business_key,
    COUNT(*) as duplicate_count
FROM {table}
WHERE load_date = CURRENT_DATE - 1
GROUP BY business_key
HAVING COUNT(*) > 1;""",
    
    3: """-- Проверка актуальности данных
SELECT 
    MAX(load_date) as last_load_date,
    CURRENT_DATE - MAX(load_date) as days_since_load
FROM {table}
HAVING CURRENT_DATE - MAX(load_date) > 1;""",
    
    4: """-- Проверка согласованности (referential integrity)
SELECT 
    a.foreign_key_id,
    COUNT(*) as orphan_count
FROM {table} a
LEFT JOIN dwh.d_reference b ON a.foreign_key_id = b.id
WHERE b.id IS NULL
  AND a.load_date = CURRENT_DATE - 1
GROUP BY a.foreign_key_id;""",
    
    5: """-- Проверка корректности формата
SELECT 
    id,
    email_field
FROM {table}
WHERE email_field !~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{{2,}}$'
  AND load_date = CURRENT_DATE - 1;""",
    
    6: """-- Бизнес-правило
SELECT 
    id,
    amount,
    transaction_type
FROM {table}
WHERE amount < 0
  AND transaction_type = 'CREDIT'
  AND load_date = CURRENT_DATE - 1;""",
}


@callback(
    Output("new-check-sql", "value"),
    Input("btn-generate-sql", "n_clicks"),
    [State("new-check-type", "value"),
     State("new-check-table", "value")],
    prevent_initial_call=True
)
def generate_sql(n_clicks, check_type, table):
    if not n_clicks:
        return dash.no_update
    
    if not check_type or not table:
        return "-- Выберите тип проверки и таблицу для генерации SQL"
    
    template = SQL_TEMPLATES.get(int(check_type), "-- Шаблон не найден")
    return template.format(table=table)


@callback(
    [Output("toast-notification", "is_open", allow_duplicate=True),
     Output("toast-notification", "children", allow_duplicate=True),
     Output("toast-notification", "header", allow_duplicate=True),
     Output("toast-notification", "icon", allow_duplicate=True)],
    Input("btn-test-sql", "n_clicks"),
    State("new-check-sql", "value"),
    prevent_initial_call=True
)
def test_sql(n_clicks, sql):
    if n_clicks and sql:
        # В демо просто показываем успех
        return True, "SQL-скрипт валиден (демо-режим)", "Тест SQL", "success"
    return False, "", "", ""
