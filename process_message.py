import sys
import json
import datetime
import traceback
import os
from chatbot import order_bot

def log_interaction(phone_number, message, response, error=None):
    """Log interaksi untuk debugging dan monitoring"""
    try:
        log_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "phone_number": phone_number,
            "user_message": message,
            "bot_response": response,
            "error": error
        }
        
        # Baca existing log atau buat baru
        try:
            with open('python_message_logs.json', 'r') as f:
                logs = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            logs = []
        
        logs.append(log_entry)
        
        # Simpan hanya 1000 log terakhir untuk mencegah file terlalu besar
        if len(logs) > 1000:
            logs = logs[-1000:]
        
        with open('python_message_logs.json', 'w') as f:
            json.dump(logs, f, indent=2, ensure_ascii=False)
            
    except Exception as log_error:
        print(f"Error logging: {log_error}")

def load_sessions():
    """Memuat session dari file"""
    try:
        with open('user_sessions.json', 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_sessions(sessions):
    """Menyimpan session ke file"""
    try:
        with open('user_sessions.json', 'w') as f:
            json.dump(sessions, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving sessions: {e}")

def validate_input(message, phone_number):
    """Validasi input dari user"""
    if not message or not message.strip():
        return False, "Pesan tidak boleh kosong."
    
    if not phone_number or not phone_number.strip():
        return False, "Nomor telefon tidak valid."
    
    # Bersihkan message dari karakter khusus yang bisa mengganggu
    cleaned_message = message.strip()
    if len(cleaned_message) > 500:
        return False, "Pesan terlalu panjang. Maksimal 500 karakter."
    
    return True, cleaned_message

def debug_session(phone_number, sessions):
    """Debug session untuk monitoring flow"""
    try:
        session_info = {
            "timestamp": datetime.datetime.now().isoformat(),
            "phone_number": phone_number,
            "current_step": sessions.get(phone_number, {}).get('step', 'none'),
            "order_data": sessions.get(phone_number, {}).get('order_data', {})
        }
        
        # Simpan debug session
        try:
            with open('session_debug.json', 'r') as f:
                debug_logs = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            debug_logs = []
        
        debug_logs.append(session_info)
        
        # Simpan hanya 500 log terakhir
        if len(debug_logs) > 500:
            debug_logs = debug_logs[-500:]
        
        with open('session_debug.json', 'w') as f:
            json.dump(debug_logs, f, indent=2, ensure_ascii=False)
            
    except Exception as e:
        print(f"Error debugging session: {e}")

def main():
    # Validasi argument
    if len(sys.argv) != 3:
        default_response = """🤖 *Warung Digital Bot*

Halo! Selamat datang di layanan pemesanan otomatis kami.

Ketik salah satu:
• *menu* - Lihat menu lengkap
• *pesan* - Mulai pemesanan
• *bantuan* - Panduan penggunaan

Atau ketik *halo* untuk memulai percakapan."""
        print(default_response)
        return
    
    message = sys.argv[1]
    phone_number = sys.argv[2]
    
    # Validasi input
    is_valid, result = validate_input(message, phone_number)
    if not is_valid:
        error_response = f"❌ {result}\n\nSilakan coba lagi dengan format yang benar."
        log_interaction(phone_number, message, error_response, "Invalid input")
        print(error_response)
        return
    
    cleaned_message = result
    response = None
    error_msg = None
    
    try:
        # Load dan set session ke bot
        sessions = load_sessions()
        order_bot.user_sessions = sessions
        
        # Debug session sebelum processing
        debug_session(phone_number, sessions)
        
        # Proses message dengan chatbot
        response = order_bot.process_message(cleaned_message, phone_number)
        
        # Simpan session yang telah diupdate
        save_sessions(order_bot.user_sessions)
        
        # Debug session setelah pemrosesan
        debug_session(phone_number, order_bot.user_sessions)
        
        # Pastikan response tidak kosong
        if not response or not response.strip():
            response = """🤖 Maaf, saya tidak mengerti pesan Anda.

Ketik *menu* untuk melihat pilihan yang tersedia, atau *bantuan* untuk panduan."""
        
        # Log interaksi sukses
        log_interaction(phone_number, cleaned_message, response)
        print(response)
        
    except Exception as e:
        error_msg = str(e)
        error_trace = traceback.format_exc()
        
        # Response error yang user-friendly
        response = """😅 Maaf, sistem sedang mengalami gangguan.

Silakan coba lagi dalam beberapa saat, atau ketik *bantuan* untuk informasi lebih lanjut.

Jika masalah berlanjut, hubungi admin kami."""
        
        # Log error untuk debugging
        log_interaction(phone_number, cleaned_message, response, error_trace)
        
        # Print error untuk debugging (tapi tidak ke user)
        print(response)
        
        # Optional: print error ke stderr untuk debugging
        sys.stderr.write(f"Error processing message: {error_msg}\n")
        sys.stderr.write(f"Traceback: {error_trace}\n")

if __name__ == "__main__":
    main()
