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

# Analisis jumlah penjualan per kategori
category_sales = sales_data.groupby('product_category_name_english').agg(
    total_sales=('product_id', 'count')
).reset_index().sort_values(by='total_sales', ascending=False)

# Analisis pendapatan per kategori
category_revenue = sales_data.groupby('product_category_name_english').agg(
    total_revenue=('price', 'sum')
).reset_index().sort_values(by='total_revenue', ascending=False)

# Menggabungkan order_payments_df dengan orders_df
merged_df = order_payments_df.merge(orders_df, on="order_id", how="left")
merged_df["order_purchase_timestamp"] = pd.to_datetime(merged_df["order_purchase_timestamp"])
merged_df["order_month"] = merged_df["order_purchase_timestamp"].dt.to_period("M")

# Distribusi metode pembayaran
payment_counts = order_payments_df["payment_type"].value_counts()

# Distribusi transaksi per bulan
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
            st.write("Grafik ini menunjukkan 10 kategori produk dengan penjualan tertinggi. Kategori 'bed_bath_table' memiliki penjualan terbanyak, diikuti oleh 'health_beauty' dan 'sports_leisure'.")
    
    with col2:
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.barh(category_revenue["product_category_name_english"].head(10), category_revenue["total_revenue"].head(10), color='orange')
        ax.set_xlabel("Total Revenue")
        ax.set_ylabel("Product Category")
        ax.set_title("Top 10 Product Categories by Revenue")
        st.pyplot(fig)
        with st.expander("Penjelasan Visualisasi"):
            st.write("Grafik ini menunjukkan 10 kategori produk dengan pendapatan tertinggi. 'health_beauty' memiliki pendapatan tertinggi, diikuti oleh 'watches_gifts' dan 'bed_bath_table'.")

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
            st.write("Grafik ini menunjukkan distribusi metode pembayaran yang digunakan pelanggan. Mayoritas pembayaran dilakukan menggunakan kartu kredit.")
    
    with col2:
        fig, ax = plt.subplots(figsize=(6, 4))
        monthly_sales.plot(kind='line', marker='o', color='red', ax=ax)
        ax.set_xlabel("Month")
        ax.set_ylabel("Number of Transactions")
        ax.set_title("Monthly Sales Trend")
        st.pyplot(fig)
        with st.expander("Penjelasan Visualisasi"):
            st.write("Grafik ini menunjukkan tren penjualan bulanan. Terlihat bahwa jumlah transaksi mengalami fluktuasi sepanjang waktu.")
