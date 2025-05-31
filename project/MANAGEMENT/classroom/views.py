from django.shortcuts import render, redirect
from .forms import ClassForm
from django.contrib.auth.decorators import login_required
from account.models import Teacher, Student
from classroom.models import Badge
from django.http import JsonResponse
from .models import Attendance
import json


@login_required
def create_class(request):
    teacher = Teacher.objects.get(user=request.user)

    if request.method == 'POST':
        form = ClassForm(request.POST)
        if form.is_valid():
            new_class = form.save(commit=False)
            new_class.teacher = teacher
            new_class.save()
            return redirect('account:teacher_dashboard_view')
    else:
        form = ClassForm()

    return render(request, 'teacher/create_class.html', {'form': form})


@login_required
def student_calendar(request):
    try:
        student = Student.objects.get(user=request.user)
        attendances = Attendance.objects.filter(student=student).order_by('-date')
    except Student.DoesNotExist:
        attendances = []

    return render(request, 'student/student_calendar.html', {
        'attendances': attendances,
    })


@login_required
def student_merit_view(request):
    try:
        student = Student.objects.get(user=request.user)
        badges = Badge.objects.filter(student=student, type='merit')
    except Student.DoesNotExist:
        badges = []

    return render(request, 'student/student_merit.html', {'badges': badges})


# ─── NEW: JSON endpoint for FullCalendar ────────────────────────────────
@login_required
def attendance_events(request):
    try:
        student = Student.objects.get(user=request.user)
        attendance_records = Attendance.objects.filter(student=student)
    except Student.DoesNotExist:
        attendance_records = []

    events = []
    for rec in attendance_records:
        # pick a color per status
        if rec.status == 'present':
            color = '#4caf50'   # green
        elif rec.status == 'absent':
            color = '#f44336'   # red
        elif rec.status == 'excused':
            color = '#ff9800'   # orange
        else:
            color = '#2196f3'   # fallback blue

        events.append({
            'title': f"{rec.class_obj.class_name} – {rec.status.capitalize()}",
            'start': rec.date.strftime('%Y-%m-%d'),
            'allDay': True,
            'color': color,
        })

    return JsonResponse(events, safe=False)

def student_announcement(request):
    # You can pass any context you need to the template
    # For example, if you have a model Announcement, fetch all:
    # announcements = Announcement.objects.all()
    # return render(request, 'student/student_announcement.html', {'announcements': announcements})
    
    return render(request, 'student/student_announcement.html')

from .models import Grade
@login_required
def student_starplot(request):
    student_obj = Student.objects.get(user=request.user)

    grades = Grade.objects.filter(student=student_obj)
    radar_chart_data = {}

    for grade in grades:
        subject_name = str(grade.class_obj)  # ensure __str__ method is meaningful
        written = grade.written_work or 0
        performance = grade.performance_task or 0
        final = grade.final_exam or 0
        total = written + performance + final
        radar_chart_data[subject_name] = total

    categories = list(radar_chart_data.keys())
    scores = list(radar_chart_data.values())

    return render(request, 'student/student_starplot.html', {
        'categories': json.dumps(categories),
        'scores': json.dumps(scores),
    })


from django.shortcuts import render, redirect
from .models import Class, Grade, Enrollment
from account.models import Teacher, Student
from django.contrib.auth.decorators import login_required
from django.db.models import Q

@login_required
def grade_sheet_view(request):
    teacher = Teacher.objects.get(user=request.user)
    
    if request.method == "POST":
        class_id = request.POST.get('class_id')
        subject = request.POST.get('subject')

        try:
            selected_class = Class.objects.get(id=class_id, teacher=teacher)
        except Class.DoesNotExist:
            return redirect('select_class_subject')  # or handle error

        enrollments = Enrollment.objects.filter(classroom=selected_class).select_related('student')
        student_data = []

        for enrollment in enrollments:
            student = enrollment.student
            grades = Grade.objects.filter(student=student, classroom=selected_class)

            written_work = grades.filter(component='written_work').first()
            performance_task = grades.filter(component='performance_task').first()
            quarterly_assessment = grades.filter(component='quarterly_assessment').first()

            student_data.append({
                'student': student,
                'written_work': written_work.score if written_work else None,
                'performance_task': performance_task.score if performance_task else None,
                'quarterly_assessment': quarterly_assessment.score if quarterly_assessment else None,
            })

        context = {
            'class': selected_class,
            'subject': subject,
            'student_data': student_data,
        }
        return render(request, 'teacher/grade_sheet.html', context)

    return redirect('select_class_subject')

from django.shortcuts import render
from .models import Class

def select_class_subject(request):
    classes = Class.objects.filter(teacher=request.user.teacher)
    return render(request, 'classroom/select_class_subject.html', {'classes': classes})

from django.shortcuts import render, get_object_or_404
from classroom.models import Class, Enrollment, Grade
from account.models import Teacher, Student  # Adjust if path differs
from django.contrib.auth.decorators import login_required


from django.shortcuts import render, get_object_or_404
from classroom.models import Class, Enrollment, Grade
from account.models import Teacher, Student  # Adjust if path differs
from django.contrib.auth.decorators import login_required

# classroom/views.py
from django.shortcuts import render
from .models import Class, Grade

def class_record_view(request):
    class_id = request.GET.get('class_obj')
    selected_class = None
    performance_task = None
    written_work = None
    final_exam = None

    if class_id:
        selected_class = Class.objects.get(id=class_id)
        # Assuming Grade is the model where performance_task, written_work, and final_exam are stored
        grades = Grade.objects.filter(class_id=class_id)

        # Retrieve grades for performance_task, written_work, final_exam
        performance_task = grades.first().performance_task if grades else None
        written_work = grades.first().written_work if grades else None
        final_exam = grades.first().final_exam if grades else None

    classes = Class.objects.all()

    return render(request, 'teacher/teacher_dashboard.html', {
        'classes': classes,
        'selected_class': selected_class,
        'performance_task': performance_task,
        'written_work': written_work,
        'final_exam': final_exam,
    })
