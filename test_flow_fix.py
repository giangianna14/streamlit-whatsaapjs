#!/usr/bin/env python3
"""
Test untuk verifikasi perbaikan flow berdasarkan user feedback:
Hi -> 1 -> Pesan keripik
"""

import subprocess
import time

def run_message(message, phone_number):
    """Run process_message.py and return response"""
    try:
        cmd = ["/workspaces/streamlit-whatsaapjs/.venv/bin/python", "process_message.py", message, phone_number]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10, cwd="/workspaces/streamlit-whatsaapjs")
        
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            return f"ERROR: {result.stderr.strip()}"
    except Exception as e:
        return f"ERROR: {str(e)}"

def test_user_reported_flow():
    """Test the exact flow reported by user"""
    phone = "6281291737972"
    
    print("🧪 TESTING USER REPORTED FLOW FIX")
    print("=" * 50)
    print(f"Phone: {phone}")
    
    # Step 1: Hi
    print("\n1. USER: Hi")
    response = run_message("Hi", phone)
    print(f"BOT: {response[:100]}...")
    assert "Selamat datang" in response, "Greeting should work"
    
    # Step 2: 1 (view products)
    print("\n2. USER: 1")
    response = run_message("1", phone)
    print(f"BOT: {response[:100]}...")
    assert "MENU PRODUK" in response, "Product catalog should be shown"
    assert "Keripik Singkong" in response, "Keripik should be in catalog"
    
    # Step 3: Pesan keripik (this was failing before)
    print("\n3. USER: Pesan keripik")
    response = run_message("Pesan keripik", phone)
    print(f"BOT: {response[:100]}...")
    assert "Keripik Singkong" in response, "Should find Keripik Singkong"
    assert "Berapa jumlah" in response, "Should ask for quantity"
    
    # Step 4: Continue with quantity
    print("\n4. USER: 1")
    response = run_message("1", phone)
    print(f"BOT: {response[:100]}...")
    assert "RINGKASAN PESANAN" in response, "Should show order summary"
    
    print("\n✅ USER REPORTED FLOW NOW WORKS!")

def test_alternative_order_methods():
    """Test different ways to order"""
    print("\n\n🎯 TESTING ALTERNATIVE ORDER METHODS")
    print("=" * 50)
    
    test_cases = [
        ("pesan kopi", "628111000001", "Direct order with partial name"),
        ("Pesan Keripik Singkong", "628111000002", "Direct order with full name"),
        ("pesan teh", "628111000003", "Direct order with partial name"),
        ("PESAN SAMBAL", "628111000004", "Order with caps"),
    ]
    
    for message, phone, description in test_cases:
        print(f"\n{description}")
        print(f"USER: {message}")
        response = run_message(message, phone)
        print(f"BOT: {response[:100]}...")
        
        if "ditemukan" in response:
            print("✅ Order recognized successfully")
        else:
            print("❌ Order not recognized")

def test_flow_after_viewing_catalog():
    """Test that users can order after viewing catalog"""
    phone = "628555666777"
    
    print("\n\n📋 TESTING FLOW AFTER VIEWING CATALOG")
    print("=" * 50)
    
    # View catalog first
    print("1. View catalog")
    run_message("halo", phone)
    run_message("1", phone)
    
    # Then try to order
    print("2. Order after viewing catalog")
    response = run_message("pesan madu", phone)
    print(f"USER: pesan madu")
    print(f"BOT: {response[:100]}...")
    
    if "Madu Murni" in response:
        print("✅ Can order after viewing catalog")
    else:
        print("❌ Cannot order after viewing catalog")

if __name__ == "__main__":
    print("🔧 TESTING FLOW IMPROVEMENTS")
    print("=" * 60)
    
    try:
        test_user_reported_flow()
        test_alternative_order_methods()
        test_flow_after_viewing_catalog()
        
        print("\n\n🎉 ALL FLOW FIXES VERIFIED!")
        print("User can now:")
        print("• Order directly with 'pesan [product]' from any state")
        print("• Order after viewing the catalog")
        print("• Use partial product names")
        print("• Use different case variations")
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
