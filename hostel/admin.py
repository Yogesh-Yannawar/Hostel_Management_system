from django.contrib import admin
from .models import Student, StudentDocument, Complaint, Leave, AcademicYear

@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
    list_display = ['label', 'start_year', 'end_year', 'is_current', 'created_at']
    list_filter = ['is_current']

class DocumentInline(admin.TabularInline):
    model = StudentDocument
    extra = 0
    readonly_fields = ['uploaded_at']

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['name', 'aadhar', 'gender', 'category', 'hostel', 'room', 'fees', 'course']
    list_filter = ['hostel', 'category', 'fees', 'gender', 'level']
    search_fields = ['name', 'aadhar', 'phone']
    inlines = [DocumentInline]

@admin.register(StudentDocument)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['student', 'doc_type', 'status', 'uploaded_at']
    list_filter = ['doc_type', 'status']

@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ['title', 'student_name', 'hostel', 'room', 'priority', 'status', 'damage_amount']
    list_filter = ['status', 'priority', 'hostel']

@admin.register(Leave)
class LeaveAdmin(admin.ModelAdmin):
    list_display = ['student', 'from_date', 'to_date', 'status']
    list_filter = ['status']
