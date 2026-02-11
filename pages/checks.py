"""
Страница списка проверок
"""
import dash
from dash import html, dcc, callback, Input, Output, State, ctx, ALL, MATCH, ClientsideFunction
import dash_bootstrap_components as dbc
import dash_ag_grid as dag
from mock_data import MOCK_CHECKS, MOCK_CHECK_TYPES, DOMAINS, OWNERS, TABLES, SCHEMAS, TABLES_BY_SCHEMA

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
                                type="search",
                            ),
                        ]),
                    ], width=3),
                    dbc.Col([
                        dcc.Dropdown(
                            id="filter-status",
                            options=[
                                {"label": "Все статусы", "value": ""},
                                {"label": "OK", "value": "OK"},
                                {"label": "FAIL", "value": "FAIL"},
                                {"label": "ERROR", "value": "ERROR"},
                            ],
                            value="",
                            placeholder="Статус...",
                            searchable=True,
                            clearable=False,
                            style={"fontSize": "0.9em"},
                        ),
                    ], width=2),
                    dbc.Col([
                        dcc.Dropdown(
                            id="filter-type",
                            options=[{"label": "Все типы", "value": ""}] + [
                                {"label": ct["check_type_name"], "value": ct["check_type_name"]}
                                for ct in MOCK_CHECK_TYPES.to_dict("records")
                            ],
                            value="",
                            placeholder="Тип...",
                            searchable=True,
                            clearable=False,
                            style={"fontSize": "0.9em"},
                        ),
                    ], width=2),
                    dbc.Col([
                        dcc.Dropdown(
                            id="filter-domain",
                            options=[{"label": "Все домены", "value": ""}] + [
                                {"label": d, "value": d} for d in DOMAINS
                            ],
                            value="",
                            placeholder="Домен...",
                            searchable=True,
                            clearable=False,
                            style={"fontSize": "0.9em"},
                        ),
                    ], width=2),
                    dbc.Col([
                        dcc.Dropdown(
                            id="filter-owner",
                            options=[{"label": "Все владельцы", "value": ""}] + [
                                {"label": o, "value": o} for o in OWNERS
                            ],
                            value="",
                            placeholder="Владелец...",
                            searchable=True,
                            clearable=False,
                            style={"fontSize": "0.9em"},
                        ),
                    ], width=2),
                    dbc.Col([
                        dbc.Button([
                            html.I(className="fas fa-filter-circle-xmark me-1"),
                            "Сбросить"
                        ], id="btn-reset-filters", color="outline-secondary", size="sm"),
                    ], width=1, className="text-end"),
                ], className="g-2"),
                dbc.Row([
                    dbc.Col([
                        dbc.Label("Схема", className="small"),
                        dcc.Dropdown(
                            id="filter-check-schema",
                            options=[{"label": "Все схемы", "value": ""}] + [
                                {"label": s, "value": s} for s in SCHEMAS
                            ],
                            value="",
                            placeholder="Схема...",
                            searchable=True,
                            clearable=False,
                            style={"fontSize": "0.9em"},
                        ),
                    ], width=2),
                    dbc.Col([
                        dbc.Label("Таблица", className="small"),
                        dcc.Dropdown(
                            id="filter-check-table",
                            options=[],
                            value="",
                            placeholder="Сначала выберите схему...",
                            searchable=True,
                            clearable=False,
                            disabled=True,
                            style={"fontSize": "0.9em"},
                        ),
                    ], width=2),
                    dbc.Col([
                        # Сохранённые фильтры
                        dbc.Label("Мои фильтры", className="small"),
                        dbc.InputGroup([
                            dcc.Dropdown(
                                id="saved-filter-select",
                                options=[],
                                placeholder="Выбрать фильтр...",
                                searchable=True,
                                clearable=True,
                                style={"fontSize": "0.9em", "flex": "1"},
                            ),
                            dbc.Button(
                                html.I(className="fas fa-save"),
                                id="btn-save-filter",
                                color="outline-primary",
                                size="sm",
                                title="Сохранить текущий фильтр",
                            ),
                        ], size="sm"),
                    ], width=3),
                ], className="g-2 mt-2"),
            ]),
        ], className="mb-3 shadow-sm"),
        
        # Статистика и массовые действия
        dbc.Row([
            dbc.Col([
                html.Span(id="checks-count", className="text-muted"),
            ], width=4),
            dbc.Col([
                # Панель массовых действий
                html.Div([
                    html.Span(id="selected-count", className="text-primary me-3 fw-bold"),
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
                            html.I(className="fas fa-clock me-1"),
                            "Выкл. на период"
                        ], id="btn-bulk-disable-period", color="warning", size="sm", outline=True,
                           title="Выключить выбранные проверки на определённый период"),
                        dbc.Button([
                            html.I(className="fas fa-calendar-check me-1"),
                            "Вкл. на период"
                        ], id="btn-bulk-enable-period", color="info", size="sm", outline=True,
                           title="Включить выбранные проверки на определённый период"),
                        dbc.Button([
                            html.I(className="fas fa-trash me-1"),
                            "Удалить"
                        ], id="btn-bulk-delete", color="danger", size="sm", outline=True),
                    ], size="sm"),
                ], id="bulk-actions-panel", style={"display": "none"}),
            ], width=8, className="text-end"),
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
                    "width": 180,
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
        _create_check_modal("modal-create-check", "Создание новой проверки", "new"),
        
        # Модальное окно редактирования проверки
        _create_check_modal("modal-edit-check", "Редактирование проверки", "edit"),
        
        # Модальное окно для периода (выключить на период)
        dbc.Modal([
            dbc.ModalHeader(dbc.ModalTitle(id="period-modal-title")),
            dbc.ModalBody([
                html.P(id="period-modal-text"),
                dbc.Form([
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Дата начала"),
                            dbc.Input(id="period-start-date", type="date"),
                        ], width=6),
                        dbc.Col([
                            dbc.Label("Дата окончания"),
                            dbc.Input(id="period-end-date", type="date"),
                        ], width=6),
                    ], className="mb-3"),
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Причина"),
                            dbc.Textarea(id="period-reason", placeholder="Укажите причину...", rows=2),
                        ]),
                    ]),
                ]),
            ]),
            dbc.ModalFooter([
                dbc.Button("Отмена", id="btn-cancel-period", color="secondary", outline=True),
                dbc.Button([
                    html.I(className="fas fa-check me-2"),
                    "Применить"
                ], id="btn-apply-period", color="primary"),
            ]),
        ], id="modal-period", size="md", is_open=False),
        
        # Модальное окно сохранения фильтра
        dbc.Modal([
            dbc.ModalHeader(dbc.ModalTitle("Сохранить фильтр")),
            dbc.ModalBody([
                dbc.Label("Название фильтра"),
                dbc.Input(id="save-filter-name", placeholder="Мой фильтр..."),
            ]),
            dbc.ModalFooter([
                dbc.Button("Отмена", id="btn-cancel-save-filter", color="secondary", outline=True),
                dbc.Button("Сохранить", id="btn-confirm-save-filter", color="primary"),
            ]),
        ], id="modal-save-filter", size="sm", is_open=False),
        
        # Store для хранения данных редактируемой проверки
        dcc.Store(id="edit-check-data", data=None),
        # Store для типа действия с периодом (disable/enable)
        dcc.Store(id="period-action-type", data="disable"),
        
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
        
        # Tooltips
        dbc.Tooltip("Нажмите для поиска в реальном времени. Результаты обновляются при вводе.",
                    target="search-checks", placement="bottom"),
        dbc.Tooltip("Сохраните текущий набор фильтров для быстрого применения в будущем",
                    target="btn-save-filter", placement="top"),
        
    ], fluid=True, className="py-3")


