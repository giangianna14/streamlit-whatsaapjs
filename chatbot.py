import re
from database import add_order, get_product_by_name, add_product, get_all_products

class OrderBot:
    def __init__(self):
        self.user_sessions = {}  # Menyimpan session percakapan user
        self.setup_default_products()
    
    def setup_default_products(self):
        """Setup produk default jika belum ada"""
        products = get_all_products()
        if not products:
            # Tambah beberapa produk contoh
            add_product("Nasi Gudeg", 15000, 100, "Nasi gudeg khas Yogyakarta dengan ayam", "Makanan")
            add_product("Es Teh Manis", 5000, 50, "Es teh manis segar", "Minuman")
            add_product("Ayam Goreng", 20000, 30, "Ayam goreng crispy", "Makanan")
            add_product("Kerupuk", 3000, 200, "Kerupuk udang renyah", "Snack")
    
    def process_message(self, message, phone_number):
        """Memproses pesan dari WhatsApp dan memberikan respon"""
        message = message.strip().lower()
        
        # Inisialisasi session jika belum ada
        if phone_number not in self.user_sessions:
            self.user_sessions[phone_number] = {
                'step': 'greeting',
                'order_data': {}
            }
        
        session = self.user_sessions[phone_number]
        
        # Greeting dan menu utama
        if message in ['hi', 'halo', 'hai', 'hello', 'menu', 'mulai']:
            session['step'] = 'main_menu'
            return self.show_main_menu()
        
        # Proses berdasarkan langkah saat ini
        if session['step'] == 'greeting' or session['step'] == 'main_menu':
            return self.handle_main_menu_selection(message, phone_number)
        
        elif session['step'] == 'waiting_product':
            return self.handle_product_selection(message, phone_number)
        
        elif session['step'] == 'waiting_quantity':
            return self.handle_quantity_input(message, phone_number)
        
        elif session['step'] == 'waiting_name':
            return self.handle_name_input(message, phone_number)
        
        elif session['step'] == 'waiting_address':
            return self.handle_address_input(message, phone_number)
        
        else:
            return self.show_main_menu()
    
    def show_main_menu(self):
        """Menampilkan menu utama"""
        menu = """🛍️ *Selamat datang di Warung Digital!*

Silakan pilih menu:
1️⃣ Lihat Menu Produk
2️⃣ Pesan Makanan
3️⃣ Status Pesanan
4️⃣ Bantuan

Ketik angka pilihan Anda (1-4) atau ketik nama produk langsung untuk memesan."""
        return menu
    
    def show_product_catalog(self):
        """Menampilkan katalog produk"""
        products = get_all_products()
        if not products:
            return "Maaf, saat ini belum ada produk tersedia."
        
        catalog = "📋 *MENU PRODUK KAMI:*\n\n"
        for product in products:
            catalog += f"🍽️ *{product[1]}*\n"
            catalog += f"💰 Harga: Rp {product[2]:,}\n"
            catalog += f"📦 Stok: {product[3]}\n"
            catalog += f"📝 {product[4]}\n"
            catalog += "─" * 30 + "\n\n"
        
        catalog += "💬 Untuk memesan, ketik: *pesan [nama produk]*\nContoh: *pesan nasi gudeg*"
        return catalog
    
    def handle_product_selection(self, message, phone_number):
        """Menangani pemilihan produk"""
        # Cari produk berdasarkan input user
        product = get_product_by_name(message)
        
        if product:
            self.user_sessions[phone_number]['order_data']['product'] = product
            self.user_sessions[phone_number]['step'] = 'waiting_quantity'
            
            return f"""✅ Produk ditemukan: *{product[1]}*
💰 Harga: Rp {product[2]:,}
📦 Stok tersedia: {product[3]}

Berapa jumlah yang ingin Anda pesan?
Ketik angka saja (contoh: 2)"""
        else:
            return f"""❌ Produk "{message}" tidak ditemukan.

{self.show_product_catalog()}"""
    
    def handle_quantity_input(self, message, phone_number):
        """Menangani input jumlah pesanan"""
        try:
            quantity = int(message)
            if quantity <= 0:
                return "❌ Jumlah harus lebih dari 0. Silakan masukkan jumlah yang valid."
            
            product = self.user_sessions[phone_number]['order_data']['product']
            if quantity > product[3]:  # Cek stok
                return f"❌ Stok tidak mencukupi. Stok tersedia: {product[3]}"
            
            self.user_sessions[phone_number]['order_data']['quantity'] = quantity
            self.user_sessions[phone_number]['step'] = 'waiting_name'
            
            total = quantity * product[2]
            
            return f"""📋 *RINGKASAN PESANAN:*
🍽️ Produk: {product[1]}
📊 Jumlah: {quantity}
💰 Harga satuan: Rp {product[2]:,}
💳 Total: Rp {total:,}

Silakan masukkan nama Anda untuk pesanan ini:"""
        
        except ValueError:
            return "❌ Silakan masukkan angka yang valid untuk jumlah pesanan."
    
    def handle_name_input(self, message, phone_number):
        """Menangani input nama pelanggan"""
        if len(message.strip()) < 2:
            return "❌ Nama terlalu pendek. Silakan masukkan nama lengkap Anda:"
        
        self.user_sessions[phone_number]['order_data']['customer_name'] = message.strip().title()
        self.user_sessions[phone_number]['step'] = 'waiting_address'
        
        return "📍 Silakan masukkan alamat pengiriman Anda:"
    
    def handle_address_input(self, message, phone_number):
        """Menangani input alamat dan finalisasi pesanan"""
        if len(message.strip()) < 5:
            return "❌ Alamat terlalu pendek. Silakan masukkan alamat lengkap:"
        
        # Finalisasi pesanan
        order_data = self.user_sessions[phone_number]['order_data']
        product = order_data['product']
        quantity = order_data['quantity']
        customer_name = order_data['customer_name']
        address = message.strip()
        
        # Simpan ke database
        order_id = add_order(
            customer_name=customer_name,
            phone_number=phone_number,
            product_name=product[1],
            quantity=quantity,
            price=product[2],
            delivery_address=address
        )
        
        # Reset session
        self.user_sessions[phone_number] = {'step': 'greeting', 'order_data': {}}
        
        total = quantity * product[2]
        
        return f"""✅ *PESANAN BERHASIL DIBUAT!*

🆔 Nomor Pesanan: #{order_id}
👤 Nama: {customer_name}
🍽️ Produk: {product[1]}
📊 Jumlah: {quantity}
💳 Total: Rp {total:,}
📍 Alamat: {address}

📞 Tim kami akan segera menghubungi Anda untuk konfirmasi pembayaran dan pengiriman.

Terima kasih telah berbelanja di Warung Digital! 🙏

Ketik *menu* untuk kembali ke menu utama."""
    
    def handle_main_menu_selection(self, message, phone_number):
        """Menangani pilihan dari menu utama"""
        session = self.user_sessions[phone_number]
        
        if message == '1':
            return self.show_product_catalog()
        
        elif message == '2':
            session['step'] = 'waiting_product'
            return """🛒 *PESAN MAKANAN*

Silakan ketik nama produk yang ingin Anda pesan.
Contoh: "nasi gudeg" atau "ayam goreng"

Atau ketik "menu" untuk melihat daftar produk."""
        
        elif message == '3':
            return """📋 *STATUS PESANAN*

Untuk mengecek status pesanan, silakan hubungi admin:
📱 WhatsApp: 08123456789
📧 Email: admin@warungdigital.com

Atau ketik "menu" untuk kembali ke menu utama."""
        
        elif message == '4':
            return """❓ *BANTUAN*

🕒 Jam Operasional: 08:00 - 22:00 WIB
📱 WhatsApp: 08123456789
📧 Email: support@warungdigital.com
📍 Alamat: Jl. Digital No. 123, Jakarta

*Cara Pemesanan:*
1. Pilih menu "2" untuk pesan
2. Ketik nama produk
3. Masukkan jumlah pesanan
4. Isi data diri dan alamat
5. Tunggu konfirmasi dari tim kami

Ketik "menu" untuk kembali ke menu utama."""
        
        else:
            # Jika input tidak sesuai menu, coba cari sebagai nama produk
            product = get_product_by_name(message)
            if product:
                session['step'] = 'waiting_quantity'
                session['order_data']['product'] = product
                return f"""✅ Produk ditemukan: *{product[1]}*
💰 Harga: Rp {product[2]:,}
📦 Stok tersedia: {product[3]}

Berapa jumlah yang ingin Anda pesan?
Ketik angka saja (contoh: 2)"""
            else:
                return f"""❌ Pilihan tidak valid atau produk tidak ditemukan.

{self.show_main_menu()}"""

# Instance global bot
order_bot = OrderBot()
