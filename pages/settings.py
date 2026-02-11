"""
Страница настроек с CRUD для шаблонов автоматических проверок
"""
import dash
from dash import html, dcc, callback, Input, Output, State, ctx
import dash_bootstrap_components as dbc
import dash_ag_grid as dag
from mock_data import MOCK_CHECK_TEMPLATES, CHECK_TYPES, OWNERS

dash.register_page(__name__, path="/settings", name="Настройки")


def layout():
    # Данные шаблонов для AG Grid
    templates_data = []
    for t in MOCK_CHECK_TEMPLATES:
        templates_data.append({
            "template_id": t["template_id"],
            "name": t["name"],
            "check_type": t["check_type"],
            "description": t["description"],
            "parameters": ", ".join(t["parameters"]),
            "is_active": t["is_active"],
            "created_by": t["created_by"],
        })
    
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H2("Настройки", className="mb-0"),
                html.P("Управление конфигурацией системы", className="text-muted"),
            ], width=8),
        ], className="mb-4"),
        
        # Табы настроек
        dbc.Tabs([
            # Таб: Шаблоны проверок
            dbc.Tab([
                dbc.Row([
                    dbc.Col([
                        html.H5("Шаблоны автоматических проверок", className="mb-1"),
                        html.P("Создавайте и управляйте шаблонами SQL-проверок для быстрого применения к новым таблицам.",
                               className="text-muted small"),
                    ], width=8),
                    dbc.Col([
                        dbc.Button([
                            html.I(className="fas fa-plus me-2"),
                            "Создать шаблон"
                        ], id="btn-create-template", color="primary"),
                    ], width=4, className="text-end"),
                ], className="mt-3 mb-3"),
                
                dag.AgGrid(
                    id="templates-grid",
                    rowData=templates_data,
                    columnDefs=[
                        {"field": "template_id", "headerName": "ID", "width": 70},
                        {"field": "name", "headerName": "Название", "width": 200},
                        {"field": "check_type", "headerName": "Тип проверки", "width": 180},
                        {"field": "description", "headerName": "Описание", "width": 250},
                        {"field": "parameters", "headerName": "Параметры", "width": 180},
                        {"field": "is_active", "headerName": "Активен", "width": 100,
                         "cellRenderer": "ActiveRenderer"},
                        {"field": "created_by", "headerName": "Автор", "width": 120},
                    ],
                    defaultColDef={"sortable": True, "resizable": True, "filter": True},
                    dashGridOptions={"pagination": True, "paginationPageSize": 10,
                                     "rowSelection": "single", "animateRows": True},
                    style={"height": "350px"},
                    className="ag-theme-alpine",
                ),
                
                # Редактор шаблона (при выборе строки)
                html.Div(id="template-editor", className="mt-3"),
            ], label="Шаблоны проверок", tab_id="tab-templates"),
            
            # Таб: Пользователи и роли
            dbc.Tab([
                dbc.Card([
                    dbc.CardBody([
                        html.H5("Пользователи и роли", className="mb-3"),
                        html.P("Управление пользователями и назначение ролей.", className="text-muted"),
                        dbc.ListGroup([
                            dbc.ListGroupItem([
                                dbc.Row([
                                    dbc.Col([html.Strong("ivanov_a"), html.Small(" - Администратор", className="text-muted")], width=6),
                                    dbc.Col([dbc.Badge("admin", color="danger")], width=3),
                                    dbc.Col([dbc.Button("Изменить", size="sm", color="outline-primary")], width=3, className="text-end"),
                                ]),
                            ]),
                            dbc.ListGroupItem([
                                dbc.Row([
                                    dbc.Col([html.Strong("petrov_b"), html.Small(" - Редактор", className="text-muted")], width=6),
                                    dbc.Col([dbc.Badge("editor", color="primary")], width=3),
                                    dbc.Col([dbc.Button("Изменить", size="sm", color="outline-primary")], width=3, className="text-end"),
                                ]),
                            ]),
                            dbc.ListGroupItem([
                                dbc.Row([
                                    dbc.Col([html.Strong("sidorova_c"), html.Small(" - Наблюдатель", className="text-muted")], width=6),
                                    dbc.Col([dbc.Badge("viewer", color="secondary")], width=3),
                                    dbc.Col([dbc.Button("Изменить", size="sm", color="outline-primary")], width=3, className="text-end"),
                                ]),
                            ]),
                            dbc.ListGroupItem([
                                dbc.Row([
                                    dbc.Col([html.Strong("kozlov_d"), html.Small(" - Редактор", className="text-muted")], width=6),
                                    dbc.Col([dbc.Badge("editor", color="primary")], width=3),
                                    dbc.Col([dbc.Button("Изменить", size="sm", color="outline-primary")], width=3, className="text-end"),
                                ]),
                            ]),
                            dbc.ListGroupItem([
                                dbc.Row([
                                    dbc.Col([html.Strong("novikova_e"), html.Small(" - Наблюдатель", className="text-muted")], width=6),
                                    dbc.Col([dbc.Badge("viewer", color="secondary")], width=3),
                                    dbc.Col([dbc.Button("Изменить", size="sm", color="outline-primary")], width=3, className="text-end"),
                                ]),
                            ]),
                        ]),
                    ])
                ], className="mt-3")
            ], label="Пользователи и роли", tab_id="tab-users"),
            
            # Таб: Подключения
            dbc.Tab([
                dbc.Card([
                    dbc.CardBody([
                        html.H5("Подключения к источникам данных", className="mb-3"),
                        dbc.ListGroup([
                            dbc.ListGroupItem([
                                dbc.Row([
                                    dbc.Col([
                                        html.I(className="fas fa-database text-primary me-2"),
                                        html.Strong("Greenplum GP100"),
                                        html.Span(" - gp100.dwh.local:5432", className="text-muted ms-2"),
                                    ], width=7),
                                    dbc.Col([
                                        html.Span("●", className="text-success me-1"),
                                        html.Small("Подключено", className="text-success"),
                                    ], width=2),
                                    dbc.Col([dbc.Button("Настроить", size="sm", color="outline-primary")], width=3, className="text-end"),
                                ]),
                            ]),
                            dbc.ListGroupItem([
                                dbc.Row([
                                    dbc.Col([
                                        html.I(className="fas fa-database text-info me-2"),
                                        html.Strong("PostgreSQL PG226"),
                                        html.Span(" - pg226.meta.local:5432", className="text-muted ms-2"),
                                    ], width=7),
                                    dbc.Col([
                                        html.Span("●", className="text-success me-1"),
                                        html.Small("Подключено", className="text-success"),
                                    ], width=2),
                                    dbc.Col([dbc.Button("Настроить", size="sm", color="outline-primary")], width=3, className="text-end"),
                                ]),
                            ]),
                            dbc.ListGroupItem([
                                dbc.Row([
                                    dbc.Col([
                                        html.I(className="fas fa-cogs text-warning me-2"),
                                        html.Strong("Airflow"),
                                        html.Span(" - airflow.internal:8080", className="text-muted ms-2"),
                                    ], width=7),
                                    dbc.Col([
                                        html.Span("●", className="text-success me-1"),
                                        html.Small("Подключено", className="text-success"),
                                    ], width=2),
                                    dbc.Col([dbc.Button("Настроить", size="sm", color="outline-primary")], width=3, className="text-end"),
                                ]),
                            ]),
                        ]),
                    ])
                ], className="mt-3")
            ], label="Подключения", tab_id="tab-connections"),
            
            # Таб: Оповещения
            dbc.Tab([
                dbc.Card([
                    dbc.CardBody([
                        html.H5("Настройки оповещений", className="mb-3"),
                        dbc.ListGroup([
                            dbc.ListGroupItem([
                                dbc.Row([
                                    dbc.Col([
                                        html.I(className="fab fa-telegram text-info me-2"),
                                        html.Strong("Telegram бот"),
                                    ], width=4),
                                    dbc.Col([html.Small("@dqt_alert_bot", className="text-muted")], width=4),
                                    dbc.Col([
                                        html.Span("●", className="text-success me-1"),
                                        html.Small("Активен", className="text-success"),
                                    ], width=2),
                                    dbc.Col([dbc.Button("Настроить", size="sm", color="outline-primary")], width=2, className="text-end"),
                                ]),
                            ]),
                            dbc.ListGroupItem([
                                dbc.Row([
                                    dbc.Col([
                                        html.I(className="fas fa-envelope text-primary me-2"),
                                        html.Strong("Email (SMTP)"),
                                    ], width=4),
                                    dbc.Col([html.Small("smtp.company.com:587", className="text-muted")], width=4),
                                    dbc.Col([
                                        html.Span("●", className="text-success me-1"),
                                        html.Small("Активен", className="text-success"),
                                    ], width=2),
                                    dbc.Col([dbc.Button("Настроить", size="sm", color="outline-primary")], width=2, className="text-end"),
                                ]),
                            ]),
                        ]),
                    ])
                ], className="mt-3")
            ], label="Оповещения", tab_id="tab-notifications"),
        ], id="settings-tabs", active_tab="tab-templates"),
        
        # Модальное окно создания/редактирования шаблона
        dbc.Modal([
            dbc.ModalHeader(dbc.ModalTitle(id="template-modal-title")),
            dbc.ModalBody([
                dbc.Form([
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Название шаблона"),
                            dbc.Input(id="tpl-name", placeholder="Например: NULL-проверка полей"),
                        ], width=6),
                        dbc.Col([
                            dbc.Label("Тип проверки"),
                            dcc.Dropdown(
                                id="tpl-check-type",
                                options=[{"label": ct["check_type_name"], "value": ct["check_type_name"]}
                                         for ct in CHECK_TYPES],
                                placeholder="Выберите тип...",
                                searchable=True, clearable=True, style={"fontSize": "0.9em"},
                            ),
                        ], width=6),
                    ], className="mb-3"),
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Описание"),
                            dbc.Input(id="tpl-description", placeholder="Краткое описание шаблона..."),
                        ]),
                    ], className="mb-3"),
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Параметры (через запятую)"),
                            dbc.Input(id="tpl-parameters", placeholder="schema, table, field",
                                      value="schema, table"),
                        ], width=6),
                        dbc.Col([
                            dbc.Label("Активен"),
                            dbc.Switch(id="tpl-is-active", value=True, label="Да"),
                        ], width=6),
                    ], className="mb-3"),
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("SQL-шаблон"),
                            dbc.Textarea(
                                id="tpl-sql",
                                placeholder="SELECT ... FROM {schema}.{table} WHERE ...",
                                rows=10,
                                style={"fontFamily": "monospace", "fontSize": "0.85em"},
                            ),
                            dbc.FormText("Используйте {param} для подстановки параметров"),
                        ]),
                    ], className="mb-3"),
                ]),
            ]),
            dbc.ModalFooter([
                dbc.Button("Отмена", id="btn-cancel-template", color="secondary", outline=True),
                dbc.Button([html.I(className="fas fa-save me-2"), "Сохранить"],
                           id="btn-save-template", color="primary"),
            ]),
        ], id="modal-template", size="lg", is_open=False),
        
        # Toast
        dbc.Toast(
            id="toast-settings",
            header="Уведомление",
            is_open=False,
            dismissable=True,
            duration=4000,
            style={"position": "fixed", "top": 66, "right": 10, "width": 350},
        ),
        
    ], fluid=True, className="py-3")


