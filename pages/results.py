"""
Страница истории результатов
"""
import dash
from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
import dash_ag_grid as dag
import plotly.express as px
from datetime import datetime, timedelta
from mock_data import MOCK_RESULTS, DOMAINS, SCHEMAS, TABLES_BY_SCHEMA
import io

dash.register_page(__name__, path="/results", name="История")


def layout():
    return dbc.Container([
        # Заголовок
        dbc.Row([
            dbc.Col([
                html.H2("История результатов", className="mb-0"),
                html.P("Все результаты проверок качества данных", className="text-muted"),
            ], width=8),
            dbc.Col([
                dbc.Button([
                    html.I(className="fas fa-file-csv me-2"),
                    "Экспорт CSV"
                ], id="btn-export-csv", color="outline-primary", className="me-2"),
                dbc.Button([
                    html.I(className="fas fa-file-excel me-2"),
                    "Экспорт Excel"
                ], id="btn-export-excel", color="outline-success"),
                dcc.Download(id="download-results"),
            ], width=4, className="text-end"),
        ], className="mb-4 align-items-center"),
        
        # Фильтры
        dbc.Card([
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        dbc.Label("Период", className="small"),
                        dcc.Dropdown(
                            id="filter-period",
                            options=[
                                {"label": "Сегодня", "value": "1"},
                                {"label": "Последние 7 дней", "value": "7"},
                                {"label": "Последние 30 дней", "value": "30"},
                                {"label": "Последние 90 дней", "value": "90"},
                            ],
                            value="7",
                            placeholder="Период...",
                            searchable=True,
                            clearable=False,
                            style={"fontSize": "0.9em"},
                        ),
                    ], width=2),
                    dbc.Col([
                        dbc.Label("Статус", className="small"),
                        dcc.Dropdown(
                            id="filter-result-status",
                            options=[
                                {"label": "Все", "value": ""},
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
                        dbc.Label("Домен", className="small"),
                        dcc.Dropdown(
                            id="filter-result-domain",
                            options=[{"label": "Все", "value": ""}] + [
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
                        dbc.Label("Схема", className="small"),
                        dcc.Dropdown(
                            id="filter-result-schema",
                            options=[{"label": "Все", "value": ""}] + [
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
                            id="filter-result-table",
                            options=[],
                            value="",
                            placeholder="Сначала схема...",
                            searchable=True,
                            clearable=False,
                            disabled=True,
                            style={"fontSize": "0.9em"},
                        ),
                    ], width=2),
                    dbc.Col([
                        dbc.Label("Поиск", className="small"),
                        dbc.Input(
                            id="search-results",
                            placeholder="Проверка...",
                            debounce=True,
                            size="sm",
                        ),
                    ], width=2),
                ], className="g-2"),
            ]),
        ], className="mb-3 shadow-sm"),
        
        # Сводка
        dbc.Row([
            dbc.Col([
                html.Div(id="results-summary"),
            ]),
        ], className="mb-3"),
        
        # График распределения
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dcc.Graph(id="results-timeline", style={"height": "200px"})
                    ])
                ], className="shadow-sm")
            ]),
        ], className="mb-3"),
        
        # Таблица результатов
        dag.AgGrid(
            id="results-grid",
            columnDefs=[
                {"field": "run_datetime", "headerName": "Время", "width": 160,
                 "sort": "desc",
                 "valueFormatter": {"function": "d3.timeFormat('%d.%m.%Y %H:%M')(new Date(params.value))"}},
                {"field": "check_name", "headerName": "Проверка", "width": 250,
                 "cellRenderer": "CheckLinkRenderer"},
                {"field": "table_name", "headerName": "Таблица", "width": 180},
                {"field": "check_type_name", "headerName": "Тип", "width": 140},
                {"field": "domain", "headerName": "Домен", "width": 120},
                {"field": "check_status_name", "headerName": "Статус", "width": 100,
                 "cellRenderer": "StatusRenderer"},
                {"field": "execution_time_sec", "headerName": "Время (с)", "width": 100},
                {"field": "rows_checked", "headerName": "Строк", "width": 110,
                 "valueFormatter": {"function": "params.value ? params.value.toLocaleString() : '-'"}},
                {"field": "rows_failed", "headerName": "Ошибок", "width": 100},
                {"field": "owner", "headerName": "Владелец", "width": 120},
            ],
            defaultColDef={"sortable": True, "resizable": True, "filter": True},
            dashGridOptions={
                "pagination": True,
                "paginationPageSize": 20,
                "animateRows": True,
            },
            style={"height": "500px"},
            className="ag-theme-alpine",
        ),
        
    ], fluid=True, className="py-3")


@callback(
    [Output("filter-result-table", "options"),
     Output("filter-result-table", "disabled"),
     Output("filter-result-table", "value")],
    Input("filter-result-schema", "value")
)
def update_result_tables_dropdown(schema):
    """Обновляет список таблиц при выборе схемы."""
    if not schema:
        return [{"label": "Все", "value": ""}], True, ""
    tables = TABLES_BY_SCHEMA.get(schema, [])
    options = [{"label": "Все", "value": ""}] + [{"label": t, "value": t} for t in tables]
    return options, False, ""


