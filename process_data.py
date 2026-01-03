import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import os
import logging
from datetime import datetime
import arabic_reshaper
from bidi.algorithm import get_display
from Constants import DATASETS_DIR

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def clean_clients_data(raw_data_dir, clean_data_dir):
    """
    Load and process clients data from raw Excel file.
    
    Args:
        raw_data_dir (str): Path to raw data directory
        clean_data_dir (str): Path to clean data directory
        
    Returns:
        pd.DataFrame or None: Processed clients dataframe or None if loading failed
    """
    try:
        logger.info("Loading Clients Data...")
        clients_df = pd.read_excel(os.path.join(raw_data_dir, "clients.xlsx"), skiprows=5, usecols=[1,2,3,4,5])
        clients_df.columns = ["name", "id", "phone", "creation_date", "status"]
        clients_df["creation_date"] = pd.to_datetime(clients_df["creation_date"])
        clients_df["phone"] = clients_df["phone"].astype(str).str.split(".").str[0]
        
        # Save cleaned data
        os.makedirs(clean_data_dir, exist_ok=True)
        clients_df.to_csv(os.path.join(clean_data_dir, "clients.csv"), index=False)
        
        logger.info(f"✅ Clients loaded: {clients_df.shape}")
        return clients_df
    except FileNotFoundError:
        logger.warning("⚠️ clients.xlsx not found. Setting clients_df to None.")
        return None
    except Exception as e:
        logger.error(f"❌ Error loading clients data: {e}")
        return None


def clean_pets_data(raw_data_dir, clean_data_dir):
    """
    Load and process pets data from raw Excel file.
    
    Args:
        raw_data_dir (str): Path to raw data directory
        clean_data_dir (str): Path to clean data directory
        
    Returns:
        pd.DataFrame or None: Processed pets dataframe or None if loading failed
    """
    try:
        logger.info("Loading Pets Data...")
        pets_df = pd.read_excel(os.path.join(raw_data_dir, "pets.xlsx"), skiprows=4, header=None, usecols=[1,2,3,4,5,7])
        pets_df.columns = ["pet_name", "code", "creation_date", "status", "type", "client_phone"]
        pets_df["creation_date"] = pd.to_datetime(pets_df["creation_date"])
        pets_df["client_phone"] = pets_df["client_phone"].astype(str).str.split(".").str[0]
        
        # Save cleaned data
        os.makedirs(clean_data_dir, exist_ok=True)
        pets_df.to_csv(os.path.join(clean_data_dir, "pets.csv"), index=False)
        
        logger.info(f"✅ Pets loaded: {pets_df.shape}")
        return pets_df
    except FileNotFoundError:
        logger.warning("⚠️ pets.xlsx not found. Setting pets_df to None.")
        return None
    except Exception as e:
        logger.error(f"❌ Error loading pets data: {e}")
        return None


def clean_services_data(raw_data_dir, clean_data_dir):
    """
    Load and process services data from raw Excel file.
    
    Args:
        raw_data_dir (str): Path to raw data directory
        clean_data_dir (str): Path to clean data directory
        
    Returns:
        pd.DataFrame or None: Processed services dataframe or None if loading failed
    """
    try:
        logger.info("Loading Services Data...")
        services_df = pd.read_excel(os.path.join(raw_data_dir, "services.xlsx"), skiprows=5, header=None, usecols=[1, 2, 3, 4, 5, 7])
        services_df.columns = ["category", "service", "quantity", "cost", "sale_price", "creation_date"]
        services_df["creation_date"] = pd.to_datetime(services_df["creation_date"])
        services_df["quantity"] = pd.to_numeric(services_df["quantity"], errors='coerce')
        services_df["cost"] = pd.to_numeric(services_df["cost"], errors='coerce')
        services_df["sale_price"] = pd.to_numeric(services_df["sale_price"], errors='coerce')
        services_df = services_df.dropna(subset=["sale_price"])
        
        # Save cleaned data
        os.makedirs(clean_data_dir, exist_ok=True)
        services_df.to_csv(os.path.join(clean_data_dir, "services.csv"), index=False)
        
        logger.info(f"✅ Services loaded: {services_df.shape}")
        return services_df
    except FileNotFoundError:
        logger.warning("⚠️ services.xlsx not found. Setting services_df to None.")
        return None
    except Exception as e:
        logger.error(f"❌ Error loading services data: {e}")
        return None


