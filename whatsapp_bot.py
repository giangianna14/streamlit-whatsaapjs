import os
import re
from flask import Flask, request
from twilio.rest import Client
from database import add_order, get_product_by_name, get_all_products
import json

app = Flask(__name__)

# Konfigurasi Twilio WhatsApp (ganti dengan credentials Anda)
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID', 'your_account_sid')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN', 'your_auth_token')
TWILIO_WHATSAPP_NUMBER = os.getenv('TWILIO_WHATSAPP_NUMBER', 'whatsapp:+14155238886')

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# State management untuk percakapan
user_sessions = {}

class OrderSession:
    def __init__(self):
        self.step = 'greeting'
        self.customer_name = ''
        self.product_name = ''
        self.quantity = 0
        self.delivery_address = ''
        self.product_info = None

def send_whatsapp_message(to_number, message):
    """Mengirim pesan WhatsApp menggunakan Twilio"""
    try:
        message = client.messages.create(
            body=message,
            from_=TWILIO_WHATSAPP_NUMBER,
            to=f'whatsapp:{to_number}'
        )
        return message.sid
    except Exception as e:
        print(f"Error sending message: {e}")
        return None

def get_product_catalog():
    """Mendapatkan katalog produk dalam format string"""
    products = get_all_products()
    if not products:
        return "Maaf, katalog produk sedang kosong."
    
    catalog = "📋 *KATALOG PRODUK KAMI:*\n\n"
    for product in products:
        catalog += f"🛍️ *{product[1]}*\n"
        catalog += f"💰 Harga: Rp {product[2]:,.0f}\n"
        catalog += f"📦 Stok: {product[3]} unit\n"
        if product[4]:  # description
            catalog += f"📝 {product[4]}\n"
        catalog += "━━━━━━━━━━━━━━━━━━━━\n"
    
    catalog += "\n💬 Ketik nama produk yang ingin dipesan!"
    return catalog