@callback(
    [Output("results-grid", "rowData"),
     Output("results-summary", "children"),
     Output("results-timeline", "figure")],
    [Input("filter-period", "value"),
     Input("filter-result-status", "value"),
     Input("filter-result-domain", "value"),
     Input("filter-result-schema", "value"),
     Input("filter-result-table", "value"),
     Input("search-results", "value")]
)
def update_results(period, status, domain, schema, table, search):
    df = MOCK_RESULTS.copy()
    
    # Фильтр по периоду
    days = int(period) if period else 7
    cutoff_date = (datetime.now() - timedelta(days=days)).date()
    df = df[df["run_date"] >= cutoff_date]
    
    # Фильтр по статусу
    if status:
        df = df[df["check_status_name"] == status]
    
    # Фильтр по домену
    if domain:
        df = df[df["domain"] == domain]
    
    # Фильтр по схеме и таблице
    if schema and table:
        full_table = f"{schema}.{table}"
        df = df[df["table_name"] == full_table]
    elif schema:
        df = df[df["table_name"].str.startswith(f"{schema}.")]
    
    # Поиск
    if search:
        search = search.lower()
        df = df[
            df["check_name"].str.lower().str.contains(search, na=False) |
            df["table_name"].str.lower().str.contains(search, na=False)
        ]
    
    # Сортировка
    df = df.sort_values("run_datetime", ascending=False)
    
    # Сводка
    total = len(df)
    ok_count = len(df[df["check_status_name"] == "OK"])
    fail_count = len(df[df["check_status_name"] == "FAIL"])
    error_count = len(df[df["check_status_name"] == "ERROR"])
    
    summary = dbc.Row([
        dbc.Col([
            html.Span(f"Всего: ", className="text-muted"),
            html.Strong(f"{total:,}"),
        ], width="auto"),
        dbc.Col([
            html.Span("OK: ", className="text-muted"),
            html.Strong(f"{ok_count:,}", className="text-success"),
        ], width="auto"),
        dbc.Col([
            html.Span("FAIL: ", className="text-muted"),
            html.Strong(f"{fail_count:,}", className="text-danger"),
        ], width="auto"),
        dbc.Col([
            html.Span("ERROR: ", className="text-muted"),
            html.Strong(f"{error_count:,}", className="text-warning"),
        ], width="auto"),
    ], className="g-4")
    
    # Timeline график
    timeline_data = df.groupby(["run_date", "check_status_name"]).size().reset_index(name="count")
    
    fig = px.bar(
        timeline_data,
        x="run_date",
        y="count",
        color="check_status_name",
        color_discrete_map={
            "OK": "#28a745",
            "FAIL": "#dc3545",
            "ERROR": "#fd7e14",
            "SKIP": "#6c757d"
        },
        labels={"run_date": "", "count": "", "check_status_name": ""},
    )
    
    fig.update_layout(
        margin=dict(l=20, r=20, t=10, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        showlegend=True,
        bargap=0.1,
    )
    
    return df.to_dict("records"), summary, fig


@callback(
    Output("download-results", "data"),
    [Input("btn-export-csv", "n_clicks"),
     Input("btn-export-excel", "n_clicks")],
    [State("filter-period", "value"),
     State("filter-result-status", "value"),
     State("filter-result-domain", "value"),
     State("filter-result-schema", "value"),
     State("filter-result-table", "value"),
     State("search-results", "value")],
    prevent_initial_call=True
)
def export_results(n_csv, n_excel, period, status, domain, schema, table, search):
    from dash import ctx
    
    # Получаем отфильтрованные данные
    df = MOCK_RESULTS.copy()
    
    # Применяем те же фильтры
    days = int(period) if period else 7
    cutoff_date = (datetime.now() - timedelta(days=days)).date()
    df = df[df["run_date"] >= cutoff_date]
    
    if status:
        df = df[df["check_status_name"] == status]
    
    if domain:
        df = df[df["domain"] == domain]
    
    # Фильтр по схеме и таблице
    if schema and table:
        full_table = f"{schema}.{table}"
        df = df[df["table_name"] == full_table]
    elif schema:
        df = df[df["table_name"].str.startswith(f"{schema}.")]
    
    if search:
        search = search.lower()
        df = df[
            df["check_name"].str.lower().str.contains(search, na=False) |
            df["table_name"].str.lower().str.contains(search, na=False)
        ]
    
    df = df.sort_values("run_datetime", ascending=False)
    
    # Выбираем колонки для экспорта
    export_cols = [
        "run_datetime", "check_name", "table_name", "check_type_name",
        "domain", "check_status_name", "execution_time_sec", 
        "rows_checked", "rows_failed", "owner"
    ]
    export_df = df[export_cols].copy()
    export_df.columns = [
        "Время", "Проверка", "Таблица", "Тип",
        "Домен", "Статус", "Время выполнения (сек)",
        "Строк проверено", "Строк с ошибками", "Владелец"
    ]
    
    triggered = ctx.triggered_id
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if triggered == "btn-export-csv":
        return dcc.send_data_frame(
            export_df.to_csv, 
            f"dqt_results_{timestamp}.csv",
            index=False
        )
    elif triggered == "btn-export-excel":
        return dcc.send_data_frame(
            export_df.to_excel,
            f"dqt_results_{timestamp}.xlsx",
            index=False
        )
    
    return None
