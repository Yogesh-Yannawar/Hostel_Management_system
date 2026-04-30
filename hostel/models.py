from django.db import models
import re
from django.core.exceptions import ValidationError

# ─── VALIDATORS ────────────────────────────────────────────────────────────────
def validate_name(value):
    if not re.match(r'^[A-Za-z\s\.]+$', value):
        raise ValidationError('Name must contain only letters, spaces, and dots.')

def validate_aadhar(value):
    if not re.match(r'^\d{12}$', value):
        raise ValidationError('Aadhaar number must be exactly 12 digits.')

def validate_phone(value):
    if not re.match(r'^[6-9]\d{9}$', value):
        raise ValidationError('Enter a valid 10-digit Indian mobile number (starting with 6-9).')

def validate_marks(value):
    if value:
        try:
            v = float(value)
            if v < 0 or v > 100:
                raise ValidationError('Marks must be between 0 and 100.')
        except ValueError:
            raise ValidationError('Enter a valid percentage (e.g. 85 or 85.5).')

# ─── ACADEMIC YEAR ─────────────────────────────────────────────────────────────
class AcademicYear(models.Model):
    label = models.CharField(max_length=20, unique=True, help_text="e.g. 2025-2026")
    start_year = models.IntegerField()
    end_year = models.IntegerField()
    is_current = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-start_year']

    def __str__(self):
        return self.label

    def save(self, *args, **kwargs):
        if self.is_current:
            AcademicYear.objects.exclude(pk=self.pk).update(is_current=False)
        super().save(*args, **kwargs)

    @classmethod
    def get_current(cls):
        return cls.objects.filter(is_current=True).first()


GENDER_CHOICES = [('Male','Male'),('Female','Female'),('Other','Other')]
CATEGORY_CHOICES = [('General','General'),('OBC','OBC'),('SC','SC'),('ST','ST'),('VJNT','VJNT'),('SBC','SBC'),('NT-A','NT-A'),('NT-B','NT-B'),('NT-C','NT-C'),('EWS','EWS'),('DT','DT'),('Other','Other')]
FEE_CHOICES = [('Pending','Pending'),('Paid','Paid'),('Partial','Partial')]
LEVEL_CHOICES = [('UG','UG (Undergraduate)'),('PG','PG (Postgraduate)')]
HOSTEL_CHOICES = [('Boys Hostel 1','Boys Hostel 1'),('Boys Hostel 2','Boys Hostel 2'),('Boys Hostel 3','Boys Hostel 3'),('Boys Hostel 4','Boys Hostel 4')]
STATUS_CHOICES = [('submitted','Submitted'),('verified','Verified'),('rejected','Rejected'),('pending','Pending')]

SCHOOL_CHOICES = [
    ('School of Chemical Sciences','School of Chemical Sciences'),
    ('School of Commerce and Management Sciences','School of Commerce and Management Sciences'),
    ('School of Computational Sciences','School of Computational Sciences'),
    ('School of Earth Sciences','School of Earth Sciences'),
    ('School of Educational Sciences','School of Educational Sciences'),
    ('School of Fine and Performing Arts','School of Fine and Performing Arts'),
    ('School of Language, Literature and Culture Studies','School of Language, Literature and Culture Studies'),
    ('School of Life Sciences','School of Life Sciences'),
    ('School of Mathematical Sciences','School of Mathematical Sciences'),
    ('School of Media Studies','School of Media Studies'),
    ('School of Pharmacy','School of Pharmacy'),
    ('School of Physical Sciences','School of Physical Sciences'),
    ('School of Social Sciences','School of Social Sciences'),
    ('School of Law','School of Law'),
    ('School of Technology','School of Technology'),
]


