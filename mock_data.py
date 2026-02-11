"""
Мок-данные для демо DQT UI
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# Типы проверок
CHECK_TYPES = [
    {"check_type_id": 1, "check_type_name": "Полнота данных", "description": "Проверка на NULL значения"},
    {"check_type_id": 2, "check_type_name": "Уникальность", "description": "Проверка уникальности ключей"},
    {"check_type_id": 3, "check_type_name": "Актуальность", "description": "Проверка даты загрузки"},
    {"check_type_id": 4, "check_type_name": "Согласованность", "description": "Проверка связей между таблицами"},
    {"check_type_id": 5, "check_type_name": "Корректность формата", "description": "Проверка форматов данных"},
    {"check_type_id": 6, "check_type_name": "Бизнес-правило", "description": "Кастомное бизнес-правило"},
]

# Статусы проверок
CHECK_STATUSES = ["OK", "FAIL", "ERROR", "SKIP"]

# Владельцы
OWNERS = ["ivanov_a", "petrov_b", "sidorova_c", "kozlov_d", "novikova_e"]

# Домены
DOMAINS = ["Клиенты", "Транзакции", "Продукты", "Риски", "Отчетность"]

# Расписания
SCHEDULES = ["daily", "hourly", "weekly", "monthly"]

# Таблицы (полные имена для совместимости)
TABLES = [
    "dwh.f_transactions",
    "dwh.d_customers", 
    "dwh.d_products",
    "dwh.f_balances",
    "dwh.d_accounts",
    "dwh.f_payments",
    "dwh.d_branches",
    "staging.stg_customers",
    "staging.stg_transactions",
    "mart.customer_profile",
    "mart.daily_summary",
    "mart.risk_scores",
]

# Схемы
SCHEMAS = ["dwh", "staging", "mart"]

# Таблицы по схемам
TABLES_BY_SCHEMA = {
    "dwh": [
        "f_transactions", 
        "d_customers", 
        "d_products", 
        "f_balances", 
        "d_accounts", 
        "f_payments", 
        "d_branches"
    ],
    "staging": [
        "stg_customers", 
        "stg_transactions"
    ],
    "mart": [
        "customer_profile", 
        "daily_summary", 
        "risk_scores"
    ],
}


def generate_checks(n=50):
    """Генерация списка проверок"""
    checks = []
    for i in range(1, n + 1):
        check_type = random.choice(CHECK_TYPES)
        table = random.choice(TABLES)
        checks.append({
            "check_id": i,
            "check_name": f"check_{table.split('.')[-1]}_{check_type['check_type_name'][:3].lower()}_{i}",
            "table_name": table,
            "schema_name": table.split('.')[0],
            "check_type_id": check_type["check_type_id"],
            "check_type_name": check_type["check_type_name"],
            "description": f"Проверка {check_type['check_type_name'].lower()} для таблицы {table}",
            "owner": random.choice(OWNERS),
            "domain": random.choice(DOMAINS),
            "schedule_main_value": random.choice(SCHEDULES),
            "is_active": random.random() > 0.1,
            "created_at": datetime.now() - timedelta(days=random.randint(1, 365)),
            "last_run": datetime.now() - timedelta(hours=random.randint(1, 72)),
            "last_status": random.choices(CHECK_STATUSES, weights=[0.7, 0.2, 0.05, 0.05])[0],
            "sql_script": generate_sql_script(check_type["check_type_name"], table),
            "threshold": random.choice([0, 0.01, 0.05, 0.1]),
            "priority": random.choice(["HIGH", "MEDIUM", "LOW"]),
        })
    return pd.DataFrame(checks)


def generate_sql_script(check_type: str, table: str) -> str:
    """Генерация примера SQL скрипта для проверки"""
    scripts = {
        "Полнота данных": f"""-- Проверка полноты данных
SELECT 
    COUNT(*) as total_rows,
    SUM(CASE WHEN important_field IS NULL THEN 1 ELSE 0 END) as null_count,
    ROUND(100.0 * SUM(CASE WHEN important_field IS NULL THEN 1 ELSE 0 END) / COUNT(*), 2) as null_pct
FROM {table}
WHERE load_date = CURRENT_DATE - 1;""",
        
        "Уникальность": f"""-- Проверка уникальности
SELECT 
    business_key,
    COUNT(*) as duplicate_count
FROM {table}
WHERE load_date = CURRENT_DATE - 1
GROUP BY business_key
HAVING COUNT(*) > 1;""",
        
        "Актуальность": f"""-- Проверка актуальности данных