def clean_revenue_data(raw_data_dir, clean_data_dir):
    """
    Load and process revenue data from raw Excel file.
    
    Args:
        raw_data_dir (str): Path to raw data directory
        clean_data_dir (str): Path to clean data directory
        
    Returns:
        pd.DataFrame or None: Processed revenue dataframe or None if loading failed
    """
    try:
        logger.info("Loading Revenue Data...")
        revenue_df = pd.read_excel(os.path.join(raw_data_dir, "revenue.xlsx"), skiprows=5, header=None, usecols=[1,2,3,4,5,6,7,8,10,11])
        revenue_df.columns = ["creation_date", "category", "client", "client_phone", "pet_name", "invoice_code", "amount", "discount", "paid", "debit"]
        revenue_df = revenue_df.iloc[:-2]
        revenue_df["client_phone"] = revenue_df["client_phone"].astype(str).str.split(".").str[0]
        revenue_df["creation_date"] = pd.to_datetime(revenue_df["creation_date"])
        revenue_df = revenue_df.dropna()
        
        # Save cleaned data
        os.makedirs(clean_data_dir, exist_ok=True)
        revenue_df.to_csv(os.path.join(clean_data_dir, "revenue.csv"), index=False)
        
        logger.info(f"✅ Revenue loaded: {revenue_df.shape}")
        return revenue_df
    except FileNotFoundError:
        logger.warning("⚠️ revenue.xlsx not found. Setting revenue_df to None.")
        return None
    except Exception as e:
        logger.error(f"❌ Error loading revenue data: {e}")
        return None


def print_loading_summary(clients_df, pets_df, services_df, revenue_df, inventory_df=None, expenses_df=None):
    """
    Print a summary of all loaded datasets.
    
    Args:
        clients_df: Clients dataframe or None
        pets_df: Pets dataframe or None
        services_df: Services dataframe or None
        revenue_df: Revenue dataframe or None
        inventory_df: Inventory dataframe or None
        expenses_df: Expenses dataframe or None
    """
    logger.info("\n" + "="*50)
    logger.info("DATA LOADING SUMMARY")
    logger.info("="*50)
    logger.info(f"Clients: {'✅ Loaded' if clients_df is not None else '❌ Not loaded'}")
    logger.info(f"Pets: {'✅ Loaded' if pets_df is not None else '❌ Not loaded'}")
    logger.info(f"Services: {'✅ Loaded' if services_df is not None else '❌ Not loaded'}")
    logger.info(f"Revenue: {'✅ Loaded' if revenue_df is not None else '❌ Not loaded'}")
    logger.info(f"Inventory: {'❌ Not loaded' if inventory_df is None else '✅ Loaded'}")
    logger.info(f"Expenses: {'❌ Not loaded' if expenses_df is None else '✅ Loaded'}")
    logger.info("="*50 + "\n")


def main():
    """Main execution function to load all datasets."""
    timestamp = datetime.now().strftime("%Y%m%d")
    raw_data_dir = os.path.join(DATASETS_DIR, f"raw/{timestamp}")
    clean_data_dir = os.path.join(DATASETS_DIR, f"clean/{timestamp}")
    
    # Check if raw data directory exists
    if not os.path.exists(raw_data_dir):
        logger.error(f"Data directory not found: {raw_data_dir}")
        logger.info("Please run api_test.py first to fetch the data")
        raise FileNotFoundError(f"Data directory not found: {raw_data_dir}")
    
    logger.info(f"Loading data from: {raw_data_dir}")
    
    # Load all datasets
    clients_df = clean_clients_data(raw_data_dir, clean_data_dir)
    pets_df = clean_pets_data(raw_data_dir, clean_data_dir)
    services_df = clean_services_data(raw_data_dir, clean_data_dir)
    revenue_df = clean_revenue_data(raw_data_dir, clean_data_dir)
    
    # Inventory and Expenses not available from API yet
    inventory_df = None
    expenses_df = None
    
    # Print summary
    print_loading_summary(clients_df, pets_df, services_df, revenue_df, inventory_df, expenses_df)
    
    return clients_df, pets_df, services_df, revenue_df, inventory_df, expenses_df


# Execute main function when script is run
if __name__ == "__main__":
    clients_df, pets_df, services_df, revenue_df, inventory_df, expenses_df = main()
