# FCM Notification API - Quick Reference

## Endpoints Summary

| Method | Endpoint | Purpose | Auth | Status |
|--------|----------|---------|------|--------|
| GET | `/api/v1/notifications/` | List all notifications | ✓ | 200 |
| GET | `/api/v1/notifications/?is_read=false` | List unread only | ✓ | 200 |
| GET | `/api/v1/notifications/<id>/` | Get detail + mark read | ✓ | 200 |
| POST | `/api/v1/notifications/create/` | Create new | ✓ | 201 |
| PATCH | `/api/v1/notifications/<id>/mark-as-read/` | Mark single as read | ✓ | 200 |
| PATCH | `/api/v1/notifications/mark-all-as-read/` | Mark all as read | ✓ | 200 |
| DELETE | `/api/v1/notifications/<id>/delete/` | Delete notification | ✓ | 204 |

## Quick Test Examples

### List Notifications
```bash
curl -X GET "http://localhost:8000/api/v1/notifications/" \
  -H "Authorization: Bearer TOKEN"
```

### Create Notification
```bash
curl -X POST "http://localhost:8000/api/v1/notifications/create/" \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Test","message":"Test message"}'
```

### Mark as Read
```bash
curl -X PATCH "http://localhost:8000/api/v1/notifications/1/mark-as-read/" \
  -H "Authorization: Bearer TOKEN"
```

### Delete
```bash
curl -X DELETE "http://localhost:8000/api/v1/notifications/1/delete/" \
  -H "Authorization: Bearer TOKEN"
```

## Database Schema

```
FcmNotification (Model)
├── id (PrimaryKey, auto-generated)
├── user (ForeignKey → User)
├── title (CharField, max_length=255)
├── message (TextField)
├── is_read (BooleanField, default=False)
├── create_at (DateTimeField, auto_now_add=True)
└── update_at (DateTimeField, auto_now=True)
```

## Files Modified/Created

1. ✅ `/api/v1/global_serializer/common_serializer.py` (UPDATED)
2. ✅ `/api/v1/global_views/fcm_notification_views.py` (CREATED)
3. ✅ `/api/v1/urls.py` (UPDATED)

## View Functions (6 Total)

1. `list_notifications()` - GET all notifications
2. `get_notification_detail()` - GET single + auto-read
3. `create_notification()` - POST new notification
4. `mark_as_read()` - PATCH single notification
5. `mark_all_as_read()` - PATCH all unread
6. `delete_notification()` - DELETE notification

## Features

- ✅ List/filter notifications
- ✅ Create & save to DB
- ✅ Retrieve single with auto-read
- ✅ Mark as read (single/all)
- ✅ Delete notifications
- ✅ JWT authentication
- ✅ User isolation
- ✅ Error handling
- ✅ Logging

## Common Response Codes

- `200 OK` - List, detail, mark as read
- `201 CREATED` - Create notification
- `204 NO CONTENT` - Delete successful
- `400 BAD REQUEST` - Validation error
- `401 UNAUTHORIZED` - Missing/invalid token
- `404 NOT FOUND` - Notification doesn't exist
- `500 INTERNAL ERROR` - Server error

## How to Use

1. **Get your JWT token** (from auth endpoints)
2. **Include token** in Authorization header
3. **Make requests** to the endpoints
4. **Parse responses** using the standard format

All endpoints are production-ready! 🎉

