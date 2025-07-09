import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import os
from database import get_all_orders, get_all_products, add_product, update_order_status
import subprocess
import time

# Konfigurasi halaman
st.set_page_config(
    page_title="Dashboard UMKM - WhatsApp Order System",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS untuk styling
st.markdown("""
<style>
.main-header {
    text-align: center;
    color: #25D366;
    font-size: 2.5rem;
    margin-bottom: 2rem;
}
.metric-card {
    background: linear-gradient(90deg, #25D366, #128C7E);
    color: white;
    padding: 1rem;
    border-radius: 10px;
    text-align: center;
}
.status-pending { color: #ff9800; }
.status-confirmed { color: #2196f3; }
.status-delivered { color: #4caf50; }
.status-cancelled { color: #f44336; }
</style>
""", unsafe_allow_html=True)

def main():
    st.markdown('<h1 class="main-header">🛍️ Dashboard UMKM - WhatsApp Order System</h1>', unsafe_allow_html=True)
    
    # Sidebar untuk navigasi
    st.sidebar.title("📱 Navigasi")
    page = st.sidebar.selectbox(
        "Pilih Halaman:",
        ["📊 Dashboard", "📋 Kelola Pesanan", "🛍️ Kelola Produk", "💬 WhatsApp Bot", "📈 Laporan"]
    )
    
    if page == "📊 Dashboard":
        show_dashboard()
    elif page == "📋 Kelola Pesanan":
        show_orders_management()
    elif page == "🛍️ Kelola Produk":
        show_products_management()
    elif page == "💬 WhatsApp Bot":
        show_whatsapp_bot()
    elif page == "📈 Laporan":
        show_reports()

def show_dashboard():
    st.header("📊 Dashboard Utama")
    
    # Ambil data pesanan
    orders = get_all_orders()
    products = get_all_products()
    
    if not orders:
        st.info("Belum ada pesanan masuk. Bot WhatsApp siap menerima pesanan!")
        return
    
    # Convert ke DataFrame
    orders_df = pd.DataFrame(orders, columns=[
        'ID', 'Nama Customer', 'No. HP', 'Produk', 'Jumlah', 
        'Harga', 'Total', 'Status', 'Tanggal', 'Alamat'
    ])
    orders_df['Tanggal'] = pd.to_datetime(orders_df['Tanggal'])
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_orders = len(orders_df)
        st.metric("📦 Total Pesanan", total_orders)
    
    with col2:
        total_revenue = orders_df['Total'].sum()
        st.metric("💰 Total Pendapatan", f"Rp {total_revenue:,.0f}")
    
    with col3:
        pending_orders = len(orders_df[orders_df['Status'] == 'pending'])
        st.metric("⏳ Pesanan Pending", pending_orders)
    
    with col4:
        avg_order = orders_df['Total'].mean()
        st.metric("📊 Rata-rata Pesanan", f"Rp {avg_order:,.0f}")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Pesanan per Hari")
        daily_orders = orders_df.groupby(orders_df['Tanggal'].dt.date).size().reset_index()
        daily_orders.columns = ['Tanggal', 'Jumlah Pesanan']
        
        if not daily_orders.empty:
            fig = px.line(daily_orders, x='Tanggal', y='Jumlah Pesanan', 
                         title="Trend Pesanan Harian")
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🥧 Status Pesanan")
        status_counts = orders_df['Status'].value_counts()
        fig = px.pie(values=status_counts.values, names=status_counts.index,
                     title="Distribusi Status Pesanan")
        st.plotly_chart(fig, use_container_width=True)
    
    # Pesanan terbaru
    st.subheader("📋 Pesanan Terbaru")
    recent_orders = orders_df.head(10)
    st.dataframe(recent_orders, use_container_width=True)

def show_orders_management():
    st.header("📋 Kelola Pesanan")
    
    orders = get_all_orders()
    
    if not orders:
        st.info("Belum ada pesanan masuk.")
        return
    
    # Convert ke DataFrame
    orders_df = pd.DataFrame(orders, columns=[
        'ID', 'Nama Customer', 'No. HP', 'Produk', 'Jumlah', 
        'Harga', 'Total', 'Status', 'Tanggal', 'Alamat'
    ])
    
    # Filter
    col1, col2 = st.columns(2)
    with col1:
        status_filter = st.selectbox("Filter Status:", 
                                   ["Semua", "pending", "confirmed", "delivered", "cancelled"])
    with col2:
        search_customer = st.text_input("Cari Nama Customer:")
    
    # Apply filters
    filtered_df = orders_df.copy()
    if status_filter != "Semua":
        filtered_df = filtered_df[filtered_df['Status'] == status_filter]
    if search_customer:
        filtered_df = filtered_df[filtered_df['Nama Customer'].str.contains(search_customer, case=False, na=False)]
    
    # Display orders dengan kemampuan edit status
    for idx, order in filtered_df.iterrows():
        with st.expander(f"Pesanan #{order['ID']} - {order['Nama Customer']}"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.write(f"**Customer:** {order['Nama Customer']}")
                st.write(f"**No. HP:** {order['No. HP']}")
                st.write(f"**Produk:** {order['Produk']}")
                st.write(f"**Jumlah:** {order['Jumlah']}")
            
            with col2:
                st.write(f"**Harga:** Rp {order['Harga']:,.0f}")
                st.write(f"**Total:** Rp {order['Total']:,.0f}")
                st.write(f"**Tanggal:** {order['Tanggal']}")
                st.write(f"**Alamat:** {order['Alamat']}")
            
            with col3:
                current_status = order['Status']
                new_status = st.selectbox(
                    "Status:", 
                    ["pending", "confirmed", "delivered", "cancelled"],
                    index=["pending", "confirmed", "delivered", "cancelled"].index(current_status),
                    key=f"status_{order['ID']}"
                )
                
                if st.button(f"Update Status", key=f"update_{order['ID']}"):
                    update_order_status(order['ID'], new_status)
                    st.success(f"Status pesanan #{order['ID']} berhasil diupdate!")
                    st.rerun()

def show_products_management():
    st.header("🛍️ Kelola Produk")
    
    # Tambah produk baru
    st.subheader("➕ Tambah Produk Baru")
    with st.form("add_product"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Nama Produk")
            price = st.number_input("Harga", min_value=0, step=1000)
        with col2:
            stock = st.number_input("Stok", min_value=0, step=1)
            category = st.text_input("Kategori")
        
        description = st.text_area("Deskripsi")
        
        if st.form_submit_button("Tambah Produk"):
            if name and price > 0:
                add_product(name, price, stock, description, category)
                st.success(f"Produk '{name}' berhasil ditambahkan!")
                st.rerun()
            else:
                st.error("Nama produk dan harga harus diisi!")
    
    # Daftar produk
    st.subheader("📋 Daftar Produk")
    products = get_all_products()
    
    if products:
        products_df = pd.DataFrame(products, columns=[
            'ID', 'Nama', 'Harga', 'Stok', 'Deskripsi', 'Kategori'
        ])
        st.dataframe(products_df, use_container_width=True)
    else:
        st.info("Belum ada produk. Tambahkan produk untuk memulai!")

def show_whatsapp_bot():
    st.header("💬 WhatsApp Bot Management")
    
    # Status bot
    if os.path.exists('bot_status.txt'):
        with open('bot_status.txt', 'r', encoding='utf-8') as f:
            status = f.read().strip()
        
        if status == 'ready':
            st.success("🟢 WhatsApp Bot sedang aktif dan siap menerima pesanan!")
        else:
            st.warning("🟡 WhatsApp Bot belum siap.")
    else:
        st.error("🔴 WhatsApp Bot belum dijalankan.")
    
    # Tombol untuk menjalankan bot
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🚀 Jalankan WhatsApp Bot"):
            st.info("Menjalankan WhatsApp Bot... Silakan scan QR code di terminal.")
            # Anda perlu menjalankan whatsapp_bot.js secara manual
    
    with col2:
        if st.button("🔄 Restart Bot"):
            st.info("Restarting WhatsApp Bot...")
    
    # QR Code
    if os.path.exists('qr_code.txt'):
        st.subheader("📱 QR Code untuk WhatsApp")
        with open('qr_code.txt', 'r', encoding='utf-8') as f:
            qr_data = f.read().strip()
        
        if qr_data:
            st.code(qr_data)
            st.info("Scan QR code di atas dengan WhatsApp Anda (WhatsApp > Pengaturan > Perangkat Tertaut)")
    
    # Log pesan
    st.subheader("📝 Log Pesan Terbaru")
    if os.path.exists('message_logs.json'):
        with open('message_logs.json', 'r', encoding='utf-8') as f:
            logs = json.load(f)
        
        # Tampilkan 10 log terakhir
        recent_logs = logs[-10:] if len(logs) > 10 else logs
        for log in reversed(recent_logs):
            if 'from' in log:  # Pesan masuk
                st.text(f"📩 {log['timestamp']} - From {log['from']}: {log['message']}")
            else:  # Response
                st.text(f"📤 {log['timestamp']} - To {log['to']}: {log['response']}")

def show_reports():
    st.header("📈 Laporan dan Analytics")
    
    orders = get_all_orders()
    if not orders:
        st.info("Belum ada data untuk laporan.")
        return
    
    orders_df = pd.DataFrame(orders, columns=[
        'ID', 'Nama Customer', 'No. HP', 'Produk', 'Jumlah', 
        'Harga', 'Total', 'Status', 'Tanggal', 'Alamat'
    ])
    orders_df['Tanggal'] = pd.to_datetime(orders_df['Tanggal'])
    
    # Filter tanggal
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Dari Tanggal", 
                                  orders_df['Tanggal'].min().date())
    with col2:
        end_date = st.date_input("Sampai Tanggal", 
                                orders_df['Tanggal'].max().date())
    
    # Filter data
    mask = (orders_df['Tanggal'].dt.date >= start_date) & (orders_df['Tanggal'].dt.date <= end_date)
    filtered_df = orders_df.loc[mask]
    
    if filtered_df.empty:
        st.warning("Tidak ada data dalam rentang tanggal yang dipilih.")
        return
    
    # Metrics untuk periode
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Pesanan", len(filtered_df))
    with col2:
        st.metric("Total Pendapatan", f"Rp {filtered_df['Total'].sum():,.0f}")
    with col3:
        st.metric("Rata-rata per Pesanan", f"Rp {filtered_df['Total'].mean():,.0f}")
    with col4:
        conversion_rate = len(filtered_df[filtered_df['Status'] == 'delivered']) / len(filtered_df) * 100
        st.metric("Tingkat Konversi", f"{conversion_rate:.1f}%")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Produk Terlaris")
        product_sales = filtered_df.groupby('Produk')['Jumlah'].sum().sort_values(ascending=False)
        fig = px.bar(x=product_sales.index, y=product_sales.values, 
                    title="Produk Terlaris")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("💰 Pendapatan Harian")
        daily_revenue = filtered_df.groupby(filtered_df['Tanggal'].dt.date)['Total'].sum()
        fig = px.line(x=daily_revenue.index, y=daily_revenue.values, 
                     title="Trend Pendapatan Harian")
        st.plotly_chart(fig, use_container_width=True)
    
    # Tabel detail
    st.subheader("📋 Detail Laporan")
    st.dataframe(filtered_df, use_container_width=True)
    
    # Download laporan
    csv = filtered_df.to_csv(index=False)
    st.download_button(
        label="📥 Download Laporan CSV",
        data=csv,
        file_name=f"laporan_pesanan_{start_date}_{end_date}.csv",
        mime="text/csv"
    )

if __name__ == "__main__":
    main()
