import requests
import json
import pandas as pd
from dotenv import load_dotenv
from datetime import datetime, timedelta
import os 
import logging
from Constants import BASE_URL, HEADERS, ENDPOINTS ,DATASETS_DIR

# ==========================================
# CONFIGURATION
# ==========================================

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Use relative path for portability

def sign_in():
    """Test login and return authentication data if successful."""
    url = ENDPOINTS["signin"]["endpoint"]
    logger.info(f"--- Attempting Login to: {url} ---")
    
    payload = {
        "emailOrUsername": os.getenv("EMAIL_OR_USERNAME"),
        "password": os.getenv("PASSWORD"),
        "clinicCode": os.getenv("CLINIC_CODE")
    }

    try:
        response = requests.post(url, json=payload, headers=HEADERS)
        if response.status_code == 200:
            logger.info("Login Successful!")
            return response.json()
        else:
            logger.error(f"Login Failed. Code: {response.status_code}")
            logger.error(f"Response: {response.text}")
            return None
    except Exception as e:
        logger.error(f"Connection Error: {e}")
        return None

def fetch_data(token, endpoint_key, dynamic_params={}):
    """
    Generic fetch function using requests params dictionary.
    """
    # 1. Validation
    if endpoint_key not in ENDPOINTS:
        logger.error(f"Endpoint '{endpoint_key}' not found in Constants.")
        return None
        
    config = ENDPOINTS[endpoint_key]
    url = config["endpoint"]
    
    # 2. Prepare Params (Merge defaults with dynamic ones)
    # Start with defaults from Constants (if any), then overwrite with dynamic dates
    params = config.get("params", {}).copy() 
    params.update(dynamic_params)
    
    logger.info(f"--- Fetching: {endpoint_key} ---")
    logger.info(f"--- Params: {params} ---")
    
    # 3. Auth Headers
    auth_headers = HEADERS.copy()
    auth_headers["Authorization"] = f"Bearer {token}"
    auth_headers.pop("Content-Type", None) # Remove Content-Type for GET requests
    
    try:
        # 4. Request (requests handles the ?key=value logic automatically)
        response = requests.get(url, headers=auth_headers, params=params)
        
        if response.status_code == 200:
            logger.info(f"{endpoint_key} fetched successfully!")
            
            content_type = response.headers.get("Content-Type", "")
            
            # Check for Excel/Zip signature (PK) or JSON
            if response.content.startswith(b'PK'):
                return {"type": "file", "content": response.content}
            elif "json" in content_type:
                return {"type": "json", "data": response.json()}
            else:
                # Fallback to file if unknown
                return {"type": "file", "content": response.content}
        else:
            logger.error(f"Failed to fetch {endpoint_key}. Code: {response.status_code}")
            logger.error(f"Error: {response.text}")
            return None

    except Exception as e:
        logger.error(f"Connection Error: {e}")
        return None

def save_data(data_package, filename_base):
    """
    Intelligently saves data based on type (File vs JSON).
    """
    if not data_package:
        return None

    try:
        # Create directory structure: data/raw/YYYY/MM/DD
        now = datetime.now()
        year = now.strftime("%Y")
        month = now.strftime("%m")
        day = now.strftime("%d")

        target_dir = os.path.join(DATASETS_DIR, "raw", year, month, day)
        os.makedirs(target_dir, exist_ok=True)
        
        # CASE 1: BINARY FILE (Excel)
        if data_package.get("type") == "file":
            filepath = os.path.join(target_dir, f"{filename_base}.xlsx")
            with open(filepath, "wb") as f:
                f.write(data_package["content"])
            logger.info(f"💾 Data saved to: {filepath}")
            return filepath
            
        # CASE 2: JSON DATA
        elif data_package.get("type") == "json":
            data = data_package["data"]
            records = []
            if isinstance(data, list):
                records = data
            elif isinstance(data, dict):
                for key in ['data', 'result', 'records']:
                    if key in data and isinstance(data[key], list):
                        records = data[key]
                        break
                if not records: records = [data]

            df = pd.DataFrame(records)
            filepath = os.path.join(target_dir, f"{filename_base}.xlsx")
            df.to_excel(filepath, index=False)
            logger.info(f"JSON converted and saved to: {filepath}")
            return filepath

    except Exception as e:
        logger.error(f"Error saving data: {e}")
        return None

def ingest_data():
    load_dotenv()
    
    auth_data = sign_in()
    
    if auth_data and auth_data.get("success"):
        # Robust token extraction
        token = auth_data.get("data", {}).get("token")
        
        if token:
            logger.info("="*50)
            
            # Dynamic Dates (Last 7 Days)
            today = datetime.now()
            thirty_days_ago = today - timedelta(days=7)
            date_to_str = today.strftime("%Y-%m-%d")
            date_from_str = thirty_days_ago.strftime("%Y-%m-%d")
            
            # Common params to override defaults
            common_params = {
                "CreatedAtFrom": date_from_str,
                "CreatedAtTo": date_to_str
            }
            
            # 1. Clients
            clients = fetch_data(token, "clients", common_params)
            save_data(clients, "clients")

            # 2. Services
            services = fetch_data(token, "services", common_params)
            save_data(services, "services")
            
            # 3. Pets
            pets = fetch_data(token, "pets", common_params)
            save_data(pets, "pets")
            
            # 4. Revenue
            revenue = fetch_data(token, "revenue", common_params)
            save_data(revenue, "revenue")

            # 5. Expenses
            expenses = fetch_data(token, "expenses", common_params)
            save_data(expenses, "expenses")
            
        else:
            logger.error("Token not found in login response.")
    else:
        logger.error("Login failed.")

if __name__ == "__main__":
    ingest_data()