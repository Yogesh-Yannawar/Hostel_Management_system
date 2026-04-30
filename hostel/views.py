import csv
import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.db.models import Q, Sum, Count
from django.views.decorators.http import require_POST
from .models import Student, StudentDocument, Complaint, Leave, AcademicYear, SCHOOL_CHOICES
from .forms import StudentForm, StudentDocumentForm, ComplaintForm, LeaveForm, AcademicYearForm, COURSE_CHOICES, HostelDetailsForm


@login_required
def dashboard(request):
    current_year = AcademicYear.get_current()
    students = Student.objects.all()
    complaints = Complaint.objects.all()
    leaves = Leave.objects.all()

    hostel_stats = []
    for hostel_name in ['Boys Hostel 1', 'Boys Hostel 2', 'Boys Hostel 3', 'Boys Hostel 4']:
        hs = students.filter(hostel=hostel_name)
        paid = hs.filter(fees='Paid')
        hostel_stats.append({
            'name': hostel_name,
            'total': hs.count(),
            'paid': paid.count(),
            'pending': hs.filter(fees='Pending').count(),
            'collected': paid.aggregate(Sum('fee_amount'))['fee_amount__sum'] or 0,
        })

    recent_students = students[:5]
    recent_complaints = complaints[:5]

    ctx = {
        'total_students': students.count(),
        'rooms_occupied': students.exclude(room='').values('room').distinct().count(),
        'fee_paid': students.filter(fees='Paid').count(),
        'fee_pending': students.filter(fees='Pending').count(),
        'total_collected': students.filter(fees='Paid').aggregate(Sum('fee_amount'))['fee_amount__sum'] or 0,
        'open_complaints': complaints.filter(status='Open').count(),
        'pending_leaves': leaves.filter(status='Pending').count(),
        'hostel_stats': hostel_stats,
        'recent_students': recent_students,
        'recent_complaints': recent_complaints,
        'current_year': current_year,
        'all_years': AcademicYear.objects.all(),
        'pending_hostel_approvals': students.filter(university_admitted=True, hostel_registered=True, hostel_approved=False).count(),
    }
    return render(request, 'hostel/dashboard.html', ctx)


# ─── STUDENTS ─────────────────────────────────────────────────────────────────
@login_required
def student_list(request):
    qs = Student.objects.all()
    q = request.GET.get('q', '')
    hostel_filter = request.GET.get('hostel', '')
    cat_filter = request.GET.get('category', '')
    fee_filter = request.GET.get('fees', '')
    dept_filter = request.GET.get('department', '')
    year_filter = request.GET.get('academic_year', '')

    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(aadhar__icontains=q) | Q(room__icontains=q) | Q(phone__icontains=q))
    if hostel_filter:
        qs = qs.filter(hostel=hostel_filter)
    if cat_filter:
        qs = qs.filter(category=cat_filter)
    if fee_filter:
        qs = qs.filter(fees=fee_filter)
    if dept_filter:
        qs = qs.filter(school=dept_filter)
    if year_filter:
        qs = qs.filter(academic_year_id=year_filter)

    ctx = {
        'students': qs,
        'q': q,
        'hostel_filter': hostel_filter,
        'cat_filter': cat_filter,
        'fee_filter': fee_filter,
        'dept_filter': dept_filter,
        'year_filter': year_filter,
        'total': qs.count(),
        'hostels': ['Boys Hostel 1', 'Boys Hostel 2', 'Boys Hostel 3', 'Boys Hostel 4'],
        'categories': ['General', 'OBC', 'SC', 'ST', 'VJNT', 'SBC', 'NT-A', 'NT-B', 'NT-C', 'EWS', 'DT'],
        'departments': SCHOOL_CHOICES,
        'all_years': AcademicYear.objects.all(),
        'current_year': AcademicYear.get_current(),
    }
    return render(request, 'hostel/student_list.html', ctx)


