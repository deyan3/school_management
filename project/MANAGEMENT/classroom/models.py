from django.db import models
from account.models import Student, Teacher  # Adjust if your Student/Teacher models are elsewhere

class Class(models.Model):
    class_name = models.CharField(max_length=255)
    subject = models.CharField(max_length=255)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.class_name} - {self.subject}"


class Enrollment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    class_obj = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='enrollments')

    class Meta:
        unique_together = ('student', 'class_obj')

    def __str__(self):
        return f"{self.student} enrolled in {self.class_obj}"


class Attendance(models.Model):
    STATUS_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('excused', 'Excused'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    class_obj = models.ForeignKey(Class, on_delete=models.CASCADE)
    date = models.DateField()
    time_in = models.TimeField(null=True, blank=True)
    time_out = models.TimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)

    def __str__(self):
        return f"{self.student} - {self.date} - {self.status}"


class Grade(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    class_obj = models.ForeignKey(Class, on_delete=models.CASCADE)
    written_work = models.FloatField()
    performance_task = models.FloatField()
    final_exam = models.FloatField()

    def __str__(self):
        return f"{self.student} - {self.class_obj} - Grade"


class Badge(models.Model):
    TYPE_CHOICES = [
        ('merit', 'Merit'),
        ('demerit', 'Demerit'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    class_obj = models.ForeignKey(Class, on_delete=models.CASCADE)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    shard_count = models.PositiveIntegerField()
    points = models.IntegerField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.type.capitalize()} for {self.student} in {self.class_obj}"
    
class Announcement(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    date_posted = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
