# FCM Notification API Endpoints

## Overview
This document describes the FCM (Firebase Cloud Messaging) notification endpoints available in the application.

## Base URLs

### General Notifications (Authentication Required)
- **Base URL**: `/notifications/`
- Authentication: JWT Token Required

### Customer-Specific Notifications
- **Base URL**: `/api/v1/customer/fcm-notifications/`
- Authentication: JWT Token Required (Customer role)

### Provider-Specific Notifications
- **Base URL**: `/api/v1/provider/fcm-notifications/`
- Authentication: JWT Token Required (Provider role)

---

## Endpoints

### 1. List All Notifications
**GET** `/notifications/` or role-specific URL

**Description**: Get all notifications for the authenticated user.

**Query Parameters**:
- `is_read` (optional): Filter by read status (true/false)

**Example Request**:
```bash
GET /notifications/?is_read=false
Authorization: Bearer <your_jwt_token>
```

**Example Response**:
```json
{
  "status": "success",
  "message": "Notifications retrieved successfully",
  "data": [
    {
      "id": 1,
      "user": 123,
      "title": "New Message",
      "message": "You have a new message from provider",
      "is_read": false,
      "create_at": "2025-12-30T10:00:00Z",
      "update_at": "2025-12-30T10:00:00Z"
    }
  ]
}
```

---

### 2. Create Notification
**POST** `/notifications/create/` or role-specific URL

**Description**: Create a new notification. Regular users create notifications for themselves. Superusers can create notifications for any user.

**Request Body**:
```json
{
  "title": "Notification Title",
  "message": "Notification message content",
  "user": 456  // Optional: Only superusers can specify another user
}
```

**Example Response**:
```json
{
  "status": "success",
  "message": "Notification created successfully",
  "data": {
    "id": 2,
    "user": 123,
    "title": "Notification Title",
    "message": "Notification message content",
    "is_read": false,
    "create_at": "2025-12-30T11:00:00Z",
    "update_at": "2025-12-30T11:00:00Z"
  }
}
```

---

### 3. Get Notification Detail
**GET** `/notifications/<notification_id>/` or role-specific URL

**Description**: Get a specific notification and automatically mark it as read.

**Example Request**:
```bash
GET /notifications/1/
Authorization: Bearer <your_jwt_token>
```

**Example Response**:
```json
{
  "status": "success",
  "message": "Notification retrieved and marked as read",
  "data": {
    "id": 1,
    "user": 123,
    "title": "New Message",
    "message": "You have a new message from provider",
    "is_read": true,
    "create_at": "2025-12-30T10:00:00Z",
    "update_at": "2025-12-30T12:00:00Z"
  }
}
```

---

### 4. Mark Notification as Read
**PATCH** `/notifications/<notification_id>/mark-as-read/` or role-specific URL

**Description**: Mark a specific notification as read.

**Example Request**:
```bash
PATCH /notifications/1/mark-as-read/
Authorization: Bearer <your_jwt_token>
```

**Example Response**:
```json
{
  "status": "success",
  "message": "Notification marked as read",
  "data": {
    "id": 1,
    "user": 123,
    "title": "New Message",
    "message": "You have a new message from provider",
    "is_read": true,
    "create_at": "2025-12-30T10:00:00Z",
    "update_at": "2025-12-30T12:00:00Z"
  }
}
```

---

### 5. Mark All Notifications as Read
**PATCH** `/notifications/mark-all-as-read/` or role-specific URL

**Description**: Mark all unread notifications as read for the authenticated user.

**Example Request**:
```bash
PATCH /notifications/mark-all-as-read/
Authorization: Bearer <your_jwt_token>
```

**Example Response**:
```json
{
  "status": "success",
  "message": "All 5 unread notification(s) marked as read",
  "data": {
    "updated_count": 5
  }
}
```

---

### 6. Delete Notification
**DELETE** `/notifications/<notification_id>/delete/` or role-specific URL

**Description**: Delete a specific notification.

**Example Request**:
```bash
DELETE /notifications/1/delete/
Authorization: Bearer <your_jwt_token>
```

**Example Response**:
```json
{
  "status": "success",
  "message": "Notification deleted successfully"
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "status": "error",
  "message": "Validation error",
  "errors": {
    "title": ["This field is required."]
  }
}
```

### 401 Unauthorized
```json
{
  "status": "error",
  "message": "Authentication credentials were not provided."
}
```

### 404 Not Found
```json
{
  "status": "error",
  "message": "Notification not found"
}
```