def _create_check_modal(modal_id, title, prefix):
    """Создание модального окна для создания/редактирования проверки."""
    return dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle(title)),
        dbc.ModalBody([
            dbc.Form([
                dbc.Row([
                    dbc.Col([
                        dbc.Label("Название проверки"),
                        dbc.Input(id=f"{prefix}-check-name", placeholder="check_table_name_type"),
                    ], width=6),
                    dbc.Col([
                        dbc.Label("Тип проверки"),
                        dcc.Dropdown(
                            id=f"{prefix}-check-type",
                            options=[
                                {"label": ct["check_type_name"], "value": ct["check_type_id"]}
                                for ct in MOCK_CHECK_TYPES.to_dict("records")
                            ],
                            placeholder="Выберите тип...",
                            searchable=True,
                            clearable=True,
                            style={"fontSize": "0.9em"},
                        ),
                    ], width=6),
                ], className="mb-3"),
                
                dbc.Row([
                    dbc.Col([
                        dbc.Label("Схема"),
                        dcc.Dropdown(
                            id=f"{prefix}-check-schema",
                            options=[{"label": s, "value": s} for s in SCHEMAS],
                            placeholder="Выберите схему...",
                            searchable=True,
                            clearable=True,
                            style={"fontSize": "0.9em"},
                        ),
                    ], width=3),
                    dbc.Col([
                        dbc.Label("Таблица"),
                        dcc.Dropdown(
                            id=f"{prefix}-check-table",
                            options=[],
                            placeholder="Сначала выберите схему...",
                            searchable=True,
                            clearable=True,
                            disabled=True,
                            style={"fontSize": "0.9em"},
                        ),
                    ], width=3),
                    dbc.Col([
                        dbc.Label("Домен"),
                        dcc.Dropdown(
                            id=f"{prefix}-check-domain",
                            options=[{"label": d, "value": d} for d in DOMAINS],
                            placeholder="Выберите домен...",
                            searchable=True,
                            clearable=True,
                            style={"fontSize": "0.9em"},
                        ),
                    ], width=6),
                ], className="mb-3"),
                
                dbc.Row([
                    dbc.Col([
                        dbc.Label("Расписание"),
                        dcc.Dropdown(
                            id=f"{prefix}-check-schedule",
                            options=[
                                {"label": "Ежедневно", "value": "daily"},
                                {"label": "Ежечасно", "value": "hourly"},
                                {"label": "Еженедельно", "value": "weekly"},
                                {"label": "Ежемесячно", "value": "monthly"},
                            ],
                            placeholder="Выберите расписание...",
                            searchable=True,
                            clearable=True,
                            style={"fontSize": "0.9em"},
                        ),
                    ], width=4),
                    dbc.Col([
                        dbc.Label("Приоритет"),
                        dcc.Dropdown(
                            id=f"{prefix}-check-priority",
                            options=[
                                {"label": "Высокий", "value": "HIGH"},
                                {"label": "Средний", "value": "MEDIUM"},
                                {"label": "Низкий", "value": "LOW"},
                            ],
                            placeholder="Выберите приоритет...",
                            searchable=True,
                            clearable=True,
                            style={"fontSize": "0.9em"},
                        ),
                    ], width=4),
                    dbc.Col([
                        dbc.Label("Владелец"),
                        dcc.Dropdown(
                            id=f"{prefix}-check-owner",
                            options=[{"label": o, "value": o} for o in OWNERS],
                            placeholder="Выберите владельца...",
                            searchable=True,
                            clearable=True,
                            style={"fontSize": "0.9em"},
                        ),
                    ], width=4),
                ], className="mb-3"),
                
                dbc.Row([
                    dbc.Col([
                        dbc.Label("Threshold (допустимый % ошибок)"),
                        dbc.InputGroup([
                            dbc.Input(
                                id=f"{prefix}-check-threshold",
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
                            id=f"{prefix}-check-description",
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
                            ], id=f"btn-generate-sql-{prefix}", color="link", size="sm", className="ms-2 p-0"),
                        ]),
                        dbc.Textarea(
                            id=f"{prefix}-check-sql",
                            placeholder="SELECT COUNT(*) FROM ... или нажмите 'Сгенерировать'",
                            rows=8,
                            style={"fontFamily": "monospace", "fontSize": "0.85em"},
                        ),
                    ]),
                ], className="mb-3"),
            ]),
        ]),
        dbc.ModalFooter([
            dbc.Button("Отмена", id=f"btn-cancel-{prefix}", color="secondary", outline=True),
            dbc.Button([
                html.I(className="fas fa-play me-2"),
                "Тест SQL"
            ], id=f"btn-test-sql-{prefix}", color="outline-info", className="me-2"),
            dbc.Button([
                html.I(className="fas fa-save me-2"),
                "Сохранить"
            ], id=f"btn-save-{prefix}", color="primary"),
        ]),
    ], id=modal_id, size="lg", is_open=False)


