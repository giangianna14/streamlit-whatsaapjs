import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from database import (
    get_all_orders, get_all_products, add_product, 
    update_order_status, add_order
)
import requests
import json

# Konfigurasi halaman
st.set_page_config(
    page_title="Dashboard UMKM - WhatsApp Bot",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #25D366;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-container {
        background: linear-gradient(90deg, #25D366, #128C7E);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    .order-card {
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        background: #f9f9f9;
    }
    .status-pending { color: #ff9800; font-weight: bold; }
    .status-confirmed { color: #4caf50; font-weight: bold; }
    .status-delivered { color: #2196f3; font-weight: bold; }
    .status-cancelled { color: #f44336; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

def load_data():
    """Memuat data dari database"""
    try:
        orders = get_all_orders()
        products = get_all_products()
        return orders, products
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return [], []

def format_currency(amount):
    """Format mata uang Rupiah"""
    return f"Rp {amount:,.0f}"

def get_order_stats(orders):
    """Menghitung statistik pesanan"""
    if not orders:
        return 0, 0, 0, 0
    
    total_orders = len(orders)
    total_revenue = sum(order[6] for order in orders)  # total_amount
    
    # Hitung pesanan hari ini
    today = datetime.now().date()
    today_orders = [order for order in orders 
                   if datetime.strptime(order[8], '%Y-%m-%d %H:%M:%S').date() == today]
    today_count = len(today_orders)
    today_revenue = sum(order[6] for order in today_orders)
    
    return total_orders, total_revenue, today_count, today_revenue

def main():
    st.markdown('<h1 class="main-header">📱 Dashboard UMKM WhatsApp Bot</h1>', unsafe_allow_html=True)
    
    # Sidebar Navigation
    st.sidebar.title("📊 Menu Dashboard")
    page = st.sidebar.selectbox(
        "Pilih Halaman:",
        ["🏠 Overview", "📦 Kelola Pesanan", "🛍️ Kelola Produk", "📤 Broadcast Message", "📊 Analytics"]
    )
    
    # Load data
    orders, products = load_data()
    
    if page == "🏠 Overview":
        show_overview(orders, products)
    elif page == "📦 Kelola Pesanan":
        show_orders_management(orders)
    elif page == "🛍️ Kelola Produk":
        show_products_management(products)
    elif page == "📤 Broadcast Message":
        show_broadcast_feature(orders)
    elif page == "📊 Analytics":
        show_analytics(orders)

def show_overview(orders, products):
    """Tampilkan halaman overview"""
    st.subheader("📊 Ringkasan Bisnis")
    
    # Statistik utama
    total_orders, total_revenue, today_orders, today_revenue = get_order_stats(orders)
    total_products = len(products)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-container">
            <h3>📦 Total Pesanan</h3>
            <h2>{total_orders}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-container">
            <h3>💰 Total Pendapatan</h3>
            <h2>{format_currency(total_revenue)}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-container">
            <h3>📅 Pesanan Hari Ini</h3>
            <h2>{today_orders}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-container">
            <h3>🛍️ Total Produk</h3>
            <h2>{total_products}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Pesanan terbaru
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📋 Pesanan Terbaru")
        if orders:
            recent_orders = orders[:5]  # 5 pesanan terbaru
            for order in recent_orders:
                status_class = f"status-{order[7].lower()}"
                st.markdown(f"""
                <div class="order-card">
                    <strong>#{order[0]} - {order[1]}</strong><br>
                    📱 {order[2]}<br>
                    🛍️ {order[3]} ({order[4]} unit)<br>
                    💰 {format_currency(order[6])}<br>
                    📅 {order[8]}<br>
                    📍 Status: <span class="{status_class}">{order[7].upper()}</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Belum ada pesanan masuk.")
    
    with col2:
        st.subheader("🎯 Status Pesanan")
        if orders:
            status_counts = {}
            for order in orders:
                status = order[7]
                status_counts[status] = status_counts.get(status, 0) + 1
            
            fig = px.pie(
                values=list(status_counts.values()),
                names=list(status_counts.keys()),
                title="Distribusi Status Pesanan"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Belum ada data untuk ditampilkan.")

def show_orders_management(orders):
    """Tampilkan halaman kelola pesanan"""
    st.subheader("📦 Kelola Pesanan")
    
    if not orders:
        st.info("Belum ada pesanan masuk.")
        return
    
    # Filter pesanan
    col1, col2, col3 = st.columns(3)
    
    with col1:
        status_filter = st.selectbox(
            "Filter berdasarkan status:",
            ["Semua", "pending", "confirmed", "delivered", "cancelled"]
        )
    
    with col2:
        # Date range filter
        date_from = st.date_input("Dari tanggal:", datetime.now().date() - timedelta(days=30))
        
    with col3:
        date_to = st.date_input("Sampai tanggal:", datetime.now().date())
    
    # Filter data
    filtered_orders = orders
    if status_filter != "Semua":
        filtered_orders = [order for order in filtered_orders if order[7] == status_filter]
    
    # Convert to DataFrame for easier manipulation
    df_orders = pd.DataFrame(filtered_orders, columns=[
        'ID', 'Nama Customer', 'No. HP', 'Produk', 'Jumlah', 
        'Harga Satuan', 'Total', 'Status', 'Tanggal', 'Alamat'
    ])
    
    if not df_orders.empty:
        # Format currency columns
        df_orders['Harga Satuan'] = df_orders['Harga Satuan'].apply(format_currency)
        df_orders['Total'] = df_orders['Total'].apply(format_currency)
        
        st.dataframe(df_orders, use_container_width=True)
        
        # Update status section
        st.markdown("---")
        st.subheader("✏️ Update Status Pesanan")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            order_id = st.selectbox(
                "Pilih ID Pesanan:",
                options=[f"#{order[0]} - {order[1]}" for order in filtered_orders]
            )
            selected_id = int(order_id.split('#')[1].split(' -')[0])
        
        with col2:
            new_status = st.selectbox(
                "Status Baru:",
                ["pending", "confirmed", "delivered", "cancelled"]
            )
        
        with col3:
            st.write("")  # Spacing
            if st.button("🔄 Update Status", type="primary"):
                try:
                    update_order_status(selected_id, new_status)
                    st.success(f"Status pesanan #{selected_id} berhasil diupdate!")
                    st.experimental_rerun()
                except Exception as e:
                    st.error(f"Error updating status: {e}")
    else:
        st.info("Tidak ada pesanan yang sesuai dengan filter.")

def show_products_management(products):
    """Tampilkan halaman kelola produk"""
    st.subheader("🛍️ Kelola Produk")
    
    # Tambah produk baru
    with st.expander("➕ Tambah Produk Baru"):
        col1, col2 = st.columns(2)
        
        with col1:
            new_name = st.text_input("Nama Produk:")
            new_price = st.number_input("Harga:", min_value=0.0, step=1000.0)
            new_stock = st.number_input("Stok:", min_value=0, step=1)
        
        with col2:
            new_description = st.text_area("Deskripsi:")
            new_category = st.text_input("Kategori:")
            
            if st.button("➕ Tambah Produk", type="primary"):
                if new_name and new_price > 0:
                    try:
                        add_product(new_name, new_price, new_stock, new_description, new_category)
                        st.success("Produk berhasil ditambahkan!")
                        st.experimental_rerun()
                    except Exception as e:
                        st.error(f"Error adding product: {e}")
                else:
                    st.error("Nama produk dan harga harus diisi!")
    
    # Tampilkan daftar produk
    st.markdown("---")
    st.subheader("📋 Daftar Produk")
    
    if products:
        df_products = pd.DataFrame(products, columns=[
            'ID', 'Nama', 'Harga', 'Stok', 'Deskripsi', 'Kategori'
        ])
        
        # Format harga
        df_products['Harga'] = df_products['Harga'].apply(format_currency)
        
        st.dataframe(df_products, use_container_width=True)
        
        # Statistik produk
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_products = len(products)
            st.metric("Total Produk", total_products)
        
        with col2:
            total_stock = sum(product[3] for product in products)
            st.metric("Total Stok", total_stock)
        
        with col3:
            avg_price = sum(product[2] for product in products) / len(products)
            st.metric("Harga Rata-rata", format_currency(avg_price))
        
    else:
        st.info("Belum ada produk dalam katalog.")

def show_broadcast_feature(orders):
    """Tampilkan fitur broadcast message"""
    st.subheader("📤 Broadcast Message")
    
    # Ambil nomor HP dari pesanan
    phone_numbers = list(set([order[2] for order in orders if order[2]]))
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("✍️ Tulis Pesan")
        message = st.text_area(
            "Pesan broadcast:",
            placeholder="Contoh: Halo! Kami memiliki promo spesial hari ini...",
            height=150
        )
        
        # Pilihan penerima
        recipient_option = st.radio(
            "Kirim ke:",
            ["Semua pelanggan", "Pilih nomor manual", "Upload file CSV"]
        )
        
        selected_numbers = []
        
        if recipient_option == "Semua pelanggan":
            selected_numbers = phone_numbers
            st.info(f"Akan dikirim ke {len(selected_numbers)} nomor")
        
        elif recipient_option == "Pilih nomor manual":
            selected_numbers = st.multiselect(
                "Pilih nomor HP:",
                options=phone_numbers,
                default=phone_numbers[:5] if len(phone_numbers) > 5 else phone_numbers
            )
        
        elif recipient_option == "Upload file CSV":
            uploaded_file = st.file_uploader(
                "Upload file CSV dengan kolom 'phone':",
                type=['csv']
            )
            if uploaded_file:
                try:
                    df = pd.read_csv(uploaded_file)
                    if 'phone' in df.columns:
                        selected_numbers = df['phone'].astype(str).tolist()
                        st.success(f"Berhasil memuat {len(selected_numbers)} nomor")
                    else:
                        st.error("File harus memiliki kolom 'phone'")
                except Exception as e:
                    st.error(f"Error reading file: {e}")
        
        # Tombol kirim
        if st.button("📤 Kirim Broadcast", type="primary"):
            if message and selected_numbers:
                try:
                    # Simulasi pengiriman (gunakan API WhatsApp bot)
                    payload = {
                        'message': message,
                        'phone_numbers': selected_numbers
                    }
                    
                    # Uncomment baris berikut jika bot server sudah berjalan
                    # response = requests.post('http://localhost:5000/send-broadcast', json=payload)
                    
                    # Untuk demo, tampilkan success message
                    st.success(f"Broadcast berhasil dikirim ke {len(selected_numbers)} nomor!")
                    
                    # Log broadcast
                    st.subheader("📊 Detail Pengiriman")
                    for i, number in enumerate(selected_numbers, 1):
                        st.write(f"{i}. {number} ✅")
                        
                except Exception as e:
                    st.error(f"Error sending broadcast: {e}")
            else:
                st.error("Pesan dan penerima harus diisi!")
    
    with col2:
        st.subheader("👥 Pelanggan Terdaftar")
        if phone_numbers:
            for i, phone in enumerate(phone_numbers[:10], 1):
                st.write(f"{i}. {phone}")
            if len(phone_numbers) > 10:
                st.write(f"... dan {len(phone_numbers) - 10} lainnya")
        else:
            st.info("Belum ada pelanggan terdaftar")
        
        # Template pesan
        st.subheader("📝 Template Pesan")
        templates = {
            "Promo": "🎉 PROMO SPESIAL! Dapatkan diskon 20% untuk semua produk. Berlaku hingga akhir bulan!",
            "Reminder": "📋 Jangan lupa untuk menyelesaikan pembayaran pesanan Anda. Terima kasih!",
            "Info Produk": "🆕 Produk baru telah tersedia! Cek katalog terbaru kami dan pesan sekarang.",
            "Terima Kasih": "🙏 Terima kasih telah berbelanja di toko kami. Sampai jumpa di pemesanan berikutnya!"
        }
        
        for title, template in templates.items():
            if st.button(f"📋 {title}"):
                st.text_area("Template akan disalin:", value=template, key=f"template_{title}")

def show_analytics(orders):
    """Tampilkan halaman analytics"""
    st.subheader("📊 Analytics & Laporan")
    
    if not orders:
        st.info("Belum ada data untuk analisis.")
        return
    
    # Convert ke DataFrame
    df = pd.DataFrame(orders, columns=[
        'ID', 'Nama', 'HP', 'Produk', 'Jumlah', 
        'Harga', 'Total', 'Status', 'Tanggal', 'Alamat'
    ])
    
    df['Tanggal'] = pd.to_datetime(df['Tanggal'])
    df['Bulan'] = df['Tanggal'].dt.to_period('M')
    
    # Metrics utama
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_revenue = df['Total'].sum()
        st.metric("💰 Total Pendapatan", format_currency(total_revenue))
    
    with col2:
        avg_order_value = df['Total'].mean()
        st.metric("📊 Rata-rata Nilai Pesanan", format_currency(avg_order_value))
    
    with col3:
        unique_customers = df['HP'].nunique()
        st.metric("👥 Pelanggan Unik", unique_customers)
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Penjualan per bulan
        monthly_sales = df.groupby('Bulan')['Total'].sum().reset_index()
        monthly_sales['Bulan'] = monthly_sales['Bulan'].astype(str)
        
        fig_monthly = px.bar(
            monthly_sales, 
            x='Bulan', 
            y='Total',
            title="📈 Penjualan Bulanan",
            labels={'Total': 'Pendapatan (Rp)', 'Bulan': 'Bulan'}
        )
        st.plotly_chart(fig_monthly, use_container_width=True)
    
    with col2:
        # Produk terlaris
        product_sales = df.groupby('Produk').agg({
            'Jumlah': 'sum',
            'Total': 'sum'
        }).reset_index()
        product_sales = product_sales.nlargest(5, 'Total')
        
        fig_products = px.bar(
            product_sales, 
            x='Produk', 
            y='Total',
            title="🛍️ Top 5 Produk Terlaris",
            labels={'Total': 'Pendapatan (Rp)', 'Produk': 'Produk'}
        )
        fig_products.update_xaxis(tickangle=45)
        st.plotly_chart(fig_products, use_container_width=True)
    
    # Tabel detail analytics
    st.markdown("---")
    st.subheader("📋 Detail Analytics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**📊 Ringkasan per Produk:**")
        product_summary = df.groupby('Produk').agg({
            'Jumlah': 'sum',
            'Total': ['sum', 'count', 'mean']
        }).round(2)
        product_summary.columns = ['Total Terjual', 'Total Pendapatan', 'Jumlah Order', 'Rata-rata per Order']
        st.dataframe(product_summary)
    
    with col2:
        st.write("**📅 Ringkasan per Status:**")
        status_summary = df.groupby('Status').agg({
            'Total': ['sum', 'count']
        }).round(2)
        status_summary.columns = ['Total Pendapatan', 'Jumlah Order']
        st.dataframe(status_summary)

if __name__ == "__main__":
    main()
