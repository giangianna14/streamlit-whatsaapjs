import sys
from chatbot import order_bot

def main():
    if len(sys.argv) != 3:
        print("Halo! Ketik 'menu' untuk melihat pilihan yang tersedia.")
        return
    
    message = sys.argv[1]
    phone_number = sys.argv[2]
    
    try:
        response = order_bot.process_message(message, phone_number)
        print(response)
    except Exception as e:
        print("Maaf, terjadi kesalahan. Silakan coba lagi nanti.")

if __name__ == "__main__":
    main()