# ============================================================
# Callbacks для фильтров таблиц (форма создания)
# ============================================================
@callback(
    [Output("new-check-table", "options"),
     Output("new-check-table", "disabled"),
     Output("new-check-table", "value")],
    Input("new-check-schema", "value")
)
def update_tables_dropdown(schema):
    if not schema:
        return [], True, None
    tables = TABLES_BY_SCHEMA.get(schema, [])
    options = [{"label": t, "value": t} for t in tables]
    return options, False, None


@callback(
    [Output("edit-check-table", "options"),
     Output("edit-check-table", "disabled"),
     Output("edit-check-table", "value")],
    Input("edit-check-schema", "value"),
    State("edit-check-data", "data"),
)
def update_edit_tables_dropdown(schema, edit_data):
    if not schema:
        return [], True, None
    tables = TABLES_BY_SCHEMA.get(schema, [])
    options = [{"label": t, "value": t} for t in tables]
    # Если это начальная загрузка с данными проверки, подставить текущую таблицу
    current_table = None
    if edit_data and edit_data.get("schema_name") == schema:
        tbl = edit_data.get("table_name", "")
        if "." in tbl:
            current_table = tbl.split(".", 1)[1]
    return options, False, current_table


@callback(
    [Output("filter-check-table", "options"),
     Output("filter-check-table", "disabled"),
     Output("filter-check-table", "value")],
    Input("filter-check-schema", "value")
)
def update_filter_tables_dropdown(schema):
    if not schema:
        return [{"label": "Все", "value": ""}], True, ""
    tables = TABLES_BY_SCHEMA.get(schema, [])
    options = [{"label": "Все", "value": ""}] + [{"label": t, "value": t} for t in tables]
    return options, False, ""