SELECT 
    MAX(load_date) as last_load_date,
    CURRENT_DATE - MAX(load_date) as days_since_load
FROM {table}
HAVING CURRENT_DATE - MAX(load_date) > 1;""",
        
        "Согласованность": f"""-- Проверка согласованности (referential integrity)
SELECT 
    a.foreign_key_id,
    COUNT(*) as orphan_count
FROM {table} a
LEFT JOIN dwh.d_reference b ON a.foreign_key_id = b.id
WHERE b.id IS NULL
  AND a.load_date = CURRENT_DATE - 1
GROUP BY a.foreign_key_id;""",
        
        "Корректность формата": f"""-- Проверка корректности формата
SELECT 
    id,
    email_field
FROM {table}
WHERE email_field !~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{{2,}}$'
  AND load_date = CURRENT_DATE - 1;""",
        
        "Бизнес-правило": f"""-- Бизнес-правило: сумма не может быть отрицательной
SELECT 
    id,
    amount
FROM {table}
WHERE amount < 0
  AND transaction_type = 'CREDIT'
  AND load_date = CURRENT_DATE - 1;""",
    }
    return scripts.get(check_type, f"SELECT * FROM {table} LIMIT 10;")


def generate_results(checks_df, days=30):
    """Генерация истории результатов проверок"""
    results = []
    result_id = 1
    
    for _, check in checks_df.iterrows():
        # Генерируем результаты за последние N дней
        for day in range(days):
            run_date = datetime.now() - timedelta(days=day)
            
            # Не все проверки запускаются каждый день
            if check["schedule_main_value"] == "daily" or random.random() > 0.3:
                status = random.choices(
                    CHECK_STATUSES, 
                    weights=[0.75, 0.15, 0.05, 0.05]
                )[0]
                
                execution_time = random.uniform(0.5, 30.0)
                rows_checked = random.randint(1000, 10000000)
                rows_failed = 0 if status == "OK" else random.randint(1, int(rows_checked * 0.1))
                
                results.append({
                    "result_id": result_id,
                    "check_id": check["check_id"],
                    "check_name": check["check_name"],
                    "table_name": check["table_name"],
                    "check_type_name": check["check_type_name"],
                    "run_date": run_date.date(),
                    "run_datetime": run_date,
                    "check_status_name": status,
                    "execution_time_sec": round(execution_time, 2),
                    "rows_checked": rows_checked,
                    "rows_failed": rows_failed,
                    "error_message": "Connection timeout" if status == "ERROR" else None,
                    "owner": check["owner"],
                    "domain": check["domain"],
                })
                result_id += 1
    
    return pd.DataFrame(results)


def get_dashboard_stats(results_df, days=7):
    """Статистика для дашборда"""
    recent = results_df[results_df["run_date"] >= (datetime.now() - timedelta(days=days)).date()]
    
    total = len(recent)
    failed = len(recent[recent["check_status_name"] == "FAIL"])
    errors = len(recent[recent["check_status_name"] == "ERROR"])
    success = len(recent[recent["check_status_name"] == "OK"])
    
    return {
        "total_runs": total,
        "failed_runs": failed,
        "error_runs": errors,
        "success_rate": round(success / total * 100, 1) if total > 0 else 0,
        "unique_checks": recent["check_id"].nunique(),
        "unique_tables": recent["table_name"].nunique(),
    }


def get_trend_data(results_df, days=30):
    """Данные для графика тренда"""
    recent = results_df[results_df["run_date"] >= (datetime.now() - timedelta(days=days)).date()]
    
    trend = recent.groupby(["run_date", "check_status_name"]).size().reset_index(name="count")
    return trend


def get_checks_by_domain(results_df):
    """Проверки по доменам"""
    return results_df.groupby(["domain", "check_status_name"]).size().reset_index(name="count")


def get_checks_by_type(results_df):
    """Проверки по типам"""
    return results_df.groupby(["check_type_name", "check_status_name"]).size().reset_index(name="count")


# Инициализация мок-данных при импорте
MOCK_CHECKS = generate_checks(50)
MOCK_RESULTS = generate_results(MOCK_CHECKS, days=30)
MOCK_CHECK_TYPES = pd.DataFrame(CHECK_TYPES)


def get_check_by_id(check_id: int):
    """Получить проверку по ID"""
    check = MOCK_CHECKS[MOCK_CHECKS["check_id"] == check_id]
    if check.empty:
        return None
    return check.iloc[0].to_dict()


def get_check_results(check_id: int, limit: int = 20):
    """Получить историю результатов проверки"""
    results = MOCK_RESULTS[MOCK_RESULTS["check_id"] == check_id].sort_values(
        "run_datetime", ascending=False
    ).head(limit)
    return results


# Каналы оповещений
ALERT_CHANNELS = ["telegram", "email"]

# Статусы алертов
ALERT_STATUSES = ["active", "acknowledged", "resolved"]


def generate_alerts(results_df, n=30):
    """Генерация списка алертов на основе FAIL/ERROR результатов"""
    alerts = []
    
    # Берём только FAIL и ERROR результаты
    failed_results = results_df[
        results_df["check_status_name"].isin(["FAIL", "ERROR"])
    ].sort_values("run_datetime", ascending=False).head(n)
    
    alert_id = 1
    for _, result in failed_results.iterrows():
        severity = "critical" if result["check_status_name"] == "FAIL" else "warning"
        status = random.choices(
            ALERT_STATUSES,
            weights=[0.5, 0.3, 0.2]
        )[0]
        
        channel = random.choice(ALERT_CHANNELS)
        acknowledged_by = random.choice(OWNERS) if status != "active" else None
        resolved_at = result["run_datetime"] + timedelta(hours=random.randint(1, 24)) if status == "resolved" else None
        
        alerts.append({
            "alert_id": alert_id,
            "check_id": result["check_id"],
            "check_name": result["check_name"],
            "table_name": result["table_name"],
            "domain": result["domain"],
            "check_status": result["check_status_name"],
            "severity": severity,
            "status": status,
            "channel": channel,
            "message": f"Проверка {result['check_name']} завершилась со статусом {result['check_status_name']}",
            "created_at": result["run_datetime"],
            "acknowledged_by": acknowledged_by,
            "acknowledged_at": result["run_datetime"] + timedelta(minutes=random.randint(5, 120)) if acknowledged_by else None,
            "resolved_at": resolved_at,
            "owner": result["owner"],
        })
        alert_id += 1
    
    return pd.DataFrame(alerts)


# Инициализация мок-алертов
MOCK_ALERTS = generate_alerts(MOCK_RESULTS, n=30)

# Добавляем поля инцидентов к алертам
def enrich_alerts_with_incidents(alerts_df):
    """Обогащение алертов данными об инцидентах (трекер, комментарии)."""
    alerts_df = alerts_df.copy()
    tracker_tasks = []
    comments_list = []
    for _, row in alerts_df.iterrows():
        has_task = random.random() > 0.5
        tracker_tasks.append({
            "has_task": has_task,
            "task_id": f"DQ-{random.randint(100, 999)}" if has_task else None,
            "task_url": f"https://tracker.example.com/DQ-{random.randint(100, 999)}" if has_task else None,
        })
        n_comments = random.randint(0, 3) if row["status"] != "active" else 0
        comments = []
        for c in range(n_comments):
            comments.append({
                "author": random.choice(OWNERS),
                "text": random.choice([
                    "Проблема воспроизведена, анализирую",
                    "Связано с обновлением ETL-пайплайна",
                    "Исправлено, ждём следующий запуск",
                    "Ложное срабатывание, нужно скорректировать threshold",
                    "Передано команде DWH",
                ]),
                "created_at": (row["created_at"] + timedelta(minutes=random.randint(10, 300))).strftime("%d.%m.%Y %H:%M"),
            })
        comments_list.append(comments)
    alerts_df["tracker_task_id"] = [t["task_id"] for t in tracker_tasks]
    alerts_df["tracker_task_url"] = [t["task_url"] for t in tracker_tasks]
    alerts_df["has_tracker_task"] = [t["has_task"] for t in tracker_tasks]
    alerts_df["comments"] = comments_list
    return alerts_df

MOCK_ALERTS = enrich_alerts_with_incidents(MOCK_ALERTS)


def get_active_alerts():
    """Получить активные алерты"""
    return MOCK_ALERTS[MOCK_ALERTS["status"] == "active"].sort_values(
        "created_at", ascending=False
    )


def get_alerts_count_by_status():
    """Статистика алертов по статусам"""
    return MOCK_ALERTS.groupby("status").size().to_dict()


# ============================================================
# История версий проверок
# ============================================================
def generate_check_versions(checks_df):
    """Генерация истории версий для каждой проверки."""
    versions = []
    version_id = 1
    change_types = [
        "Создание проверки",
        "Изменение SQL-скрипта",
        "Изменение расписания",
        "Изменение threshold",
        "Изменение владельца",
        "Изменение приоритета",
    ]
    for _, check in checks_df.iterrows():
        n_versions = random.randint(1, 5)
        base_date = check["created_at"]
        for v in range(1, n_versions + 1):
            change_date = base_date + timedelta(days=random.randint(0, 30) * v)
            ct = "Создание проверки" if v == 1 else random.choice(change_types[1:])
            versions.append({
                "version_id": version_id,
                "check_id": check["check_id"],
                "version": v,
                "change_type": ct,
                "changed_by": check["owner"] if v == 1 else random.choice(OWNERS),
                "changed_at": change_date,
                "sql_script": check["sql_script"] if v == n_versions else check["sql_script"].replace(
                    "CURRENT_DATE - 1", f"CURRENT_DATE - {random.randint(1, 7)}"
                ),
                "threshold": check["threshold"] if v == n_versions else random.choice([0, 0.01, 0.05]),
                "schedule": check["schedule_main_value"],
                "is_current": v == n_versions,
            })
            version_id += 1
    return pd.DataFrame(versions)


MOCK_CHECK_VERSIONS = generate_check_versions(MOCK_CHECKS)


def get_check_versions(check_id: int):
    """Получить историю версий проверки."""
    versions = MOCK_CHECK_VERSIONS[MOCK_CHECK_VERSIONS["check_id"] == check_id].sort_values(
        "version", ascending=False
    )
    return versions


# ============================================================
# Lineage (граф зависимостей таблиц)
# ============================================================
LINEAGE_GRAPH = {
    "staging.stg_customers": {
        "sources": ["src.crm_customers", "src.crm_contacts"],
        "targets": ["dwh.d_customers"],
    },
    "staging.stg_transactions": {
        "sources": ["src.core_transactions", "src.core_payments"],
        "targets": ["dwh.f_transactions", "dwh.f_payments"],
    },
    "dwh.d_customers": {
        "sources": ["staging.stg_customers"],
        "targets": ["mart.customer_profile", "mart.risk_scores"],
    },
    "dwh.d_products": {
        "sources": ["src.product_catalog"],
        "targets": ["mart.daily_summary"],
    },
    "dwh.d_accounts": {
        "sources": ["src.core_accounts"],
        "targets": ["dwh.f_balances"],
    },
    "dwh.d_branches": {
        "sources": ["src.org_structure"],
        "targets": [],
    },
    "dwh.f_transactions": {
        "sources": ["staging.stg_transactions"],
        "targets": ["mart.daily_summary", "mart.risk_scores"],
    },
    "dwh.f_balances": {
        "sources": ["dwh.d_accounts", "src.core_balances"],
        "targets": ["mart.daily_summary"],
    },
    "dwh.f_payments": {
        "sources": ["staging.stg_transactions"],
        "targets": ["mart.daily_summary"],
    },
    "mart.customer_profile": {
        "sources": ["dwh.d_customers", "dwh.f_transactions"],
        "targets": [],
    },
    "mart.daily_summary": {
        "sources": ["dwh.f_transactions", "dwh.f_payments", "dwh.f_balances", "dwh.d_products"],
        "targets": [],
    },
    "mart.risk_scores": {
        "sources": ["dwh.d_customers", "dwh.f_transactions"],
        "targets": [],
    },
}


def get_lineage(table_name: str):
    """Получить lineage для таблицы в формате Cytoscape."""
    nodes = set()
    edges = []

    info = LINEAGE_GRAPH.get(table_name, {"sources": [], "targets": []})

    # Центральный узел
    nodes.add(table_name)

    # Источники
    for src in info.get("sources", []):
        nodes.add(src)
        edges.append({"source": src, "target": table_name})
        # Второй уровень
        src_info = LINEAGE_GRAPH.get(src, {})
        for src2 in src_info.get("sources", []):
            nodes.add(src2)
            edges.append({"source": src2, "target": src})

    # Потребители
    for tgt in info.get("targets", []):
        nodes.add(tgt)
        edges.append({"source": table_name, "target": tgt})
        tgt_info = LINEAGE_GRAPH.get(tgt, {})
        for tgt2 in tgt_info.get("targets", []):
            nodes.add(tgt2)
            edges.append({"source": tgt, "target": tgt2})

    # Формат Cytoscape
    cyto_elements = []
    for node in nodes:
        layer = "source"
        if node == table_name:
            layer = "center"
        elif node in info.get("targets", []):
            layer = "target"
        elif any(node in LINEAGE_GRAPH.get(t, {}).get("targets", []) for t in info.get("targets", [])):
            layer = "target"
        cyto_elements.append({"data": {"id": node, "label": node.split(".")[-1], "full_name": node, "layer": layer}})
    for edge in edges:
        cyto_elements.append({"data": {"source": edge["source"], "target": edge["target"]}})

    return cyto_elements


# ============================================================
# Шаблоны автоматических проверок
# ============================================================
MOCK_CHECK_TEMPLATES = [
    {
        "template_id": 1,
        "name": "NULL-проверка полей",
        "check_type": "Полнота данных",
        "description": "Проверяет процент NULL-значений в указанном поле",
        "parameters": ["schema", "table", "field"],
        "sql_template": """SELECT 
    COUNT(*) as total,
    SUM(CASE WHEN {field} IS NULL THEN 1 ELSE 0 END) as null_count,
    ROUND(100.0 * SUM(CASE WHEN {field} IS NULL THEN 1 ELSE 0 END) / COUNT(*), 2) as null_pct
