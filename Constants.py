import os

BASE_URL = "https://vicapipro.veticareapp.com/v1/api"

ENDPOINTS = {
    "signin":{"endpoint":f"{BASE_URL}/signin"},
    "clients":{"endpoint": f"{BASE_URL}/exportreports/clientsreport", "params": {"CreatedAtFrom": "2025-12-27", "CreatedAtTo": "2025-12-27", "IsActive": "true"}},
    "services":{"endpoint": f"{BASE_URL}/exportreports/servicesReport", "params": {"CreatedAtFrom": "2025-12-27", "CreatedAtTo": "2025-12-27", "IsActive": "true","userId":"","ServiceId":"","ServiceCategoryId":""}},
    "pets":{"endpoint": f"{BASE_URL}/exportreports/petReport", "params": {"CreatedAtFrom": "2025-12-27", "CreatedAtTo": "2025-12-27", "IsActive": "true","SpecieId":""}},
    "revenue":{"endpoint": f"{BASE_URL}/exportreports/revenue", "params": {"CreatedAtFrom": "2025-12-27", "CreatedAtTo": "2025-12-27","Type":""}},
    "expenses":{"endpoint": f"{BASE_URL}/exportreports/expenses", "params": {"CreatedAtFrom": "2025-12-27", "CreatedAtTo": "2025-12-27"}}
}


HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json, application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
}

TIME_ZONE = "+02:00"

DATASETS_DIR = os.path.join(os.getcwd(), "data",)
