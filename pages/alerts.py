"""
Страница алертов и уведомлений
"""
import dash
from dash import html, dcc, callback, Input, Output, State, ctx
import dash_bootstrap_components as dbc
import dash_ag_grid as dag
from datetime import datetime, timedelta
from mock_data import MOCK_ALERTS, DOMAINS, OWNERS, get_alerts_count_by_status

dash.register_page(__name__, path="/alerts", name="Алерты")


def create_alert_card(severity, count, title, icon):
    """Создание карточки статистики алертов"""
    colors = {
        "critical": "danger",
        "warning": "warning",
        "active": "danger",
        "acknowledged": "info",
        "resolved": "success",
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
            dbc.Col(create_alert_card(
                "active", 
                stats.get("active", 0), 
                "Активных алертов",
                "fa-bell"
            ), width=3),
            dbc.Col(create_alert_card(
                "acknowledged", 
                stats.get("acknowledged", 0), 
                "На рассмотрении",
                "fa-eye"
            ), width=3),
            dbc.Col(create_alert_card(
                "resolved", 
                stats.get("resolved", 0), 
                "Решено",
                "fa-check-circle"
            ), width=3),
            dbc.Col(create_alert_card(
                "critical", 
                len(MOCK_ALERTS[MOCK_ALERTS["severity"] == "critical"]), 
                "Критических",
                "fa-exclamation-circle"
            ), width=3),
        ], className="mb-4 g-3"),
        
        # Фильтры
        dbc.Card([
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        dbc.InputGroup([
                            dbc.InputGroupText(html.I(className="fas fa-search")),
                            dbc.Input(
                                id="search-alerts",
                                placeholder="Поиск по проверке, таблице...",
                                debounce=True,
                            ),
                        ]),
                    ], width=3),
                    dbc.Col([
                        dbc.Select(
                            id="filter-alert-status",
                            options=[
                                {"label": "Все статусы", "value": ""},
                                {"label": "Активные", "value": "active"},
                                {"label": "На рассмотрении", "value": "acknowledged"},
                                {"label": "Решённые", "value": "resolved"},
                            ],
                            value="",
                        ),
                    ], width=2),
                    dbc.Col([
                        dbc.Select(
                            id="filter-alert-severity",
                            options=[
                                {"label": "Все уровни", "value": ""},
                                {"label": "Критический", "value": "critical"},
                                {"label": "Предупреждение", "value": "warning"},
                            ],
                            value="",
                        ),
                    ], width=2),
                    dbc.Col([
                        dbc.Select(
                            id="filter-alert-domain",
                            options=[{"label": "Все домены", "value": ""}] + [
                                {"label": d, "value": d} for d in DOMAINS
                            ],
                            value="",
                        ),
                    ], width=2),
                    dbc.Col([
                        dbc.Select(
                            id="filter-alert-channel",
                            options=[
                                {"label": "Все каналы", "value": ""},
                                {"label": "Telegram", "value": "telegram"},
                                {"label": "Email", "value": "email"},
                            ],
                            value="",
                        ),
                    ], width=2),
                    dbc.Col([
                        dbc.Button([
                            html.I(className="fas fa-filter-circle-xmark"),
                        ], id="btn-reset-alert-filters", color="outline-secondary", size="sm"),
                    ], width=1, className="text-end"),
                ], className="g-2"),
            ]),
        ], className="mb-3 shadow-sm"),
        
        # Статистика
        dbc.Row([
            dbc.Col([
                html.Span(id="alerts-count", className="text-muted"),
            ]),
        ], className="mb-2"),
        
        # Лента алертов
        html.Div(id="alerts-feed"),
        
        # Модальное окно создания правила
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
                            dbc.Select(
                                id="new-rule-condition",
                                options=[
                                    {"label": "При статусе FAIL", "value": "FAIL"},
                                    {"label": "При статусе ERROR", "value": "ERROR"},
                                    {"label": "При FAIL или ERROR", "value": "FAIL_OR_ERROR"},
                                    {"label": "При превышении threshold", "value": "THRESHOLD"},
                                ],
                            ),
                        ], width=6),
                        dbc.Col([
                            dbc.Label("Канал оповещения"),
                            dbc.Select(
                                id="new-rule-channel",
                                options=[
                                    {"label": "Telegram", "value": "telegram"},
                                    {"label": "Email", "value": "email"},
                                    {"label": "Оба канала", "value": "both"},
                                ],
                            ),
                        ], width=6),
                    ], className="mb-3"),
                    
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Применить к"),
                            dbc.Select(
                                id="new-rule-scope",
                                options=[
                                    {"label": "Все проверки", "value": "all"},
                                    {"label": "Домен", "value": "domain"},
                                    {"label": "Конкретная проверка", "value": "check"},
                                ],
                            ),
                        ], width=6),
                        dbc.Col([
                            dbc.Label("Домен / Проверка"),
                            dbc.Select(
                                id="new-rule-target",
                                options=[{"label": d, "value": d} for d in DOMAINS],
                            ),
                        ], width=6),
                    ], className="mb-3"),
                    
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Получатели (Telegram username или email)"),
                            dbc.Input(id="new-rule-recipients", placeholder="@user1, @user2 или user@company.com"),
                        ], width=12),
                    ], className="mb-3"),
                ]),
            ]),
            dbc.ModalFooter([
                dbc.Button("Отмена", id="btn-cancel-rule", color="secondary", outline=True),
                dbc.Button([
                    html.I(className="fas fa-save me-2"),
                    "Сохранить"
                ], id="btn-save-rule", color="primary"),
            ]),
        ], id="modal-create-rule", size="lg", is_open=False),
        
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
    """Создание элемента ленты алертов"""
    severity_colors = {
        "critical": "danger",
        "warning": "warning",
    }
    status_badges = {
        "active": ("Активен", "danger"),
        "acknowledged": ("На рассмотрении", "info"),
        "resolved": ("Решён", "success"),
    }
    channel_icons = {
        "telegram": "fab fa-telegram",
        "email": "fas fa-envelope",
    }
    
    badge_text, badge_color = status_badges.get(alert["status"], ("", "secondary"))
    
    return dbc.Card([
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    # Индикатор серьёзности
                    html.Div(
                        className=f"bg-{severity_colors.get(alert['severity'], 'secondary')}",
                        style={"width": "4px", "height": "100%", "position": "absolute", "left": 0, "top": 0, "borderRadius": "4px 0 0 4px"}
                    ),
                ], width="auto", style={"position": "relative", "paddingLeft": "8px"}),
                dbc.Col([
                    dbc.Row([
                        dbc.Col([
                            html.Div([
                                dbc.Badge(badge_text, color=badge_color, className="me-2"),
                                dbc.Badge(alert["severity"].upper(), 
                                         color=severity_colors.get(alert["severity"], "secondary"),
                                         className="me-2"),
                                html.I(className=f"{channel_icons.get(alert['channel'], '')} me-2 text-muted"),
                                html.A(
                                    html.Strong(alert["check_name"]),
                                    href=f"/check/{alert['check_id']}",
                                    className="text-decoration-none"
                                ),
                            ]),
                            html.P(alert["message"], className="text-muted mb-1 small"),
                            html.Small([
                                html.I(className="fas fa-table me-1"),
                                alert["table_name"],
                                html.Span(" | ", className="text-muted"),
                                html.I(className="fas fa-folder me-1"),
                                alert["domain"],
                                html.Span(" | ", className="text-muted"),
                                html.I(className="fas fa-user me-1"),
                                alert["owner"],
                            ], className="text-muted"),
                        ], width=8),
                        dbc.Col([
                            html.Div([
                                html.Small(
                                    alert["created_at"].strftime("%d.%m.%Y %H:%M"),
                                    className="text-muted d-block"
                                ),
                                html.Small(
                                    f"Принял: {alert['acknowledged_by']}" if alert['acknowledged_by'] else "",
                                    className="text-info d-block"
                                ) if alert['acknowledged_by'] else None,
                            ], className="text-end"),
                        ], width=2),
                        dbc.Col([
                            dbc.ButtonGroup([
                                dbc.Button([
                                    html.I(className="fas fa-eye"),
                                ], color="outline-info", size="sm", title="Принять",
                                   disabled=alert["status"] != "active",
                                   id={"type": "btn-ack-alert", "index": alert["alert_id"]}),
                                dbc.Button([
                                    html.I(className="fas fa-check"),
                                ], color="outline-success", size="sm", title="Решено",
                                   disabled=alert["status"] == "resolved",
                                   id={"type": "btn-resolve-alert", "index": alert["alert_id"]}),
                            ], size="sm"),
                        ], width=2, className="text-end"),
                    ]),
                ]),
            ]),
        ], className="py-2"),
    ], className="mb-2 shadow-sm", style={"position": "relative", "overflow": "hidden"})


@callback(
    [Output("alerts-feed", "children"),
     Output("alerts-count", "children")],
    [Input("search-alerts", "value"),
     Input("filter-alert-status", "value"),
     Input("filter-alert-severity", "value"),
     Input("filter-alert-domain", "value"),
     Input("filter-alert-channel", "value")]
)
def update_alerts_feed(search, status, severity, domain, channel):
    df = MOCK_ALERTS.copy()
    
    # Применяем фильтры
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
    
    if channel:
        df = df[df["channel"] == channel]
    
    df = df.sort_values("created_at", ascending=False)
    
    # Создаём карточки алертов
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
     Output("filter-alert-channel", "value", allow_duplicate=True)],
    Input("btn-reset-alert-filters", "n_clicks"),
    prevent_initial_call=True
)
def reset_alert_filters(n_clicks):
    return "", "", "", "", ""


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
    State("new-rule-name", "value"),
    prevent_initial_call=True
)
def save_rule(n_clicks, name):
    if n_clicks:
        if name:
            return True, f"Правило '{name}' успешно создано!", "Успех", "success"
        else:
            return True, "Введите название правила", "Ошибка", "danger"
    return False, "", "", ""
