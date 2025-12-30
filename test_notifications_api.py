"""
Test script for FCM Notification API endpoints
Run this after starting the Django server
"""
import requests
import json

# Configuration
BASE_URL = "http://127.0.0.1:8000"
# Replace with actual JWT token after authentication
JWT_TOKEN = "YOUR_JWT_TOKEN_HERE"

headers = {
    "Authorization": f"Bearer {JWT_TOKEN}",
    "Content-Type": "application/json"
}

def test_list_notifications():
    """Test listing all notifications"""
    print("\n=== Testing: List Notifications ===")
    url = f"{BASE_URL}/notifications/"
    response = requests.get(url, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.json()

def test_create_notification():
    """Test creating a notification"""
    print("\n=== Testing: Create Notification ===")
    url = f"{BASE_URL}/notifications/create/"
    data = {
        "title": "Test Notification",
        "message": "This is a test notification created via API"
    }
    response = requests.post(url, headers=headers, json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.json()

def test_get_notification_detail(notification_id):
    """Test getting notification detail"""
    print(f"\n=== Testing: Get Notification Detail (ID: {notification_id}) ===")
    url = f"{BASE_URL}/notifications/{notification_id}/"
    response = requests.get(url, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.json()

def test_mark_as_read(notification_id):
    """Test marking notification as read"""
    print(f"\n=== Testing: Mark as Read (ID: {notification_id}) ===")
    url = f"{BASE_URL}/notifications/{notification_id}/mark-as-read/"
    response = requests.patch(url, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.json()

def test_mark_all_as_read():
    """Test marking all notifications as read"""
    print("\n=== Testing: Mark All as Read ===")
    url = f"{BASE_URL}/notifications/mark-all-as-read/"
    response = requests.patch(url, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.json()

def test_delete_notification(notification_id):
    """Test deleting a notification"""
    print(f"\n=== Testing: Delete Notification (ID: {notification_id}) ===")
    url = f"{BASE_URL}/notifications/{notification_id}/delete/"
    response = requests.delete(url, headers=headers)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 204:
        print("Response: Notification deleted successfully (204 No Content)")
    else:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response

def test_list_unread_notifications():
    """Test listing only unread notifications"""
    print("\n=== Testing: List Unread Notifications ===")
    url = f"{BASE_URL}/notifications/?is_read=false"
    response = requests.get(url, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.json()

def run_full_test():
    """Run all tests in sequence"""
    print("=" * 60)
    print("FCM Notification API Tests")
    print("=" * 60)

    if JWT_TOKEN == "YOUR_JWT_TOKEN_HERE":
        print("\n⚠️  ERROR: Please set a valid JWT_TOKEN in the script first!")
        print("To get a token:")
        print("1. Register: POST /auth/register/")
        print("2. Verify OTP: POST /auth/verify-otp/")
        print("3. Copy the 'access' token from the response")
        return

    # Test 1: List all notifications (before creating any)
    test_list_notifications()

    # Test 2: Create a notification
    create_response = test_create_notification()
    if create_response.get('status') == 'success':
        notification_id = create_response['data']['id']

        # Test 3: Get notification detail (auto marks as read)
        test_get_notification_detail(notification_id)

        # Test 4: Create another notification
        test_create_notification()

        # Test 5: List unread notifications
        test_list_unread_notifications()

        # Test 6: Mark specific notification as read
        test_mark_as_read(notification_id)

        # Test 7: Mark all as read
        test_mark_all_as_read()

        # Test 8: List all notifications (after marking as read)
        test_list_notifications()

        # Test 9: Delete notification
        test_delete_notification(notification_id)

        # Test 10: List all notifications (after deletion)
        test_list_notifications()

    print("\n" + "=" * 60)
    print("Tests completed!")
    print("=" * 60)

if __name__ == "__main__":
    # You can run individual tests or the full suite

    # Option 1: Run full test suite
    run_full_test()

    # Option 2: Run individual tests (uncomment to use)
    # test_list_notifications()
    # test_create_notification()
    # test_mark_all_as_read()

