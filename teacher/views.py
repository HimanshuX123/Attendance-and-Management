def teacher_login(request):
    return render(request, 'teacher_login.html')


# Create your views here.
from datetime import datetime, timedelta

from authentication.forms import TeacherProfileForm

import re


def extract_number(text):
    match = re.search(r'\d+', text)  # Extract first number
    return int(match.group()) if match else float('inf')


from django.shortcuts import render, redirect
from django.contrib import messages

from .forms import AttendanceForm

from datetime import date
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from admin_panel.models import Class, Section, Subject
from .forms import AttendanceForm

from datetime import date
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from admin_panel.models import Class, Section
from authentication.models import TeacherProfile

from datetime import date
from django.shortcuts import render, redirect
from django.contrib import messages
from admin_panel.models import Class, Section
from authentication.models import TeacherProfile
from datetime import date
from django.shortcuts import render, redirect
from django.contrib import messages

from authentication.models import TeacherProfile

from datetime import date
from django.shortcuts import render, redirect

from .forms import AttendanceForm

from django.contrib import messages
from django.shortcuts import render, redirect
from .forms import AttendanceForm
from .models import Attendance
from datetime import date


def take_attendance(request):
    if not hasattr(request.user, 'teacher_profile'):
        messages.error(request, "You do not have permission to take attendance.")
        return redirect("dashboard")

    teacher = request.user.teacher_profile
    assigned_subject = teacher.subject  # Get assigned subject

    if not assigned_subject:
        messages.error(request, "You are not assigned to any subject.")
        return redirect("dashboard")

    # Handle class and section choices
    class_choices = sorted(
        set(Class.objects.values_list("name", flat=True)),
        key=lambda x: int(''.join(filter(str.isdigit, x))) if any(c.isdigit() for c in x) else float('inf')
    )
    section_choices = sorted(set(Section.objects.values_list("section_name", flat=True)))

    if request.method == "POST":
        form = AttendanceForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.date = date.today()  # Force today's date
            instance.subject = assigned_subject  # Auto-assign subject

            # Debugging: Print the form data and check for missing fields
            print("Form Data:", form.cleaned_data)

            # Check if attendance already exists for the student
            if Attendance.objects.filter(
                    student=instance.student,
                    date=date.today(),
                    subject=assigned_subject
            ).exists():
                messages.error(request, f"Attendance is already marked for {instance.student} today.")
            else:
                instance.save()  # Save the attendance record
                messages.success(request, "Attendance marked successfully!")
                return redirect("take_attendance")
        else:
            # Debugging: Print form errors if validation fails
            print("Form Errors:", form.errors)
            messages.error(request, "Invalid form submission. Please check the details.")
    else:
        form = AttendanceForm(initial={"subject": assigned_subject})  # Auto-fill subject

    return render(request, "teacher/take_attendance.html", {
        "form": form,
        "class_choices": class_choices,
        "section_choices": section_choices,
        "current_date": date.today().strftime("%B %d, %Y"),
        "assigned_subject": assigned_subject,
    })


from authentication.models import StudentProfile  # Adjust according to your model


def get_students(request):
    class_name = request.GET.get('class_name')
    section = request.GET.get('section')
    subject = request.GET.get('subject')
    attendance_date = request.GET.get('date')

    print(
        f"Received Parameters -> class_name: {class_name}, section: {section}, subject: {subject}, date: {attendance_date}")

    if not class_name or not section:
        return JsonResponse({"error": "Missing class or section parameter"}, status=400)

    students = StudentProfile.objects.filter(class_name=class_name, section=section)
    student_data = [{"id": s.id, "full_name": s.full_name, "roll_number": s.roll_number} for s in students]

    return JsonResponse({"students": student_data})


# ✅ API to submit attendance

from django.views.decorators.csrf import csrf_exempt
import json
from .models import Attendance
from authentication.models import StudentProfile
from datetime import datetime
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from authentication.models import StudentProfile  # Ensure correct import
from teacher.models import Attendance  # Ensure correct import
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json
from datetime import date
from authentication.models import StudentProfile

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.timezone import now
import json
from django.shortcuts import get_object_or_404

from django.utils.timezone import now


