from django.shortcuts import redirect, render

# Create your views here.
def test(request):
    pass

def welcome(request):
    return render(request, "EducationSystem/pages/welcome.html")

def login_view(request):
    if request.method == "POST":
        student_id = request.POST.get("student_id")
        password = request.POST.get("password")

        # TODO:
        return redirect("dashboard")

    return render(request, "EducationSystem/pages/login.html")

# صفحه داشبورد
def dashboard_view(request):
    return render(request, "EducationSystem/pages/dashboard.html")

# صفحه پروفایل
def profile_view(request):
    return render(request, "EducationSystem/pages/profile.html")