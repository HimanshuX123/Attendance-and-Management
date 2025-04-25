from django.db import models
from django.utils.timezone import now
from django.core.exceptions import ValidationError


class Attendance(models.Model):
    CLASS_CHOICES = [(str(i), f"Class {i}") for i in range(1, 11)]  # Classes 1-10
    SECTION_CHOICES = [('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')]  # Sections A-D
    SUBJECT_CHOICES = [
        ('Marathi', 'Marathi'),
        ('Hindi', 'Hindi'),
        ('English', 'English'),
        ('Mathematics', 'Mathematics'),
        ('Science', 'Science'),
        ('History', 'History'),
        ('Geography', 'Geography'),
        ('Physical Education', 'Physical Education'),
    ]
    STATUS_CHOICES = [('Present', 'Present'), ('Absent', 'Absent')]

    student = models.ForeignKey(
        'authentication.StudentProfile',  # ✅ Correct reference
        on_delete=models.CASCADE,
        related_name="attendance_records"
    )
    teacher = models.ForeignKey(
        'authentication.TeacherProfile',  # ✅ Correct reference
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="marked_attendance"
    )
    class_grade = models.CharField(max_length=10)  # ✅ Class (1-10)
    section = models.CharField(max_length=1, choices=SECTION_CHOICES)  # ✅ Section (A-D)
    subject = models.CharField(max_length=20, choices=SUBJECT_CHOICES)  # ✅ Predefined subjects
    date = models.DateField(default=now)  # ✅ Default to today
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)  # ✅ Attendance status
    time = models.TimeField(auto_now=True)  # ✅ Updates time when record is modified


    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['student', 'class_grade', 'section', 'subject', 'date'],
                name='unique_attendance_per_student'
            )
        ]

    def clean(self):
        """ Ensure attendance is not marked more than once for a student on the same date, class, and subject. """
        if Attendance.objects.filter(
                student=self.student,
                class_grade=self.class_grade,
                section=self.section,
                subject=self.subject,
                date=self.date
        ).exists() and self._state.adding:  # Check if the instance is being added (not updated)
            raise ValidationError("Attendance for this student, class, subject, and date is already marked.")

    def save(self, *args, **kwargs):
        # Only call the clean method when adding a new attendance (not when updating)
        if self._state.adding:
            self.clean()  # Call validation before saving
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student.full_name} - {self.class_grade}{self.section} - {self.subject} - {self.date} - {self.status}"
