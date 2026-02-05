import time
import requests
import sqlite3
import os

BASE_URL = "http://localhost:8000/api/v1"
DB_PATH = "database.db"

def test_admin_flow():
    # Use the configured admin email
    admin_email = "kootain@gmail.com"
    password = "password123"
    
    print(f"--- Testing Admin Flow with email: {admin_email} ---")
    
    # 1. Register Admin User (if not exists, or just login if exists)
    # We try to register, if fails (already exists), we verify code manually
    print("1. Registering/Logging in Admin...")
    resp = requests.post(f"{BASE_URL}/auth/register", json={
        "email": admin_email,
        "password": password,
        "name": "Admin User"
    })
    
    # If registration failed because user exists, that's fine, we proceed to check DB
    if resp.status_code == 400 and "registered" in resp.text:
         print("   User already registered, proceeding...")
    
    # 1.5 Get verification code from DB
    time.sleep(0.5)
    
    if not os.path.exists(DB_PATH):
        print(f"   Error: Database file {DB_PATH} not found.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT verification_code, is_verified FROM user WHERE email = ?", (admin_email,))
    row = cursor.fetchone()
    
    if not row:
        print("   Error: Admin user not found in DB.")
        # Try registering again to be sure?
        # Actually if 400 was returned, user SHOULD exist. 
        # Maybe DB file path is wrong? Or timing issue?
        # Let's verify DB path
        print(f"   DB Path: {os.path.abspath(DB_PATH)}")
        conn.close()
        return

    code = row[0]
    is_verified = row[1]
    
    if not is_verified and code:
        print(f"   Verifying with code: {code}")
        requests.post(f"{BASE_URL}/auth/verify", json={
            "email": admin_email,
            "code": code
        })
    
    # 2. Login (This should trigger admin promotion)
    print("2. Logging in...")
    resp = requests.post(f"{BASE_URL}/auth/login", json={
        "email": admin_email,
        "password": password
    })
    
    if resp.status_code != 200:
        print(f"Login failed: {resp.text}")
        conn.close()
        return

    data = resp.json()
    token = data["token"]
    user_data = data["user"]
    print(f"   Login Success! Is Admin: {user_data.get('is_admin')}")
    
    assert user_data.get('is_admin') is True, "User should be admin"

    headers = {"Authorization": f"Bearer {token}"}

    # 3. Create a book to test retrieval
    print("3. Creating a test book...")
    book_data = {
        "title": "Admin Test Book",
        "requirements": {
            "topic": "Testing",
            "targetAudience": "Developers",
            "tone": "Technical",
            "keyGoals": ["Test Admin"],
            "pageCountEstimate": 10
        }
    }
    book_resp = requests.post(f"{BASE_URL}/books", json=book_data, headers=headers)
    
    if book_resp.status_code != 200:
        print(f"   Failed to create book: {book_resp.text}")
        return
        
    book_id = book_resp.json()["id"]

    # 4. Test Admin Get All Books (with user data)
    print("4. Testing Admin Get All Books...")
    resp = requests.get(f"{BASE_URL}/admin/books", headers=headers)
    assert resp.status_code == 200
    books = resp.json()
    
    print(f"   Found {len(books)} books in system.")
    
    # Verify user data is present in the response
    # Note: The response model for book might not explicitly include 'user' unless updated
    # Let's check the first book in the list
    if books:
        first_book = books[0]
        print(f"   Checking book: {first_book.get('title')}")
        if 'user' in first_book and first_book['user']:
            print(f"   User data found: {first_book['user']}")
        else:
            print("   WARNING: 'user' field not found or empty in response.")
            raise Exception("'user' field missing from admin book list response")

    # 5. Clean up
    print("5. Cleaning up...")
    requests.delete(f"{BASE_URL}/books/{book_id}", headers=headers)
    conn.close()
    
    print("\n--- ADMIN TEST PASSED! ---")

if __name__ == "__main__":
    try:
        test_admin_flow()
    except Exception as e:
        print(f"Test failed: {e}")
