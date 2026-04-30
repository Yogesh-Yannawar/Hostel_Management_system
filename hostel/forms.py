from django import forms
from django.core.exceptions import ValidationError
import re
from .models import Student, StudentDocument, Complaint, Leave, AcademicYear

ROOM_CHOICES_BH1 = [(f'G-{str(i).zfill(2)}', f'G-{str(i).zfill(2)}') for i in range(1, 61)] + [(f'F-{str(i).zfill(3)}', f'F-{str(i).zfill(3)}') for i in range(1, 61)]
ROOM_CHOICES_BH2 = [(f'G-{str(i).zfill(2)}', f'G-{str(i).zfill(2)}') for i in range(61, 91)] + [(f'F-{str(i).zfill(3)}', f'F-{str(i).zfill(3)}') for i in range(61, 91)]
ROOM_CHOICES_BH3 = [(f'G-{str(i).zfill(2)}', f'G-{str(i).zfill(2)}') for i in range(1, 15)] + [(f'F-{str(i).zfill(3)}', f'F-{str(i).zfill(3)}') for i in range(101, 120)]
ROOM_CHOICES_BH4 = [(f'G-{str(i).zfill(2)}', f'G-{str(i).zfill(2)}') for i in range(1, 13)] + [(f'F-{str(i).zfill(3)}', f'F-{str(i).zfill(3)}') for i in range(1, 13)]
ALL_ROOMS = [('', '— Select Room —')] + ROOM_CHOICES_BH1 + ROOM_CHOICES_BH2 + ROOM_CHOICES_BH3 + ROOM_CHOICES_BH4

COURSE_CHOICES = [
    ('', '— Select Course —'),
    ('B.Sc. Chemistry', 'B.Sc. Chemistry'), ('M.Sc. Chemistry', 'M.Sc. Chemistry'), ('M.Sc. Analytical Chemistry', 'M.Sc. Analytical Chemistry'),
    ('B.Com', 'B.Com'), ('BBA', 'BBA'), ('M.Com', 'M.Com'), ('MBA', 'MBA'),
    ('B.Sc. Computer Science', 'B.Sc. Computer Science'), ('BCA', 'BCA'), ('B.Sc. IT', 'B.Sc. IT'), ('M.Sc. Computer Science', 'M.Sc. Computer Science'), ('MCA', 'MCA'), ('M.Sc. IT', 'M.Sc. IT'),
    ('B.Sc. Geography', 'B.Sc. Geography'), ('M.Sc. Geography', 'M.Sc. Geography'), ('M.Sc. Geology', 'M.Sc. Geology'),
    ('B.Ed', 'B.Ed'), ('M.Ed', 'M.Ed'), ('M.A. Education', 'M.A. Education'),
    ('B.A. Fine Arts', 'B.A. Fine Arts'), ('B.A. Music', 'B.A. Music'), ('M.A. Fine Arts', 'M.A. Fine Arts'), ('M.A. Music', 'M.A. Music'),
    ('B.A. Marathi', 'B.A. Marathi'), ('B.A. Hindi', 'B.A. Hindi'), ('B.A. English', 'B.A. English'), ('B.A. Urdu', 'B.A. Urdu'), ('M.A. Marathi', 'M.A. Marathi'), ('M.A. Hindi', 'M.A. Hindi'), ('M.A. English', 'M.A. English'), ('M.A. Urdu', 'M.A. Urdu'),
    ('B.Sc. Botany', 'B.Sc. Botany'), ('B.Sc. Zoology', 'B.Sc. Zoology'), ('B.Sc. Biotechnology', 'B.Sc. Biotechnology'), ('M.Sc. Botany', 'M.Sc. Botany'), ('M.Sc. Zoology', 'M.Sc. Zoology'), ('M.Sc. Biotechnology', 'M.Sc. Biotechnology'), ('M.Sc. Microbiology', 'M.Sc. Microbiology'),
    ('B.Sc. Mathematics', 'B.Sc. Mathematics'), ('B.Sc. Statistics', 'B.Sc. Statistics'), ('M.Sc. Mathematics', 'M.Sc. Mathematics'), ('M.Sc. Statistics', 'M.Sc. Statistics'),
    ('B.A. Journalism', 'B.A. Journalism'), ('B.A. Mass Communication', 'B.A. Mass Communication'), ('M.A. Journalism', 'M.A. Journalism'), ('M.A. Mass Communication', 'M.A. Mass Communication'),
    ('B.Pharmacy', 'B.Pharmacy'), ('D.Pharmacy', 'D.Pharmacy'), ('M.Pharmacy', 'M.Pharmacy'),
    ('B.Sc. Physics', 'B.Sc. Physics'), ('M.Sc. Physics', 'M.Sc. Physics'), ('M.Sc. Electronics', 'M.Sc. Electronics'),
    ('B.A. Sociology', 'B.A. Sociology'), ('B.A. Political Science', 'B.A. Political Science'), ('B.A. Economics', 'B.A. Economics'), ('B.A. History', 'B.A. History'), ('B.A. Psychology', 'B.A. Psychology'),
    ('M.A. Sociology', 'M.A. Sociology'), ('M.A. Political Science', 'M.A. Political Science'), ('M.A. Economics', 'M.A. Economics'), ('M.A. History', 'M.A. History'), ('M.A. Psychology', 'M.A. Psychology'), ('M.S.W.', 'M.S.W.'),
    ('B.A. LL.B', 'B.A. LL.B'), ('BBA LL.B', 'BBA LL.B'), ('LL.M', 'LL.M'),
    ('B.E. Computer', 'B.E. Computer'), ('B.E. Electronics', 'B.E. Electronics'), ('B.E. Mechanical', 'B.E. Mechanical'), ('B.E. Civil', 'B.E. Civil'), ('M.E. Computer', 'M.E. Computer'), ('M.Tech IT', 'M.Tech IT'),
]