### 500 Internal Server Error
```json
{
  "status": "error",
  "message": "Error fetching notifications",
  "errors": "Detailed error message"
}
```

---

## Frontend Constants (JavaScript/TypeScript)

Update your frontend constants as follows:

```javascript
// Notification Endpoints
const API_NOTIFICATION_LIST = "notifications/";
const API_NOTIFICATION_CREATE = "notifications/create/";
const API_NOTIFICATION_DETAIL = (id) => `notifications/${id}/`;
const API_NOTIFICATION_MARK_READ = (id) => `notifications/${id}/mark-as-read/`;
const API_NOTIFICATION_MARK_ALL_READ = "notifications/mark-all-as-read/";
const API_NOTIFICATION_DELETE = (id) => `notifications/${id}/delete/`;

// For Customer-specific
const API_CUSTOMER_NOTIFICATION_LIST = "api/v1/customer/fcm-notifications/";
const API_CUSTOMER_NOTIFICATION_CREATE = "api/v1/customer/fcm-notifications/create/";
const API_CUSTOMER_NOTIFICATION_DETAIL = (id) => `api/v1/customer/fcm-notifications/${id}/`;
const API_CUSTOMER_NOTIFICATION_MARK_READ = (id) => `api/v1/customer/fcm-notifications/${id}/mark-as-read/`;
const API_CUSTOMER_NOTIFICATION_MARK_ALL_READ = "api/v1/customer/fcm-notifications/mark-all-as-read/";
const API_CUSTOMER_NOTIFICATION_DELETE = (id) => `api/v1/customer/fcm-notifications/${id}/delete/`;

// For Provider-specific
const API_PROVIDER_NOTIFICATION_LIST = "api/v1/provider/fcm-notifications/";
const API_PROVIDER_NOTIFICATION_CREATE = "api/v1/provider/fcm-notifications/create/";
const API_PROVIDER_NOTIFICATION_DETAIL = (id) => `api/v1/provider/fcm-notifications/${id}/`;
const API_PROVIDER_NOTIFICATION_MARK_READ = (id) => `api/v1/provider/fcm-notifications/${id}/mark-as-read/`;
const API_PROVIDER_NOTIFICATION_MARK_ALL_READ = "api/v1/provider/fcm-notifications/mark-all-as-read/";
const API_PROVIDER_NOTIFICATION_DELETE = (id) => `api/v1/provider/fcm-notifications/${id}/delete/`;
```

---

## Notes

1. **Authentication**: All endpoints require JWT authentication.
2. **User Assignment**: Notifications are automatically assigned to the authenticated user. Only superusers can create notifications for other users.
3. **Read-only Fields**: The `id`, `create_at`, `update_at`, and `user` fields are read-only and set automatically.
4. **Auto-Read**: Getting notification details automatically marks the notification as read.
5. **Ordering**: Notifications are ordered by creation date (newest first).

---

## Firebase Authentication Issue Fix

The error "No auth provider found for the given identifier (CONFIGURATION_NOT_FOUND)" has been addressed with the following improvements:

### 1. Phone Number Formatting
- Phone numbers are now automatically formatted to E.164 format (e.g., +201060074850)
- If a phone number doesn't start with '+', it will be automatically prefixed

### 2. Error Handling
- Better error messages for Firebase authentication issues
- Handles PhoneNumberAlreadyExistsError gracefully
- Provides clear logging messages

### 3. Required Firebase Configuration
To completely resolve the Firebase authentication issue, you need to:

1. **Enable Phone Authentication in Firebase Console**:
   - Go to [Firebase Console](https://console.firebase.google.com/)
   - Select your project: `daberny-ff5fd`
   - Navigate to: **Authentication** > **Sign-in method**
   - Enable **Phone** authentication provider
   - Configure the settings as needed

2. **Verify Service Account Key**:
   - The `serviceAccountKey.json` file is correctly configured
   - Ensure it has proper permissions in Firebase IAM

3. **Check Phone Number Format**:
   - Ensure all phone numbers in your database start with country code
   - Format: +[country code][number] (e.g., +201060074850)

---

## Testing

You can test the endpoints using cURL or Postman:

```bash
# List notifications
curl -X GET "http://127.0.0.1:8000/notifications/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Create notification
curl -X POST "http://127.0.0.1:8000/notifications/create/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Test", "message": "Test message"}'

# Mark as read
curl -X PATCH "http://127.0.0.1:8000/notifications/1/mark-as-read/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Delete notification
curl -X DELETE "http://127.0.0.1:8000/notifications/1/delete/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

