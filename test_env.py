#!/usr/bin/env python3
"""Test script to verify environment variables in Railway"""
import os
import sys

print("=" * 50)
print("Environment Variable Test")
print("=" * 50)

# Check for Railway environment
if os.getenv('RAILWAY_ENVIRONMENT'):
    print("✅ Running in Railway environment")
    print(f"   Environment: {os.getenv('RAILWAY_ENVIRONMENT')}")
else:
    print("❌ Not running in Railway environment")

print("\n" + "=" * 50)
print("Email Configuration Check")
print("=" * 50)

# Check email configuration
gmail_email = os.getenv('GMAIL_EMAIL')
gmail_password = os.getenv('GMAIL_APP_PASSWORD')

if gmail_email:
    print(f"✅ GMAIL_EMAIL is set: {gmail_email[:3]}...{gmail_email[-10:]}")
else:
    print("❌ GMAIL_EMAIL is NOT set")

if gmail_password:
    print(f"✅ GMAIL_APP_PASSWORD is set: {'*' * 16}")
else:
    print("❌ GMAIL_APP_PASSWORD is NOT set")

print("\n" + "=" * 50)
print("All Environment Variables")
print("=" * 50)

# Show all environment variables (be careful with sensitive data)
for key, value in sorted(os.environ.items()):
    if 'PASSWORD' in key.upper() or 'SECRET' in key.upper() or 'KEY' in key.upper():
        print(f"{key}={'*' * len(value)}")
    elif key == 'GMAIL_EMAIL':
        if '@' in value:
            parts = value.split('@')
            print(f"{key}={parts[0][:3]}...@{parts[1]}")
        else:
            print(f"{key}={value}")
    else:
        print(f"{key}={value[:50]}..." if len(value) > 50 else f"{key}={value}")

print("\n" + "=" * 50)
print("Test Complete")
print("=" * 50)
sys.exit(0)