class Student(models.Model):
    name = models.CharField(max_length=200, validators=[validate_name])
    aadhar = models.CharField(max_length=12, unique=True, validators=[validate_aadhar])
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='Male')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='General')
    phone = models.CharField(max_length=10, validators=[validate_phone])
    email = models.EmailField(blank=True)
    father_name = models.CharField(max_length=200, blank=True, validators=[validate_name])
    mother_name = models.CharField(max_length=200, blank=True, validators=[validate_name])
    guardian_phone = models.CharField(max_length=10, blank=True)
    school = models.CharField(max_length=200, choices=SCHOOL_CHOICES, blank=True)
    level = models.CharField(max_length=5, choices=LEVEL_CHOICES, default='UG')
    course = models.CharField(max_length=200)
    year = models.CharField(max_length=20)
    hostel = models.CharField(max_length=50, choices=HOSTEL_CHOICES, blank=True, default='')
    room = models.CharField(max_length=20, blank=True)
    admission_date = models.DateField(null=True, blank=True)
    address = models.TextField(blank=True)
    district = models.CharField(max_length=100, blank=True)
    fees = models.CharField(max_length=10, choices=FEE_CHOICES, default='Pending')
    fee_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fee_paid_date = models.DateField(null=True, blank=True)
    receipt_number = models.CharField(max_length=50, blank=True)
    marks_10 = models.CharField(max_length=6, blank=True, validators=[validate_marks])
    marks_12 = models.CharField(max_length=6, blank=True, validators=[validate_marks])
    cet_marks_obtained = models.CharField(max_length=6, blank=True, validators=[validate_marks], help_text="CET marks obtained")
    cet_marks_total = models.CharField(max_length=6, blank=True, validators=[validate_marks], help_text="CET total marks")
    marks_ug = models.CharField(max_length=6, blank=True, validators=[validate_marks])
    marks_pg = models.CharField(max_length=6, blank=True, validators=[validate_marks])
    biometric_id = models.CharField(max_length=50, blank=True)
    remarks = models.TextField(blank=True)
    photo = models.ImageField(upload_to='student_photos/', blank=True, null=True)
    academic_year = models.ForeignKey(
        'AcademicYear', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='students'
    )
    # University Admission Flag
    university_admitted = models.BooleanField(default=False, help_text="Has university admission been confirmed?")
    university_receipt_no = models.CharField(max_length=50, help_text="University admission receipt number")
    hostel_registered = models.BooleanField(default=False, help_text="Has hostel registration been done?")
    hostel_receipt_no = models.CharField(max_length=50, help_text="Hostel registration receipt number")
    hostel_approved = models.BooleanField(default=False, help_text="Approved for hostel admission")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.aadhar})"

    @property
    def merit_score(self):
        """
        Merit rank logic:
        - If student has UG marks → rank by UG %
        - Else if student gave CET → rank by CET percentage (obtained/total * 100)
        - Else → rank by 12th marks
        """
        # Priority 1: UG marks (student completed UG)
        if self.marks_ug:
            try:
                return round(float(self.marks_ug), 2)
            except ValueError:
                pass
        # Priority 2: CET marks (student gave CET exam)
        if self.cet_marks_obtained and self.cet_marks_total:
            try:
                obtained = float(self.cet_marks_obtained)
                total = float(self.cet_marks_total)
                if total > 0:
                    return round((obtained / total) * 100, 2)
            except ValueError:
                pass
        # Priority 3: 12th marks (fresh after 12th, for UG admission)
        if self.marks_12:
            try:
                return round(float(self.marks_12), 2)
            except ValueError:
                pass
        return 0.0

    @property
    def merit_basis(self):
        """Returns the basis used for merit scoring."""
        if self.marks_ug:
            try:
                float(self.marks_ug)
                return 'UG Marks'
            except ValueError:
                pass
        if self.cet_marks_obtained and self.cet_marks_total:
            try:
                float(self.cet_marks_obtained)
                float(self.cet_marks_total)
                return 'CET Marks'
            except ValueError:
                pass
        if self.marks_12:
            try:
                float(self.marks_12)
                return '12th Marks'
            except ValueError:
                pass
        return 'N/A'

    class Meta:
        ordering = ['-created_at']


class StudentDocument(models.Model):
    DOC_TYPE_CHOICES = [
        ('marksheet_10', '10th Marksheet'),
        ('marksheet_12', '12th Marksheet'),
        ('ug_marksheet', 'UG Marksheet'),
        ('income_certificate', 'Income Certificate'),
        ('caste_certificate', 'Caste Certificate'),
        ('aadhar_card', 'Aadhaar Card'),
        ('domicile_certificate', 'Domicile Certificate'),
        ('nationality_certificate', 'Nationality Certificate'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='documents')
    doc_type = models.CharField(max_length=30, choices=DOC_TYPE_CHOICES)
    file = models.FileField(upload_to='student_documents/')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='submitted')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    remarks = models.CharField(max_length=300, blank=True)

    def __str__(self):
        return f"{self.student.name} - {self.get_doc_type_display()}"

    def filename(self):
        return self.file.name.split('/')[-1] if self.file else ''

    class Meta:
        unique_together = ('student', 'doc_type')
        ordering = ['doc_type']


class Complaint(models.Model):
    PRIORITY_CHOICES = [('Normal','Normal'),('High','High'),('Urgent','Urgent')]
    STATUS_CHOICES_C = [('Open','Open'),('In Progress','In Progress'),('Resolved','Resolved')]
    TYPE_CHOICES = [('Property Damage','Property Damage'),('Maintenance','Maintenance'),('Electrical','Electrical'),('Plumbing','Plumbing'),('Other','Other')]

    student = models.ForeignKey(Student, on_delete=models.SET_NULL, null=True, blank=True)
    student_name = models.CharField(max_length=200)
    room = models.CharField(max_length=20, blank=True)
    hostel = models.CharField(max_length=50, blank=True)
    title = models.CharField(max_length=300)
    complaint_type = models.CharField(max_length=30, choices=TYPE_CHOICES, default='Property Damage')
    description = models.TextField(blank=True)
    damage_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, blank=True, null=True)
    damage_date = models.DateField(null=True, blank=True)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='Normal')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES_C, default='Open')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.student_name}"

    class Meta:
        ordering = ['-created_at']


class Leave(models.Model):
    STATUS_CHOICES_L = [('Pending','Pending'),('Approved','Approved'),('Rejected','Rejected')]

    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    from_date = models.DateField()
    to_date = models.DateField()
    reason = models.TextField()
    destination = models.CharField(max_length=300, blank=True)
    contact_during_leave = models.CharField(max_length=10, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES_L, default='Pending')
    applied_at = models.DateTimeField(auto_now_add=True)
    remarks = models.CharField(max_length=300, blank=True)
    certificate = models.FileField(upload_to='leave_certificates/', blank=True, null=True)

    def __str__(self):
        return f"{self.student.name} leave {self.from_date} to {self.to_date}"

    class Meta:
        ordering = ['-applied_at']
