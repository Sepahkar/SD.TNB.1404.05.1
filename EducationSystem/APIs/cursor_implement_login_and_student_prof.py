# Implement login and student profile APIs
_Exported on 11/29/2025 at 01:09:48 GMT+3:30 from Cursor (2.1.39)_

---

**User**

write this API based on my codebase:در ادامه دو پرامپت جداگانه برای AI آماده کرده‌ام:



1. پرامپت کامل برای ورود با نام کاربری و رمز عبور (Login)

2. پرامپت کامل برای اطلاعات اولیه دانشجو برای هدر (Basic Student Profile)



هر پرامپت به طور کامل از روی PDF استخراج شده و جاهایی که فارسی بوده کاملاً فارسی نگه داشته شده است.

(رفرنس به PDF: )



---



# ✅ PROMPT 1 — Login API (ورود با نام کاربری و رمز عبور)



### Copy–Paste Prompt for Cursor / ChatGPT Agent



You are a Senior Backend Engineer.

Implement the login API exactly based on the following extracted specification.

Preserve all Persian text exactly as shown.



---



## 📌 API Specification — Login



### Endpoint:



POST /auth/login



### Description (from PDF):



ورود با نام کاربری و رمز عبور



### Request Body Example:





{

  "studentId": "string",

  "password": "string"

}





### Response Example:





{

  "token": "JWT_TOKEN",

  "...": "..."

}





---



## 🎯 AI Tasks



1. Create API route: POST /auth/login

2. Validate studentId + password

3. Authenticate the student

4. Return a JWT token in this exact Persian-style structure:



   

   { "token": "JWT_TOKEN" }

   

5. Keep the Persian description exactly as in the PDF:



   * ورود با نام کاربری و رمز عبور

6. Use clean architecture:



   * Controller / service / route separation

   * Proper error handling

   * Optional DB model (if missing, add TODO)



---



## 📦 Output requirements



* File/folder structure

* Route code

* Controller logic

* Password validation + JWT generation

* Example requests/responses

* Add notes if something is missing from spec



---



---



# ✅ PROMPT 2 — Basic Student Profile API (اطلاعات اولیه دانشجو برای هدر)



### Copy–Paste Prompt for Cursor / ChatGPT Agent



You are a Senior Backend Engineer.

Implement the Basic Student Profile API exactly based on the extracted PDF specification.

Persian fields must be preserved.



---



## 📌 API Specification — Student Basic Info for Header



### Endpoint:



GET /student/profile/basic



### Description (from PDF):



اطلاعات اولیه دانشجو برای هدر



### Response Example (EXACT Persian fields preserved):





{

  "studentId": "string",

  "fullName": "string",

  "gender": "Female"

}





---



## 🎯 AI Tasks



1. Implement route: GET /student/profile/basic

2. Fetch the student's basic info:



   * studentId

   * fullName

   * gender

3. Preserve Persian description:



   * اطلاعات اولیه دانشجو برای هدر

4. Support token-based auth (likely JWT from login)

5. Use clean architecture:



   * Route → Controller → Service → DB

6. Add error cases:



   * Student not found

   * Invalid token



---



## 📦 Output Requirements



Your output must include:



* File/folder structure

* Route implementation

* Controller/service logic

* Model (if needed)

* Response examples

* Authorization handling

* Persian fields kept exactly

---

**Cursor**


Exploring the codebase structure to understand the architecture.



Reviewing key files to understand the current structure:



Checking permissions and verifying the URL structure:



Updating URLs to match the exact paths: `/auth/login` and `/student/profile/basic`.



Updating URLs to match the exact specification. Verifying the implementation is complete:


```python
from django.urls import path
from . import views

app_name = 'EducationSystem'

urlpatterns = [
    # Authentication APIs
    # ورود با نام کاربری و رمز عبور
    # POST /auth/login
    path('auth/login/', views.login, name='login'),
    
    # Student Profile APIs
    # اطلاعات اولیه دانشجو برای هدر
    # GET /student/profile/basic
    path('student/profile/basic/', views.student_basic_profile, name='student_basic_profile'),
]

```


Verifying the implementation and checking for issues:



Checking REST framework settings and verifying the implementation:



Implementation looks complete. Verifying the final state and preparing a summary:



## Implementation summary

### 1. Login API — POST /auth/login
- Route: `auth/login/`
- Description: ورود با نام کاربری و رمز عبور (preserved)
- Request: `{"studentId": "string", "password": "string"}`
- Response: `{"token": "JWT_TOKEN"}`
- Features:
  - Validates studentId and password
  - Authenticates using the Student model
  - Returns JWT token (24-hour expiration)
  - Error handling for invalid credentials

### 2. Student Basic Profile API — GET /student/profile/basic
- Route: `student/profile/basic/`
- Description: اطلاعات اولیه دانشجو برای هدر (preserved)
- Authentication: JWT Bearer token required
- Response: `{"studentId": "int", "fullName": "string", "gender": "Female"}`
- Features:
  - Token-based authentication
  - Returns student basic info for header
  - Error handling for missing/invalid tokens

## Architecture

- Routes: `EducationSystem/urls.py`
- Controllers: `EducationSystem/views.py`
- Services: `EducationSystem/services.py`
- Serializers: `EducationSystem/serializers.py`
- JWT Auth: `EducationSystem/auth_service.py`
- Permissions: `EducationSystem/permissions.py`

## Files updated

1. `EducationSystem/urls.py` — Updated routes to match exact specification

## Testing

You can test the APIs:

1. Login:
```bash
POST http://localhost:8000/auth/login/
Content-Type: application/json

{
  "studentId": "1",
  "password": "your_password"
}
```

2. Get Basic Profile:
```bash
GET http://localhost:8000/student/profile/basic/
Authorization: Bearer <JWT_TOKEN>
```

The implementation is complete and ready to use. All Persian text has been preserved as specified, and the code follows clean architecture principles with proper separation of concerns.

```shellscript
POST http://localhost:8000/auth/login/
Content-Type: application/json

{
  "studentId": "1",
  "password": "your_password"
}
```

```shellscript
GET http://localhost:8000/student/profile/basic/
Authorization: Bearer <JWT_TOKEN>
```