# ============================================================
# Основной callback фильтрации таблицы
# ============================================================
@callback(
    [Output("checks-grid", "rowData"),
     Output("checks-count", "children")],
    [Input("search-checks", "value"),
     Input("filter-status", "value"),
     Input("filter-type", "value"),
     Input("filter-domain", "value"),
     Input("filter-owner", "value"),
     Input("filter-check-schema", "value"),
     Input("filter-check-table", "value")]
)
def update_checks_table(search, status, check_type, domain, owner, schema, table):
    df = MOCK_CHECKS.copy()
    
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
    if schema and table:
        full_table = f"{schema}.{table}"
        df = df[df["table_name"] == full_table]
    elif schema:
        df = df[df["table_name"].str.startswith(f"{schema}.")]
    
    count_text = f"Найдено проверок: {len(df)}"
    return df.to_dict("records"), count_text


# ============================================================
# Сброс фильтров
# ============================================================
@callback(
    [Output("search-checks", "value"),
     Output("filter-status", "value", allow_duplicate=True),
     Output("filter-type", "value", allow_duplicate=True),
     Output("filter-domain", "value", allow_duplicate=True),
     Output("filter-owner", "value", allow_duplicate=True),
     Output("filter-check-schema", "value", allow_duplicate=True),
     Output("filter-check-table", "value", allow_duplicate=True)],
    Input("btn-reset-filters", "n_clicks"),
    prevent_initial_call=True
)
def reset_filters(n_clicks):
    return "", "", "", "", "", "", ""


# ============================================================
# Модальное окно создания проверки
# ============================================================
@callback(
    Output("modal-create-check", "is_open"),
    [Input("btn-create-check", "n_clicks"),
     Input("btn-cancel-new", "n_clicks"),
     Input("btn-save-new", "n_clicks")],
    State("modal-create-check", "is_open"),
    prevent_initial_call=True
)
def toggle_create_modal(n_create, n_cancel, n_save, is_open):
    return not is_open


