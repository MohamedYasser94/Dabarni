# Firebase Authentication Configuration Guide

## Issue
**Error Message**: "No auth provider found for the given identifier (CONFIGURATION_NOT_FOUND)"

## Root Cause
This error occurs when:
1. Firebase Phone Authentication is not enabled in the Firebase Console
2. Phone numbers are not in the correct E.164 format
3. The Firebase project is not properly configured for phone auth

## Solution Implemented

### 1. Code Improvements (Already Done)

#### Phone Number Formatting
The authentication code now automatically formats phone numbers to E.164 format:
- Before: `201060074850` or `01060074850`
- After: `+201060074850`

Location: `api/v1/authentication.py` (lines ~145-165)

#### Enhanced Error Handling
- Catches `UserNotFoundError` and creates new Firebase users
- Handles `PhoneNumberAlreadyExistsError` gracefully
- Provides detailed logging for debugging
- Shows clear error messages when phone auth is not configured

### 2. Required Firebase Console Configuration

#### Step-by-Step Guide:

1. **Open Firebase Console**
   - Go to: https://console.firebase.google.com/
   - Login with your Google account

2. **Select Your Project**
   - Select project: `daberny-ff5fd`

3. **Enable Phone Authentication**
   - In the left sidebar, click **Authentication**
   - Click on the **Sign-in method** tab
   - Find **Phone** in the list of providers
   - Click on **Phone**
   - Toggle the **Enable** switch to ON
   - Click **Save**

4. **Configure Phone Authentication Settings**
   - **Test phone numbers** (Optional for development):
     - Add test phone numbers with verification codes
     - Format: +201234567890 with code: 123456
   - **reCAPTCHA** (For web):
     - Configure reCAPTCHA settings if using web app
   - **App Verification** (For mobile):
     - Configure APNs for iOS
     - Configure Firebase Cloud Messaging for Android

5. **Verify Service Account Permissions**
   - Go to **Project Settings** (gear icon)
   - Navigate to **Service Accounts** tab
   - Verify that your service account has proper permissions
   - The service account email should be:
     `firebase-adminsdk-fbsvc@daberny-ff5fd.iam.gserviceaccount.com`

### 3. Database Phone Number Format

Ensure all phone numbers in your User model are stored in E.164 format:

```python
# Correct format
+201060074850  # Egypt
+966501234567  # Saudi Arabia
+971501234567  # UAE

# Incorrect format (will be auto-corrected by the code)
201060074850
01060074850
00201060074850
```

### 4. Testing Phone Authentication

#### Test 1: Register a New User
```bash
curl -X POST "http://127.0.0.1:8000/auth/register/" \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "+201060074850",
    "access_level": "Client"
  }'
```

#### Test 2: Verify OTP
```bash
curl -X POST "http://127.0.0.1:8000/auth/verify-otp/" \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "+201060074850",
    "otp": "123456",
    "access_level": "Client"
  }'
```

Expected response should include:
- `firebase_token`: A valid Firebase custom token
- `firebase_uid`: The Firebase user UID
- No CONFIGURATION_NOT_FOUND error

### 5. Troubleshooting

#### If you still see the error:

1. **Check Firebase Console Logs**
   - Firebase Console > Authentication > Users
   - Verify users are being created

2. **Verify Service Account Key**
   - Ensure `serviceAccountKey.json` is in the project root
   - Verify the project_id matches: `daberny-ff5fd`
   - Check file permissions

3. **Check Django Logs**
   - Look for detailed error messages in console
   - Check `debug.log` file for Firebase-related errors

4. **Verify Phone Number Format**
   ```python
   # In Django shell
   from user.models import User
   
   # Check a user's phone format
   user = User.objects.get(id=1)
   print(f"Phone: {user.phone}")
   # Should print: +201060074850
   ```

5. **Test Firebase Directly**
   ```python
   # In Django shell
   from firebase_admin import auth as firebase_auth
   
   # Try to create a test user
   user = firebase_auth.create_user(
       phone_number='+201234567890',
       display_name='Test User'
   )
   print(f"Created user: {user.uid}")
   ```

### 6. Alternative Solutions

If phone authentication cannot be enabled:

#### Option A: Use Email Authentication
Modify the authentication flow to use email instead of phone

#### Option B: Skip Firebase User Creation
Modify code to only use Django authentication without Firebase

#### Option C: Use Custom Tokens Only
Generate custom tokens without creating Firebase users:
```python
# This bypasses the need for phone auth provider
custom_token = firebase_auth.create_custom_token(
    uid=f"user_{user.id}",
    additional_claims={'django_user_id': user.id}
)
```

### 7. Production Considerations

When deploying to production:

1. **Update Environment Variables**
   - Update Firebase credentials in `.env`
   - Use production Firebase project if different

2. **Enable Required APIs**
   - Identity Toolkit API
   - Firebase Authentication API

3. **Configure Quotas**
   - Check Firebase free tier limits
   - Configure billing if needed

4. **Security Rules**
   - Set up proper Firebase security rules
   - Configure CORS settings

5. **Monitoring**
   - Set up Firebase Analytics
   - Monitor authentication errors
   - Set up alerts for failures

### 8. Summary of Changes Made

Files modified:
1. ✅ `api/v1/authentication.py` - Enhanced Firebase auth with better error handling
2. ✅ `api/v1/urls.py` - Fixed notification URL structure
3. ✅ `api/v1/global_serializer/common_serializer.py` - Made user field read-only
4. ✅ `api/v1/global_views/fcm_notification_views.py` - Fixed user assignment in create
5. ✅ `api/v1/provider/urls.py` - Organized notification endpoints
6. ✅ `api/v1/customer/urls.py` - Organized notification endpoints

### 9. Next Steps

1. ✅ Code changes completed
2. ⏳ **You need to**: Enable Phone Authentication in Firebase Console
3. ⏳ Test the authentication flow
4. ⏳ Update frontend API constants
5. ⏳ Deploy and monitor

---

## Contact & Support

If you continue to experience issues:
1. Check Firebase Console for specific error messages
2. Review Django logs for detailed stack traces
3. Verify all phone numbers in database are in E.164 format
4. Ensure Firebase service account has correct permissions

