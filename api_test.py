import requests
import json
import pandas as pd
from dotenv import load_dotenv
from datetime import datetime, timedelta
import os 

# ==========================================
# CONFIGURATION
# ==========================================
BASE_URL = "https://vicapipro.veticareapp.com/v1/api"
LOGIN_URL = f"{BASE_URL}/signin"

HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json, application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
}

# Use relative path for portability
DATASETS_DIR = os.path.join(os.getcwd(), "data", "raw")

def sign_in():
    """Test login and return authentication data if successful."""
    print(f"--- Attempting Login to: {LOGIN_URL} ---")
    
    payload = {
        "emailOrUsername": os.getenv("EMAIL_OR_USERNAME"),
        "password": os.getenv("PASSWORD"),
        "clinicCode": os.getenv("CLINIC_CODE")
    }

    try:
        response = requests.post(LOGIN_URL, json=payload, headers=HEADERS)
        if response.status_code == 200:
            print("✅ Login Successful!")
            return response.json()
        else:
            print(f"❌ Login Failed. Code: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        return None

def fetch_clients_data(token, date_from, date_to, is_active=""):
    """
    Fetch clients report. Handles both JSON responses and Direct File Downloads.
    """
    endpoint = f"{BASE_URL}/exportreports/clientsreport"
    params = f"?CreatedAtFrom={date_from}&CreatedAtTo={date_to}&IsActive={is_active}"
    full_url = endpoint + params
    
    print(f"--- Fetching: {full_url} ---")
    
    auth_headers = HEADERS.copy()
    auth_headers["Authorization"] = f"Bearer {token}"
    auth_headers.pop("Content-Type", None) # Remove Content-Type for GET requests
    
    try:
        response = requests.get(full_url, headers=auth_headers)
        
        if response.status_code == 200:
            print("✅ Data fetched successfully!")
            
            # Check if it's a file or JSON based on headers or content
            content_type = response.headers.get("Content-Type", "")
            
            # If the response starts with PK... it's a ZIP/Excel file
            if response.content.startswith(b'PK'):
                return {"type": "file", "content": response.content}
            elif "json" in content_type:
                return {"type": "json", "data": response.json()}
            else:
                # Fallback: Assume file if not JSON
                return {"type": "file", "content": response.content}
        else:
            print(f"❌ Failed. Code: {response.status_code}")
            print(response.text)
            return None

    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def fetch_services_data(token, date_from, date_to, user_id="", service_id="", service_category_id="", time_zone="+02:00"):
    """
    Fetch services report. Handles both JSON responses and Direct File Downloads.
    
    Args:
        token (str): Authentication token from login
        date_from (str): Start date in format 'YYYY-MM-DD'
        date_to (str): End date in format 'YYYY-MM-DD'
        user_id (str): Filter by user ID (optional)
        service_id (str): Filter by service ID (optional)
        service_category_id (str): Filter by service category ID (optional)
        time_zone (str): Timezone offset (default: '+02:00')
    
    Returns:
        dict: Response data with type indicator or None if failed
    """
    endpoint = f"{BASE_URL}/exportreports/servicesReport"
    params = f"?CreatedAtFrom={date_from}&CreatedAtTo={date_to}&UserId={user_id}&ServiceId={service_id}&ServiceCategoryId={service_category_id}&TimeZone={time_zone}"
    full_url = endpoint + params
    
    print(f"--- Fetching: {full_url} ---")
    
    auth_headers = HEADERS.copy()
    auth_headers["Authorization"] = f"Bearer {token}"
    auth_headers.pop("Content-Type", None)  # Remove Content-Type for GET requests
    
    try:
        response = requests.get(full_url, headers=auth_headers)
        
        if response.status_code == 200:
            print("✅ Services data fetched successfully!")
            
            # Check if it's a file or JSON based on headers or content
            content_type = response.headers.get("Content-Type", "")
            
            # If the response starts with PK... it's a ZIP/Excel file
            if response.content.startswith(b'PK'):
                return {"type": "file", "content": response.content}
            elif "json" in content_type:
                return {"type": "json", "data": response.json()}
            else:
                # Fallback: Assume file if not JSON
                return {"type": "file", "content": response.content}
        else:
            print(f"❌ Failed to fetch services. Code: {response.status_code}")
            print(response.text)
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def fetch_pets_data(token, date_from, date_to, is_active="", specie_id=""):
    """
    Fetch pets report. Handles both JSON responses and Direct File Downloads.
    
    Args:
        token (str): Authentication token from login
        date_from (str): Start date in format 'YYYY-MM-DD'
        date_to (str): End date in format 'YYYY-MM-DD'
        is_active (str): Filter by active status (optional)
        specie_id (str): Filter by species ID (optional)
    
    Returns:
        dict: Response data with type indicator or None if failed
    """
    endpoint = f"{BASE_URL}/exportreports/petReport"
    params = f"?CreatedAtFrom={date_from}&CreatedAtTo={date_to}&IsActive={is_active}&SpecieId={specie_id}"
    full_url = endpoint + params
    
    print(f"--- Fetching pets: {full_url} ---")
    
    auth_headers = HEADERS.copy()
    auth_headers["Authorization"] = f"Bearer {token}"
    auth_headers.pop("Content-Type", None)  # Remove Content-Type for GET requests
    
    try:
        response = requests.get(full_url, headers=auth_headers)
        
        if response.status_code == 200:
            print("✅ Pets data fetched successfully!")
            
            # Check if it's a file or JSON based on headers or content
            content_type = response.headers.get("Content-Type", "")
            
            # If the response starts with PK... it's a ZIP/Excel file
            if response.content.startswith(b'PK'):
                return {"type": "file", "content": response.content}
            elif "json" in content_type:
                return {"type": "json", "data": response.json()}
            else:
                # Fallback: Assume file if not JSON
                return {"type": "file", "content": response.content}
        else:
            print(f"❌ Failed to fetch pets. Code: {response.status_code}")
            print(response.text)
            return None

    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def save_data(data_package, filename_base):
    """
    Intelligently saves data based on type (File vs JSON).
    """
    try:
        os.makedirs(DATASETS_DIR, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # CASE 1: BINARY FILE (The one you are getting now)
        if data_package.get("type") == "file":
            filepath = os.path.join(DATASETS_DIR, f"{filename_base}_{timestamp}.xlsx")
            
            # Write bytes mode ('wb')
            with open(filepath, "wb") as f:
                f.write(data_package["content"])
                
            print(f"✅ SUCCESS: Excel file saved to: {filepath}")
            return filepath

        ''' 
        # CASE 2: JSON DATA (Future proofing)
        elif data_package.get("type") == "json":
            data = data_package["data"]
            records = []
            if isinstance(data, list):
                records = data
            elif isinstance(data, dict):
                # Try to find the list inside
                for key in ['data', 'result', 'records']:
                    if key in data and isinstance(data[key], list):
                        records = data[key]
                        break
                if not records: records = [data]

            df = pd.DataFrame(records)
            filepath = os.path.join(DATASETS_DIR, f"{filename_base}_{timestamp}.xlsx")
            df.to_excel(filepath, index=False)
            print(f"✅ SUCCESS: JSON converted and saved to: {filepath}")
            return filepath
            '''

    except Exception as e:
        print(f"❌ Error saving data: {e}")
        return None

if __name__ == "__main__":
    load_dotenv()
    
    auth_data = sign_in()
    
    if auth_data and auth_data.get("success"):
        token = auth_data.get("data", {}).get("token")
        
        if token:
            print("\n" + "="*50)
            
            # Using your dates
            thirty_days_ago = datetime(2025, 12, 3)
            today = datetime(2025, 12, 27)
            
            date_to_str = today.strftime("%Y-%m-%d")
            date_from_str = thirty_days_ago.strftime("%Y-%m-%d")
            
            result = fetch_clients_data(token, date_from_str, date_to_str)
            service_results=fetch_services_data(token,date_from_str,date_to_str)
            
            if result:
                save_data(result, "clients_report")
                save_data(service_results,"services_report")

            # Fetch pets data
        print("\n" + "="*50)
        pets_data = fetch_pets_data(token, date_from_str, date_to_str)

        if pets_data:
            save_data(pets_data, "pets_report")
        else:
            print("❌ Token not found.")
    else:
        print("❌ Login failed.")