# ============================================================
# Callbacks
# ============================================================

@callback(
    Output("template-editor", "children"),
    Input("templates-grid", "selectedRows"),
)
def show_template_editor(selected_rows):
    if not selected_rows:
        return dbc.Alert([
            html.I(className="fas fa-info-circle me-2"),
            "Выберите шаблон в таблице для просмотра SQL"
        ], color="light")
    
    row = selected_rows[0]
    # Найдём полный шаблон
    tpl = None
    for t in MOCK_CHECK_TEMPLATES:
        if t["template_id"] == row["template_id"]:
            tpl = t
            break
    
    if not tpl:
        return dbc.Alert("Шаблон не найден", color="warning")
    
    return dbc.Card([
        dbc.CardHeader([
            html.I(className="fas fa-code me-2"),
            f"SQL-шаблон: {tpl['name']}",
        ]),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.Strong("Параметры: "),
                        *[dbc.Badge(p, color="info", className="me-1") for p in tpl["parameters"]],
                    ], className="mb-2"),
                    dcc.Markdown(
                        f"```sql\n{tpl['sql_template']}\n```",
                        className="border rounded p-2 bg-light",
                        style={"fontSize": "0.85em"},
                    ),
                ], width=8),
                dbc.Col([
                    html.Div([
                        html.Strong("Тип: "), html.Span(tpl["check_type"]),
                    ], className="mb-2"),
                    html.Div([
                        html.Strong("Автор: "), html.Span(tpl["created_by"]),
                    ], className="mb-2"),
                    html.Div([
                        html.Strong("Активен: "),
                        dbc.Badge("Да" if tpl["is_active"] else "Нет",
                                  color="success" if tpl["is_active"] else "secondary"),
                    ], className="mb-2"),
                    html.Hr(),
                    dbc.Button([html.I(className="fas fa-edit me-1"), "Редактировать"],
                               id="btn-edit-template", size="sm", color="outline-primary", className="me-2"),
                    dbc.Button([html.I(className="fas fa-trash me-1"), "Удалить"],
                               id="btn-delete-template", size="sm", color="outline-danger"),
                ], width=4),
            ]),
        ]),
    ], className="shadow-sm")


