"""
Страница алертов и уведомлений
"""
import dash
from dash import html, dcc, callback, Input, Output, State, ctx
import dash_bootstrap_components as dbc
import dash_ag_grid as dag
from datetime import datetime, timedelta
from mock_data import MOCK_ALERTS, MOCK_CHECKS, DOMAINS, OWNERS, SCHEMAS, TABLES_BY_SCHEMA, get_alerts_count_by_status

dash.register_page(__name__, path="/alerts", name="Алерты")


def create_alert_card(severity, count, title, icon):
    """Создание карточки статистики алертов"""
    colors = {
        "critical": "danger", "warning": "warning",
        "active": "danger", "acknowledged": "info", "resolved": "success",
    }
    return dbc.Card([
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.H3(count, className=f"mb-0 text-{colors.get(severity, 'secondary')}"),
                    html.Small(title, className="text-muted"),
                ], width=8),
                dbc.Col([
                    html.I(className=f"fas {icon} fa-2x text-{colors.get(severity, 'secondary')} opacity-50"),
                ], width=4, className="text-end"),
            ], align="center"),
        ])
    ], className="shadow-sm h-100")


def layout():
    stats = get_alerts_count_by_status()
    
    return dbc.Container([
        # Заголовок
        dbc.Row([
            dbc.Col([
                html.H2("Алерты и уведомления", className="mb-0"),
                html.P("Мониторинг проблем качества данных", className="text-muted"),
            ], width=8),
            dbc.Col([
                dbc.Button([
                    html.I(className="fas fa-plus me-2"),
                    "Создать правило"
                ], id="btn-create-alert-rule", color="primary"),
            ], width=4, className="text-end"),
        ], className="mb-4 align-items-center"),
        
        # KPI карточки
        dbc.Row([
            dbc.Col(create_alert_card("active", stats.get("active", 0), "Активных алертов", "fa-bell"), width=3),
            dbc.Col(create_alert_card("acknowledged", stats.get("acknowledged", 0), "На рассмотрении", "fa-eye"), width=3),
            dbc.Col(create_alert_card("resolved", stats.get("resolved", 0), "Решено", "fa-check-circle"), width=3),
            dbc.Col(create_alert_card("critical", len(MOCK_ALERTS[MOCK_ALERTS["severity"] == "critical"]), "Критических", "fa-exclamation-circle"), width=3),
        ], className="mb-4 g-3"),
        
        # Фильтры
        dbc.Card([
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        dbc.InputGroup([
                            dbc.InputGroupText(html.I(className="fas fa-search")),
                            dbc.Input(id="search-alerts", placeholder="Поиск по проверке, таблице...", debounce=True, type="search"),
                        ]),
                    ], width=3),
                    dbc.Col([
                        dcc.Dropdown(id="filter-alert-status", options=[
                            {"label": "Все статусы", "value": ""},
                            {"label": "Активные", "value": "active"},
                            {"label": "На рассмотрении", "value": "acknowledged"},
                            {"label": "Решённые", "value": "resolved"},
                        ], value="", placeholder="Статус...", searchable=True, clearable=False, style={"fontSize": "0.9em"}),
                    ], width=2),
                    dbc.Col([
                        dcc.Dropdown(id="filter-alert-severity", options=[
                            {"label": "Все уровни", "value": ""},
                            {"label": "Критический", "value": "critical"},
                            {"label": "Предупреждение", "value": "warning"},
                        ], value="", placeholder="Уровень...", searchable=True, clearable=False, style={"fontSize": "0.9em"}),
                    ], width=2),
                    dbc.Col([
                        dcc.Dropdown(id="filter-alert-domain", options=[{"label": "Все домены", "value": ""}] + [
                            {"label": d, "value": d} for d in DOMAINS
                        ], value="", placeholder="Домен...", searchable=True, clearable=False, style={"fontSize": "0.9em"}),
                    ], width=2),
                    dbc.Col([
                        dcc.Dropdown(id="filter-alert-schema", options=[{"label": "Все схемы", "value": ""}] + [
                            {"label": s, "value": s} for s in SCHEMAS
                        ], value="", placeholder="Схема...", searchable=True, clearable=False, style={"fontSize": "0.9em"}),
                    ], width=2),
                    dbc.Col([
                        dcc.Dropdown(id="filter-alert-table", options=[], value="", placeholder="Таблица...",
                                     searchable=True, clearable=False, disabled=True, style={"fontSize": "0.9em"}),
                    ], width=2),
                ], className="g-2 mb-2"),
                dbc.Row([
                    dbc.Col([
                        dbc.Button([html.I(className="fas fa-filter-circle-xmark me-1"), "Сбросить"],
                                   id="btn-reset-alert-filters", color="outline-secondary", size="sm"),
                    ], className="text-end"),
                ]),
            ]),
        ], className="mb-3 shadow-sm"),
        
        # Статистика
        dbc.Row([dbc.Col([html.Span(id="alerts-count", className="text-muted")])], className="mb-2"),
        
        # Лента алертов
        html.Div(id="alerts-feed"),
        
        # Модальное окно создания правила (расширенное)
        dbc.Modal([
            dbc.ModalHeader(dbc.ModalTitle("Создание правила оповещения")),
            dbc.ModalBody([
                dbc.Form([
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Название правила"),
                            dbc.Input(id="new-rule-name", placeholder="Алерт на FAIL проверок домена"),
                        ], width=12),
                    ], className="mb-3"),
                    
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Условие срабатывания"),
                            dcc.Dropdown(id="new-rule-condition", options=[
                                {"label": "При статусе FAIL", "value": "FAIL"},
                                {"label": "При статусе ERROR", "value": "ERROR"},
                                {"label": "При FAIL или ERROR", "value": "FAIL_OR_ERROR"},
                                {"label": "При превышении threshold", "value": "THRESHOLD"},
                            ], placeholder="Выберите условие...", searchable=True, clearable=True, style={"fontSize": "0.9em"}),
                        ], width=6),
                        dbc.Col([
                            dbc.Label("Канал оповещения"),
                            dcc.Dropdown(id="new-rule-channel", options=[
                                {"label": "Telegram", "value": "telegram"},
                                {"label": "Email", "value": "email"},
                                {"label": "Оба канала", "value": "both"},
                            ], placeholder="Выберите канал...", searchable=True, clearable=True, style={"fontSize": "0.9em"}),
                        ], width=6),
                    ], className="mb-3"),
                    
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Применить к"),
                            dcc.Dropdown(id="new-rule-scope", options=[
                                {"label": "Все проверки", "value": "all"},
                                {"label": "Домен", "value": "domain"},
                                {"label": "Группа проверок (по типу)", "value": "check_type"},
                                {"label": "Конкретная проверка", "value": "check"},
                            ], placeholder="Выберите область...", searchable=True, clearable=True, style={"fontSize": "0.9em"}),
                        ], width=6),
                        dbc.Col([
                            dbc.Label("Домен / Группа / Проверка"),
                            dcc.Dropdown(id="new-rule-target", options=[], placeholder="Сначала выберите область...",
                                         searchable=True, clearable=True, disabled=True, style={"fontSize": "0.9em"}),
                        ], width=6),
                    ], className="mb-3"),
                    
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Получатели (Telegram username или email)"),
                            dbc.Input(id="new-rule-recipients", placeholder="@user1, @user2 или user@company.com"),
                        ], width=12),
                    ], className="mb-3"),
                    
                    # Шаблон сообщения
                    html.Hr(),
                    html.H6([html.I(className="fas fa-envelope-open-text me-2"), "Шаблон сообщения"], className="mb-3"),
                    
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Тема сообщения"),
                            dbc.Input(
                                id="new-rule-msg-subject",
                                placeholder="[DQT] Алерт: {check_name} - {status}",
                                value="[DQT] Алерт: {check_name} - {status}",
                            ),
                        ], width=12),
                    ], className="mb-3"),
                    
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Тело сообщения"),
                            dbc.Textarea(
                                id="new-rule-msg-body",
                                placeholder="Шаблон тела сообщения...",
                                value="Проверка: {check_name}\nТаблица: {table_name}\nСтатус: {status}\nВремя: {run_time}\nОшибок: {rows_failed} из {rows_checked}\n\nДомен: {domain}\nВладелец: {owner}",
                                rows=6,
                                style={"fontFamily": "monospace", "fontSize": "0.85em"},
                            ),
                        ], width=7),
                        dbc.Col([
                            dbc.Label("Доступные переменные"),
                            html.Div([
                                dbc.Badge("{check_name}", color="light", text_color="dark", className="me-1 mb-1"),
                                dbc.Badge("{table_name}", color="light", text_color="dark", className="me-1 mb-1"),
                                dbc.Badge("{status}", color="light", text_color="dark", className="me-1 mb-1"),
                                dbc.Badge("{run_time}", color="light", text_color="dark", className="me-1 mb-1"),
                                dbc.Badge("{rows_checked}", color="light", text_color="dark", className="me-1 mb-1"),
                                dbc.Badge("{rows_failed}", color="light", text_color="dark", className="me-1 mb-1"),
                                dbc.Badge("{domain}", color="light", text_color="dark", className="me-1 mb-1"),
                                dbc.Badge("{owner}", color="light", text_color="dark", className="me-1 mb-1"),
                                dbc.Badge("{error_message}", color="light", text_color="dark", className="me-1 mb-1"),
                                dbc.Badge("{threshold}", color="light", text_color="dark", className="me-1 mb-1"),
                            ], className="mb-3"),
                            dbc.Label("Предпросмотр", className="mt-2"),
                            html.Div(id="msg-template-preview", className="border rounded p-2 bg-light small",
                                     style={"minHeight": "80px", "whiteSpace": "pre-wrap", "fontFamily": "monospace", "fontSize": "0.8em"}),
                        ], width=5),
                    ], className="mb-3"),
                ]),
            ]),
            dbc.ModalFooter([
                dbc.Button("Отмена", id="btn-cancel-rule", color="secondary", outline=True),
                dbc.Button([html.I(className="fas fa-save me-2"), "Сохранить"], id="btn-save-rule", color="primary"),
            ]),
        ], id="modal-create-rule", size="xl", is_open=False),
        
        # Toast
        dbc.Toast(
            id="toast-alert-action",
            header="Уведомление",
            is_open=False,
            dismissable=True,
            duration=4000,
            style={"position": "fixed", "top": 66, "right": 10, "width": 350},
        ),
        
    ], fluid=True, className="py-3")


