from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.core.mail import send_mail

from authentication.models import StudentProfile, TeacherProfile
from principal.models import Announcement
from student.models import LeaveRequest
from student.forms import LeaveApplicationForm

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from teacher.models import Attendance
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from teacher.models import Attendance

@login_required
def student_attendance(request):
    try:
        student = request.user.student_profile  # ✅ Use the correct related_name
        attendance_records = Attendance.objects.filter(student=student).order_by('-date')
    except AttributeError:
        return render(request, "student/error.html", {"message": "Student profile not found!"})

    return render(request, "student/student_attendance.html", {
        "attendance_records": attendance_records
    })

@login_required
def student_dashboard(request):
    try:
        student = StudentProfile.objects.get(user=request.user)
    except StudentProfile.DoesNotExist:
        messages.error(request, "⚠ No student profile found. Please contact the admin.")
        return render(request, "student/dashboard.html", {"student": None})

    # Fetch classmates in the same class & section
    classmates = StudentProfile.objects.filter(class_name=student.class_name, section=student.section).exclude(
        user=request.user
    )

    # Fetch assigned teachers
    assigned_teachers = TeacherProfile.objects.filter(class_name=student.class_name)

    # Fetch all teachers (for leave request dropdown)
    all_teachers = TeacherProfile.objects.all()

    # Fetch student's leave history
    leave_requests = LeaveRequest.objects.filter(student=student).order_by("-start_date")

    if request.method == "POST":
        # Update Profile
        student.full_name = request.POST["full_name"]
        student.phone_number = request.POST["phone_number"]
        student.address = request.POST["address"]
        student.save()
        messages.success(request, "Profile updated successfully!")
        return redirect("student_dashboard")

    return render(request, "student/dashboard.html", {
        "student": student,
        "classmates": classmates,
        "assigned_teachers": assigned_teachers,
        "all_teachers": all_teachers,
        "leave_requests": leave_requests,
    })


def student_login(request):
    return render(request, 'student/student_login.html')


def student_logout(request):
    logout(request)
    return redirect("student_login")  # Redirect to the login page after logout


from django.shortcuts import render, redirect
from django.contrib import messages
from .models import LeaveRequest
from authentication.models import StudentProfile, TeacherProfile

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from authentication.models import TeacherProfile
from student.models import StudentProfile, LeaveRequest


@login_required
def apply_leave(request):
    if request.method == "POST":
        student = StudentProfile.objects.get(user=request.user)
        teacher_id = request.POST.get("teacher_id")
        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")
        reason = request.POST.get("reason")

        LeaveRequest.objects.create(
            student=student,
            teacher_id=teacher_id,
            start_date=start_date,
            end_date=end_date,
            reason=reason,
            status="Pending",
        )

        messages.success(request, "Leave request submitted successfully!")
        return redirect("student_dashboard")


def success(request):
    return render(request, 'student/success.html')


from django.shortcuts import render
from teacher.models import Attendance




@login_required
def announcement_list(request):
    announcements = Announcement.objects.all().order_by('-created_at')  # Show newest first
    return render(request, "student/announcement_list.html", {"announcements": announcements})


from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from teacher.models import Attendance  # Adjust if needed
