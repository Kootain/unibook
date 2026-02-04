import time
import requests

BASE_URL = "http://localhost:8000"

def test_flow():
    email = f"test_{int(time.time())}@example.com"
    password = "password123"
    
    print(f"--- Testing with email: {email} ---")
    
    # 1. Register
    print("1. Registering...")
    resp = requests.post(f"{BASE_URL}/auth/register", json={
        "email": email,
        "password": password,
        "name": "Test User"
    })
    assert resp.status_code == 200, resp.text
    data = resp.json()
    token = data["token"]
    user_id = data["user"]["id"]
    print(f"   Success! Token: {token[:20]}...")

    headers = {"Authorization": f"Bearer {token}"}

    # 2. Login
    print("2. Logging in...")
    resp = requests.post(f"{BASE_URL}/auth/login", json={
        "email": email,
        "password": password
    })
    assert resp.status_code == 200
    assert resp.json()["token"] == token
    print("   Success!")

    # 3. Create Book with Base64 Image
    print("3. Creating Book...")
    fake_base64 = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
    book_data = {
        "title": "My AI Book",
        "coverImage": fake_base64,
        "requirements": {
            "topic": "FastAPI",
            "targetAudience": "Developers",
            "tone": "Technical",
            "keyGoals": ["Learn", "Build"],
            "pageCountEstimate": 50
        },
        "outline": [
            {"chapterNumber": 1, "title": "Intro", "description": "Intro chapter", "keyPoints": ["A", "B"]}
        ],
        "chapters": [],
        "status": "draft"
    }
    resp = requests.post(f"{BASE_URL}/books", json=book_data, headers=headers)
    assert resp.status_code == 200
    book = resp.json()
    book_id = book["id"]
    print(f"   Success! Created book ID: {book_id}")
    assert book["coverImage"] == fake_base64

    # 4. Get Books List
    print("4. Getting Books List...")
    resp = requests.get(f"{BASE_URL}/books", headers=headers)
    assert resp.status_code == 200
    books = resp.json()
    assert len(books) >= 1
    assert any(b["id"] == book_id for b in books)
    print(f"   Success! Found {len(books)} books.")

    # 5. Update Book
    print("5. Updating Book...")
    resp = requests.put(f"{BASE_URL}/books/{book_id}", json={"status": "completed"}, headers=headers)
    assert resp.status_code == 200
    assert resp.json()["status"] == "completed"
    print("   Success!")

    # 6. Delete Book
    print("6. Deleting Book...")
    resp = requests.delete(f"{BASE_URL}/books/{book_id}", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["success"] is True
    print("   Success!")

    print("\n--- ALL TESTS PASSED! ---")

if __name__ == "__main__":
    # Note: Ensure the server is running before executing this
    try:
        test_flow()
    except Exception as e:
        print(f"Test failed: {e}")
