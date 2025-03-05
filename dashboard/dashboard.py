import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Load Data
@st.cache_data
def load_data():
    order_items_df = pd.read_csv("https://raw.githubusercontent.com/Amrasykr/dashboard_e-commerce/main/data/order_items_dataset.csv")
    order_payments_df = pd.read_csv("https://raw.githubusercontent.com/Amrasykr/dashboard_e-commerce/main/data/order_payments_dataset.csv")
    orders_df = pd.read_csv("https://raw.githubusercontent.com/Amrasykr/dashboard_e-commerce/main/data/orders_dataset.csv")
    product_category_df = pd.read_csv("https://raw.githubusercontent.com/Amrasykr/dashboard_e-commerce/main/data/product_category_name_translation.csv")
    products_df = pd.read_csv("https://raw.githubusercontent.com/Amrasykr/dashboard_e-commerce/main/data/products_dataset.csv")
    
    return order_items_df, products_df, product_category_df, order_payments_df, orders_df

order_items_df, products_df, product_category_df, order_payments_df, orders_df = load_data()

# Merge data untuk analisis penjualan per kategori
sales_data = order_items_df.merge(
    products_df[['product_id', 'product_category_name']],
    on='product_id', 
    how='left'
)
sales_data = sales_data.merge(product_category_df, on='product_category_name', how='left')

# Konversi tanggal
orders_df["order_purchase_timestamp"] = pd.to_datetime(orders_df["order_purchase_timestamp"])

# Filter berdasarkan rentang tanggal
st.sidebar.header("Filter Data")
start_date = st.sidebar.date_input("Tanggal Mulai", orders_df["order_purchase_timestamp"].min().date())
end_date = st.sidebar.date_input("Tanggal Akhir", orders_df["order_purchase_timestamp"].max().date())

filtered_orders = orders_df[(orders_df["order_purchase_timestamp"].dt.date >= start_date) & (orders_df["order_purchase_timestamp"].dt.date <= end_date)]

# Gabungkan order_items_df dengan filtered_orders
filtered_sales_data = sales_data[sales_data["order_id"].isin(filtered_orders["order_id"])]

# Analisis jumlah penjualan per kategori
category_sales = filtered_sales_data.groupby('product_category_name_english').agg(
    total_sales=('product_id', 'count')
).reset_index().sort_values(by='total_sales', ascending=False)

# Analisis pendapatan per kategori
category_revenue = filtered_sales_data.groupby('product_category_name_english').agg(
    total_revenue=('price', 'sum')
).reset_index().sort_values(by='total_revenue', ascending=False)

# Filter berdasarkan kategori
category_options = ["All"] + list(category_sales["product_category_name_english"].unique())
selected_category = st.sidebar.selectbox("Pilih Kategori Produk", category_options)

if selected_category != "All":
    filtered_sales_data = filtered_sales_data[filtered_sales_data["product_category_name_english"] == selected_category]

# Distribusi metode pembayaran
payment_counts = order_payments_df[order_payments_df["order_id"].isin(filtered_sales_data["order_id"])]
payment_counts = payment_counts["payment_type"].value_counts()

# Distribusi transaksi per bulan
merged_df = order_payments_df.merge(orders_df, on="order_id", how="left")
merged_df["order_purchase_timestamp"] = pd.to_datetime(merged_df["order_purchase_timestamp"])
merged_df["order_month"] = merged_df["order_purchase_timestamp"].dt.to_period("M")
monthly_sales = merged_df.groupby("order_month").size()

# Streamlit Dashboard
st.title("E-Commerce Sales Dashboard")

tabs = st.tabs(["Distribusi Penjualan", "Pola Pembayaran Pelanggan"])

with tabs[0]:
    st.subheader("Distribusi Penjualan Berdasarkan Kategori Produk")
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.barh(category_sales["product_category_name_english"].head(10), category_sales["total_sales"].head(10), color='skyblue')
        ax.set_xlabel("Total Sales")
        ax.set_ylabel("Product Category")
        ax.set_title("Top 10 Product Categories by Sales")
        st.pyplot(fig)
        with st.expander("Penjelasan Visualisasi"):
            st.write("Grafik ini menunjukkan 10 kategori produk dengan penjualan tertinggi berdasarkan rentang tanggal yang dipilih.")
    
    with col2:
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.barh(category_revenue["product_category_name_english"].head(10), category_revenue["total_revenue"].head(10), color='orange')
        ax.set_xlabel("Total Revenue")
        ax.set_ylabel("Product Category")
        ax.set_title("Top 10 Product Categories by Revenue")
        st.pyplot(fig)
        with st.expander("Penjelasan Visualisasi"):
            st.write("Grafik ini menunjukkan 10 kategori produk dengan pendapatan tertinggi berdasarkan rentang tanggal yang dipilih.")

with tabs[1]:
    st.subheader("Waktu dan Pola Pembayaran Pelanggan")
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.bar(payment_counts.index, payment_counts.values, color='green')
        ax.set_xlabel("Payment Method")
        ax.set_ylabel("Count")
        ax.set_title("Distribution of Payment Methods")
        st.pyplot(fig)
        with st.expander("Penjelasan Visualisasi"):
            st.write("Grafik ini menunjukkan distribusi metode pembayaran berdasarkan kategori produk yang dipilih.")
    
    with col2:
        fig, ax = plt.subplots(figsize=(6, 4))
        monthly_sales.plot(kind='line', marker='o', color='red', ax=ax)
        ax.set_xlabel("Month")
        ax.set_ylabel("Number of Transactions")
        ax.set_title("Monthly Sales Trend")
        st.pyplot(fig)
        with st.expander("Penjelasan Visualisasi"):
            st.write("Grafik ini menunjukkan tren penjualan bulanan berdasarkan kategori produk yang dipilih.")
