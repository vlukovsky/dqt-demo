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


def get_active_alerts():
    """Получить активные алерты"""
    return MOCK_ALERTS[MOCK_ALERTS["status"] == "active"].sort_values(
        "created_at", ascending=False
    )


def get_alerts_count_by_status():
    """Статистика алертов по статусам"""
    return MOCK_ALERTS.groupby("status").size().to_dict()
