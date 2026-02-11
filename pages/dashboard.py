"""
Главный дашборд DQT
"""
import dash
from dash import html, dcc, callback, Input, Output, State, ctx
import dash_bootstrap_components as dbc
import dash_cytoscape as cyto
import plotly.express as px
import plotly.graph_objects as go
from mock_data import (
    MOCK_CHECKS, MOCK_RESULTS, DOMAINS, TABLES,
    get_dashboard_stats, get_trend_data, 
    get_checks_by_domain, get_checks_by_type,
    LINEAGE_GRAPH,
)

dash.register_page(__name__, path="/", name="Дашборд")


def create_kpi_card(title, value, icon, color, delta=None):
    """Создание KPI карточки"""
    delta_element = None
    if delta is not None:
        delta_color = "success" if delta >= 0 else "danger"
        delta_icon = "fa-arrow-up" if delta >= 0 else "fa-arrow-down"
        delta_element = html.Span([
            html.I(className=f"fas {delta_icon} me-1"),
            f"{abs(delta)}%"
        ], className=f"text-{delta_color} small")
    
    return dbc.Card([
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.P(title, className="text-muted mb-1 small"),
                    html.H3(value, className="mb-0 fw-bold"),
                    delta_element,
                ], width=8),
                dbc.Col([
                    html.Div([
                        html.I(className=f"fas {icon} fa-2x")
                    ], className=f"text-{color} opacity-75")
                ], width=4, className="text-end"),
            ], align="center"),
        ])
    ], className="shadow-sm h-100")


def _build_full_lineage_graph():
    """Построение полного графа связей для дашборда."""
    elements = []
    nodes = set()
    
    for table_name, info in LINEAGE_GRAPH.items():
        nodes.add(table_name)
        for src in info.get("sources", []):
            nodes.add(src)
        for tgt in info.get("targets", []):
            nodes.add(tgt)
    
    # Определяем слой по схеме
    for node in nodes:
        schema = node.split(".")[0] if "." in node else "other"
        layer_map = {"src": "source", "staging": "staging", "dwh": "dwh", "mart": "mart"}
        layer = layer_map.get(schema, "other")
        elements.append({"data": {"id": node, "label": node.split(".")[-1], "full_name": node, "layer": layer}})
    
    for table_name, info in LINEAGE_GRAPH.items():
        for src in info.get("sources", []):
            elements.append({"data": {"source": src, "target": table_name}})
        for tgt in info.get("targets", []):
            elements.append({"data": {"source": table_name, "target": tgt}})
    
    return elements


