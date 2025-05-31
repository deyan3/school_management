# account/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from datetime import date
import json

from .forms import StudentLoginForm, TeacherLoginForm
from .models import Student, Teacher, Announcement
from classroom.models import Attendance, Grade, Badge, Class


def student_login(request):
    if request.user.is_authenticated:
        return redirect('account:student_dashboard')  # redirect if already logged in

    form = StudentLoginForm(request.POST or None)
    if form.is_valid():
        lrn = form.cleaned_data['lrn']
        student = Student.objects.get(lrn=lrn)
        user = student.user
        login(request, user)
        return redirect('account:student_dashboard')
    return render(request, 'student/student_login.html', {'form': form})


def teacher_login(request):
    if request.user.is_authenticated:
        return redirect('account:teacher_dashboard')  # redirect if already logged in

    form = TeacherLoginForm(request.POST or None)
    if form.is_valid():
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']

        user = authenticate(request, username=username, password=password)

        if user is not None and user.role.lower() == 'teacher':  # Ensure the user is a teacher
            login(request, user)
            return redirect('account:teacher_dashboard')
        else:
            messages.error(request, "Invalid credentials or not a teacher")

    return render(request, 'teacher/teacher_login.html', {'form': form})


@login_required
def student_dashboard(request):
    student_obj = Student.objects.get(user=request.user)

    # Attendance - Format dates as "YYYY-MM-DD" strings to match flatpickr format
    attendance_qs = Attendance.objects.filter(student=student_obj)
    attendance_data = {
        record.date.strftime("%Y-%m-%d"): {
            'status': record.status,
            'time_in': str(record.time_in),
            'time_out': str(record.time_out),
        }
        for record in attendance_qs
    }

    # Badges
    badges = Badge.objects.filter(student=student_obj).order_by('-timestamp')

    # Grades for Radar Plot
    grades = Grade.objects.filter(student=student_obj)
    radar_chart_data = {}
    for grade in grades:
        subject_name = str(grade.class_obj)  # Use __str__ method of Class model
        written = grade.written_work or 0
        performance = grade.performance_task or 0
        final = grade.final_exam or 0
        total = written + performance + final
        radar_chart_data[subject_name] = total

    categories = list(radar_chart_data.keys())
    scores = list(radar_chart_data.values())

    # Announcements
    announcements = Announcement.objects.order_by('-date_posted')[:10]

    context = {
        'attendance_data': json.dumps(attendance_data),  # dump to JSON string
        'badges': badges,
        'today': date.today(),
        'categories': json.dumps(categories),
        'scores': json.dumps(scores),
        'announcements': announcements,
    }

    return render(request, 'student/student_dashboard.html', context)


@login_required
def teacher_dashboard(request):
    teacher = get_object_or_404(Teacher, user=request.user)
    classes = Class.objects.filter(teacher=teacher)

    announcements = Announcement.objects.order_by('-date_posted')
    # If you have an AnnouncementForm, handle it here
    # from .forms import AnnouncementForm
    # form = AnnouncementForm()
    # Add form handling logic if needed

    context = {
        'classes': classes,
        'announcements': announcements,
        # 'form': form,  # Uncomment if you add the form
    }
    return render(request, 'teacher/teacher_dashboard.html', context)


def logout_view(request):
    logout(request)
    return redirect('account:student_login')  # or redirect based on role


@login_required
def student_merit_view(request):
    # Your merit view logic here
    return render(request, 'student/student_merit.html')


from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def qr_login(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            lrn = data.get('lrn')
            student = Student.objects.get(lrn=lrn)
            login(request, student.user)
            return JsonResponse({'success': True, 'redirect_url': '/student/dashboard/'})
        except Student.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Invalid QR code'})
    return JsonResponse({'success': False, 'error': 'Invalid request'})
