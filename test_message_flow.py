#!/usr/bin/env python3
"""
Script untuk testing flow message bot WhatsApp
"""

import subprocess
import sys
import json
import time

def run_message(message, phone_number):
    """Jalankan process_message.py dan return response"""
    try:
        cmd = ["/workspaces/streamlit-whatsaapjs/.venv/bin/python", "process_message.py", message, phone_number]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            return f"ERROR: {result.stderr.strip()}"
    except subprocess.TimeoutExpired:
        return "ERROR: Timeout"
    except Exception as e:
        return f"ERROR: {str(e)}"

def test_complete_order_flow():
    """Test complete order flow"""
    phone = "628777666555"
    
    print("🧪 TESTING COMPLETE ORDER FLOW")
    print("=" * 50)
    
    # Test 1: Greeting
    print("\n1. Testing greeting...")
    response = run_message("halo", phone)
    print(f"USER: halo")
    print(f"BOT: {response[:100]}...")
    
    # Test 2: Choose option 2 (order)
    print("\n2. Testing option 2 (order)...")
    response = run_message("2", phone)
    print(f"USER: 2")
    print(f"BOT: {response[:100]}...")
    
    # Test 3: Choose product
    print("\n3. Testing product selection...")
    response = run_message("kopi arabika", phone)
    print(f"USER: kopi arabika")
    print(f"BOT: {response[:100]}...")
    
    # Test 4: Choose quantity
    print("\n4. Testing quantity input...")
    response = run_message("2", phone)
    print(f"USER: 2")
    print(f"BOT: {response[:100]}...")
    
    # Test 5: Enter name
    print("\n5. Testing name input...")
    response = run_message("Test User", phone)
    print(f"USER: Test User")
    print(f"BOT: {response[:100]}...")
    
    # Test 6: Enter address
    print("\n6. Testing address input...")
    response = run_message("Jl. Test No. 123, Jakarta", phone)
    print(f"USER: Jl. Test No. 123, Jakarta")
    print(f"BOT: {response[:100]}...")
    
def test_error_cases():
    """Test error handling"""
    phone = "628555444333"
    
    print("\n\n🚨 TESTING ERROR CASES")
    print("=" * 50)
    
    # Test empty message
    print("\n1. Testing empty message...")
    response = run_message("", phone)
    print(f"USER: (empty)")
    print(f"BOT: {response[:100]}...")
    
    # Test invalid product
    print("\n2. Testing invalid product...")
    run_message("2", phone)  # Enter order mode
    response = run_message("produk tidak ada", phone)
    print(f"USER: produk tidak ada")
    print(f"BOT: {response[:100]}...")
    
    # Test invalid quantity
    print("\n3. Testing invalid quantity...")
    run_message("halo", phone)  # Reset
    run_message("2", phone)     # Order mode
    run_message("kopi arabika", phone)  # Select product
    response = run_message("abc", phone)  # Invalid quantity
    print(f"USER: abc")
    print(f"BOT: {response[:100]}...")

def test_session_persistence():
    """Test session persistence between calls"""
    phone = "628333222111"
    
    print("\n\n💾 TESTING SESSION PERSISTENCE")
    print("=" * 50)
    
    # Check if session is saved correctly
    print("\n1. Starting order flow...")
    run_message("halo", phone)
    run_message("2", phone)
    run_message("kopi arabika", phone)
    
    # Check session state
    try:
        with open('user_sessions.json', 'r') as f:
            sessions = json.load(f)
            if phone in sessions:
                step = sessions[phone].get('step', 'none')
                print(f"Session step for {phone}: {step}")
                product = sessions[phone].get('order_data', {}).get('product')
                if product:
                    print(f"Selected product: {product[1]}")
                else:
                    print("No product in session")
            else:
                print(f"No session found for {phone}")
    except Exception as e:
        print(f"Error reading session: {e}")

def test_menu_navigation():
    """Test different menu options"""
    phone = "628111000999"
    
    print("\n\n📋 TESTING MENU NAVIGATION")
    print("=" * 50)
    
    # Test option 1 - product catalog
    print("\n1. Testing product catalog...")
    run_message("halo", phone)
    response = run_message("1", phone)
    print(f"USER: 1")
    print(f"BOT: {response[:200]}...")
    
    # Test option 3 - order status
    print("\n2. Testing order status...")
    response = run_message("3", phone)
    print(f"USER: 3")
    print(f"BOT: {response[:100]}...")
    
    # Test option 4 - help
    print("\n3. Testing help...")
    response = run_message("4", phone)
    print(f"USER: 4")
    print(f"BOT: {response[:100]}...")

def test_direct_product_order():
    """Test ordering product directly from main menu"""
    phone = "628000111222"
    
    print("\n\n🎯 TESTING DIRECT PRODUCT ORDER")
    print("=" * 50)
    
    # Test direct product order from main menu
    print("\n1. Testing direct product order...")
    run_message("halo", phone)
    response = run_message("kopi arabika", phone)
    print(f"USER: kopi arabika (directly from main menu)")
    print(f"BOT: {response[:100]}...")
    
    # Continue with quantity
    response = run_message("1", phone)
    print(f"USER: 1")
    print(f"BOT: {response[:100]}...")

def test_edge_cases():
    """Test edge cases and boundary conditions"""
    phone = "628999000111"
    
    print("\n\n⚠️ TESTING EDGE CASES")
    print("=" * 50)
    
    # Test very long message
    print("\n1. Testing very long message...")
    long_message = "a" * 600  # Exceeds 500 char limit
    response = run_message(long_message, phone)
    print(f"USER: (600 character message)")
    print(f"BOT: {response[:100]}...")
    
    # Test special characters
    print("\n2. Testing special characters...")
    response = run_message("@#$%^&*()", phone)
    print(f"USER: @#$%^&*()")
    print(f"BOT: {response[:100]}...")
    
    # Test quantity edge cases
    print("\n3. Testing quantity edge cases...")
    run_message("halo", phone)
    run_message("2", phone)
    run_message("kopi arabika", phone)
    
    # Test zero quantity
    response = run_message("0", phone)
    print(f"USER: 0")
    print(f"BOT: {response[:100]}...")
    
    # Test negative quantity  
    response = run_message("-5", phone)
    print(f"USER: -5")
    print(f"BOT: {response[:100]}...")
    
    # Test very large quantity (exceeding stock)
    response = run_message("999", phone)
    print(f"USER: 999")
    print(f"BOT: {response[:100]}...")

if __name__ == "__main__":
    print("🤖 WHATSAPP BOT MESSAGE FLOW TESTING")
    print("=" * 60)
    
    try:
        test_complete_order_flow()
        test_error_cases()
        test_session_persistence()
        test_menu_navigation()
        test_direct_product_order()
        test_edge_cases()
        
        print("\n\n✅ ALL TESTS COMPLETED!")
        print("Check python_message_logs.json and session_debug.json for detailed logs.")
        
    except KeyboardInterrupt:
        print("\n\n❌ Testing interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error during testing: {e}")
        sys.exit(1)
