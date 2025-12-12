# FCM Notification API Documentation

## Overview
Complete REST API for managing FCM (Firebase Cloud Messaging) notifications with list, create, read, mark as read, and delete operations.

## API Endpoints

### 1. List All Notifications
**Endpoint:** `GET /api/v1/notifications/`
**Authentication:** Required (JWT Token)
**Query Parameters:**
- `is_read` (optional): Filter by read status - `true` or `false`

**Example:**
```bash
GET /api/v1/notifications/
GET /api/v1/notifications/?is_read=false  # Get only unread notifications
GET /api/v1/notifications/?is_read=true   # Get only read notifications
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
            "title": "Order Update",
            "message": "Your order has been confirmed",
            "is_read": false,
            "create_at": "2025-12-12T10:30:00Z",
            "update_at": "2025-12-12T10:30:00Z"
        }
    ]
}
```

---

### 2. Get Notification Detail (and Mark as Read)
**Endpoint:** `GET /api/v1/notifications/<notification_id>/`
**Authentication:** Required (JWT Token)
**Method:** GET
**Description:** Retrieve a specific notification and automatically mark it as read

**Example:**
```bash
GET /api/v1/notifications/1/
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
        "title": "Order Update",
        "message": "Your order has been confirmed",
        "is_read": true,
        "create_at": "2025-12-12T10:30:00Z",
        "update_at": "2025-12-12T10:30:00Z"
    }
}
```

---

### 3. Create Notification
**Endpoint:** `POST /api/v1/notifications/create/`
**Authentication:** Required (JWT Token)
**Method:** POST
**Description:** Create a new notification. Regular users create notifications for themselves. Superusers/admins can create for other users.

**Request Body:**
```json
{
    "title": "Notification Title",
    "message": "Notification message content",
    "user": 1
}
```

**Note:** If you're not a superuser and don't provide a user ID, the notification will be created for your own account.

**Response (201 Created):**
```json
{
    "isSuccess": true,
    "message": "Notification created successfully",
    "statusCode": 201,
    "data": {
        "id": 2,
        "user": 1,
        "title": "Notification Title",
        "message": "Notification message content",
        "is_read": false,
        "create_at": "2025-12-12T10:35:00Z",
        "update_at": "2025-12-12T10:35:00Z"
    }
}
```

---

### 4. Mark Single Notification as Read
**Endpoint:** `PATCH /api/v1/notifications/<notification_id>/mark-as-read/`
**Authentication:** Required (JWT Token)
**Method:** PATCH
**Description:** Mark a specific notification as read

**Example:**
```bash
PATCH /api/v1/notifications/1/mark-as-read/
```

**Response (200 OK):**
```json
{
    "isSuccess": true,
    "message": "Notification marked as read",
    "statusCode": 200,
    "data": {
        "id": 1,
        "user": 1,
        "title": "Order Update",
        "message": "Your order has been confirmed",
        "is_read": true,
        "create_at": "2025-12-12T10:30:00Z",
        "update_at": "2025-12-12T10:30:00Z"
    }
}
```

---

### 5. Mark All Notifications as Read
**Endpoint:** `PATCH /api/v1/notifications/mark-all-as-read/`
**Authentication:** Required (JWT Token)
**Method:** PATCH
**Description:** Mark all unread notifications as read for the authenticated user

**Example:**
```bash
PATCH /api/v1/notifications/mark-all-as-read/
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

---

### 6. Delete Notification
**Endpoint:** `DELETE /api/v1/notifications/<notification_id>/delete/`
**Authentication:** Required (JWT Token)
**Method:** DELETE
**Description:** Delete a specific notification

**Example:**
```bash
DELETE /api/v1/notifications/1/delete/
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

## Error Responses

### 404 Not Found
```json
{
    "isSuccess": false,
    "message": "Notification not found",
    "statusCode": 404,
    "errors": null
}
```

### 400 Bad Request (Validation Error)
```json
{
    "isSuccess": false,
    "message": "Validation error",
    "statusCode": 400,
    "errors": {
        "title": ["This field is required."],
        "message": ["This field is required."]
    }
}
```

### 401 Unauthorized (Missing Token)
```json
{
    "detail": "Authentication credentials were not provided."
}
```

### 500 Internal Server Error
```json
{
    "isSuccess": false,
    "message": "Error creating notification",
    "statusCode": 500,
    "errors": "error details"
}
```

---

## cURL Examples

### List Notifications
```bash
curl -X GET "http://localhost:8000/api/v1/notifications/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json"
```

### Get Notification Detail
```bash
curl -X GET "http://localhost:8000/api/v1/notifications/1/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json"
```

### Create Notification
```bash
curl -X POST "http://localhost:8000/api/v1/notifications/create/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "New Order",
    "message": "You have a new order from customer"
  }'
```

### Mark as Read
```bash
curl -X PATCH "http://localhost:8000/api/v1/notifications/1/mark-as-read/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json"
```

### Mark All as Read
```bash
curl -X PATCH "http://localhost:8000/api/v1/notifications/mark-all-as-read/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json"
```

### Delete Notification
```bash
curl -X DELETE "http://localhost:8000/api/v1/notifications/1/delete/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json"
```

---

## Features

✅ **List Notifications** - Retrieve all notifications with optional filtering
✅ **Get Detail** - Retrieve single notification and auto-mark as read
✅ **Create** - Create new notifications in the database
✅ **Mark as Read** - Mark individual or all notifications as read
✅ **Delete** - Remove notifications
✅ **JWT Authentication** - Secure endpoints with token-based authentication
✅ **Filtering** - Filter by read status
✅ **Error Handling** - Comprehensive error responses
✅ **Logging** - All operations are logged for debugging

---

## Model Fields

The FcmNotification model contains:
- **id** - Primary key (auto-generated)
- **user** - ForeignKey to User (who receives the notification)
- **title** - Notification title (max 255 characters)
- **message** - Notification message (text field)
- **is_read** - Boolean flag (default: False)
- **create_at** - Auto-generated timestamp
- **update_at** - Auto-updated timestamp

---

## Security Notes

1. All endpoints require JWT authentication
2. Users can only access/modify their own notifications
3. Superusers/admins can create notifications for any user
4. All operations are logged for audit purposes
5. Proper error handling prevents information leakage

