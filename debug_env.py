import os
print("=== DEBUG ENV ===")
print(f"SUPABASE_URL: {os.getenv('SUPABASE_URL', 'NOT SET')[:50]}...")
api_key = os.getenv('SUPABASE_API_KEY', 'NOT SET')
if api_key != 'NOT SET':
    # نمایش بخشی از کلید برای تشخیص نوع
    import base64, json
    try:
        payload = api_key.split('.')[1]
        payload += '=' * (4 - len(payload) % 4)
        decoded = json.loads(base64.b64decode(payload))
        print(f"API Key Role: {decoded.get('role', 'unknown')}")
    except:
        print("Could not decode API key")
print("=================")
