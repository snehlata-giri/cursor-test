#!/usr/bin/env python3
"""
Test script to verify the system is working
"""

import requests
import json
import time

def test_backend_health():
    """Test backend health endpoint"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend health check: PASSED")
            print(f"   Response: {response.json()}")
            return True
        else:
            print(f"❌ Backend health check: FAILED (Status: {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ Backend health check: FAILED (Error: {e})")
        return False

def test_frontend():
    """Test frontend accessibility"""
    try:
        response = requests.get("http://localhost:3000", timeout=5)
        if response.status_code == 200:
            print("✅ Frontend accessibility: PASSED")
            return True
        else:
            print(f"❌ Frontend accessibility: FAILED (Status: {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ Frontend accessibility: FAILED (Error: {e})")
        return False

def test_websocket_connection():
    """Test WebSocket connection"""
    try:
        import websocket
        import threading
        
        def on_message(ws, message):
            print(f"✅ WebSocket message received: {message[:100]}...")
            ws.close()
        
        def on_error(ws, error):
            print(f"❌ WebSocket error: {error}")
        
        def on_close(ws, close_status_code, close_msg):
            print("✅ WebSocket connection closed")
        
        def on_open(ws):
            print("✅ WebSocket connection opened")
            # Send a test message
            test_message = {
                "type": "user",
                "content": "Hello, test message",
                "timestamp": "2024-01-01T00:00:00Z"
            }
            ws.send(json.dumps(test_message))
        
        ws = websocket.WebSocketApp(
            "ws://localhost:8000/ws/test_client",
            on_open=on_open,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close
        )
        
        # Run WebSocket in a separate thread
        wst = threading.Thread(target=ws.run_forever)
        wst.daemon = True
        wst.start()
        
        # Wait for connection
        time.sleep(2)
        
        if wst.is_alive():
            print("✅ WebSocket connection: PASSED")
            return True
        else:
            print("❌ WebSocket connection: FAILED")
            return False
            
    except ImportError:
        print("⚠️  WebSocket test skipped (websocket-client not installed)")
        return True
    except Exception as e:
        print(f"❌ WebSocket connection: FAILED (Error: {e})")
        return False

def test_dynamic_query():
    """Test dynamic query parsing"""
    try:
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
        
        from agents.query_parser import QueryParser
        
        parser = QueryParser()
        test_query = "List all vendors costing more than $10,000 a month"
        
        parsed = parser.parse_query(test_query)
        
        if parsed.intent and parsed.sql_query:
            print("✅ Dynamic query parsing: PASSED")
            print(f"   Intent: {parsed.intent.value}")
            print(f"   SQL: {parsed.sql_query[:100]}...")
            return True
        else:
            print("❌ Dynamic query parsing: FAILED")
            return False
            
    except Exception as e:
        print(f"❌ Dynamic query parsing: FAILED (Error: {e})")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Vendor Management System")
    print("=" * 50)
    
    tests = [
        ("Backend Health", test_backend_health),
        ("Frontend Accessibility", test_frontend),
        ("WebSocket Connection", test_websocket_connection),
        ("Dynamic Query Parsing", test_dynamic_query),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Testing {test_name}...")
        if test_func():
            passed += 1
        time.sleep(1)
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! System is ready.")
        print("\n🌐 Access the application at:")
        print("   Frontend: http://localhost:3000")
        print("   Backend API: http://localhost:8000")
        print("   Health Check: http://localhost:8000/health")
    else:
        print("⚠️  Some tests failed. Check the logs above.")

if __name__ == "__main__":
    main()