@login_required
def student_detail(request, pk):
    student = get_object_or_404(Student, pk=pk)
    documents = student.documents.all()
    doc_form = StudentDocumentForm()
    doc_types_uploaded = list(documents.values_list('doc_type', flat=True))
    all_doc_types = StudentDocument.DOC_TYPE_CHOICES
    contact_info = [
        ('Phone', student.phone),
        ('Email', student.email),
        ('Father', student.father_name),
        ('Mother', student.mother_name),
        ('Guardian Phone', student.guardian_phone),
        ('Category', student.category),
    ]
    ctx = {
        'student': student,
        'documents': documents,
        'doc_form': doc_form,
        'doc_types_uploaded': doc_types_uploaded,
        'all_doc_types': all_doc_types,
        'missing_docs': [d for d in all_doc_types if d[0] not in doc_types_uploaded],
        'contact_info': contact_info,
    }
    return render(request, 'hostel/student_detail.html', ctx)


@login_required
def student_add(request):
    """
    Two-stage view:
    Stage 1 (GET / verify step): Show verification form with Hostel Reg No & Admission Reg No.
    Stage 2 (POST verify): Check both numbers match an existing pre-registered record,
                            then show the full student form.
    Stage 3 (POST student form): Save student.
    """
    # Stage 3: Saving the full student form
    if request.method == 'POST' and 'save_student' in request.POST:
        form = StudentForm(request.POST, request.FILES)
        hostel_reg_no = request.POST.get('verified_hostel_reg_no', '').strip()
        admission_reg_no = request.POST.get('verified_admission_reg_no', '').strip()
        if form.is_valid():
            student = form.save(commit=False)
            # Store the verified receipt numbers
            student.hostel_receipt_no = hostel_reg_no
            student.hostel_registered = True
            student.university_receipt_no = admission_reg_no
            student.university_admitted = True
            student.save()
            messages.success(request, f'Student {student.name} added successfully!')
            return redirect('student_detail', pk=student.pk)
        else:
            messages.error(request, 'Please fix the errors below.')
        return render(request, 'hostel/student_form.html', {
            'form': form,
            'title': 'Add New Student',
            'course_choices': COURSE_CHOICES,
            'verified_hostel_reg_no': hostel_reg_no,
            'verified_admission_reg_no': admission_reg_no,
        })

    # Stage 2: Verification check
    if request.method == 'POST' and 'verify_student' in request.POST:
        hostel_reg_no = request.POST.get('hostel_reg_no', '').strip()
        admission_reg_no = request.POST.get('admission_reg_no', '').strip()
        errors = []
        if not hostel_reg_no:
            errors.append('Hostel Registration Number is required.')
        if not admission_reg_no:
            errors.append('Admission Registration Number is required.')
        # Check duplicate: student with same receipt numbers already exists?
        if hostel_reg_no and Student.objects.filter(hostel_receipt_no=hostel_reg_no).exists():
            errors.append(f'A student with Hostel Registration Number "{hostel_reg_no}" is already registered.')
        if admission_reg_no and Student.objects.filter(university_receipt_no=admission_reg_no).exists():
            errors.append(f'A student with Admission Registration Number "{admission_reg_no}" is already registered.')
        if errors:
            return render(request, 'hostel/student_verify.html', {
                'errors': errors,
                'hostel_reg_no': hostel_reg_no,
                'admission_reg_no': admission_reg_no,
            })
        # Verification passed — show full student form
        form = StudentForm()
        return render(request, 'hostel/student_form.html', {
            'form': form,
            'title': 'Add New Student',
            'course_choices': COURSE_CHOICES,
            'verified_hostel_reg_no': hostel_reg_no,
            'verified_admission_reg_no': admission_reg_no,
        })

    # Stage 1: Show verification page
    return render(request, 'hostel/student_verify.html', {})