def process_order_flow(phone_number, message_body):
    """Memproses alur pemesanan"""
    if phone_number not in user_sessions:
        user_sessions[phone_number] = OrderSession()
    
    session = user_sessions[phone_number]
    response = ""
    
    if session.step == 'greeting':
        if any(keyword in message_body.lower() for keyword in ['halo', 'hai', 'hello', 'hi', 'mulai', 'pesan']):
            response = """👋 *Selamat datang di UMKM Kita!*

Saya adalah asisten otomatis untuk membantu Anda berbelanja.

Pilih menu:
1️⃣ Lihat Katalog Produk
2️⃣ Pesan Langsung
3️⃣ Bantuan

Ketik angka pilihan Anda (1, 2, atau 3)"""
            session.step = 'menu_selection'
        else:
            response = "👋 Halo! Ketik 'halo' atau 'pesan' untuk memulai pemesanan."
    
    elif session.step == 'menu_selection':
        if message_body.strip() == '1':
            response = get_product_catalog()
            session.step = 'product_selection'
        elif message_body.strip() == '2':
            response = "📝 Silakan masukkan nama Anda:"
            session.step = 'get_name'
        elif message_body.strip() == '3':
            response = """🆘 *BANTUAN*

Cara memesan:
1. Ketik 'halo' untuk memulai
2. Pilih menu yang tersedia
3. Ikuti instruksi step by step

📞 Kontak langsung: 0812-3456-7890
🕒 Jam operasional: 08:00-20:00 WIB

Ketik 'mulai' untuk memulai pemesanan."""
            session.step = 'greeting'
        else:
            response = "❌ Pilihan tidak valid. Ketik 1, 2, atau 3."
    
    elif session.step == 'product_selection':
        product = get_product_by_name(message_body)
        if product:
            session.product_info = product
            session.product_name = product[1]
            response = f"""✅ Produk ditemukan!

🛍️ *{product[1]}*
💰 Harga: Rp {product[2]:,.0f}
📦 Stok tersedia: {product[3]} unit

📝 Silakan masukkan nama Anda:"""
            session.step = 'get_name'
        else:
            response = f"❌ Produk '{message_body}' tidak ditemukan.\n\n{get_product_catalog()}"
    
    elif session.step == 'get_name':
        session.customer_name = message_body.strip()
        if session.product_info:
            response = f"👋 Halo {session.customer_name}!\n\n📦 Berapa unit *{session.product_name}* yang ingin Anda pesan?"
        else:
            response = f"👋 Halo {session.customer_name}!\n\n🛍️ Produk apa yang ingin Anda pesan? (ketik nama produk)"
            session.step = 'product_selection'
            return response
        session.step = 'get_quantity'
    
    elif session.step == 'get_quantity':
        try:
            quantity = int(message_body.strip())
            if quantity <= 0:
                response = "❌ Jumlah harus lebih dari 0. Silakan masukkan jumlah yang valid:"
            elif session.product_info and quantity > session.product_info[3]:
                response = f"❌ Stok tidak mencukupi. Stok tersedia: {session.product_info[3]} unit. Silakan masukkan jumlah yang valid:"
            else:
                session.quantity = quantity
                if session.product_info:
                    total = quantity * session.product_info[2]
                    response = f"""📋 *KONFIRMASI PESANAN*

👤 Nama: {session.customer_name}
🛍️ Produk: {session.product_name}
📦 Jumlah: {quantity} unit
💰 Harga satuan: Rp {session.product_info[2]:,.0f}
💸 Total: Rp {total:,.0f}

📍 Silakan masukkan alamat pengiriman:"""
                    session.step = 'get_address'
                else:
                    response = "🛍️ Produk apa yang ingin Anda pesan? (ketik nama produk)"
                    session.step = 'product_selection'
        except ValueError:
            response = "❌ Format tidak valid. Silakan masukkan angka untuk jumlah pesanan:"
    
    elif session.step == 'get_address':
        session.delivery_address = message_body.strip()
        
        # Simpan pesanan ke database
        try:
            order_id = add_order(
                session.customer_name,
                phone_number,
                session.product_name,
                session.quantity,
                session.product_info[2],
                session.delivery_address
            )
            
            total = session.quantity * session.product_info[2]
            response = f"""✅ *PESANAN BERHASIL!*

🎫 ID Pesanan: #{order_id}
👤 Nama: {session.customer_name}
🛍️ Produk: {session.product_name}
📦 Jumlah: {session.quantity} unit
💸 Total: Rp {total:,.0f}
📍 Alamat: {session.delivery_address}

💬 Tim kami akan menghubungi Anda untuk konfirmasi pembayaran dan pengiriman.

Terima kasih telah berbelanja! 🙏

Ketik 'mulai' untuk pemesanan baru."""
            
            # Reset session
            user_sessions[phone_number] = OrderSession()
            
        except Exception as e:
            response = f"❌ Terjadi kesalahan saat menyimpan pesanan. Silakan coba lagi.\n\nKetik 'mulai' untuk memulai kembali."
            user_sessions[phone_number] = OrderSession()
    
    return response

@app.route('/webhook', methods=['POST'])
def whatsapp_webhook():
    """Webhook untuk menerima pesan WhatsApp dari Twilio"""
    try:
        # Mendapatkan data dari Twilio
        from_number = request.form.get('From', '').replace('whatsapp:', '')
        message_body = request.form.get('Body', '').strip()
        
        if not from_number or not message_body:
            return 'OK', 200
        
        # Proses pesan dan dapatkan response
        response_message = process_order_flow(from_number, message_body)
        
        # Kirim response
        if response_message:
            send_whatsapp_message(from_number, response_message)
        
        return 'OK', 200
        
    except Exception as e:
        print(f"Error in webhook: {e}")
        return 'Error', 500

@app.route('/send-broadcast', methods=['POST'])
def send_broadcast():
    """Endpoint untuk mengirim broadcast message"""
    try:
        data = request.get_json()
        message = data.get('message', '')
        phone_numbers = data.get('phone_numbers', [])
        
        results = []
        for phone in phone_numbers:
            result = send_whatsapp_message(phone, message)
            results.append({'phone': phone, 'status': 'sent' if result else 'failed'})
        
        return {'status': 'success', 'results': results}, 200
        
    except Exception as e:
        return {'status': 'error', 'message': str(e)}, 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return {'status': 'healthy', 'service': 'WhatsApp Bot'}, 200

if __name__ == '__main__':
    print("🤖 WhatsApp Bot Server starting...")
    print("📱 Webhook URL: http://localhost:5001/webhook")
    print("🌐 Konfigurasi webhook ini di Twilio Console")
    app.run(debug=True, host='0.0.0.0', port=5001)