FROM {schema}.{table}
WHERE load_date = CURRENT_DATE - 1;""",
        "is_active": True,
        "created_by": "system",
    },
    {
        "template_id": 2,
        "name": "Уникальность ключа",
        "check_type": "Уникальность",
        "description": "Проверяет уникальность бизнес-ключа в таблице",
        "parameters": ["schema", "table", "key_field"],
        "sql_template": """SELECT 
    {key_field},
    COUNT(*) as cnt
FROM {schema}.{table}
WHERE load_date = CURRENT_DATE - 1
GROUP BY {key_field}
HAVING COUNT(*) > 1;""",
        "is_active": True,
        "created_by": "system",
    },
    {
        "template_id": 3,
        "name": "Актуальность загрузки",
        "check_type": "Актуальность",
        "description": "Проверяет, что данные были загружены не позднее N дней назад",
        "parameters": ["schema", "table", "max_days"],
        "sql_template": """SELECT 
    MAX(load_date) as last_load,
    CURRENT_DATE - MAX(load_date) as days_lag
FROM {schema}.{table}
HAVING CURRENT_DATE - MAX(load_date) > {max_days};""",
        "is_active": True,
        "created_by": "system",
    },
    {
        "template_id": 4,
        "name": "Ссылочная целостность",
        "check_type": "Согласованность",
        "description": "Проверяет ссылочную целостность между двумя таблицами",
        "parameters": ["schema", "table", "fk_field", "ref_schema", "ref_table", "ref_field"],
        "sql_template": """SELECT a.{fk_field}, COUNT(*) as orphan_count
