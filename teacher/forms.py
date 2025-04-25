from datetime import date

from django import forms
from authentication.models import TeacherProfile


class TeacherProfileForm(forms.ModelForm):
    class Meta:
        model = TeacherProfile
        exclude = ["user"]  # Exclude user field (set automatically)
        widgets = {
            "date_of_birth": forms.DateInput(attrs={"type": "date"}),
            "address": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Make fields readonly
        readonly_fields = ["full_name", "employee_id", "date_of_birth"]
        for field in readonly_fields:
            self.fields[field].widget.attrs["readonly"] = True
            self.fields[field].widget.attrs["class"] = "readonly-field"

        # Email should be fetched from the user model
        self.fields["email"] = forms.EmailField(
            initial=self.instance.user.email if self.instance and self.instance.user else "",
            disabled=True,  # Prevent editing
            widget=forms.EmailInput(attrs={"class": "readonly-field"})
        )


from django import forms
from authentication.models import StudentProfile
from .models import Attendance


class AttendanceForm(forms.ModelForm):
    student = forms.ModelChoiceField(queryset=StudentProfile.objects.all(), label="Select Student")
    class_name = forms.CharField(label="Class")
    section = forms.CharField(label="Section")
    subject = forms.CharField(label="Subject", disabled=True)  # Auto-filled with teacher's subject
    status = forms.ChoiceField(choices=[('Present', 'Present'), ('Absent', 'Absent')], label="Status")

    class Meta:
        model = Attendance
        fields = ['student', 'class_name', 'section', 'subject', 'status']  # ✅ Removed `attendance_date`

    def clean(self):
        cleaned_data = super().clean()
        student = cleaned_data.get("student")
        class_name = cleaned_data.get("class_name")
        section = cleaned_data.get("section")
        subject = cleaned_data.get("subject")
        today = date.today()

        # ✅ Check if attendance already exists for today
        if Attendance.objects.filter(
                student=student, class_name=class_name, section=section, subject=subject, date=today
        ).exists():
            raise forms.ValidationError("Attendance has already been marked for this student today.")

        return cleaned_data