YEAR_CHOICES = [('1st Year','1st Year'),('2nd Year','2nd Year'),('3rd Year','3rd Year'),('4th Year','4th Year')]


class StudentForm(forms.ModelForm):
    course = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'list': 'course-datalist',
            'placeholder': 'Select or type course name…',
            'autocomplete': 'off',
        })
    )
    year = forms.ChoiceField(choices=YEAR_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}))

    def clean_name(self):
        v = self.cleaned_data.get('name', '').strip()
        if not v:
            raise ValidationError('Student name is required.')
        if not re.match(r'^[A-Za-z\s\.]+$', v):
            raise ValidationError('Name must contain only letters, spaces, and dots.')
        return v

    def clean_aadhar(self):
        v = self.cleaned_data.get('aadhar', '').strip()
        if not re.match(r'^\d{12}$', v):
            raise ValidationError('Aadhaar number must be exactly 12 digits (no letters or symbols).')
        return v

    def clean_phone(self):
        v = self.cleaned_data.get('phone', '').strip()
        if not re.match(r'^[6-9]\d{9}$', v):
            raise ValidationError('Enter a valid 10-digit Indian mobile number starting with 6, 7, 8, or 9.')
        return v

    def clean_guardian_phone(self):
        v = self.cleaned_data.get('guardian_phone', '').strip()
        if v and not re.match(r'^[6-9]\d{9}$', v):
            raise ValidationError('Enter a valid 10-digit Indian mobile number starting with 6, 7, 8, or 9.')
        return v

    def clean_father_name(self):
        v = self.cleaned_data.get('father_name', '').strip()
        if v and not re.match(r'^[A-Za-z\s\.]+$', v):
            raise ValidationError('Father name must contain only letters, spaces, and dots.')
        return v

    def clean_mother_name(self):
        v = self.cleaned_data.get('mother_name', '').strip()
        if v and not re.match(r'^[A-Za-z\s\.]+$', v):
            raise ValidationError('Mother name must contain only letters, spaces, and dots.')
        return v

    def clean_marks_10(self):
        v = self.cleaned_data.get('marks_10', '').strip()
        if v:
            try:
                f = float(v)
                if f < 0 or f > 100:
                    raise ValidationError('Marks must be between 0 and 100.')
            except ValueError:
                raise ValidationError('Enter a valid percentage (e.g. 85 or 85.5).')
        return v

    def clean_marks_12(self):
        v = self.cleaned_data.get('marks_12', '').strip()
        if v:
            try:
                f = float(v)
                if f < 0 or f > 100:
                    raise ValidationError('Marks must be between 0 and 100.')
            except ValueError:
                raise ValidationError('Enter a valid percentage.')
        return v

    def clean_marks_ug(self):
        v = self.cleaned_data.get('marks_ug', '').strip()
        if v:
            try:
                f = float(v)
                if f < 0 or f > 100:
                    raise ValidationError('Marks must be between 0 and 100.')
            except ValueError:
                raise ValidationError('Enter a valid percentage.')
        return v

    def clean_marks_pg(self):
        v = self.cleaned_data.get('marks_pg', '').strip()
        if v:
            try:
                f = float(v)
                if f < 0 or f > 100:
                    raise ValidationError('Marks must be between 0 and 100.')
            except ValueError:
                raise ValidationError('Enter a valid percentage.')
        return v

    def clean_cet_marks_obtained(self):
        v = self.cleaned_data.get('cet_marks_obtained', '').strip()
        if v:
            try:
                f = float(v)
                if f < 0:
                    raise ValidationError('CET marks obtained cannot be negative.')
            except ValueError:
                raise ValidationError('Enter a valid number (e.g. 150).')
        return v

    def clean_cet_marks_total(self):
        v = self.cleaned_data.get('cet_marks_total', '').strip()
        if v:
            try:
                f = float(v)
                if f <= 0:
                    raise ValidationError('CET total marks must be greater than 0.')
            except ValueError:
                raise ValidationError('Enter a valid number (e.g. 200).')
        return v

    def clean(self):
        cleaned = super().clean()
        obtained = cleaned.get('cet_marks_obtained', '').strip()
        total = cleaned.get('cet_marks_total', '').strip()
        if obtained and not total:
            self.add_error('cet_marks_total', 'Please enter CET total marks when CET obtained marks are provided.')
        if total and not obtained:
            self.add_error('cet_marks_obtained', 'Please enter CET obtained marks when CET total marks are provided.')
        if obtained and total:
            try:
                if float(obtained) > float(total):
                    self.add_error('cet_marks_obtained', 'CET obtained marks cannot exceed total marks.')
            except ValueError:
                pass
        return cleaned

    class Meta:
        model = Student
        exclude = ['created_at', 'updated_at', 'hostel_approved', 'hostel', 'room',
                   'hostel_registered', 'hostel_receipt_no',
                   'university_admitted', 'university_receipt_no']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Student full name (letters and dots only)'}),
            'aadhar': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '12-digit Aadhaar number', 'maxlength': '12', 'inputmode': 'numeric', 'pattern': r'\d{12}'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '10-digit Indian mobile', 'maxlength': '10', 'inputmode': 'numeric'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'student@email.com'}),
            'father_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Father's full name"}),
            'mother_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Mother's full name"}),
            'guardian_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Guardian's 10-digit phone", 'maxlength': '10', 'inputmode': 'numeric'}),
            'school': forms.Select(attrs={'class': 'form-select'}),
            'level': forms.Select(attrs={'class': 'form-select'}),
            'admission_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'district': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Nanded'}),
            'fees': forms.Select(attrs={'class': 'form-select'}),
            'fee_amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0'}),
            'fee_paid_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'receipt_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. RCP-2024-001'}),
            'marks_10': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 85'}),
            'marks_12': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 80'}),
            'cet_marks_obtained': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 150'}),
            'cet_marks_total': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 200'}),
            'marks_ug': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 70'}),
            'marks_pg': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 75'}),
            'biometric_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. BIO001'}),
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'photo': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'academic_year': forms.Select(attrs={'class': 'form-select'}),
        }


