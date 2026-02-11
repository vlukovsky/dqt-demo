"""
DQT - Data Quality Tool UI
Демо-версия на Plotly Dash
"""
import dash
from dash import Dash, html, dcc
import dash_bootstrap_components as dbc

from components.navbar import create_navbar
from components.sidebar import create_sidebar

# Инициализация приложения
app = Dash(
    __name__,
    use_pages=True,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        dbc.icons.FONT_AWESOME,
        "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap"
    ],
    suppress_callback_exceptions=True,
    title="DQT - Data Quality Tool",
    update_title="DQT | Загрузка...",
)

server = app.server

# Глобальный обработчик ошибок -- показываем понятные сообщения
app.config.suppress_callback_exceptions = True

# Главный layout
app.layout = html.Div([
    dcc.Location(id="url", refresh=False),
    
    # Store для текущей роли пользователя
    dcc.Store(id="user-role-store", data="admin", storage_type="local"),
    # Store для настроек персонализации дашборда
    dcc.Store(id="dashboard-settings-store", data={
        "show_trend": True, "show_type": True, "show_domain": True, "show_issues": True,
    }, storage_type="local"),
    # Store для сохранённых фильтров
    dcc.Store(id="saved-filters-store", data=[], storage_type="local"),
    
    # Navbar
    create_navbar(),
    
    # Основной контент
    dbc.Container([
        dbc.Row([
            # Sidebar
            dbc.Col(
                create_sidebar(),
                id="sidebar-col",
                width=2,
                className="bg-light border-end p-0 sidebar-col",
                style={"position": "sticky", "top": "56px", "height": "calc(100vh - 56px)"}
            ),
            
            # Page content
            dbc.Col(
                dash.page_container,
                width=10,
                className="p-0 content-col",
                style={"minHeight": "calc(100vh - 56px)", "backgroundColor": "#f8f9fa"}
            ),
        ], className="g-0"),
    ], fluid=True, className="p-0"),
    
], style={"minHeight": "100vh"})


# Custom JavaScript для AG Grid рендереров
app.clientside_callback(
    """
    function(id) {
        // Регистрация кастомных рендереров для AG Grid
        if (window.dashAgGridComponentFunctions) {
            window.dashAgGridComponentFunctions.StatusRenderer = function(params) {
                if (!params.value) return '';
                const colors = {
                    'OK': '#28a745',
                    'FAIL': '#dc3545',
                    'ERROR': '#fd7e14',
                    'SKIP': '#6c757d'
                };
                const color = colors[params.value] || '#6c757d';
                return `<span style="color: ${color}; font-weight: 500;">● ${params.value}</span>`;
            };
            
            window.dashAgGridComponentFunctions.ActiveRenderer = function(params) {
                const isActive = params.value;
                const btnClass = isActive ? 'btn-success' : 'btn-outline-secondary';
                const icon = isActive ? 'fa-toggle-on' : 'fa-toggle-off';
                const title = isActive ? 'Выключить' : 'Включить';
                return `
                    <button class="btn btn-sm ${btnClass} toggle-active-btn" 
                            data-check-id="${params.data.check_id}"
                            title="${title}"
                            style="min-width: 70px;">
                        <i class="fas ${icon} me-1"></i>${isActive ? 'Вкл' : 'Выкл'}
                    </button>
                `;
            };
            
            window.dashAgGridComponentFunctions.PriorityRenderer = function(params) {
                const colors = {
                    'HIGH': 'danger',
                    'MEDIUM': 'warning',
                    'LOW': 'secondary'
                };
                const color = colors[params.value] || 'secondary';
                return `<span class="badge bg-${color}">${params.value}</span>`;
            };
            
            window.dashAgGridComponentFunctions.ScheduleRenderer = function(params) {
                const icons = {
                    'daily': '📅',
                    'hourly': '⏰',
                    'weekly': '📆',
                    'monthly': '🗓️'
                };
                return `${icons[params.value] || ''} ${params.value}`;
            };
            
            window.dashAgGridComponentFunctions.CheckNameRenderer = function(params) {
                return `<a href="/check/${params.data.check_id}" style="text-decoration: none;">${params.value}</a>`;
            };
            
            window.dashAgGridComponentFunctions.CheckLinkRenderer = function(params) {
                return `<a href="/check/${params.data.check_id}" style="text-decoration: none;">${params.value}</a>`;
            };
            
            window.dashAgGridComponentFunctions.ActionsRenderer = function(params) {
                return `
                    <div style="display: flex; gap: 4px;">
                        <a href="/check/${params.data.check_id}" class="btn btn-sm btn-outline-primary" title="Просмотр">
                            <i class="fas fa-eye"></i>
                        </a>
                        <button class="btn btn-sm btn-outline-warning edit-check-btn" 
                                data-check-id="${params.data.check_id}" title="Редактировать"
                                onclick="window.dispatchEvent(new CustomEvent('editCheck', {detail: ${JSON.stringify(params.data)}}))">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-success run-check-btn" 
                                data-check-id="${params.data.check_id}" title="Запустить">
                            <i class="fas fa-play"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-danger delete-check-btn" 
                                data-check-id="${params.data.check_id}" title="Удалить">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                `;
            };
        }
        return window.dash_clientside.no_update;
    }
    """,
    dash.Output("url", "pathname"),
    dash.Input("url", "pathname"),
)


# ============================================================
# Callback: Обновление роли в Store
# ============================================================
@dash.callback(
    dash.Output("user-role-store", "data"),
    dash.Input("role-selector", "value"),
    prevent_initial_call=True
)
def update_user_role(role):
    return role or "admin"


# ============================================================
# Callback: Toggle sidebar на мобильных
# ============================================================
@dash.callback(
    dash.Output("sidebar-col", "className"),
    dash.Input("btn-sidebar-toggle", "n_clicks"),
    dash.State("sidebar-col", "className"),
    prevent_initial_call=True
)
def toggle_sidebar(n_clicks, current_class):
    if "sidebar-hidden" in (current_class or ""):
        return "bg-light border-end p-0 sidebar-col"
    return "bg-light border-end p-0 sidebar-col sidebar-hidden"


# ============================================================
# Callback: скрытие элементов по роли (для страницы проверок)
# ============================================================
@dash.callback(
    [dash.Output("btn-create-check", "style"),
     dash.Output("btn-create-check", "disabled")],
    dash.Input("user-role-store", "data"),
)
def apply_role_checks_page(role):
    if role == "viewer":
        return {"display": "none"}, True
    return {}, False


if __name__ == "__main__":
    print("\n" + "="*60)
    print("DQT - Data Quality Tool Demo")
    print("="*60)
    print("\nOtkroyte v brauzere: http://localhost:8050")
    print("\nDostupnye stranitsy:")
    print("   /         - Dashboard")
    print("   /checks   - Proverki")
    print("   /results  - Istoriya")
    print("   /check/1  - Detali proverki")
    print("\nRezhim razrabotki s hot reload")
    print("="*60 + "\n")
    
    app.run(debug=True, host="0.0.0.0", port=8050)
