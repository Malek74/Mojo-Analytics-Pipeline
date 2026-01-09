import streamlit as st
import pandas as pd
import plotly.express as px
import os
import zipfile
import io
from datetime import datetime, date
import arabic_reshaper
from bidi.algorithm import get_display

#TODO:some things should be data dynamic while others won't 

# ==========================================
# 1. CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="Mojo Vet Analytics",
    page_icon="🐾",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .element-container { direction: rtl; }
    .stMarkdown { text-align: right; }
    div[data-testid="stMetric"] {
        background-color: #e8f5e9;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
    }
    div[data-testid="stMetric"] label {
        color: #1e4620 !important;
        font-weight: 600;
    }
    div[data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #000000 !important;
        font-size: 1.5rem !important;
        font-weight: 700;
    }
</style>
""", unsafe_allow_html=True)

CLEAN_DATA_ROOT = os.path.join(os.getcwd(), "data", "clean")
DATABASE_DIR = os.path.join(os.getcwd(), "database")

# ==========================================
# 2. HELPER FUNCTIONS
# ==========================================
def get_latest_data_dir():
    """Finds the latest dated directory in data/clean."""
    base_dir = CLEAN_DATA_ROOT
    if not os.path.exists(base_dir): return None
    
    # Nested finder: Year -> Month -> Day
    years = [d for d in os.listdir(base_dir) if d.isdigit()]
    if not years: return None
    year_path = os.path.join(base_dir, max(years))
    
    months = [d for d in os.listdir(year_path) if d.isdigit()]
    if not months: return None
    month_path = os.path.join(year_path, max(months))
    
    days = [d for d in os.listdir(month_path) if d.isdigit()]
    if not days: return None
    return os.path.join(month_path, max(days))

def fix_arabic(text):
    if not isinstance(text, str): return text
    return get_display(arabic_reshaper.reshape(text))

def create_zip_export(latest_dir):
    if not latest_dir: return None
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for filename in ["revenue.csv", "clients.csv", "services.csv", "pets.csv", "expenses.csv"]:
            file_path = os.path.join(DATABASE_DIR, filename)
            if os.path.exists(file_path):
                zip_file.write(file_path, filename)
    zip_buffer.seek(0)
    return zip_buffer.getvalue()

@st.cache_data
def load_data():
    data = {}
    files = {
        "revenue": "revenue.csv",
        "clients": "clients.csv",
        "services": "services.csv",
        "pets": "pets.csv",
        "expenses": "expenses.csv" # Added Expenses
    }
    
    latest_dir = DATABASE_DIR
    
    if latest_dir is None:
        st.error("⚠️ No data found. Run pipeline first.")
        for key in files: data[key] = pd.DataFrame()
        return data, None
        
    for key, filename in files.items():
        path = os.path.join(latest_dir, filename)
        if os.path.exists(path):
            data[key] = pd.read_csv(path)
            if "creation_date" in data[key].columns:
                data[key]["creation_date"] = pd.to_datetime(data[key]["creation_date"])
            # Assuming expenses has a date column too
            elif key == "expenses" and "date" in data[key].columns:
                 data[key]["date"] = pd.to_datetime(data[key]["date"])
        else:
            data[key] = pd.DataFrame()
            
    return data, latest_dir

# ==========================================
# 3. LOAD DATA
# ==========================================
dfs, latest_dir = load_data()
revenue_df = dfs["revenue"]
clients_df = dfs["clients"]
services_df = dfs["services"]
pets_df = dfs["pets"]
expenses_df = dfs["expenses"]

# --- SIDEBAR ---
st.sidebar.title("🐾 Mojo Vet")

# Initialize session state for page selection
if 'page' not in st.session_state:
    st.session_state.page = "🏠 Overview"

# Navigation buttons
st.sidebar.subheader("Navigate")
if st.sidebar.button("🏠 Overview", use_container_width=True):
    st.session_state.page = "🏠 Overview"
if st.sidebar.button("💸 Financial Performance", use_container_width=True):
    st.session_state.page = "💸 Financial Performance"
if st.sidebar.button("🩺 Operations", use_container_width=True):
    st.session_state.page = "🩺 Operations"
if st.sidebar.button("👥 Clients", use_container_width=True):
    st.session_state.page = "👥 Clients"

page = st.session_state.page
st.sidebar.markdown("---")

# Global Date Filter
min_date = date(2020, 1, 1)
max_date = date.today()

if not revenue_df.empty:
    min_date = revenue_df['creation_date'].min().date()
    max_date = revenue_df['creation_date'].max().date()

st.sidebar.header("📅 Date Filter")
from_date = st.sidebar.date_input("From", min_date, min_value=min_date, max_value=max_date)
to_date = st.sidebar.date_input("To", max_date, min_value=min_date, max_value=max_date)

# Filter Logic
def filter_df(df, date_col='creation_date'):
    if df.empty or date_col not in df.columns: return df
    mask = (df[date_col].dt.date >= from_date) & (df[date_col].dt.date <= to_date)
    return df.loc[mask]

rev_filtered = filter_df(revenue_df)
clients_filtered = filter_df(clients_df)
services_filtered = filter_df(services_df)
pets_filtered = filter_df(pets_df)
# Handle Expenses Date Column (might be 'date' or 'creation_date')
exp_date_col = 'date' if not expenses_df.empty and 'date' in expenses_df.columns else 'creation_date'
expenses_filtered = filter_df(expenses_df, exp_date_col)

# Export
if latest_dir:
    zip_data = create_zip_export(latest_dir)
    if zip_data:
        st.sidebar.download_button("📥 Download All Data", zip_data, f"mojo_data_{datetime.now().date()}.zip", "application/zip")

# ==========================================
# 4. PAGE LOGIC
# ==========================================

if page == "🏠 Overview":
    st.title("📊 Overview")
    
    # KPIs
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    
    total_rev = rev_filtered['paid'].sum() if not rev_filtered.empty else 0
    total_exp = expenses_filtered['amount'].sum() if not expenses_filtered.empty else 0
    net_profit = total_rev - total_exp
    
    kpi1.metric("💰 Total Revenue", f"{total_rev:,.0f} EGP")
    kpi2.metric("💸 Total Expenses", f"{total_exp:,.0f} EGP")
    kpi3.metric("📈 Net Profit", f"{net_profit:,.0f} EGP", delta_color="normal")
    
    new_clients = len(clients_filtered) if not clients_filtered.empty else 0
    kpi4.metric("👥 New Clients", new_clients)

    st.markdown("---")
    
    # Revenue Trend
    st.subheader("Revenue Trend Over Time")
    if not rev_filtered.empty:
        # Aggregate Revenue
        daily_rev = rev_filtered.set_index('creation_date').resample('W')['paid'].sum().reset_index()
        daily_rev.columns = ['date', 'amount']
        
        fig = px.line(daily_rev, x='date', y='amount', 
                      color_discrete_sequence=['#00CC96'],
                      labels={'date': 'Date', 'amount': 'Revenue (EGP)'})
        fig.update_traces(line=dict(width=3))
        st.plotly_chart(fig, use_container_width=True)

elif page == "💸 Financial Performance":
    st.title("💸 Financial Performance")
    kpi1,kpi2,kpi3=st.columns(3)
     #TODO: mean bill amount from sevuce or revenue?
    kpi1.metric("Mean Bill Amount", f"{rev_filtered['paid'].mean():,.0f} EGP")
    kpi2.metric("Mean Bill Cost", f"{services_filtered['cost'].mean():,.0f} EGP")
    kpi3.metric("Number of Bills", f"{len(rev_filtered):,.0f}")
elif page == "🩺 Operations":
    st.title("🩺 Operations")
    if not services_filtered.empty:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Top Services (By Volume)")
            top_vol = services_filtered.groupby('service')['quantity'].sum().sort_values(ascending=False).head(10).reset_index()
            fig_vol = px.bar(top_vol, x='quantity', y='service', orientation='h', color_continuous_scale='Greens')
            st.plotly_chart(fig_vol, use_container_width=True)
        with col2:
            st.subheader("Top Services (By Value)")
            top_val = services_filtered.groupby('service')['sale_price'].sum().sort_values(ascending=False).head(10).reset_index()
            top_val['sales'] = top_val['sale_price']
            fig_val = px.bar(top_val, x='sales', y='service', orientation='h', color_continuous_scale='Greens')
            st.plotly_chart(fig_val, use_container_width=True)

        col3,col4=st.columns(2)
        with col3:
            st.subheader("Doctors' Performance ")
            docs=services_df["doctor"].value_counts()
            docs=docs.reset_index()
            docs.columns=["doctor","Number of Appointments"]
            fig_docs = px.bar(docs, x='Number of Appointments', y='doctor', orientation='v', color_continuous_scale='Greens')
            st.plotly_chart(fig_docs, use_container_width=True)
        with col4:
            #staff 
            pass
    else:
        st.info("ℹ️ No services data available yet. Ensure 'services.csv' is in the processed folder.")

elif page == "👥 Clients":
    st.title("👥 Client Insights")
    
    # KPIs
    kpi1, kpi2, kpi3 = st.columns(3)
    
    total_clients = len(clients_df) if not clients_df.empty else 0
    clients_with_debt = revenue_df[revenue_df['debit'] > 0]['client'].nunique() if not revenue_df.empty else 0
    active_clients = clients_filtered[clients_filtered['status']=='Active'].count()[0]
    
    # Group by date to see client growth over time
    if not clients_filtered.empty:
        three_months_ago = clients_df['creation_date'].max() - pd.DateOffset(months=3)
        clients_growth = clients_df[clients_df['creation_date'] >= three_months_ago].groupby('creation_date').size().reset_index(name='New Clients')
    kpi1.metric("Total Clients", total_clients)
    kpi2.metric("New Clients", active_clients)
    kpi3.metric("Clients with Debt", clients_with_debt)
    
    st.markdown("---")
    
    # Client Growth
    if not clients_growth.empty:
        fig_growth = px.line(clients_growth, x='creation_date', y='New Clients', title="Client Growth", color_discrete_sequence=['#00CC96'])
        st.plotly_chart(fig_growth, use_container_width=True)        
    
    st.markdown("---")
    
    # Top Debitors and Top Payees
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Highest Debitors")
        if not revenue_df.empty:
            top_debitors = revenue_df.groupby('client')['debit'].sum()
            top_debitors=top_debitors[top_debitors>0].sort_values(ascending=False).head(10)
            top_debitors=top_debitors.reset_index()
            fig_debitors = px.bar(
                top_debitors, 
                x='client', 
                y='debit', 
                labels={'client': 'Client', 'debit': 'Debit Amount'},
                color_discrete_sequence=['#00CC96']
            )
            fig_debitors.update_layout(xaxis_tickangle=-45, showlegend=False)
            st.plotly_chart(fig_debitors, use_container_width=True)
        else:
            st.info("No debt data available")
    
    with col2:
        st.subheader("Highest Payees")
        if not revenue_df.empty:
            top_payees = revenue_df.groupby('client')['paid'].sum().sort_values(ascending=False).head(10).reset_index()
            fig_payees = px.bar(
                top_payees, 
                x='client', 
                y='paid', 
                color_discrete_sequence=['#00CC96'],
                labels={'client': 'Client', 'paid': 'Paid Amount'}
            )
            fig_payees.update_layout(xaxis_tickangle=-45, showlegend=False)
            st.plotly_chart(fig_payees, use_container_width=True)
        else:
            st.info("No payment data available")