class StudentDocumentForm(forms.ModelForm):
    class Meta:
        model = StudentDocument
        fields = ['doc_type', 'file', 'remarks']
        widgets = {
            'doc_type': forms.Select(attrs={'class': 'form-select'}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
            'remarks': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Optional remarks'}),
        }


class ComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ['student', 'title', 'complaint_type', 'description', 'damage_amount', 'damage_date', 'priority', 'status']
        widgets = {
            'student': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Brief title'}),
            'complaint_type': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Optional: describe the damage…'}),
            'damage_amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0 (optional)'}),
            'damage_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['description'].required = False
        self.fields['damage_amount'].required = False


class LeaveForm(forms.ModelForm):
    def clean_contact_during_leave(self):
        v = self.cleaned_data.get('contact_during_leave', '').strip()
        if v and not re.match(r'^[6-9]\d{9}$', v):
            raise ValidationError('Enter a valid 10-digit Indian mobile number.')
        return v

    class Meta:
        model = Leave
        fields = ['student', 'from_date', 'to_date', 'reason', 'destination', 'contact_during_leave', 'certificate']
        widgets = {
            'student': forms.Select(attrs={'class': 'form-select'}),
            'from_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'to_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'destination': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Destination address'}),
            'contact_during_leave': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone during leave (10-digit)', 'maxlength': '10', 'inputmode': 'numeric'}),
            'certificate': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.jpg,.jpeg,.png'}),
        }


class AcademicYearForm(forms.ModelForm):
    class Meta:
        model = AcademicYear
        fields = ['label', 'start_year', 'end_year', 'is_current']
        widgets = {
            'label': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 2025-2026'}),
            'start_year': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '2025'}),
            'end_year': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '2026'}),
            'is_current': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class HostelDetailsForm(forms.ModelForm):
    """Separate form for hostel assignment — asked AFTER student is added."""

    def clean_hostel_receipt_no(self):
        v = self.cleaned_data.get('hostel_receipt_no', '').strip()
        if not v:
            raise ValidationError('Hostel registration receipt number is required.')
        return v

    def clean_hostel(self):
        v = self.cleaned_data.get('hostel', '').strip()
        if not v:
            raise ValidationError('Please select a hostel.')
        return v

    class Meta:
        model = Student
        fields = ['hostel', 'room', 'hostel_registered', 'hostel_receipt_no']
        widgets = {
            'hostel': forms.Select(attrs={'class': 'form-select'}),
            'room': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. G-01 or F-001', 'list': 'room-datalist', 'autocomplete': 'off'}),
            'hostel_registered': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'hostel_receipt_no': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Hostel registration receipt no. (Required)'}),
        }
