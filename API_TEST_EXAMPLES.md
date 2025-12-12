# FCM Notification API - Test Examples

## HTTP Request Examples (Use in Postman, Thunder Client, Insomnia, etc.)

### Prerequisites
- Django server running: `python manage.py runserver`
- Valid JWT token from login endpoint

---

## 1. LIST NOTIFICATIONS

### GET All Notifications
```http
GET http://localhost:8000/api/v1/notifications/
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json
```

**Response (200 OK):**
```json
{
    "isSuccess": true,
    "message": "Notifications retrieved successfully",
    "statusCode": 200,
    "data": [
        {
            "id": 1,
            "user": 1,
            "title": "Order Confirmed",
            "message": "Your order #123 has been confirmed",
            "is_read": false,
            "create_at": "2025-12-12T10:30:00Z",
            "update_at": "2025-12-12T10:30:00Z"
        },
        {
            "id": 2,
            "user": 1,
            "title": "Payment Received",
            "message": "We received your payment of $50",
            "is_read": true,
            "create_at": "2025-12-11T15:20:00Z",
            "update_at": "2025-12-11T15:25:00Z"
        }
    ]
}
```

---

### GET Only Unread Notifications
```http
GET http://localhost:8000/api/v1/notifications/?is_read=false
Authorization: Bearer YOUR_JWT_TOKEN
Content-Type: application/json
```

**Response (200 OK):**
```json
{
    "isSuccess": true,
    "message": "Notifications retrieved successfully",
    "statusCode": 200,
    "data": [
        {
            "id": 1,
            "user": 1,
            "title": "Order Confirmed",
            "message": "Your order #123 has been confirmed",
            "is_read": false,
            "create_at": "2025-12-12T10:30:00Z",
            "update_at": "2025-12-12T10:30:00Z"
        }
    ]
}
```

---

### GET Only Read Notifications
```http
GET http://localhost:8000/api/v1/notifications/?is_read=true
Authorization: Bearer YOUR_JWT_TOKEN
Content-Type: application/json
```

---

## 2. GET SINGLE NOTIFICATION (Auto-marks as read)

### GET Notification by ID
```http
GET http://localhost:8000/api/v1/notifications/1/
Authorization: Bearer YOUR_JWT_TOKEN
Content-Type: application/json
```

**Response (200 OK):**
```json
{
    "isSuccess": true,
    "message": "Notification retrieved and marked as read",
    "statusCode": 200,
    "data": {
        "id": 1,
        "user": 1,
        "title": "Order Confirmed",
        "message": "Your order #123 has been confirmed",
        "is_read": true,
        "create_at": "2025-12-12T10:30:00Z",
        "update_at": "2025-12-12T10:30:00Z"
    }
}
```

**Note:** The `is_read` field will be set to `true` automatically.

---

## 3. CREATE NOTIFICATION

### POST New Notification (Regular User)
```http
POST http://localhost:8000/api/v1/notifications/create/
Authorization: Bearer YOUR_JWT_TOKEN
Content-Type: application/json

{
    "title": "New Order Arrived",
    "message": "You have a new order from John Doe"
}
```

**Response (201 Created):**
```json
{
    "isSuccess": true,
    "message": "Notification created successfully",
    "statusCode": 201,
    "data": {
        "id": 3,
        "user": 1,
        "title": "New Order Arrived",
        "message": "You have a new order from John Doe",
        "is_read": false,
        "create_at": "2025-12-12T11:45:00Z",
        "update_at": "2025-12-12T11:45:00Z"
    }
}
```

---

### POST Notification (Admin for Another User)
```http
POST http://localhost:8000/api/v1/notifications/create/
Authorization: Bearer YOUR_ADMIN_JWT_TOKEN
Content-Type: application/json

{
    "user": 5,
    "title": "Account Suspended",
    "message": "Your account has been suspended due to policy violation"
}
```