def create_alert_item(alert):
    """Создание элемента ленты алертов с информацией об инциденте."""
    severity_colors = {"critical": "danger", "warning": "warning"}
    status_badges = {
        "active": ("Активен", "danger"),
        "acknowledged": ("На рассмотрении", "info"),
        "resolved": ("Решён", "success"),
    }
    channel_icons = {"telegram": "fab fa-telegram", "email": "fas fa-envelope"}
    
    badge_text, badge_color = status_badges.get(alert["status"], ("", "secondary"))
    
    # Информация об инциденте
    incident_info = []
    if alert.get("has_tracker_task"):
        incident_info.append(
            html.Span([
                html.I(className="fas fa-external-link-alt me-1"),
                html.A(alert["tracker_task_id"], href=alert.get("tracker_task_url", "#"),
                       className="text-decoration-none", target="_blank"),
            ], className="me-3")
        )
    
    # Комментарии
    comments = alert.get("comments", [])
    comments_section = None
    if comments:
        comments_items = []
        for c in comments:
            comments_items.append(
                html.Div([
                    html.Small([
                        html.Strong(c["author"]),
                        html.Span(f" ({c['created_at']})", className="text-muted"),
                    ]),
                    html.P(c["text"], className="mb-1 small"),
                ], className="border-start border-2 ps-2 mb-1")
            )
        comments_section = html.Div([
            html.Small([
                html.I(className="fas fa-comments me-1"),
                f"Комментарии ({len(comments)}):",
            ], className="text-muted d-block mt-2"),
            html.Div(comments_items, className="mt-1"),
        ])
    
    return dbc.Card([
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.Div([
                        dbc.Badge(badge_text, color=badge_color, className="me-2"),
                        dbc.Badge(alert["severity"].upper(), 
                                 color=severity_colors.get(alert["severity"], "secondary"), className="me-2"),
                        html.I(className=f"{channel_icons.get(alert['channel'], '')} me-2 text-muted"),
                        html.A(html.Strong(alert["check_name"]),
                               href=f"/check/{alert['check_id']}", className="text-decoration-none"),
                    ]),
                    html.P(alert["message"], className="text-muted mb-1 small"),
                    html.Div([
                        html.Small([
                            html.I(className="fas fa-table me-1"), alert["table_name"],
                            html.Span(" | ", className="text-muted"),
                            html.I(className="fas fa-folder me-1"), alert["domain"],
                            html.Span(" | ", className="text-muted"),
                            html.I(className="fas fa-user me-1"), alert["owner"],
                        ], className="text-muted"),
                    ]),
                    # Инцидент
                    html.Div(incident_info, className="mt-1") if incident_info else None,
                    # Комментарии
                    comments_section,
                ], width=8),
                dbc.Col([
                    html.Div([
                        html.Small(alert["created_at"].strftime("%d.%m.%Y %H:%M"), className="text-muted d-block"),
                        html.Small(f"Принял: {alert['acknowledged_by']}", className="text-info d-block")
                        if alert['acknowledged_by'] else None,
                        # Бейдж задачи в трекере
                        dbc.Badge([
                            html.I(className="fas fa-tasks me-1"),
                            "Задача создана"
                        ], color="info", className="mt-1") if alert.get("has_tracker_task") else
                        dbc.Badge("Без задачи", color="light", text_color="secondary", className="mt-1"),
                    ], className="text-end"),
                ], width=2),
                dbc.Col([
                    dbc.ButtonGroup([
                        dbc.Button([html.I(className="fas fa-eye")],
                                   color="outline-info", size="sm", title="Принять",
                                   disabled=alert["status"] != "active",
                                   id={"type": "btn-ack-alert", "index": alert["alert_id"]}),
                        dbc.Button([html.I(className="fas fa-check")],
                                   color="outline-success", size="sm", title="Решено",
                                   disabled=alert["status"] == "resolved",
                                   id={"type": "btn-resolve-alert", "index": alert["alert_id"]}),
                    ], size="sm"),
                ], width=2, className="text-end"),
            ]),
        ], className="py-2"),
    ], className="mb-2 shadow-sm", style={"position": "relative", "overflow": "hidden"})