@csrf_exempt  # Remove this in production
def submit_attendance(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method."}, status=400)

    try:
        data = json.loads(request.body.decode("utf-8"))
        attendance_records = data.get("attendance", [])
        section = data.get("section")
        subject = data.get("subject")
        attendance_date = data.get("attendance_date", now().date())

        if not section or not subject or not attendance_date:
            return JsonResponse({"error": "Section, Subject, and Date are required."}, status=400)

        if not attendance_records:
            return JsonResponse({"error": "No attendance records submitted."}, status=400)

        duplicate_students = []

        for record in attendance_records:
            student_id = record.get("student_id")
            status = record.get("status")

            if not student_id or not status:
                return JsonResponse({"error": "Missing student_id or status."}, status=400)

            student = get_object_or_404(StudentProfile, id=student_id)

            # ✅ Check for duplicate attendance
            if Attendance.objects.filter(student=student, date=attendance_date, subject=subject).exists():
                duplicate_students.append(student.full_name)  # Store student names for error
            else:
                # ✅ Save new attendance entry with REAL-TIME time tracking
                Attendance.objects.create(
                    student=student,
                    class_grade=student.class_name,
                    section=section,
                    subject=subject,
                    date=attendance_date,
                    time=now().time(),  # ✅ Set current time dynamically
                    status=status
                )

        if duplicate_students:
            return JsonResponse({
                "error": f"⚠️ Attendance already submitted for: {', '.join(duplicate_students)}. Contact admin for changes."
            }, status=400)

        return JsonResponse({"message": "✅ Attendance submitted successfully!"})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from authentication.models import TeacherProfile

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import TeacherProfileForm


@login_required(login_url='/authentication/login/')  # Ensure only logged-in users can access
def teacher_profile(request):
    teacher = get_object_or_404(TeacherProfile, user=request.user)

    if request.method == "POST":
        form = TeacherProfileForm(request.POST, instance=teacher)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('teacher_profile')  # Redirect using the correct name from urls.py
    else:
        form = TeacherProfileForm(instance=teacher)

    return render(request, 'teacher/teacher_profile.html', {'teacher': teacher, 'form': form})


def update_profile(request):
    teacher = get_object_or_404(TeacherProfile, user=request.user)
    if request.method == "POST":
        form = TeacherProfileForm(request.POST, instance=teacher)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('teacher_profile')  # Redirect to the profile page
    else:
        form = TeacherProfileForm(instance=teacher)

    return render(request, 'teacher/update_profile.html', {'form': form})


# views.py
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
from .models import Attendance


def attendance_graph(request):
    labels_last_7_days, present_last_7_days, absent_last_7_days = [], [], []
    labels_monthly, present_monthly, absent_monthly = [], [], []
    today = timezone.now()

    class_filter = request.GET.get('class_grade')
    section_filter = request.GET.get('section')
    month_filter = request.GET.get('month')

    # Last 7 days attendance
    for i in range(7):
        date = today - timedelta(days=i)
        labels_last_7_days.append(date.strftime('%Y-%m-%d'))

        attendance_qs = Attendance.objects.filter(date=date)
        if class_filter:
            attendance_qs = attendance_qs.filter(class_grade=class_filter)
        if section_filter:
            attendance_qs = attendance_qs.filter(section=section_filter)

        present_last_7_days.append(attendance_qs.filter(status="Present").count())
        absent_last_7_days.append(attendance_qs.filter(status="Absent").count())

    # Monthly attendance
    if month_filter:
        year = today.year
        try:
            month = int(month_filter)
        except ValueError:
            return JsonResponse({'error': 'Invalid month'}, status=400)

        for day in range(1, 32):
            try:
                date = timezone.datetime(year, month, day)
                labels_monthly.append(date.strftime('%Y-%m-%d'))

                attendance_qs = Attendance.objects.filter(date=date)
                if class_filter:
                    attendance_qs = attendance_qs.filter(class_grade=class_filter)
                if section_filter:
                    attendance_qs = attendance_qs.filter(section=section_filter)

                present_monthly.append(attendance_qs.filter(status="Present").count())
                absent_monthly.append(attendance_qs.filter(status="Absent").count())
            except ValueError:
                break

    return JsonResponse({
        'labels_last_7_days': labels_last_7_days[::-1],
        'present_last_7_days': present_last_7_days[::-1],
        'absent_last_7_days': absent_last_7_days[::-1],
        'labels_monthly': labels_monthly,
        'present_monthly': present_monthly,
        'absent_monthly': absent_monthly
    })


def attendance_chart_view(request):
    return render(request, 'teacher/attendance_report.html')


from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from student.models import LeaveRequest

# Import Notification model


from django.shortcuts import render, get_object_or_404
from authentication.models import TeacherProfile
from student.models import LeaveRequest
from admin_panel.models import Notification


@login_required
def teacher_dashboard(request):
    teacher_profile = get_object_or_404(TeacherProfile, user=request.user)

    # ❗ Fetch only pending leave requests
    leave_requests = LeaveRequest.objects.filter(
        teacher=teacher_profile, status="Pending"  # ✅ Only show PENDING
    ).order_by('-start_date')

    # Fetch unread notifications for the teacher
    notifications = Notification.objects.filter(recipient=request.user, is_read=False)

    return render(request, 'teacher/teacher_dashboard.html', {
        'teacher_profile': teacher_profile,
        'leave_requests': leave_requests,
        'notifications': notifications
    })


from django.shortcuts import get_object_or_404, redirect
from admin_panel.models import Notification


def mark_notification_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, recipient=request.user)  # ✅ Correct field
    notification.is_read = True
    notification.save()
    return redirect('teacher_dashboard')  # Redirect to teacher dashboard after marking as read


