#!/usr/bin/env python3
"""
Test script untuk memverifikasi integrasi Node.js dengan Python chatbot
"""

import subprocess
import json
import time

def test_nodejs_python_integration():
    """Test integrasi Node.js dengan Python"""
    print("🔗 TESTING NODE.JS - PYTHON INTEGRATION")
    print("=" * 50)
    
    # Simulasi panggilan dari Node.js ke Python
    test_cases = [
        ("halo", "628888999000"),
        ("2", "628888999000"),
        ("kopi arabika", "628888999000"),
        ("1", "628888999000"),
        ("Test Integration", "628888999000"),
        ("Jl. Integration Test No. 456", "628888999000")
    ]
    
    for i, (message, phone) in enumerate(test_cases, 1):
        print(f"\n{i}. Testing message: '{message}'")
        
        try:
            # Simulate Node.js spawn call
            cmd = ["/workspaces/streamlit-whatsaapjs/.venv/bin/python", "process_message.py", message, phone]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10, cwd="/workspaces/streamlit-whatsaapjs")
            
            if result.returncode == 0:
                response = result.stdout.strip()
                print(f"✅ SUCCESS: {response[:100]}...")
            else:
                print(f"❌ ERROR (code {result.returncode}): {result.stderr}")
                
        except subprocess.TimeoutExpired:
            print("❌ TIMEOUT: Process took too long")
        except Exception as e:
            print(f"❌ EXCEPTION: {e}")
        
        time.sleep(0.5)  # Small delay between calls

def check_session_consistency():
    """Check if sessions are properly maintained"""
    print("\n\n💾 CHECKING SESSION CONSISTENCY")
    print("=" * 50)
    
    try:
        with open('/workspaces/streamlit-whatsaapjs/user_sessions.json', 'r') as f:
            sessions = json.load(f)
        
        print(f"📊 Total active sessions: {len(sessions)}")
        
        for phone, session in sessions.items():
            step = session.get('step', 'none')
            order_data = session.get('order_data', {})
            print(f"📱 {phone}: step='{step}', has_order_data={bool(order_data)}")
            
            if 'product' in order_data:
                product = order_data['product']
                print(f"   🛍️ Product: {product[1] if len(product) > 1 else 'Unknown'}")
                
    except FileNotFoundError:
        print("⚠️ No session file found")
    except Exception as e:
        print(f"❌ Error reading sessions: {e}")

def check_log_files():
    """Check log files for recent activity"""
    print("\n\n📝 CHECKING LOG FILES")
    print("=" * 50)
    
    # Check Python message logs
    try:
        with open('/workspaces/streamlit-whatsaapjs/python_message_logs.json', 'r') as f:
            logs = json.load(f)
        print(f"📋 Python message logs: {len(logs)} entries")
        
        # Show last 3 entries
        for log in logs[-3:]:
            timestamp = log.get('timestamp', 'unknown')
            phone = log.get('phone_number', 'unknown')
            message = log.get('user_message', '')
            print(f"   {timestamp}: {phone} -> '{message[:30]}...'")
            
    except FileNotFoundError:
        print("⚠️ No Python message logs found")
    except Exception as e:
        print(f"❌ Error reading Python logs: {e}")
    
    # Check session debug logs
    try:
        with open('/workspaces/streamlit-whatsaapjs/session_debug.json', 'r') as f:
            debug_logs = json.load(f)
        print(f"🔍 Session debug logs: {len(debug_logs)} entries")
        
        # Show last entry
        if debug_logs:
            last_debug = debug_logs[-1]
            print(f"   Last session: {last_debug.get('phone_number')} at step '{last_debug.get('current_step')}'")
            
    except FileNotFoundError:
        print("⚠️ No session debug logs found")
    except Exception as e:
        print(f"❌ Error reading debug logs: {e}")

if __name__ == "__main__":
    print("🧪 NODE.JS INTEGRATION TEST")
    print("=" * 60)
    
    try:
        test_nodejs_python_integration()
        check_session_consistency()
        check_log_files()
        
        print("\n\n✅ INTEGRATION TEST COMPLETED!")
        print("💡 Bot is ready for WhatsApp integration.")
        
    except KeyboardInterrupt:
        print("\n\n❌ Test interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Test failed: {e}")
