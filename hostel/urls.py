from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    # Students
    path('students/', views.student_list, name='student_list'),
    path('students/add/', views.student_add, name='student_add'),
    path('students/<int:pk>/', views.student_detail, name='student_detail'),
    path('students/<int:pk>/edit/', views.student_edit, name='student_edit'),
    path('students/<int:pk>/delete/', views.student_delete, name='student_delete'),
    path('students/<int:pk>/hostel-details/', views.student_hostel_details, name='student_hostel_details'),
    # Receipts
    path('students/<int:pk>/university-receipt/', views.university_receipt, name='university_receipt'),
    path('students/<int:pk>/hostel-receipt/', views.hostel_receipt, name='hostel_receipt'),
    # Hostel Admission Config
    path('hostel-admission/', views.hostel_admission_config, name='hostel_admission_config'),
    path('hostel-admission/<int:pk>/approve/', views.hostel_approve_student, name='hostel_approve_student'),
    path('hostel-admission/<int:pk>/revoke/', views.hostel_revoke_student, name='hostel_revoke_student'),
    # Merit List (disabled — removed per requirements)
    # path('merit-list/', views.merit_list, name='merit_list'),
    # path('merit-list/pdf/', views.merit_list_pdf, name='merit_list_pdf'),
    # Documents
    path('students/<int:student_pk>/upload-document/', views.upload_document, name='upload_document'),
    path('documents/<int:pk>/delete/', views.delete_document, name='delete_document'),
    path('documents/<int:pk>/status/', views.update_doc_status, name='update_doc_status'),
    # Rooms
    path('rooms/', views.room_grid, name='room_grid'),
    path('rooms/assign/', views.room_assign, name='room_assign'),
    path('rooms/allocate/', views.room_allocation, name='room_allocation'),
    path('rooms/students-json/', views.room_students_json, name='room_students_json'),
    # Fees
    path('fees/', views.fee_tracking, name='fee_tracking'),
    path('fees/<int:pk>/update/', views.update_fee, name='update_fee'),
    # Complaints
    path('complaints/', views.complaint_list, name='complaint_list'),
    path('complaints/add/', views.complaint_add, name='complaint_add'),
    path('complaints/<int:pk>/edit/', views.complaint_edit, name='complaint_edit'),
    path('complaints/<int:pk>/delete/', views.complaint_delete, name='complaint_delete'),
    path('complaints/<int:pk>/status/', views.update_complaint_status, name='update_complaint_status'),
    # Leave
    path('leave/', views.leave_list, name='leave_list'),
    path('leave/add/', views.leave_add, name='leave_add'),
    path('leave/<int:pk>/status/', views.leave_update_status, name='leave_update_status'),
    path('leave/<int:pk>/delete/', views.leave_delete, name='leave_delete'),
    # Export
    path('export/', views.export_reports, name='export_reports'),
    path('export/students.csv', views.export_students_csv, name='export_students_csv'),
    path('export/complaints.csv', views.export_complaints_csv, name='export_complaints_csv'),
    # Academic Year
    path('academic-years/', views.academic_year_list, name='academic_year_list'),
    path('academic-years/<int:pk>/set-current/', views.academic_year_set_current, name='academic_year_set_current'),
    path('academic-years/<int:pk>/delete/', views.academic_year_delete, name='academic_year_delete'),
]