from django.db.models import Q

from django.shortcuts import get_object_or_404
from django.db.models import Q
from authentication.models import TeacherProfile, StudentProfile

from django.shortcuts import get_object_or_404
from django.contrib import messages

import logging
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from admin_panel.models import Notification

logger = logging.getLogger(__name__)


def approve_leave(request, leave_id):
    if request.method == "POST":
        try:
            leave_request = get_object_or_404(LeaveRequest, id=leave_id)

            logger.info(f"🔄 Approving leave request ID: {leave_request.id}, Current status: {leave_request.status}")

            # ✅ Force update the status and save
            leave_request.status = "Approved"
            leave_request.save(update_fields=['status'])

            # ✅ Refresh from DB to verify changes
            leave_request.refresh_from_db()
            logger.info(f"✅ Leave request ID: {leave_request.id}, New status: {leave_request.status}")

            if leave_request.status != "Approved":
                logger.error(f"❌ Status update failed. Current DB value: {leave_request.status}")
                return JsonResponse({"success": False, "error": "Status update failed."}, status=500)

            # ✅ Create a notification for the student
            Notification.objects.create(
                recipient=leave_request.student.user,
                message=f"Your leave request from {leave_request.start_date} to {leave_request.end_date} has been approved.",
                is_read=False
            )

            return JsonResponse({"success": True})

        except Exception as e:
            logger.error(f"❌ Error approving leave: {e}")
            return JsonResponse({"success": False, "error": str(e)}, status=500)

    return JsonResponse({"success": False, "error": "Invalid request"}, status=400)


# Redirect to the pending leaves page

@login_required
def reject_leave(request, leave_id):
    if request.method == "POST":
        leave_request = get_object_or_404(LeaveRequest, id=leave_id)
        leave_request.status = "Rejected"
        leave_request.save()

        # Send notification to student
        Notification.objects.create(
            recipient=leave_request.student.user,
            message=f"Your leave request from {leave_request.start_date} to {leave_request.end_date} has been rejected."
        )

        return JsonResponse({"success": True})  # Return JSON response
    return JsonResponse({"success": False, "error": "Invalid request"}, status=400)


from django.shortcuts import render
from student.models import LeaveRequest  # Import your LeaveRequest model


def pending_leaves(request):
    # Fetch only pending leave requests
    leaves = LeaveRequest.objects.filter(status='Pending')
    return render(request, 'teacher/pending_leaves.html', {'leaves': leaves})


from django.shortcuts import render
from .models import Attendance


def view_attendance(request):
    attendances = Attendance.objects.all()
    return render(request, "teacher/attendance_list.html", {"attendances": attendances})


from django.shortcuts import render
from authentication.models import StudentProfile, TeacherProfile


def teacher_student_list(request):
    students = StudentProfile.objects.all()
    return render(request, 'teacher/teacher_student_list.html', {'students': students})


def teacher_teacher_list(request):
    teachers = TeacherProfile.objects.all()
    return render(request, 'teacher/teacher_teacher_list.html', {'teachers': teachers})


def teacher_view_student(request, student_id):
    student = get_object_or_404(StudentProfile, id=student_id)
    return render(request, 'teacher/teacher_view_student.html', {'student': student})


from django.shortcuts import render
from django.http import JsonResponse
from datetime import datetime, timedelta
from .models import Attendance
from authentication.models import StudentProfile  # Ensure you have Attendance model

from django.shortcuts import render
from admin_panel.models import Class, Section, Subject

from django.shortcuts import render
from admin_panel.models import Class, Section, Subject