# ============================================================
# Модальное окно редактирования проверки
# ============================================================
@callback(
    [Output("modal-edit-check", "is_open"),
     Output("edit-check-data", "data"),
     Output("edit-check-name", "value"),
     Output("edit-check-type", "value"),
     Output("edit-check-schema", "value"),
     Output("edit-check-domain", "value"),
     Output("edit-check-schedule", "value"),
     Output("edit-check-priority", "value"),
     Output("edit-check-owner", "value"),
     Output("edit-check-threshold", "value"),
     Output("edit-check-description", "value"),
     Output("edit-check-sql", "value")],
    [Input("checks-grid", "cellClicked"),
     Input("btn-cancel-edit", "n_clicks"),
     Input("btn-save-edit", "n_clicks")],
    State("modal-edit-check", "is_open"),
    prevent_initial_call=True
)
def toggle_edit_modal(cell_clicked, n_cancel, n_save, is_open):
    triggered = ctx.triggered_id
    
    if triggered == "btn-cancel-edit" or triggered == "btn-save-edit":
        return False, None, "", None, None, None, None, None, None, 0, "", ""
    
    if triggered == "checks-grid" and cell_clicked:
        col_id = cell_clicked.get("colId", "")
        if col_id == "actions":
            # Получаем данные строки
            row_id = cell_clicked.get("rowId", "")
            if row_id:
                check = MOCK_CHECKS[MOCK_CHECKS["check_id"] == int(row_id)]
                if not check.empty:
                    c = check.iloc[0]
                    schema_name = c["table_name"].split(".")[0] if "." in c["table_name"] else ""
                    return (
                        True,
                        c.to_dict(),
                        c["check_name"],
                        c["check_type_id"],
                        schema_name,
                        c["domain"],
                        c["schedule_main_value"],
                        c["priority"],
                        c["owner"],
                        c["threshold"] * 100,
                        c["description"],
                        c["sql_script"],
                    )
    
    return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update


# ============================================================
# Уведомления при создании/редактировании/действиях
# ============================================================
@callback(
    [Output("toast-notification", "is_open"),
     Output("toast-notification", "children"),
     Output("toast-notification", "header"),
     Output("toast-notification", "icon")],
    [Input("btn-save-new", "n_clicks"),
     Input("btn-save-edit", "n_clicks"),
     Input("checks-grid", "cellClicked")],
    [State("new-check-name", "value"),
     State("new-check-table", "value"),
     State("edit-check-name", "value")],
    prevent_initial_call=True
)
def handle_actions(n_save_new, n_save_edit, cell_clicked, new_name, new_table, edit_name):
    triggered = ctx.triggered_id
    
    if triggered == "btn-save-new" and n_save_new:
        if new_name and new_table:
            return True, f"Проверка '{new_name}' успешно создана!", "Успех", "success"
        else:
            return True, "Заполните обязательные поля (название, таблица)", "Ошибка", "danger"
    
    if triggered == "btn-save-edit" and n_save_edit:
        if edit_name:
            return True, f"Проверка '{edit_name}' успешно обновлена!", "Успех", "success"
        else:
            return True, "Заполните обязательные поля", "Ошибка", "danger"
    
    if triggered == "checks-grid" and cell_clicked:
        col_id = cell_clicked.get("colId", "")
        check_id = cell_clicked.get("rowId", "")
        
        if col_id == "is_active":
            current_status = cell_clicked.get("value", False)
            new_status = "выключена" if current_status else "включена"
            return True, f"Проверка #{check_id} {new_status}", "Статус изменён", "success"
    
    return False, "", "", ""


# ============================================================
# Панель массовых действий (bulk) с исправленным счётчиком
# ============================================================
@callback(
    [Output("bulk-actions-panel", "style"),
     Output("selected-count", "children")],
    Input("checks-grid", "selectedRows"),
)
def toggle_bulk_actions(selected_rows):
    if selected_rows and len(selected_rows) > 0:
        count = len(selected_rows)
        return {"display": "inline-flex", "alignItems": "center", "gap": "8px", "flexWrap": "wrap"}, f"Выбрано: {count}"
    return {"display": "none"}, ""