def layout():
    stats = get_dashboard_stats(MOCK_RESULTS)
    
    return dbc.Container([
        # Заголовок
        dbc.Row([
            dbc.Col([
                html.H2("Дашборд Data Quality", className="mb-0"),
                html.P("Обзор состояния качества данных за последние 7 дней", className="text-muted"),
            ], width=6),
            dbc.Col([
                # Персонализация
                dbc.Button([
                    html.I(className="fas fa-sliders-h me-2"),
                    "Настроить"
                ], id="btn-customize-dashboard", color="outline-secondary", className="me-2", size="sm"),
                dbc.Button([
                    html.I(className="fas fa-sync-alt me-2"),
                    "Обновить"
                ], id="btn-refresh", color="outline-primary", className="me-2"),
                dbc.Button([
                    html.I(className="fas fa-download me-2"),
                    "Экспорт"
                ], color="outline-secondary"),
            ], width=6, className="text-end"),
        ], className="mb-4 align-items-center"),
        
        # Панель настройки виджетов
        dbc.Collapse([
            dbc.Card([
                dbc.CardBody([
                    html.H6("Настройка виджетов дашборда", className="mb-3"),
                    dbc.Row([
                        dbc.Col([
                            dbc.Checklist(
                                id="dashboard-widgets-toggle",
                                options=[
                                    {"label": " Тренд результатов", "value": "show_trend"},
                                    {"label": " По типам проверок", "value": "show_type"},
                                    {"label": " Результаты по доменам", "value": "show_domain"},
                                    {"label": " Последние запуски", "value": "show_issues"},
                                ],
                                value=["show_trend", "show_type", "show_domain", "show_issues"],
                                inline=True,
                                className="mb-0",
                            ),
                        ]),
                    ]),
                ]),
            ], className="mb-3 shadow-sm"),
        ], id="customize-collapse", is_open=False),
        
        # KPI карточки
        dbc.Row([
            dbc.Col(create_kpi_card("Всего запусков", f"{stats['total_runs']:,}", "fa-play-circle", "primary", delta=5), width=3),
            dbc.Col(create_kpi_card("Успешность", f"{stats['success_rate']}%", "fa-check-circle", "success", delta=2), width=3),
            dbc.Col(create_kpi_card("Проверок FAIL", f"{stats['failed_runs']}", "fa-exclamation-triangle", "danger", delta=-8), width=3),
            dbc.Col(create_kpi_card("Уникальных таблиц", f"{stats['unique_tables']}", "fa-database", "info"), width=3),
        ], className="mb-4 g-3"),
        
        # Графики - первый ряд (тренд + типы)
        html.Div(id="row-trend-type", children=[
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([html.I(className="fas fa-chart-area me-2"), "Тренд результатов проверок"]),
                        dbc.CardBody([dcc.Graph(id="trend-chart", style={"height": "300px"})])
                    ], className="shadow-sm")
                ], width=8, id="col-trend"),
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([html.I(className="fas fa-chart-pie me-2"), "По типам проверок"]),
                        dbc.CardBody([dcc.Graph(id="type-chart", style={"height": "300px"})])
                    ], className="shadow-sm")
                ], width=4, id="col-type"),
            ], className="mb-4"),
        ]),
        
        # Графики - второй ряд (домены + последние запуски)
        html.Div(id="row-domain-issues", children=[
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([html.I(className="fas fa-chart-bar me-2"), "Результаты по доменам"]),
                        dbc.CardBody([dcc.Graph(id="domain-chart", style={"height": "300px"})])
                    ], className="shadow-sm")
                ], width=6, id="col-domain"),
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([html.I(className="fas fa-list me-2"), "Последние запуски"]),
                        dbc.CardBody([html.Div(id="recent-issues")])
                    ], className="shadow-sm")
                ], width=6, id="col-issues"),
            ], className="mb-4"),
        ]),
        
        # Здоровье данных на уровне объекта
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.I(className="fas fa-heartbeat me-2"),
                        "Здоровье данных по объектам",
                    ]),
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                dcc.Dropdown(
                                    id="health-object-filter",
                                    options=[{"label": t, "value": t} for t in TABLES],
                                    placeholder="Выберите объект для детализации...",
                                    searchable=True,
                                    clearable=True,
                                    style={"fontSize": "0.9em"},
                                ),
                            ], width=4),
                        ], className="mb-3"),
                        html.Div(id="health-object-detail"),
                    ])
                ], className="shadow-sm")
            ]),
        ], className="mb-4"),
        
        # Граф связей проверок/объектов
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.I(className="fas fa-project-diagram me-2"),
                        "Граф связей: проверки, объекты DWH",
                    ]),
                    dbc.CardBody([
                        html.P("Интерактивный граф зависимостей между таблицами. Цвет узла зависит от слоя (src/staging/dwh/mart).",
                               className="text-muted small"),
                        cyto.Cytoscape(
                            id="dashboard-graph",
                            elements=_build_full_lineage_graph(),
                            layout={"name": "breadthfirst", "directed": True, "spacingFactor": 1.2, "avoidOverlap": True},
                            style={"width": "100%", "height": "400px", "border": "1px solid #dee2e6", "borderRadius": "8px"},
                            stylesheet=[
                                {"selector": "node", "style": {
                                    "label": "data(label)", "text-valign": "center", "text-halign": "center",
                                    "background-color": "#6c757d", "color": "#fff", "font-size": "10px",
                                    "width": "100px", "height": "30px", "shape": "round-rectangle",
                                    "text-wrap": "wrap", "text-max-width": "90px", "padding": "5px",
                                }},
                                {"selector": 'node[layer = "source"]', "style": {"background-color": "#6c757d"}},
                                {"selector": 'node[layer = "staging"]', "style": {"background-color": "#17a2b8"}},
                                {"selector": 'node[layer = "dwh"]', "style": {"background-color": "#0d6efd"}},
                                {"selector": 'node[layer = "mart"]', "style": {"background-color": "#198754"}},
                                {"selector": 'node[layer = "other"]', "style": {"background-color": "#6c757d"}},
                                {"selector": "edge", "style": {
                                    "curve-style": "bezier", "target-arrow-shape": "triangle",
                                    "target-arrow-color": "#adb5bd", "line-color": "#adb5bd", "width": 1.5,
                                }},
                            ],
                        ),
                        html.Div([
                            dbc.Badge("src (источники)", color="secondary", className="me-2"),
                            dbc.Badge("staging", color="info", className="me-2"),
                            dbc.Badge("dwh", color="primary", className="me-2"),
                            dbc.Badge("mart", color="success", className="me-2"),
                        ], className="mt-2"),
                    ])
                ], className="shadow-sm")
            ]),
        ], className="mb-4"),
        
        # Автообновление
        dcc.Interval(id="interval-component", interval=60*1000, n_intervals=0),
        
    ], fluid=True, className="py-3")