def attendance_report(request):
    classes = Class.objects.all()
    sections = Section.objects.all()
    subjects = Subject.objects.all()

    print("Classes:", classes)  # Debugging
    print("Sections:", sections)  # Debugging
    print("Subjects:", subjects)  # Debugging

    return render(request, "teacher/attendance_report.html", {
        "class_choices": classes,
        "section_choices": sections,
        "subjects": subjects,
    })


from django.http import JsonResponse
from django.utils.timezone import now
from datetime import timedelta
from .models import Attendance  # Your Attendance model (if it's in the same app)
from admin_panel.models import Class, Subject, Section  # Import models from admin_panel

from django.http import JsonResponse
from admin_panel.models import Class, Section, Subject


def get_classes(request):
    classes = list(Class.objects.values("id", "name"))
    return JsonResponse({"classes": classes})


def get_sections(request):
    sections = list(Section.objects.values("id", "section_name"))
    return JsonResponse({"sections": sections})


def get_subjects(request):
    subjects = list(Subject.objects.values("id", "name"))
    return JsonResponse({"subjects": subjects})


from .models import Attendance  # Ensure you have the correct model

from django.http import JsonResponse

from django.http import JsonResponse
from .models import Attendance  # Ensure you import the right model

from django.http import JsonResponse
from .models import Attendance
from django.http import JsonResponse
from teacher.models import Attendance
from django.http import JsonResponse
from .models import Attendance
from django.http import JsonResponse
from teacher.models import Attendance
from admin_panel.models import Class, Section, Subject


def get_attendance_report(request):
    time_range = request.GET.get("time_range")
    class_id = request.GET.get("class_id")
    section = request.GET.get("section_filter")  # ✅ Correct key
    subject_id = request.GET.get("subject_id")

    # 🔥 Fetch Class & Subject Names Dynamically
    class_name = Class.objects.filter(id=class_id).values_list("name", flat=True).first()
    subject = Subject.objects.filter(id=subject_id).values_list("name", flat=True).first()
    section_name = Section.objects.filter(id=section).values_list("section_name", flat=True).first()

    print(f"🔍 API Query → Class: {class_name}, Section: {section_name}, Subject: {subject}")

    # ✅ Build Query with Filters
    filters = {}
    if class_name:
        filters["class_grade__iexact"] = class_name
    if subject:
        filters["subject__iexact"] = subject
    if section_name:
        filters["section__iexact"] = section_name

    attendance_records = Attendance.objects.filter(**filters)

    # ✅ Debugging - Print Retrieved Data
    print("🎯 Retrieved Attendance:", list(attendance_records.values("class_grade", "section", "subject", "status")))

    present_count = attendance_records.filter(status__iexact="Present").count()
    absent_count = attendance_records.filter(status__iexact="Absent").count()

    print(f"🚀 Final API Counts → Present: {present_count}, Absent: {absent_count}")

    return JsonResponse({
        "present_count": present_count,
        "absent_count": absent_count,
        "debug_data": list(attendance_records.values("class_grade", "section", "subject", "status"))  # ✅ Debug data
    })


from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from admin_panel.models import ClassSubjectAssignment
from django.shortcuts import render
from teacher.models import Attendance
from authentication.models import TeacherProfile

from django.shortcuts import render, redirect
from teacher.models import Attendance
from authentication.models import TeacherProfile

from django.shortcuts import render, redirect
from authentication.models import TeacherProfile
from teacher.models import Attendance

from django.shortcuts import render, redirect
from authentication.models import TeacherProfile
from teacher.models import Attendance
from admin_panel.models import ClassSubjectAssignment  # ✅ Import your assignment model

from django.shortcuts import render, redirect
from authentication.models import TeacherProfile
from admin_panel.models import Subject


def attendance_list(request):
    if not request.user.is_authenticated:
        return redirect('login')

    try:
        teacher_profile = request.user.teacher_profile
    except TeacherProfile.DoesNotExist:
        return render(request, "teacher/no_access.html", {"message": "You are not assigned as a teacher."})

    # 🔹 Get the subject assigned to the teacher from TeacherProfile
    assigned_subject = teacher_profile.subject  # Assuming subject is a CharField

    print("Assigned Subject:", assigned_subject)  # Debugging line

    # 🔹 Filter attendance for this subject
    attendance_records = Attendance.objects.filter(
        subject=assigned_subject  # Match subject name directly
    )

    print("Attendance Records:", attendance_records)  # Debugging line

    return render(request, 'teacher/teacher_att_list.html', {'attendance_records': attendance_records})