# ============================================================
# Обработка массовых действий
# ============================================================
@callback(
    [Output("toast-notification", "is_open", allow_duplicate=True),
     Output("toast-notification", "children", allow_duplicate=True),
     Output("toast-notification", "header", allow_duplicate=True),
     Output("toast-notification", "icon", allow_duplicate=True)],
    [Input("btn-bulk-run", "n_clicks"),
     Input("btn-bulk-enable", "n_clicks"),
     Input("btn-bulk-disable", "n_clicks"),
     Input("btn-bulk-delete", "n_clicks"),
     Input("btn-apply-period", "n_clicks")],
    [State("checks-grid", "selectedRows"),
     State("period-action-type", "data"),
     State("period-start-date", "value"),
     State("period-end-date", "value"),
     State("period-reason", "value")],
    prevent_initial_call=True
)
def handle_bulk_actions(n_run, n_enable, n_disable, n_delete, n_period,
                        selected_rows, period_action, period_start, period_end, period_reason):
    triggered = ctx.triggered_id
    
    if triggered == "btn-apply-period":
        count = len(selected_rows) if selected_rows else 0
        action_text = "выключены" if period_action == "disable" else "включены"
        period_text = f"с {period_start} по {period_end}" if period_start and period_end else "на указанный период"
        return True, f"{count} проверок {action_text} {period_text}. Причина: {period_reason or 'не указана'}", "Период установлен", "success"
    
    if not selected_rows:
        return False, "", "", ""
    
    count = len(selected_rows)
    check_ids = [row["check_id"] for row in selected_rows]
    
    if triggered == "btn-bulk-run":
        check_names = [row["check_name"] for row in selected_rows[:3]]
        names_text = ", ".join(check_names)
        if count > 3:
            names_text += f" и ещё {count - 3}"
        msg = html.Div([
            html.P(f"Запущено {count} проверок. Проверки поставлены в очередь.", className="mb-2"),
            html.Div([
                html.Small("Очередь: ", className="text-muted"),
                html.Small(names_text),
            ], className="mb-1"),
            dbc.Progress(value=0, id="bulk-run-progress", striped=True, animated=True,
                         color="success", className="mt-2", style={"height": "6px"}),
            html.Small("Приоритет: высокий (мультизапуск)", className="text-muted"),
        ])
        return True, msg, "Массовый запуск", "success"
    elif triggered == "btn-bulk-enable":
        return True, f"Включено {count} проверок", "Массовое включение", "success"
    elif triggered == "btn-bulk-disable":
        return True, f"Выключено {count} проверок", "Массовое выключение", "warning"
    elif triggered == "btn-bulk-delete":
        return True, f"Удалено {count} проверок", "Массовое удаление", "danger"
    
    return False, "", "", ""


# ============================================================
# Модальное окно «Включить/Выключить на период»
# ============================================================
@callback(
    [Output("modal-period", "is_open"),
     Output("period-modal-title", "children"),
     Output("period-modal-text", "children"),
     Output("period-action-type", "data")],
    [Input("btn-bulk-disable-period", "n_clicks"),
     Input("btn-bulk-enable-period", "n_clicks"),
     Input("btn-cancel-period", "n_clicks"),
     Input("btn-apply-period", "n_clicks")],
    [State("modal-period", "is_open"),
     State("checks-grid", "selectedRows")],
    prevent_initial_call=True
)
def toggle_period_modal(n_disable, n_enable, n_cancel, n_apply, is_open, selected_rows):
    triggered = ctx.triggered_id
    count = len(selected_rows) if selected_rows else 0
    
    if triggered == "btn-cancel-period" or triggered == "btn-apply-period":
        return False, "", "", dash.no_update
    
    if triggered == "btn-bulk-disable-period":
        return True, "Выключить на период", f"Выключить {count} выбранных проверок на указанный период:", "disable"
    
    if triggered == "btn-bulk-enable-period":
        return True, "Включить на период", f"Включить {count} выбранных проверок на указанный период:", "enable"
    
    return False, "", "", dash.no_update


# ============================================================
# SQL генерация
# ============================================================
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
    Input("btn-generate-sql-new", "n_clicks"),
    [State("new-check-type", "value"),
     State("new-check-schema", "value"),
     State("new-check-table", "value")],
    prevent_initial_call=True
)
def generate_sql_new(n_clicks, check_type, schema, table):
    if not n_clicks:
        return dash.no_update
    if not check_type or not schema or not table:
        return "-- Выберите тип проверки, схему и таблицу для генерации SQL"
    full_table_name = f"{schema}.{table}"
    template = SQL_TEMPLATES.get(int(check_type), "-- Шаблон не найден")
    return template.format(table=full_table_name)