# ============================================================
# Callbacks
# ============================================================
@callback(
    [Output("filter-alert-table", "options"),
     Output("filter-alert-table", "disabled"),
     Output("filter-alert-table", "value")],
    Input("filter-alert-schema", "value")
)
def update_alert_tables_dropdown(schema):
    if not schema:
        return [{"label": "Все", "value": ""}], True, ""
    tables = TABLES_BY_SCHEMA.get(schema, [])
    options = [{"label": "Все", "value": ""}] + [{"label": t, "value": t} for t in tables]
    return options, False, ""


@callback(
    [Output("new-rule-target", "options"),
     Output("new-rule-target", "value"),
     Output("new-rule-target", "disabled")],
    Input("new-rule-scope", "value")
)
def update_rule_target_by_scope(scope):
    if not scope or scope == "all":
        return [], None, True
    if scope == "domain":
        options = [{"label": d, "value": d} for d in DOMAINS]
        return options, None, False
    if scope == "check_type":
        from mock_data import MOCK_CHECK_TYPES
        options = [{"label": ct["check_type_name"], "value": ct["check_type_name"]}
                   for ct in MOCK_CHECK_TYPES.to_dict("records")]
        return options, None, False
    if scope == "check":
        checks = MOCK_CHECKS.to_dict("records")
        options = [{"label": f"{r['check_name']} ({r['table_name']})", "value": r["check_id"]} for r in checks]
        return options, None, False
    return [], None, True


