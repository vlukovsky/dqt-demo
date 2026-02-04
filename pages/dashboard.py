"""
Главный дашборд DQT
"""
import dash
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
from mock_data import (
    MOCK_CHECKS, MOCK_RESULTS, 
    get_dashboard_stats, get_trend_data, 
    get_checks_by_domain, get_checks_by_type
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


def layout():
    stats = get_dashboard_stats(MOCK_RESULTS)
    
    return dbc.Container([
        # Заголовок
        dbc.Row([
            dbc.Col([
                html.H2("Дашборд Data Quality", className="mb-0"),
                html.P("Обзор состояния качества данных за последние 7 дней", className="text-muted"),
            ], width=8),
            dbc.Col([
                dbc.Button([
                    html.I(className="fas fa-sync-alt me-2"),
                    "Обновить"
                ], id="btn-refresh", color="outline-primary", className="me-2"),
                dbc.Button([
                    html.I(className="fas fa-download me-2"),
                    "Экспорт"
                ], color="outline-secondary"),
            ], width=4, className="text-end"),
        ], className="mb-4 align-items-center"),
        
        # KPI карточки
        dbc.Row([
            dbc.Col(create_kpi_card(
                "Всего запусков", 
                f"{stats['total_runs']:,}", 
                "fa-play-circle", 
                "primary",
                delta=5
            ), width=3),
            dbc.Col(create_kpi_card(
                "Успешность", 
                f"{stats['success_rate']}%", 
                "fa-check-circle", 
                "success",
                delta=2
            ), width=3),
            dbc.Col(create_kpi_card(
                "Проверок FAIL", 
                f"{stats['failed_runs']}", 
                "fa-exclamation-triangle", 
                "danger",
                delta=-8
            ), width=3),
            dbc.Col(create_kpi_card(
                "Уникальных таблиц", 
                f"{stats['unique_tables']}", 
                "fa-database", 
                "info"
            ), width=3),
        ], className="mb-4 g-3"),
        
        # Графики - первый ряд
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.I(className="fas fa-chart-area me-2"),
                        "Тренд результатов проверок"
                    ]),
                    dbc.CardBody([
                        dcc.Graph(id="trend-chart", style={"height": "300px"})
                    ])
                ], className="shadow-sm")
            ], width=8),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.I(className="fas fa-chart-pie me-2"),
                        "По типам проверок"
                    ]),
                    dbc.CardBody([
                        dcc.Graph(id="type-chart", style={"height": "300px"})
                    ])
                ], className="shadow-sm")
            ], width=4),
        ], className="mb-4"),
        
        # Графики - второй ряд
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.I(className="fas fa-chart-bar me-2"),
                        "Результаты по доменам"
                    ]),
                    dbc.CardBody([
                        dcc.Graph(id="domain-chart", style={"height": "300px"})
                    ])
                ], className="shadow-sm")
            ], width=6),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.I(className="fas fa-list me-2"),
                        "Последние проблемы"
                    ]),
                    dbc.CardBody([
                        html.Div(id="recent-issues")
                    ])
                ], className="shadow-sm")
            ], width=6),
        ], className="mb-4"),
        
        # Автообновление
        dcc.Interval(id="interval-component", interval=60*1000, n_intervals=0),
        
    ], fluid=True, className="py-3")


@callback(
    Output("trend-chart", "figure"),
    Input("interval-component", "n_intervals")
)
def update_trend_chart(n):
    trend_data = get_trend_data(MOCK_RESULTS, days=30)
    
    # Создаем area chart со стеком
    fig = px.area(
        trend_data,
        x="run_date",
        y="count",
        color="check_status_name",
        color_discrete_map={
            "OK": "#28a745",
            "FAIL": "#dc3545", 
            "ERROR": "#fd7e14",
            "SKIP": "#6c757d"
        },
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
    type_data = get_checks_by_type(MOCK_RESULTS)
    
    # Только последние результаты
    latest = MOCK_RESULTS.sort_values("run_datetime").drop_duplicates(
        subset=["check_id"], keep="last"
    )
    
    type_summary = latest.groupby("check_type_name")["check_status_name"].value_counts().unstack(fill_value=0)
    
    fig = go.Figure(data=[
        go.Pie(
            labels=type_summary.index,
            values=type_summary.sum(axis=1),
            hole=0.4,
            marker_colors=px.colors.qualitative.Set2,
        )
    ])
    
    fig.update_layout(
        margin=dict(l=20, r=20, t=20, b=20),
        showlegend=True,
        legend=dict(font=dict(size=10)),
    )
    
    return fig


@callback(
    Output("domain-chart", "figure"),
    Input("interval-component", "n_intervals")
)
def update_domain_chart(n):
    domain_data = get_checks_by_domain(MOCK_RESULTS)
    
    fig = px.bar(
        domain_data,
        x="domain",
        y="count",
        color="check_status_name",
        barmode="group",
        color_discrete_map={
            "OK": "#28a745",
            "FAIL": "#dc3545",
            "ERROR": "#fd7e14", 
            "SKIP": "#6c757d"
        },
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
def update_recent_issues(n):
    # Последние FAIL/ERROR
    issues = MOCK_RESULTS[
        MOCK_RESULTS["check_status_name"].isin(["FAIL", "ERROR"])
    ].sort_values("run_datetime", ascending=False).head(5)
    
    if issues.empty:
        return html.P("Нет проблем 🎉", className="text-success")
    
    items = []
    for _, row in issues.iterrows():
        status_color = "danger" if row["check_status_name"] == "FAIL" else "warning"
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
                        html.Small(
                            row["run_datetime"].strftime("%d.%m %H:%M"),
                            className="text-muted"
                        ),
                    ], width=3, className="text-end"),
                ]),
            ], className="py-2", action=True, href=f"/check/{row['check_id']}")
        )
    
    return dbc.ListGroup(items, flush=True)