@callback(
    Output("edit-check-sql", "value", allow_duplicate=True),
    Input("btn-generate-sql-edit", "n_clicks"),
    [State("edit-check-type", "value"),
     State("edit-check-schema", "value"),
     State("edit-check-table", "value")],
    prevent_initial_call=True
)
def generate_sql_edit(n_clicks, check_type, schema, table):
    if not n_clicks:
        return dash.no_update
    if not check_type or not schema or not table:
        return "-- Выберите тип проверки, схему и таблицу для генерации SQL"
    full_table_name = f"{schema}.{table}"
    template = SQL_TEMPLATES.get(int(check_type), "-- Шаблон не найден")
    return template.format(table=full_table_name)


@callback(
    [Output("toast-notification", "is_open", allow_duplicate=True),
     Output("toast-notification", "children", allow_duplicate=True),
     Output("toast-notification", "header", allow_duplicate=True),
     Output("toast-notification", "icon", allow_duplicate=True)],
    [Input("btn-test-sql-new", "n_clicks"),
     Input("btn-test-sql-edit", "n_clicks")],
    [State("new-check-sql", "value"),
     State("edit-check-sql", "value")],
    prevent_initial_call=True
)
def test_sql(n_new, n_edit, new_sql, edit_sql):
    triggered = ctx.triggered_id
    sql = new_sql if triggered == "btn-test-sql-new" else edit_sql
    if sql:
        return True, "SQL-скрипт валиден (демо-режим)", "Тест SQL", "success"
    return True, "Введите SQL-скрипт для тестирования", "Ошибка", "danger"


# ============================================================
# Сохранение и загрузка фильтров
# ============================================================
@callback(
    Output("modal-save-filter", "is_open"),
    [Input("btn-save-filter", "n_clicks"),
     Input("btn-cancel-save-filter", "n_clicks"),
     Input("btn-confirm-save-filter", "n_clicks")],
    State("modal-save-filter", "is_open"),
    prevent_initial_call=True
)
def toggle_save_filter_modal(n_save, n_cancel, n_confirm, is_open):
    return not is_open


@callback(
    [Output("saved-filters-store", "data"),
     Output("saved-filter-select", "options")],
    Input("btn-confirm-save-filter", "n_clicks"),
    [State("save-filter-name", "value"),
     State("search-checks", "value"),
     State("filter-status", "value"),
     State("filter-type", "value"),
     State("filter-domain", "value"),
     State("filter-owner", "value"),
     State("filter-check-schema", "value"),
     State("filter-check-table", "value"),
     State("saved-filters-store", "data")],
    prevent_initial_call=True
)
def save_filter(n_clicks, name, search, status, ftype, domain, owner, schema, table, existing_filters):
    if not name:
        return dash.no_update, dash.no_update
    
    filters = existing_filters or []
    new_filter = {
        "name": name,
        "search": search or "",
        "status": status or "",
        "type": ftype or "",
        "domain": domain or "",
        "owner": owner or "",
        "schema": schema or "",
        "table": table or "",
    }
    filters.append(new_filter)
    options = [{"label": f["name"], "value": i} for i, f in enumerate(filters)]
    return filters, options


@callback(
    [Output("search-checks", "value", allow_duplicate=True),
     Output("filter-status", "value", allow_duplicate=True),
     Output("filter-type", "value", allow_duplicate=True),
     Output("filter-domain", "value", allow_duplicate=True),
     Output("filter-owner", "value", allow_duplicate=True),
     Output("filter-check-schema", "value", allow_duplicate=True)],
    Input("saved-filter-select", "value"),
    State("saved-filters-store", "data"),
    prevent_initial_call=True
)
def load_saved_filter(selected_idx, filters):
    if selected_idx is None or not filters:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update
    
    f = filters[selected_idx]
    return f["search"], f["status"], f["type"], f["domain"], f["owner"], f["schema"]