@callback(
    Output("msg-template-preview", "children"),
    [Input("new-rule-msg-subject", "value"),
     Input("new-rule-msg-body", "value")]
)
def update_template_preview(subject, body):
    # Показываем пример с подставленными значениями
    example_values = {
        "{check_name}": "check_f_transactions_пол_12",
        "{table_name}": "dwh.f_transactions",
        "{status}": "FAIL",
        "{run_time}": "2026-02-11 14:30",
        "{rows_checked}": "1,500,000",
        "{rows_failed}": "2,340",
        "{domain}": "Транзакции",
        "{owner}": "ivanov_a",
        "{error_message}": "",
        "{threshold}": "0.05%",
    }
    
    preview_subject = subject or ""
    preview_body = body or ""
    for key, val in example_values.items():
        preview_subject = preview_subject.replace(key, val)
        preview_body = preview_body.replace(key, val)
    
    return html.Div([
        html.Strong(f"Тема: {preview_subject}"),
        html.Hr(className="my-1"),
        html.Span(preview_body),
    ])


@callback(
    [Output("alerts-feed", "children"),
     Output("alerts-count", "children")],
    [Input("search-alerts", "value"),
     Input("filter-alert-status", "value"),
     Input("filter-alert-severity", "value"),
     Input("filter-alert-domain", "value"),
     Input("filter-alert-schema", "value"),
     Input("filter-alert-table", "value")]
)
def update_alerts_feed(search, status, severity, domain, schema, table):
    df = MOCK_ALERTS.copy()
    
    if search:
        search = search.lower()
        df = df[
            df["check_name"].str.lower().str.contains(search, na=False) |
            df["table_name"].str.lower().str.contains(search, na=False)
        ]
    if status:
        df = df[df["status"] == status]
    if severity:
        df = df[df["severity"] == severity]
    if domain:
        df = df[df["domain"] == domain]
    if schema and table:
        full_table = f"{schema}.{table}"
        df = df[df["table_name"] == full_table]
    elif schema:
        df = df[df["table_name"].str.startswith(f"{schema}.")]
    
    df = df.sort_values("created_at", ascending=False)
    
    alerts_items = [create_alert_item(row.to_dict()) for _, row in df.iterrows()]
    
    if not alerts_items:
        alerts_items = [dbc.Alert("Нет алертов по заданным фильтрам", color="info")]
    
    count_text = f"Найдено алертов: {len(df)}"
    return alerts_items, count_text


