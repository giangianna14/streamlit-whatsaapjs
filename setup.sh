#!/bin/bash

echo "🚀 Starting UMKM WhatsApp Bot System..."

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Initialize database
echo "🗄️ Initializing database..."
python -c "from database import init_database; init_database(); print('Database initialized successfully!')"

# Add sample products
echo "🛍️ Adding sample products..."
python -c "
from database import add_product
products = [
    ('Kopi Arabika Premium', 75000, 50, 'Kopi arabika pilihan dengan cita rasa khas', 'Minuman'),
    ('Teh Herbal Alami', 45000, 30, 'Teh herbal 100% alami untuk kesehatan', 'Minuman'),
    ('Keripik Singkong', 25000, 100, 'Keripik singkong renyah dan gurih', 'Makanan'),
    ('Sambal Homemade', 35000, 25, 'Sambal buatan rumah dengan rasa pedas mantap', 'Makanan'),
    ('Madu Murni', 85000, 20, 'Madu murni 100% dari peternak lokal', 'Kesehatan')
]
for name, price, stock, desc, cat in products:
    add_product(name, price, stock, desc, cat)
print('Sample products added!')
"

echo "✅ Setup completed!"
echo ""
echo "📱 Cara menjalankan sistem:"
echo "1. Jalankan WhatsApp Bot Server:"
echo "   python whatsapp_bot.py"
echo ""
echo "2. Jalankan Dashboard (terminal baru):"
echo "   streamlit run dashboard.py"
echo ""
echo "3. Setup Twilio WhatsApp:"
echo "   - Daftar di twilio.com"
echo "   - Dapatkan WhatsApp Sandbox"
echo "   - Copy credentials ke .env"
echo "   - Set webhook URL ke server Anda"
echo ""
echo "🎉 Happy coding!"
