# Quick Reference Guide - Notification System

## 🚀 Quick Start

### 1. Authentication
First, get a JWT token:

```bash
# Step 1: Register
curl -X POST "http://127.0.0.1:8000/auth/register/" \
  -H "Content-Type: application/json" \
  -d '{"phone": "+201060074850", "access_level": "Client"}'

# Step 2: Verify OTP (use the OTP from response or SMS)
curl -X POST "http://127.0.0.1:8000/auth/verify-otp/" \
  -H "Content-Type: application/json" \
  -d '{"phone": "+201060074850", "otp": "123456", "access_level": "Client"}'

# Copy the "access" token from the response
```

### 2. Use Notifications

```bash
# Set your token
TOKEN="your_jwt_token_here"

# List notifications
curl -X GET "http://127.0.0.1:8000/notifications/" \
  -H "Authorization: Bearer $TOKEN"

# Create notification
curl -X POST "http://127.0.0.1:8000/notifications/create/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Test", "message": "Hello World"}'

# Mark all as read
curl -X PATCH "http://127.0.0.1:8000/notifications/mark-all-as-read/" \
  -H "Authorization: Bearer $TOKEN"
```

---

## 📍 API Endpoints

### Base URLs
- **General:** `/notifications/`
- **Customer:** `/api/v1/customer/fcm-notifications/`
- **Provider:** `/api/v1/provider/fcm-notifications/`

### Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | List all notifications |
| GET | `/?is_read=false` | List unread notifications |
| POST | `/create/` | Create new notification |
| GET | `/<id>/` | Get detail (auto-marks as read) |
| PATCH | `/<id>/mark-as-read/` | Mark specific as read |
| PATCH | `/mark-all-as-read/` | Mark all as read |
| DELETE | `/<id>/delete/` | Delete notification |

---

## 🔑 Request/Response Examples

### Create Notification
**Request:**
```json
POST /notifications/create/
{
  "title": "New Order",
  "message": "You have a new order #12345"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Notification created successfully",
  "data": {
    "id": 1,
    "user": 123,
    "title": "New Order",
    "message": "You have a new order #12345",
    "is_read": false,
    "create_at": "2025-12-30T12:00:00Z",
    "update_at": "2025-12-30T12:00:00Z"
  }
}
```

### List Notifications
**Request:**
```
GET /notifications/
```

**Response:**
```json
{
  "status": "success",
  "message": "Notifications retrieved successfully",
  "data": [
    {
      "id": 1,
      "user": 123,
      "title": "New Order",
      "message": "You have a new order #12345",
      "is_read": false,
      "create_at": "2025-12-30T12:00:00Z",
      "update_at": "2025-12-30T12:00:00Z"
    }
  ]
}
```

---

## 🐛 Common Issues & Solutions

### Issue 1: 404 Not Found
**Problem:** Getting 404 on `/notifications/notifications/`
**Solution:** ✅ Fixed! Use `/notifications/` instead

### Issue 2: User ID not saving
**Problem:** Notifications created without user association
**Solution:** ✅ Fixed! User is now automatically assigned

### Issue 3: Firebase CONFIGURATION_NOT_FOUND
**Problem:** Firebase authentication error
**Solution:** Enable Phone Auth in Firebase Console (see FIREBASE_AUTH_FIX.md)

---

## 🎨 Frontend Integration (React/Vue/Angular)

### JavaScript Constants
```javascript
const API_BASE = "http://127.0.0.1:8000";
const API_NOTIFICATION = {
  LIST: "/notifications/",
  CREATE: "/notifications/create/",
  DETAIL: (id) => `/notifications/${id}/`,
  MARK_READ: (id) => `/notifications/${id}/mark-as-read/`,
  MARK_ALL_READ: "/notifications/mark-all-as-read/",
  DELETE: (id) => `/notifications/${id}/delete/`,
};
```

### Axios Example
```javascript
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://127.0.0.1:8000',
  headers: {
    'Authorization': `Bearer ${localStorage.getItem('token')}`,
    'Content-Type': 'application/json'
  }
});

// List notifications
const getNotifications = async () => {
  const response = await api.get('/notifications/');
  return response.data;
};

// Create notification
const createNotification = async (title, message) => {
  const response = await api.post('/notifications/create/', {
    title,
    message
  });
  return response.data;
};

// Mark all as read
const markAllAsRead = async () => {
  const response = await api.patch('/notifications/mark-all-as-read/');
  return response.data;
};
```

### Fetch API Example
```javascript
const token = localStorage.getItem('token');

// List notifications
fetch('http://127.0.0.1:8000/notifications/', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
})
.then(res => res.json())
.then(data => console.log(data));

// Create notification
fetch('http://127.0.0.1:8000/notifications/create/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    title: 'Test',
    message: 'Test message'
  })
})
.then(res => res.json())
.then(data => console.log(data));
```

---

## 📱 Mobile Integration (React Native/Flutter)

### React Native Example
```javascript
import AsyncStorage from '@react-native-async-storage/async-storage';

const getToken = async () => {
  return await AsyncStorage.getItem('jwt_token');
};

const fetchNotifications = async () => {
  const token = await getToken();
  const response = await fetch('http://YOUR_IP:8000/notifications/', {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  return await response.json();
};
```

### Flutter/Dart Example
```dart
import 'package:http/http.dart' as http;
import 'dart:convert';

Future<List<Notification>> getNotifications(String token) async {
  final response = await http.get(
    Uri.parse('http://YOUR_IP:8000/notifications/'),
    headers: {
      'Authorization': 'Bearer $token',
    },
  );
  
  if (response.statusCode == 200) {
    final data = json.decode(response.body);
    return data['data'].map((n) => Notification.fromJson(n)).toList();
  } else {
    throw Exception('Failed to load notifications');
  }
}
```

---

## ✅ Testing Checklist

- [ ] Django server running without errors
- [ ] Can list notifications
- [ ] Can create notifications
- [ ] Notifications have user_id assigned
- [ ] Can mark notifications as read
- [ ] Can delete notifications
- [ ] 404 errors resolved
- [ ] Firebase Phone Auth enabled (optional)
- [ ] Frontend integrated and tested

---

## 📞 Support Files

- **Full API Docs:** `NOTIFICATION_API_ENDPOINTS.md`
- **Firebase Fix:** `FIREBASE_AUTH_FIX.md`
- **Changes Summary:** `CHANGES_SUMMARY.md`
- **Test Script:** `test_notifications_api.py`

---

## 🎯 Production Deployment

Before deploying:
1. Update `DEBUG=False` in settings
2. Configure production database
3. Set up proper CORS headers
4. Enable Firebase Phone Auth
5. Update frontend API base URLs
6. Set up SSL/HTTPS
7. Configure proper error logging

---

**Last Updated:** December 30, 2025