@callback(
    [Output("modal-template", "is_open"),
     Output("template-modal-title", "children")],
    [Input("btn-create-template", "n_clicks"),
     Input("btn-edit-template", "n_clicks"),
     Input("btn-cancel-template", "n_clicks"),
     Input("btn-save-template", "n_clicks")],
    State("modal-template", "is_open"),
    prevent_initial_call=True
)
def toggle_template_modal(n_create, n_edit, n_cancel, n_save, is_open):
    triggered = ctx.triggered_id
    if triggered == "btn-create-template":
        return True, "Создание нового шаблона"
    if triggered == "btn-edit-template":
        return True, "Редактирование шаблона"
    return False, ""


@callback(
    [Output("toast-settings", "is_open"),
     Output("toast-settings", "children"),
     Output("toast-settings", "header"),
     Output("toast-settings", "icon")],
    [Input("btn-save-template", "n_clicks"),
     Input("btn-delete-template", "n_clicks")],
    [State("tpl-name", "value")],
    prevent_initial_call=True
)
def handle_template_actions(n_save, n_delete, name):
    triggered = ctx.triggered_id
    
    if triggered == "btn-save-template" and n_save:
        if not name:
            return True, "Введите название шаблона", "Ошибка", "danger"
        return True, f"Шаблон \"{name}\" сохранён", "Успех", "success"
    
    if triggered == "btn-delete-template" and n_delete:
        return True, "Шаблон удалён", "Удаление", "warning"
    
    return False, "", "", ""
