#!/usr/bin/env python3
"""
Dashboard untuk monitoring dan analisis bot WhatsApp
"""

import json
import sqlite3
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import sys

def load_message_logs():
    """Load message logs"""
    try:
        with open('python_message_logs.json', 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def load_session_debug():
    """Load session debug logs"""
    try:
        with open('session_debug.json', 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def get_orders_from_db():
    """Get orders from database"""
    try:
        conn = sqlite3.connect('orders.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM orders ORDER BY order_date DESC")
        orders = cursor.fetchall()
        conn.close()
        return orders
    except Exception as e:
        print(f"Error reading orders: {e}")
        return []

def analyze_message_patterns():
    """Analyze message patterns and user behavior"""
    logs = load_message_logs()
    
    if not logs:
        print("❌ No message logs found")
        return
    
    print("📊 MESSAGE PATTERN ANALYSIS")
    print("=" * 50)
    
    # User activity analysis
    user_activity = defaultdict(int)
    message_types = Counter()
    hourly_activity = defaultdict(int)
    daily_activity = defaultdict(int)
    
    for log in logs:
        phone = log['phone_number']
        user_activity[phone] += 1
        
        # Analyze message content
        message = log['user_message'].lower()
        if message in ['halo', 'hi', 'hai', 'hello', 'menu']:
            message_types['greeting'] += 1
        elif message in ['1', '2', '3', '4']:
            message_types['menu_selection'] += 1
        elif any(product in message for product in ['kopi', 'teh', 'keripik', 'sambal', 'madu']):
            message_types['product_query'] += 1
        elif message.isdigit():
            message_types['quantity'] += 1
        else:
            message_types['other'] += 1
        
        # Time analysis
        try:
            timestamp = datetime.fromisoformat(log['timestamp'])
            hour = timestamp.hour
            date = timestamp.date()
            hourly_activity[hour] += 1
            daily_activity[date] += 1
        except:
            pass
    
    # Top active users
    print(f"📱 Total unique users: {len(user_activity)}")
    print(f"💬 Total messages: {len(logs)}")
    print(f"📈 Average messages per user: {len(logs) / max(len(user_activity), 1):.1f}")
    
    print("\n🔥 Top 5 Most Active Users:")
    for phone, count in sorted(user_activity.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"  {phone[-6:]}**: {count} messages")
    
    print("\n📋 Message Type Distribution:")
    for msg_type, count in message_types.most_common():
        percentage = (count / len(logs)) * 100
        print(f"  {msg_type.title()}: {count} ({percentage:.1f}%)")
    
    print("\n🕐 Peak Activity Hours:")
    for hour, count in sorted(hourly_activity.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"  {hour:02d}:00 - {hour+1:02d}:00: {count} messages")

def analyze_order_success():
    """Analyze order completion success rate"""
    orders = get_orders_from_db()
    sessions = load_session_debug()
    
    print("\n\n💰 ORDER ANALYSIS")
    print("=" * 50)
    
    if not orders:
        print("❌ No orders found in database")
        return
    
    # Order statistics
    total_orders = len(orders)
    total_revenue = sum(order[6] for order in orders)  # total_amount column
    avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
    
    print(f"🛒 Total orders: {total_orders}")
    print(f"💰 Total revenue: Rp {total_revenue:,.0f}")
    print(f"📊 Average order value: Rp {avg_order_value:,.0f}")
    
    # Product popularity
    product_sales = Counter()
    for order in orders:
        product_name = order[3]
        quantity = order[4]
        product_sales[product_name] += quantity
    
    print("\n🏆 Best Selling Products:")
    for product, quantity in product_sales.most_common(5):
        print(f"  {product}: {quantity} units sold")
    
    # Recent orders
    print("\n📅 Recent Orders (Last 5):")
    for order in orders[:5]:
        order_id, customer, phone, product, qty, price, total, status, date, address = order
        print(f"  #{order_id}: {customer} - {product} x{qty} = Rp {total:,.0f} ({date})")

def analyze_conversion_funnel():
    """Analyze conversion funnel from greeting to order"""
    logs = load_message_logs()
    sessions = load_session_debug()
    
    print("\n\n🔄 CONVERSION FUNNEL ANALYSIS")
    print("=" * 50)
    
    # Track user journey stages
    user_stages = defaultdict(set)
    
    for log in logs:
        phone = log['phone_number']
        message = log['user_message'].lower()
        
        if message in ['halo', 'hi', 'hai', 'hello', 'menu']:
            user_stages['greeted'].add(phone)
        elif message == '2':
            user_stages['started_order'].add(phone)
        elif any(product in message for product in ['kopi', 'teh', 'keripik', 'sambal', 'madu']):
            user_stages['selected_product'].add(phone)
    
    # Count orders completed
    orders = get_orders_from_db()
    completed_orders = set(order[2] for order in orders)  # phone_number column
    
    total_greeted = len(user_stages['greeted'])
    started_orders = len(user_stages['started_order'])
    selected_products = len(user_stages['selected_product'])
    completed = len(completed_orders)
    
    print(f"👋 Users who greeted: {total_greeted}")
    print(f"🛒 Users who started ordering: {started_orders} ({started_orders/max(total_greeted,1)*100:.1f}%)")
    print(f"📦 Users who selected products: {selected_products} ({selected_products/max(started_orders,1)*100:.1f}%)")
    print(f"✅ Users who completed orders: {completed} ({completed/max(selected_products,1)*100:.1f}%)")

def analyze_errors():
    """Analyze errors and failed interactions"""
    logs = load_message_logs()
    
    print("\n\n🚨 ERROR ANALYSIS")
    print("=" * 50)
    
    error_logs = [log for log in logs if log.get('error')]
    total_errors = len(error_logs)
    
    if total_errors == 0:
        print("✅ No errors found in logs")
        return
    
    print(f"❌ Total errors: {total_errors}")
    print(f"📊 Error rate: {(total_errors/len(logs))*100:.2f}%")
    
    # Most common errors
    error_types = Counter()
    for log in error_logs:
        error = log.get('error', '')
        if 'Invalid input' in error:
            error_types['Invalid Input'] += 1
        elif 'timeout' in error.lower():
            error_types['Timeout'] += 1
        elif 'database' in error.lower():
            error_types['Database Error'] += 1
        else:
            error_types['Other'] += 1
    
    print("\n🔍 Error Types:")
    for error_type, count in error_types.most_common():
        print(f"  {error_type}: {count}")

def generate_daily_report():
    """Generate daily summary report"""
    today = datetime.now().date()
    logs = load_message_logs()
    orders = get_orders_from_db()
    
    print("\n\n📅 TODAY'S SUMMARY REPORT")
    print("=" * 50)
    
    # Today's logs
    today_logs = []
    for log in logs:
        try:
            log_date = datetime.fromisoformat(log['timestamp']).date()
            if log_date == today:
                today_logs.append(log)
        except:
            pass
    
    # Today's orders
    today_orders = []
    for order in orders:
        try:
            order_date = datetime.strptime(order[8], '%Y-%m-%d %H:%M:%S').date()
            if order_date == today:
                today_orders.append(order)
        except:
            pass
    
    unique_users_today = len(set(log['phone_number'] for log in today_logs))
    total_messages_today = len(today_logs)
    total_orders_today = len(today_orders)
    revenue_today = sum(order[6] for order in today_orders)
    
    print(f"📱 Active users today: {unique_users_today}")
    print(f"💬 Messages today: {total_messages_today}")
    print(f"🛒 Orders today: {total_orders_today}")
    print(f"💰 Revenue today: Rp {revenue_today:,.0f}")
    
    if total_orders_today > 0:
        conversion_rate = (total_orders_today / unique_users_today) * 100 if unique_users_today > 0 else 0
        print(f"📈 Conversion rate: {conversion_rate:.1f}%")

if __name__ == "__main__":
    print("🤖 WHATSAPP BOT ANALYTICS DASHBOARD")
    print("=" * 60)
    print(f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        analyze_message_patterns()
        analyze_order_success()
        analyze_conversion_funnel()
        analyze_errors()
        generate_daily_report()
        
        print("\n\n✅ Analytics completed!")
        print("💡 Use this data to optimize bot performance and user experience.")
        
    except Exception as e:
        print(f"\n\n❌ Error generating analytics: {e}")
        sys.exit(1)