FROM {schema}.{table} a
LEFT JOIN {ref_schema}.{ref_table} b ON a.{fk_field} = b.{ref_field}
WHERE b.{ref_field} IS NULL
  AND a.load_date = CURRENT_DATE - 1
GROUP BY a.{fk_field};""",
        "is_active": True,
        "created_by": "system",
    },
    {
        "template_id": 5,
        "name": "Проверка формата email",
        "check_type": "Корректность формата",
        "description": "Проверяет корректность email-адресов",
        "parameters": ["schema", "table", "email_field"],
        "sql_template": """SELECT id, {email_field}
FROM {schema}.{table}
WHERE {email_field} !~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{{2,}}$'
  AND load_date = CURRENT_DATE - 1;""",
        "is_active": True,
        "created_by": "system",
    },
    {
        "template_id": 6,
        "name": "Неотрицательные суммы",
        "check_type": "Бизнес-правило",
        "description": "Проверяет, что суммы транзакций неотрицательны",
        "parameters": ["schema", "table", "amount_field"],
        "sql_template": """SELECT id, {amount_field}
FROM {schema}.{table}
WHERE {amount_field} < 0
  AND load_date = CURRENT_DATE - 1;""",
        "is_active": False,
        "created_by": "ivanov_a",
    },
]


# Роли пользователей
USER_ROLES = {
    "admin": {
        "label": "Администратор",
        "permissions": ["view", "create", "edit", "delete", "run", "settings", "manage_users"],
    },
    "editor": {
        "label": "Редактор",
        "permissions": ["view", "create", "edit", "run"],
    },
    "viewer": {
        "label": "Наблюдатель",
        "permissions": ["view"],
    },
}
