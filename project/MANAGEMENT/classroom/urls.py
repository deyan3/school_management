# classroom/urls.py
from django.urls import path
from . import views

app_name = 'classroom'

urlpatterns = [
    path('teacher/classes/create/', views.create_class, name='create_class'),
    path('student/calendar/', views.student_calendar, name='student_calendar'),
    path('student/merit/', views.student_merit_view, name='student_merit_view'),
    path('student-announcement/', views.student_announcement, name='student_announcement'),
    path('student_starplot/', views.student_starplot, name='student_starplot'),
    path('class-record/', views.select_class_subject, name='select_class_subject'),
    path('grade-sheet/', views.grade_sheet_view, name='grade_sheet'),
    path('teacher/class-record/', views.class_record_view, name='class_record_view'),
]