**Response (201 Created):**
```json
{
    "isSuccess": true,
    "message": "Notification created successfully",
    "statusCode": 201,
    "data": {
        "id": 4,
        "user": 5,
        "title": "Account Suspended",
        "message": "Your account has been suspended due to policy violation",
        "is_read": false,
        "create_at": "2025-12-12T11:50:00Z",
        "update_at": "2025-12-12T11:50:00Z"
    }
}
```

---

### POST Error - Missing Required Field
```http
POST http://localhost:8000/api/v1/notifications/create/
Authorization: Bearer YOUR_JWT_TOKEN
Content-Type: application/json

{
    "title": "Missing message field"
}
```

**Response (400 Bad Request):**
```json
{
    "isSuccess": false,
    "message": "Validation error",
    "statusCode": 400,
    "errors": {
        "message": ["This field is required."]
    }
}
```

---

## 4. MARK SINGLE NOTIFICATION AS READ

### PATCH Mark as Read
```http
PATCH http://localhost:8000/api/v1/notifications/2/mark-as-read/
Authorization: Bearer YOUR_JWT_TOKEN
Content-Type: application/json
```

**Response (200 OK):**
```json
{
    "isSuccess": true,
    "message": "Notification marked as read",
    "statusCode": 200,
    "data": {
        "id": 2,
        "user": 1,
        "title": "Payment Received",
        "message": "We received your payment of $50",
        "is_read": true,
        "create_at": "2025-12-11T15:20:00Z",
        "update_at": "2025-12-12T11:55:00Z"
    }
}
```

---

### PATCH Error - Notification Not Found
```http
PATCH http://localhost:8000/api/v1/notifications/999/mark-as-read/
Authorization: Bearer YOUR_JWT_TOKEN
Content-Type: application/json
```

**Response (404 Not Found):**
```json
{
    "isSuccess": false,
    "message": "Notification not found",
    "statusCode": 404,
    "errors": null
}
```

---

## 5. MARK ALL NOTIFICATIONS AS READ

### PATCH Mark All as Read
```http
PATCH http://localhost:8000/api/v1/notifications/mark-all-as-read/
Authorization: Bearer YOUR_JWT_TOKEN
Content-Type: application/json
```

**Response (200 OK):**
```json
{
    "isSuccess": true,
    "message": "All 5 unread notification(s) marked as read",
    "statusCode": 200,
    "data": {
        "updated_count": 5
    }
}
```

**Note:** Returns the count of notifications that were updated.

---

## 6. DELETE NOTIFICATION

### DELETE Notification
```http
DELETE http://localhost:8000/api/v1/notifications/3/delete/
Authorization: Bearer YOUR_JWT_TOKEN
Content-Type: application/json
```

**Response (204 No Content):**
```json
{
    "isSuccess": true,
    "message": "Notification deleted successfully",
    "statusCode": 204
}
```

---

### DELETE Error - Not Found
```http
DELETE http://localhost:8000/api/v1/notifications/999/delete/
Authorization: Bearer YOUR_JWT_TOKEN
Content-Type: application/json
```

**Response (404 Not Found):**
```json
{
    "isSuccess": false,
    "message": "Notification not found",
    "statusCode": 404,
    "errors": null
}
```

---

## CURL Command Examples

### List Notifications
```bash
curl -X GET "http://localhost:8000/api/v1/notifications/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json"
```

### Create Notification
```bash
curl -X POST "http://localhost:8000/api/v1/notifications/create/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Notification",
    "message": "This is a test notification"
  }'
```

### Get Single Notification
```bash
curl -X GET "http://localhost:8000/api/v1/notifications/1/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json"
```

### Mark as Read
```bash
curl -X PATCH "http://localhost:8000/api/v1/notifications/1/mark-as-read/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json"
```

### Mark All as Read
```bash
curl -X PATCH "http://localhost:8000/api/v1/notifications/mark-all-as-read/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json"
```

### Delete Notification
```bash
curl -X DELETE "http://localhost:8000/api/v1/notifications/1/delete/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json"
```

---

## Python Requests Examples