@callback(
    [Output("search-alerts", "value"),
     Output("filter-alert-status", "value", allow_duplicate=True),
     Output("filter-alert-severity", "value", allow_duplicate=True),
     Output("filter-alert-domain", "value", allow_duplicate=True),
     Output("filter-alert-schema", "value", allow_duplicate=True),
     Output("filter-alert-table", "value", allow_duplicate=True)],
    Input("btn-reset-alert-filters", "n_clicks"),
    prevent_initial_call=True
)
def reset_alert_filters(n_clicks):
    return "", "", "", "", "", ""


@callback(
    Output("modal-create-rule", "is_open"),
    [Input("btn-create-alert-rule", "n_clicks"),
     Input("btn-cancel-rule", "n_clicks"),
     Input("btn-save-rule", "n_clicks")],
    State("modal-create-rule", "is_open"),
    prevent_initial_call=True
)
def toggle_rule_modal(n_create, n_cancel, n_save, is_open):
    return not is_open


@callback(
    [Output("toast-alert-action", "is_open"),
     Output("toast-alert-action", "children"),
     Output("toast-alert-action", "header"),
     Output("toast-alert-action", "icon")],
    Input("btn-save-rule", "n_clicks"),
    [State("new-rule-name", "value"),
     State("new-rule-condition", "value"),
     State("new-rule-scope", "value"),
     State("new-rule-target", "value"),
     State("new-rule-msg-subject", "value"),
     State("new-rule-msg-body", "value")],
    prevent_initial_call=True
)
def save_rule(n_clicks, name, condition, scope, target, msg_subject, msg_body):
    if n_clicks:
        if not name:
            return True, "Введите название правила", "Ошибка", "danger"
        condition_text = condition or "не задано"
        if scope == "all" or not scope:
            scope_text = "все проверки"
        elif scope == "domain":
            scope_text = f"домен \"{target}\"" if target else "домен (не выбран)"
        elif scope == "check_type":
            scope_text = f"группа \"{target}\"" if target else "группа (не выбрана)"
        else:
            scope_text = f"проверка #{target}" if target else "проверка (не выбрана)"
        
        template_info = ""
        if msg_subject or msg_body:
            template_info = " Шаблон сообщения сохранён."
        
        msg = f"Правило \"{name}\" создано: при {condition_text} для {scope_text}.{template_info}"
        return True, msg, "Успех", "success"
    return False, "", "", ""
