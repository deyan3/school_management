# account/models.py

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class User(AbstractUser):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        ('admin', 'Admin'),  # For superuser support
        ('admin', 'Admin'),  # For superuser support
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.username} ({self.role})"

    def is_student(self):
        return self.role == 'student'

    def is_teacher(self):
        return self.role == 'teacher'

    def is_admin(self):
        return self.role == 'admin'
    
class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    lrn = models.CharField(max_length=50, unique=True)
    level = models.CharField(max_length=10)
    section = models.CharField(max_length=50)
    parent_name = models.CharField(max_length=255)
    parent_email = models.EmailField()
    parent_contact = models.CharField(max_length=50)
    photo = models.ImageField(upload_to='student_photos/')

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.level}-{self.section}"

   
class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher_profile')
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher_profile')
    license_number = models.CharField(max_length=50, unique=True)
    department = models.CharField(max_length=255)
    photo = models.ImageField(upload_to='teacher_photos/')

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.department})"

