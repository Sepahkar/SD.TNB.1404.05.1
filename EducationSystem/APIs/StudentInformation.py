# app/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Student
from .serializers import StudentFullSerializer

# Optional: if you use Simple JWT
from rest_framework_simplejwt.authentication import JWTAuthentication

class StudentProfileFullView(APIView):
    """
    GET /student/profile/full
    Prefer student id from JWT (claim 'student_id' or 'studentId').
    Fallback to query param ?studentId=...
    """
    authentication_classes = [JWTAuthentication]  # optional
    permission_classes = []  # allow both authenticated and unauthenticated (we check payload)

    def get(self, request, *args, **kwargs):
        student_id = None

        # try extract from JWT payload if present
        try:
            token = getattr(request, 'auth', None)
            if token:
                payload = getattr(token, 'payload', None) or token
                if isinstance(payload, dict):
                    student_id = payload.get('student_id') or payload.get('studentId') or payload.get('sub')
        except Exception:
            student_id = None

        # fallback to query param
        if not student_id:
            student_id = request.query_params.get('studentId') or request.query_params.get('student_id')

        if not student_id:
            return Response({"detail": "studentId not provided. Provide Authorization JWT or ?studentId=..."},
                            status=status.HTTP_400_BAD_REQUEST)

        # ensure integer
        try:
            student_id = int(student_id)
        except Exception:
            return Response({"detail": "studentId must be integer"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            student = Student.objects.get(student_id=student_id)
        except Student.DoesNotExist:
            return Response({"detail": "Student not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = StudentFullSerializer(student)
        return Response(serializer.data, status=status.HTTP_200_OK)