### List Notifications
```python
import requests

url = "http://localhost:8000/api/v1/notifications/"
headers = {
    "Authorization": "Bearer YOUR_JWT_TOKEN",
    "Content-Type": "application/json"
}

response = requests.get(url, headers=headers)
print(response.json())
```

### Create Notification
```python
import requests

url = "http://localhost:8000/api/v1/notifications/create/"
headers = {
    "Authorization": "Bearer YOUR_JWT_TOKEN",
    "Content-Type": "application/json"
}
data = {
    "title": "Test Notification",
    "message": "This is a test"
}

response = requests.post(url, json=data, headers=headers)
print(response.json())
```

### Mark as Read
```python
import requests

notification_id = 1
url = f"http://localhost:8000/api/v1/notifications/{notification_id}/mark-as-read/"
headers = {
    "Authorization": "Bearer YOUR_JWT_TOKEN",
    "Content-Type": "application/json"
}

response = requests.patch(url, headers=headers)
print(response.json())
```

### Delete Notification
```python
import requests

notification_id = 1
url = f"http://localhost:8000/api/v1/notifications/{notification_id}/delete/"
headers = {
    "Authorization": "Bearer YOUR_JWT_TOKEN",
    "Content-Type": "application/json"
}

response = requests.delete(url, headers=headers)
print(response.json())
```

---

## JavaScript/Fetch Examples

### List Notifications
```javascript
const token = "YOUR_JWT_TOKEN";
const url = "http://localhost:8000/api/v1/notifications/";

fetch(url, {
    method: "GET",
    headers: {
        "Authorization": `Bearer ${token}`,
        "Content-Type": "application/json"
    }
})
.then(response => response.json())
.then(data => console.log(data))
.catch(error => console.error("Error:", error));
```

### Create Notification
```javascript
const token = "YOUR_JWT_TOKEN";
const url = "http://localhost:8000/api/v1/notifications/create/";

fetch(url, {
    method: "POST",
    headers: {
        "Authorization": `Bearer ${token}`,
        "Content-Type": "application/json"
    },
    body: JSON.stringify({
        title: "Test Notification",
        message: "This is a test notification"
    })
})
.then(response => response.json())
.then(data => console.log(data))
.catch(error => console.error("Error:", error));
```

### Mark as Read
```javascript
const token = "YOUR_JWT_TOKEN";
const notificationId = 1;
const url = `http://localhost:8000/api/v1/notifications/${notificationId}/mark-as-read/`;

fetch(url, {
    method: "PATCH",
    headers: {
        "Authorization": `Bearer ${token}`,
        "Content-Type": "application/json"
    }
})
.then(response => response.json())
.then(data => console.log(data))
.catch(error => console.error("Error:", error));
```

### Delete Notification
```javascript
const token = "YOUR_JWT_TOKEN";
const notificationId = 1;
const url = `http://localhost:8000/api/v1/notifications/${notificationId}/delete/`;

fetch(url, {
    method: "DELETE",
    headers: {
        "Authorization": `Bearer ${token}`,
        "Content-Type": "application/json"
    }
})
.then(response => response.json())
.then(data => console.log(data))
.catch(error => console.error("Error:", error));
```

---

## Testing Workflow

1. **Get your JWT token:**
   - Use your login endpoint to get a token
   - Copy the token value

2. **List all notifications:**
   - Use the GET request above
   - Verify you see your notifications

3. **Create a test notification:**
   - Use the POST request
   - Verify it appears in the list

4. **Mark as read:**
   - Use PATCH request
   - Verify `is_read` changed to `true`

5. **Delete notification:**
   - Use DELETE request
   - Verify it no longer appears in the list

---

## Postman Setup

1. **Create Environment Variables:**
   - `base_url` = `http://localhost:8000`
   - `token` = Your JWT token

2. **Use in requests:**
   - URL: `{{base_url}}/api/v1/notifications/`
   - Header: `Authorization: Bearer {{token}}`

3. **Import Collection:**
   - Create each request with examples above
   - Save as collection for reuse

---

Ready to test! 🧪