@login_required
def student_edit(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        form = StudentForm(request.POST, request.FILES, instance=student)
        hostel_form = HostelDetailsForm(request.POST, instance=student)
        # Both forms share the same POST data — validate both
        form_valid = form.is_valid()
        hostel_valid = hostel_form.is_valid()
        if form_valid and hostel_valid:
            student = form.save(commit=False)
            hd = hostel_form.cleaned_data
            student.hostel = hd.get('hostel', student.hostel)
            student.room = hd.get('room', student.room)
            student.hostel_registered = hd.get('hostel_registered', student.hostel_registered)
            student.hostel_receipt_no = hd.get('hostel_receipt_no', student.hostel_receipt_no)
            student.save()
            messages.success(request, 'Student updated successfully!')
            return redirect('student_detail', pk=pk)
        else:
            messages.error(request, 'Please fix the errors below.')
    else:
        form = StudentForm(instance=student)
        hostel_form = HostelDetailsForm(instance=student)
    return render(request, 'hostel/student_form.html', {
        'form': form,
        'hostel_form': hostel_form,
        'title': 'Edit Student',
        'student': student,
        'course_choices': COURSE_CHOICES,
        'is_edit': True,
    })


@login_required
def student_hostel_details(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        form = HostelDetailsForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, f'Hostel details saved for {student.name}!')
            return redirect('student_detail', pk=pk)
        else:
            messages.error(request, 'Please fix the errors below.')
    else:
        form = HostelDetailsForm(instance=student)
    return render(request, 'hostel/hostel_details_form.html', {
        'form': form,
        'student': student,
        'title': f'Hostel Details — {student.name}',
        'course_choices': COURSE_CHOICES,
    })


@login_required
def student_delete(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        name = student.name
        student.delete()
        messages.success(request, f'Student {name} deleted.')
        return redirect('student_list')
    return render(request, 'hostel/confirm_delete.html', {'obj': student, 'type': 'Student'})


# ─── UNIVERSITY ADMISSION RECEIPT ─────────────────────────────────────────────
@login_required
def university_receipt(request, pk):
    student = get_object_or_404(Student, pk=pk)
    return render(request, 'hostel/university_receipt.html', {'student': student})


# ─── HOSTEL REGISTRATION RECEIPT ──────────────────────────────────────────────
@login_required
def hostel_receipt(request, pk):
    student = get_object_or_404(Student, pk=pk)
    return render(request, 'hostel/hostel_receipt.html', {'student': student})


# ─── HOSTEL ADMISSION CONFIGURATION ──────────────────────────────────────────
@login_required
def hostel_admission_config(request):
    """
    Eligible students must satisfy BOTH conditions:
    1) Present in Admission receipt (university_admitted=True + university_receipt_no filled)
    2) Present in Hostel receipt (hostel_registered=True + hostel_receipt_no filled)
    """
    all_students = Student.objects.all()
    eligible_pks = []
    not_eligible_list = []
    for s in all_students:
        has_uni = s.university_admitted and bool(s.university_receipt_no.strip())
        has_hostel = s.hostel_registered and bool(s.hostel_receipt_no.strip())
        if has_uni and has_hostel:
            eligible_pks.append(s.pk)
        else:
            reasons = []
            if not has_uni:
                reasons.append('Admission receipt missing / University admission not confirmed')
            if not has_hostel:
                reasons.append('Hostel receipt missing / Hostel registration not done')
            not_eligible_list.append({'student': s, 'reasons': reasons})

    eligible = Student.objects.filter(pk__in=eligible_pks)
    approved = eligible.filter(hostel_approved=True)
    pending_approval = eligible.filter(hostel_approved=False)

    ctx = {
        'eligible': eligible,
        'not_eligible_list': not_eligible_list,
        'approved': approved,
        'pending_approval': pending_approval,
    }
    return render(request, 'hostel/hostel_admission_config.html', ctx)


@login_required
@require_POST
def hostel_approve_student(request, pk):
    student = get_object_or_404(Student, pk=pk)
    errors = []
    if not student.university_admitted or not student.university_receipt_no.strip():
        errors.append('University admission receipt is missing.')
    if not student.hostel_registered or not student.hostel_receipt_no.strip():
        errors.append('Hostel registration receipt is missing.')
    if errors:
        messages.error(request, f'Cannot approve {student.name}: ' + ' | '.join(errors))
        return redirect('hostel_admission_config')
    student.hostel_approved = True
    student.save()
    messages.success(request, f'{student.name} approved for room allocation.')
    return redirect('hostel_admission_config')


@login_required
@require_POST
def hostel_revoke_student(request, pk):
    student = get_object_or_404(Student, pk=pk)
    student.hostel_approved = False
    student.save()
    messages.success(request, f'{student.name} hostel approval revoked.')
    return redirect('hostel_admission_config')


# ─── MERIT LIST ───────────────────────────────────────────────────────────────
@login_required
def merit_list(request):
    dept_filter = request.GET.get('department', '')
    hostel_filter = request.GET.get('hostel', '')
    year_filter = request.GET.get('academic_year', '')
    level_filter = request.GET.get('level', '')

    qs = Student.objects.all()
    if dept_filter:
        qs = qs.filter(school=dept_filter)
    if hostel_filter:
        qs = qs.filter(hostel=hostel_filter)
    if year_filter:
        qs = qs.filter(academic_year_id=year_filter)
    if level_filter:
        qs = qs.filter(level=level_filter)

    # Only include students who have some marks (appear in merit list)
    students_with_score = []
    for s in qs:
        score = s.merit_score
        if score > 0:
            students_with_score.append((s, score, s.merit_basis))
    students_with_score.sort(key=lambda x: x[1], reverse=True)

    # Group by school/department
    dept_groups = {}
    for s, score, basis in students_with_score:
        dept = s.school or 'Unassigned'
        if dept not in dept_groups:
            dept_groups[dept] = []
        dept_groups[dept].append({'student': s, 'score': score, 'basis': basis, 'rank': 0})
    for dept, items in dept_groups.items():
        for i, item in enumerate(items, 1):
            item['rank'] = i

    ctx = {
        'dept_groups': dept_groups,
        'students_with_score': students_with_score,
        'dept_filter': dept_filter,
        'hostel_filter': hostel_filter,
        'year_filter': year_filter,
        'level_filter': level_filter,
        'departments': SCHOOL_CHOICES,
        'hostels': ['Boys Hostel 1', 'Boys Hostel 2', 'Boys Hostel 3', 'Boys Hostel 4'],
        'all_years': AcademicYear.objects.all(),
        'total': len(students_with_score),
    }
    return render(request, 'hostel/merit_list.html', ctx)


# ─── MERIT LIST PDF ───────────────────────────────────────────────────────────
@login_required
def merit_list_pdf(request):
    """Generate a printable HTML page for merit list (browser print-to-PDF)."""
    dept_filter = request.GET.get('department', '')
    hostel_filter = request.GET.get('hostel', '')
    year_filter = request.GET.get('academic_year', '')
    level_filter = request.GET.get('level', '')

    qs = Student.objects.all()
    if dept_filter:
        qs = qs.filter(school=dept_filter)
    if hostel_filter:
        qs = qs.filter(hostel=hostel_filter)
    if year_filter:
        qs = qs.filter(academic_year_id=year_filter)
    if level_filter:
        qs = qs.filter(level=level_filter)

    students_with_score = []
    for s in qs:
        score = s.merit_score
        if score > 0:
            students_with_score.append((s, score, s.merit_basis))
    students_with_score.sort(key=lambda x: x[1], reverse=True)

    dept_groups = {}
    for s, score, basis in students_with_score:
        dept = s.school or 'Unassigned'
        if dept not in dept_groups:
            dept_groups[dept] = []
        dept_groups[dept].append({'student': s, 'score': score, 'basis': basis, 'rank': 0})
    for dept, items in dept_groups.items():
        for i, item in enumerate(items, 1):
            item['rank'] = i

    from datetime import date
    ctx = {
        'dept_groups': dept_groups,
        'students_with_score': students_with_score,
        'dept_filter': dept_filter,
        'hostel_filter': hostel_filter,
        'year_filter': year_filter,
        'level_filter': level_filter,
        'total': len(students_with_score),
        'today': date.today(),
        'current_year': AcademicYear.get_current(),
    }
    return render(request, 'hostel/merit_list_pdf.html', ctx)
@login_required
def upload_document(request, student_pk):
    student = get_object_or_404(Student, pk=student_pk)
    if request.method == 'POST':
        doc_type = request.POST.get('doc_type')
        file = request.FILES.get('file')
        remarks = request.POST.get('remarks', '')
        if not file:
            messages.error(request, 'Please select a file to upload.')
            return redirect('student_detail', pk=student_pk)
        StudentDocument.objects.filter(student=student, doc_type=doc_type).delete()
        StudentDocument.objects.create(student=student, doc_type=doc_type, file=file, remarks=remarks, status='submitted')
        messages.success(request, 'Document uploaded successfully!')
    return redirect('student_detail', pk=student_pk)


@login_required
def delete_document(request, pk):
    doc = get_object_or_404(StudentDocument, pk=pk)
    student_pk = doc.student.pk
    if request.method == 'POST':
        doc.file.delete(save=False)
        doc.delete()
        messages.success(request, 'Document deleted.')
    return redirect('student_detail', pk=student_pk)


@login_required
def update_doc_status(request, pk):
    doc = get_object_or_404(StudentDocument, pk=pk)
    if request.method == 'POST':
        doc.status = request.POST.get('status', doc.status)
        doc.save()
        messages.success(request, 'Document status updated.')
    return redirect('student_detail', pk=doc.student.pk)


# ─── ROOM GRID ─────────────────────────────────────────────────────────────────
@login_required
def room_grid(request):
    students = Student.objects.exclude(room='').values('hostel', 'room', 'name', 'course', 'year', 'fees', 'category', 'pk')
    occ = {}
    for s in students:
        key = f"{s['hostel']}|{s['room']}"
        if key not in occ:
            occ[key] = []
        occ[key].append(s)

    hostels_data = []
    def gen_rooms(g_start, g_end, f_start, f_end):
        r = []
        for i in range(g_start, g_end+1): r.append(f'G-{str(i).zfill(2)}')
        for i in range(f_start, f_end+1): r.append(f'F-{str(i).zfill(3)}')
        return r

    hostel_configs = [
        ('Boys Hostel 1', '#1a3a6e', gen_rooms(1,60,1,60)),
        ('Boys Hostel 2', '#0891b2', gen_rooms(61,90,61,90)),
        ('Boys Hostel 3', '#7c3aed', gen_rooms(1,14,101,119)),
        ('Boys Hostel 4', '#16a34a', gen_rooms(1,12,1,12)),
    ]

    unmatched_students = []
    for name, color, rooms in hostel_configs:
        room_set = set(rooms)
        room_data = []
        matched_keys = set()
        for room in rooms:
            key = f"{name}|{room}"
            studs = occ.get(key, [])
            matched_keys.add(key)
            room_data.append({'room': room, 'students': studs, 'occupied': len(studs) > 0})
        for key, studs in occ.items():
            parts = key.split('|', 1)
            if len(parts) == 2 and parts[0] == name and key not in matched_keys:
                for s in studs:
                    unmatched_students.append({**s, 'stored_room': parts[1]})
        g_rooms = [r for r in room_data if r['room'].startswith('G')]
        f_rooms = [r for r in room_data if r['room'].startswith('F')]
        occupied_count = sum(1 for r in room_data if r['occupied'])
        hostels_data.append({
            'name': name, 'color': color,
            'g_rooms': g_rooms, 'f_rooms': f_rooms,
            'total': len(rooms), 'occupied': occupied_count,
            'empty': len(rooms) - occupied_count,
            'student_count': sum(len(r['students']) for r in room_data),
        })

    import json as json_mod
    hostels_json = json_mod.dumps([{
        'name': h['name'],
        'g_rooms': [{'room': r['room'], 'students': list(r['students']), 'occupied': r['occupied']} for r in h['g_rooms']],
        'f_rooms': [{'room': r['room'], 'students': list(r['students']), 'occupied': r['occupied']} for r in h['f_rooms']],
    } for h in hostels_data])
    hostel_colors = json_mod.dumps([h['color'] for h in hostels_data])
    return render(request, 'hostel/room_grid.html', {
        'hostels_data': hostels_data,
        'hostels_json': hostels_json,
        'hostel_colors': hostel_colors,
        'unmatched_students': unmatched_students,
    })


# ─── FEES ─────────────────────────────────────────────────────────────────────
@login_required
def fee_tracking(request):
    qs = Student.objects.all()
    q = request.GET.get('q', '')
    fee_filter = request.GET.get('fees', '')
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(aadhar__icontains=q) | Q(room__icontains=q))
    if fee_filter:
        qs = qs.filter(fees=fee_filter)
    total_paid = Student.objects.filter(fees='Paid').aggregate(Sum('fee_amount'))['fee_amount__sum'] or 0
    ctx = {
        'students': qs, 'q': q, 'fee_filter': fee_filter,
        'total_paid': total_paid,
        'pending_count': Student.objects.filter(fees='Pending').count(),
        'total_students': Student.objects.count(),
    }
    return render(request, 'hostel/fees.html', ctx)


@login_required
def update_fee(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        student.fees = request.POST.get('fees', student.fees)
        student.fee_amount = request.POST.get('fee_amount', student.fee_amount) or 0
        fee_paid_date = request.POST.get('fee_paid_date', '')
        student.fee_paid_date = fee_paid_date if fee_paid_date else None
        student.save()
        messages.success(request, f'Fee updated for {student.name}')
    return redirect('fee_tracking')


# ─── COMPLAINTS ───────────────────────────────────────────────────────────────
@login_required
def complaint_list(request):
    qs = Complaint.objects.all()
    q = request.GET.get('q', '')
    status_filter = request.GET.get('status', '')
    if q:
        qs = qs.filter(Q(student_name__icontains=q) | Q(title__icontains=q) | Q(room__icontains=q))
    if status_filter:
        qs = qs.filter(status=status_filter)
    total_dmg = qs.aggregate(Sum('damage_amount'))['damage_amount__sum'] or 0
    pending_dmg = qs.filter(status='Open').aggregate(Sum('damage_amount'))['damage_amount__sum'] or 0
    ctx = {
        'complaints': qs, 'q': q, 'status_filter': status_filter,
        'total_complaints': Complaint.objects.count(),
        'open_count': Complaint.objects.filter(status='Open').count(),
        'total_dmg': total_dmg, 'pending_dmg': pending_dmg,
        'students': Student.objects.all(),
    }
    return render(request, 'hostel/complaints.html', ctx)


@login_required
def complaint_add(request):
    if request.method == 'POST':
        form = ComplaintForm(request.POST)
        if form.is_valid():
            c = form.save(commit=False)
            if c.student:
                c.student_name = c.student.name
                c.room = c.student.room
                c.hostel = c.student.hostel
            c.save()
            messages.success(request, 'Complaint filed successfully!')
            return redirect('complaint_list')
    else:
        form = ComplaintForm()
    return render(request, 'hostel/complaint_form.html', {'form': form, 'title': 'File Complaint'})


@login_required
def complaint_edit(request, pk):
    complaint = get_object_or_404(Complaint, pk=pk)
    if request.method == 'POST':
        form = ComplaintForm(request.POST, instance=complaint)
        if form.is_valid():
            c = form.save(commit=False)
            if c.student:
                c.student_name = c.student.name
                c.room = c.student.room
                c.hostel = c.student.hostel
            c.save()
            messages.success(request, 'Complaint updated!')
            return redirect('complaint_list')
    else:
        form = ComplaintForm(instance=complaint)
    return render(request, 'hostel/complaint_form.html', {'form': form, 'title': 'Edit Complaint', 'complaint': complaint})


@login_required
def complaint_delete(request, pk):
    complaint = get_object_or_404(Complaint, pk=pk)
    if request.method == 'POST':
        complaint.delete()
        messages.success(request, 'Complaint deleted.')
        return redirect('complaint_list')
    return render(request, 'hostel/confirm_delete.html', {'obj': complaint, 'type': 'Complaint'})


@login_required
def update_complaint_status(request, pk):
    complaint = get_object_or_404(Complaint, pk=pk)
    if request.method == 'POST':
        complaint.status = request.POST.get('status', complaint.status)
        complaint.save()
        messages.success(request, 'Status updated.')
    return redirect('complaint_list')


# ─── LEAVE ─────────────────────────────────────────────────────────────────────
@login_required
def leave_list(request):
    qs = Leave.objects.select_related('student').all()
    status_filter = request.GET.get('status', '')
    if status_filter:
        qs = qs.filter(status=status_filter)
    ctx = {
        'leaves': qs,
        'status_filter': status_filter,
        'pending_count': Leave.objects.filter(status='Pending').count(),
        'approved_count': Leave.objects.filter(status='Approved').count(),
        'students': Student.objects.all(),
    }
    return render(request, 'hostel/leave.html', ctx)


@login_required
def leave_add(request):
    if request.method == 'POST':
        form = LeaveForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Leave application submitted!')
            return redirect('leave_list')
    else:
        form = LeaveForm()
    return render(request, 'hostel/leave_form.html', {'form': form, 'title': 'Apply for Leave'})


@login_required
def leave_update_status(request, pk):
    leave = get_object_or_404(Leave, pk=pk)
    if request.method == 'POST':
        leave.status = request.POST.get('status', leave.status)
        leave.remarks = request.POST.get('remarks', leave.remarks)
        leave.save()
        messages.success(request, 'Leave status updated.')
    return redirect('leave_list')


@login_required
def leave_delete(request, pk):
    leave = get_object_or_404(Leave, pk=pk)
    if request.method == 'POST':
        leave.delete()
        messages.success(request, 'Leave deleted.')
    return redirect('leave_list')


# ─── EXPORT / REPORTS ─────────────────────────────────────────────────────────
@login_required
def export_reports(request):
    students = Student.objects.all()
    hostel_summary = []
    for h in ['Boys Hostel 1', 'Boys Hostel 2', 'Boys Hostel 3', 'Boys Hostel 4']:
        hs = students.filter(hostel=h)
        paid = hs.filter(fees='Paid')
        hostel_summary.append({
            'name': h, 'total': hs.count(), 'paid': paid.count(),
            'pending': hs.filter(fees='Pending').count(),
            'collected': paid.aggregate(Sum('fee_amount'))['fee_amount__sum'] or 0,
        })
    categories = ['General', 'OBC', 'SC', 'ST', 'VJNT', 'SBC', 'NT-A', 'NT-B', 'NT-C', 'EWS', 'DT']
    cat_data = []
    total = students.count()
    for cat in categories:
        count = students.filter(category=cat).count()
        if count:
            cat_data.append({'name': cat, 'count': count, 'pct': round(count/total*100) if total else 0})
    complaints = Complaint.objects.all()
    ctx = {
        'hostel_summary': hostel_summary, 'cat_data': cat_data,
        'total_students': total, 'complaints': complaints,
        'total_dmg': complaints.aggregate(Sum('damage_amount'))['damage_amount__sum'] or 0,
        'hostels': ['Boys Hostel 1', 'Boys Hostel 2', 'Boys Hostel 3', 'Boys Hostel 4'],
        'categories': categories,
    }
    return render(request, 'hostel/export_reports.html', ctx)


@login_required
def export_students_csv(request):
    hostel_f = request.GET.get('hostel', '')
    cat_f = request.GET.get('category', '')
    fee_f = request.GET.get('fees', '')
    qs = Student.objects.all()
    if hostel_f: qs = qs.filter(hostel=hostel_f)
    if cat_f: qs = qs.filter(category=cat_f)
    if fee_f: qs = qs.filter(fees=fee_f)
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="SRTMU_Hostel_Students.csv"'
    response.write('\ufeff')
    writer = csv.writer(response)
    writer.writerow(['Student Name','Cast','Department','Adhar Number','Hostel Name','Room Number','Fees','Amount Paid (Rs)','Date','Receipt Number','Mobile Number','Address'])
    for s in qs:
        writer.writerow([s.name, s.category, s.school, '\t'+str(s.aadhar), s.hostel, s.room, s.fees, s.fee_amount, s.admission_date, s.receipt_number, '\t'+str(s.phone), s.address])
    return response


@login_required
def export_complaints_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="SRTMU_Hostel_Complaints.csv"'
    response.write('\ufeff')
    writer = csv.writer(response)
    writer.writerow(['Student','Room','Hostel','Title','Type','Description','Damage Amount','Date','Priority','Status'])
    for c in Complaint.objects.all():
        writer.writerow([c.student_name, c.room, c.hostel, c.title, c.complaint_type, c.description, c.damage_amount, c.damage_date, c.priority, c.status])
    return response


# ─── ACADEMIC YEAR MANAGEMENT ─────────────────────────────────────────────────
@login_required
def academic_year_list(request):
    years = AcademicYear.objects.all()
    form = AcademicYearForm()
    if request.method == 'POST':
        form = AcademicYearForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Academic year created!')
            return redirect('academic_year_list')
    ctx = {'years': years, 'form': form}
    return render(request, 'hostel/academic_year_list.html', ctx)


@login_required
def academic_year_set_current(request, pk):
    year = get_object_or_404(AcademicYear, pk=pk)
    year.is_current = True
    year.save()
    messages.success(request, f'{year.label} set as current academic year.')
    return redirect('academic_year_list')


@login_required
def academic_year_delete(request, pk):
    year = get_object_or_404(AcademicYear, pk=pk)
    if request.method == 'POST':
        if year.students.exists():
            messages.error(request, f'Cannot delete: {year.students.count()} students linked to this year.')
        else:
            year.delete()
            messages.success(request, 'Academic year deleted.')
    return redirect('academic_year_list')


# ─── ROOM ASSIGN (AJAX) ───────────────────────────────────────────────────────
@login_required
@require_POST
def room_assign(request):
    student_pk = request.POST.get('student_pk')
    room = request.POST.get('room', '').strip()
    hostel = request.POST.get('hostel', '').strip()
    student = get_object_or_404(Student, pk=student_pk)

    # If room is being CLEARED (unassign), skip eligibility check
    if room:
        # 2-condition check before room allocation
        errors = []
        if not (student.university_admitted and student.university_receipt_no.strip()):
            errors.append('Admission receipt missing')
        if not (student.hostel_registered and student.hostel_receipt_no.strip()):
            errors.append('Hostel receipt missing')
        if not student.hostel_approved:
            errors.append('Hostel approval pending — go to Hostel Admission page to approve')
        if errors:
            return JsonResponse({'ok': False, 'error': 'Cannot allocate room: ' + ' | '.join(errors)}, status=400)

    student.room = room
    if hostel:
        student.hostel = hostel
    student.save()
    return JsonResponse({'ok': True, 'student': student.name, 'room': room, 'hostel': hostel})


@login_required
def room_students_json(request):
    hostel = request.GET.get('hostel', '')
    eligible_only = request.GET.get('eligible_only', '')
    qs = Student.objects.all()
    if hostel:
        qs = qs.filter(hostel=hostel)
    if eligible_only:
        # For room-grid assignment: only hostel-approved students
        qs = qs.filter(hostel_approved=True)
    data = list(qs.values('pk', 'name', 'room', 'hostel', 'course', 'year', 'hostel_approved'))
    return JsonResponse({'students': data})


# ─── ROOM ALLOCATION (Separate dedicated page) ─────────────────────────────────
@login_required
def room_allocation(request):
    """Dedicated room allocation page — separate from student add form and room grid."""
    hostels = ['Boys Hostel 1', 'Boys Hostel 2', 'Boys Hostel 3', 'Boys Hostel 4']
    # Approved students without a room (pending allocation)
    unallocated = Student.objects.filter(hostel_approved=True, room='')
    # Already allocated
    allocated = Student.objects.filter(hostel_approved=True).exclude(room='')

    if request.method == 'POST':
        student_pk = request.POST.get('student_pk', '').strip()
        hostel = request.POST.get('hostel', '').strip()
        room = request.POST.get('room', '').strip()
        if student_pk and hostel and room:
            student = get_object_or_404(Student, pk=student_pk)
            if not student.hostel_approved:
                messages.error(request, f'{student.name} is not yet approved for hostel. Please approve from Hostel Admission page first.')
            else:
                student.hostel = hostel
                student.room = room
                student.save()
                messages.success(request, f'Room {room} in {hostel} allocated to {student.name}.')
        else:
            messages.error(request, 'Please select a student, hostel, and room number.')
        return redirect('room_allocation')

    ctx = {
        'hostels': hostels,
        'unallocated': unallocated,
        'allocated': allocated,
    }
    return render(request, 'hostel/room_allocation.html', ctx)