# ============================================================
# Callbacks
# ============================================================

@callback(
    Output("customize-collapse", "is_open"),
    Input("btn-customize-dashboard", "n_clicks"),
    State("customize-collapse", "is_open"),
    prevent_initial_call=True
)
def toggle_customize(n_clicks, is_open):
    return not is_open


@callback(
    [Output("row-trend-type", "style"),
     Output("row-domain-issues", "style")],
    Input("dashboard-widgets-toggle", "value"),
)
def update_widget_visibility(values):
    values = values or []
    trend_type_visible = "show_trend" in values or "show_type" in values
    domain_issues_visible = "show_domain" in values or "show_issues" in values
    
    return (
        {} if trend_type_visible else {"display": "none"},
        {} if domain_issues_visible else {"display": "none"},
    )


@callback(
    Output("trend-chart", "figure"),
    Input("interval-component", "n_intervals")
)
def update_trend_chart(n):
    trend_data = get_trend_data(MOCK_RESULTS, days=30)
    
    fig = px.area(
        trend_data, x="run_date", y="count", color="check_status_name",
        color_discrete_map={"OK": "#28a745", "FAIL": "#dc3545", "ERROR": "#fd7e14", "SKIP": "#6c757d"},
        labels={"run_date": "Дата", "count": "Количество", "check_status_name": "Статус"},
    )
    fig.update_layout(
        margin=dict(l=20, r=20, t=20, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hovermode="x unified",
    )
    return fig


@callback(
    Output("type-chart", "figure"),
    Input("interval-component", "n_intervals")
)
def update_type_chart(n):
    latest = MOCK_RESULTS.sort_values("run_datetime").drop_duplicates(subset=["check_id"], keep="last")
    type_summary = latest.groupby("check_type_name")["check_status_name"].value_counts().unstack(fill_value=0)
    
    fig = go.Figure(data=[
        go.Pie(labels=type_summary.index, values=type_summary.sum(axis=1), hole=0.4,
               marker_colors=px.colors.qualitative.Set2)
    ])
    fig.update_layout(margin=dict(l=20, r=20, t=20, b=20), showlegend=True, legend=dict(font=dict(size=10)))
    return fig


@callback(
    Output("domain-chart", "figure"),
    Input("interval-component", "n_intervals")
)
def update_domain_chart(n):
    domain_data = get_checks_by_domain(MOCK_RESULTS)
    
    fig = px.bar(
        domain_data, x="domain", y="count", color="check_status_name", barmode="group",
        color_discrete_map={"OK": "#28a745", "FAIL": "#dc3545", "ERROR": "#fd7e14", "SKIP": "#6c757d"},
        labels={"domain": "Домен", "count": "Количество", "check_status_name": "Статус"},
    )
    fig.update_layout(
        margin=dict(l=20, r=20, t=20, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    return fig


@callback(
    Output("recent-issues", "children"),
    Input("interval-component", "n_intervals")
)
def update_recent_runs(n):
    """Показываем все последние запуски (не только FAIL/ERROR)."""
    recent = MOCK_RESULTS.sort_values("run_datetime", ascending=False).head(8)
    
    if recent.empty:
        return html.P("Нет данных", className="text-muted")
    
    items = []
    for _, row in recent.iterrows():
        status_colors = {"OK": "success", "FAIL": "danger", "ERROR": "warning", "SKIP": "secondary"}
        status_color = status_colors.get(row["check_status_name"], "secondary")
        items.append(
            dbc.ListGroupItem([
                dbc.Row([
                    dbc.Col([
                        html.Div([
                            dbc.Badge(row["check_status_name"], color=status_color, className="me-2"),
                            html.Strong(row["check_name"], className="small"),
                        ]),
                        html.Small(f"{row['table_name']}", className="text-muted d-block"),
                    ], width=9),
                    dbc.Col([
                        html.Small(row["run_datetime"].strftime("%d.%m %H:%M"), className="text-muted"),
                    ], width=3, className="text-end"),
                ]),
            ], className="py-2", action=True, href=f"/check/{row['check_id']}")
        )
    
    return dbc.ListGroup(items, flush=True)


@callback(
    Output("health-object-detail", "children"),
    Input("health-object-filter", "value"),
)
def update_health_detail(table_name):
    """Здоровье данных на уровне конкретного объекта."""
    if not table_name:
        # Общая сводка по доменам
        domain_health = []
        for domain in DOMAINS:
            domain_results = MOCK_RESULTS[MOCK_RESULTS["domain"] == domain]
            if domain_results.empty:
                continue
            total = len(domain_results)
            ok = len(domain_results[domain_results["check_status_name"] == "OK"])
            rate = round(ok / total * 100, 1) if total > 0 else 0
            color = "success" if rate >= 90 else "warning" if rate >= 70 else "danger"
            domain_health.append(
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H6(domain, className="mb-1"),
                            dbc.Progress(value=rate, color=color, className="mb-1", style={"height": "8px"}),
                            html.Small(f"{rate}% успешных", className=f"text-{color}"),
                        ])
                    ], className="shadow-sm")
                ], width=True)
            )
        return dbc.Row(domain_health, className="g-3")
    
    # Детализация по конкретному объекту
    obj_results = MOCK_RESULTS[MOCK_RESULTS["table_name"] == table_name].sort_values("run_datetime", ascending=False)
    
    if obj_results.empty:
        return dbc.Alert(f"Нет данных по объекту {table_name}", color="info")
    
    total = len(obj_results)
    ok = len(obj_results[obj_results["check_status_name"] == "OK"])
    fail = len(obj_results[obj_results["check_status_name"] == "FAIL"])
    error = len(obj_results[obj_results["check_status_name"] == "ERROR"])
    rate = round(ok / total * 100, 1) if total > 0 else 0
    color = "success" if rate >= 90 else "warning" if rate >= 70 else "danger"
    
    # Связанные проверки
    related_checks = MOCK_CHECKS[MOCK_CHECKS["table_name"] == table_name]
    checks_list = []
    for _, ch in related_checks.iterrows():
        sc = "success" if ch["last_status"] == "OK" else "danger" if ch["last_status"] == "FAIL" else "warning"
        checks_list.append(
            html.Li([
                dbc.Badge(ch["last_status"], color=sc, className="me-2"),
                html.A(ch["check_name"], href=f"/check/{ch['check_id']}", className="text-decoration-none"),
                html.Small(f" ({ch['check_type_name']})", className="text-muted"),
            ], className="mb-1")
        )
    
    return dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5(table_name, className="mb-2"),
                    dbc.Progress(value=rate, color=color, className="mb-2", style={"height": "12px"}),
                    dbc.Row([
                        dbc.Col([html.Span("Успешность: ", className="text-muted"), html.Strong(f"{rate}%", className=f"text-{color}")]),
                        dbc.Col([html.Span("Всего: ", className="text-muted"), html.Strong(f"{total}")]),
                        dbc.Col([html.Span("OK: ", className="text-muted"), html.Strong(f"{ok}", className="text-success")]),
                        dbc.Col([html.Span("FAIL: ", className="text-muted"), html.Strong(f"{fail}", className="text-danger")]),
                        dbc.Col([html.Span("ERROR: ", className="text-muted"), html.Strong(f"{error}", className="text-warning")]),
                    ]),
                ])
            ], className="shadow-sm")
        ], width=8),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H6("Связанные проверки", className="mb-2"),
                    html.Ul(checks_list, className="list-unstyled mb-0") if checks_list else html.P("Нет проверок", className="text-muted small"),
                ])
            ], className="shadow-sm")
        ], width=4),
    ], className="g-3")
