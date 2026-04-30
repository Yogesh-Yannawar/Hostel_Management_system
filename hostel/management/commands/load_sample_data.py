from django.core.management.base import BaseCommand
from hostel.models import Student, Complaint

STUDENTS = [
    dict(name="Rahul Sharma", aadhar="123456789012", gender="Male", category="OBC", phone="9876543210", email="rahul@email.com",
         father_name="Suresh Sharma", mother_name="Sunita Sharma", guardian_phone="9876543211",
         school="School of Computational Sciences", level="UG", course="B.Sc. Computer Science", year="2nd Year",
         hostel="Boys Hostel 1", room="G-01", address="Nanded, Maharashtra", district="Nanded",
         fees="Paid", fee_amount=3200, marks_10="88", marks_12="82", biometric_id="BIO001", remarks="Merit student"),
    dict(name="Amit Patil", aadhar="234567890123", gender="Male", category="SC", phone="9765432109", email="amit@email.com",
         father_name="Vikas Patil", mother_name="Rekha Patil", guardian_phone="9765432108",
         school="School of Social Sciences", level="UG", course="B.A. Sociology", year="1st Year",
         hostel="Boys Hostel 2", room="G-61", address="Latur, Maharashtra", district="Latur",
         fees="Pending", fee_amount=0, marks_10="75", marks_12="71", biometric_id="BIO002"),
    dict(name="Sunil Jadhav", aadhar="345678901234", gender="Male", category="ST", phone="9654321098", email="sunil@email.com",
         father_name="Kiran Jadhav", mother_name="Lata Jadhav", guardian_phone="9654321097",
         school="School of Commerce and Management Sciences", level="PG", course="MBA", year="1st Year",
         hostel="Boys Hostel 1", room="F-001", address="Osmanabad, Maharashtra", district="Osmanabad",
         fees="Partial", fee_amount=1600, marks_10="79", marks_12="76", marks_ug="68", biometric_id="BIO003"),
    dict(name="Prashant Deshmukh", aadhar="456789012345", gender="Male", category="General", phone="9543210987",
         father_name="Anil Deshmukh", mother_name="Seema Deshmukh", guardian_phone="9543210986",
         school="School of Technology", level="UG", course="B.E. Computer", year="3rd Year",
         hostel="Boys Hostel 3", room="G-01", address="Aurangabad, Maharashtra", district="Aurangabad",
         fees="Paid", fee_amount=3700, marks_10="92", marks_12="89", biometric_id="BIO004", remarks="Sports captain"),
    dict(name="Kiran More", aadhar="567890123456", gender="Male", category="VJNT", phone="9432109876",
         father_name="Balu More", mother_name="Pushpa More", guardian_phone="9432109875",
         school="School of Mathematical Sciences", level="PG", course="M.Sc. Mathematics", year="2nd Year",
         hostel="Boys Hostel 4", room="G-01", address="Hingoli, Maharashtra", district="Hingoli",
         fees="Paid", fee_amount=3200, marks_10="85", marks_12="83", marks_ug="74", biometric_id="BIO005"),
]

class Command(BaseCommand):
    help = 'Load sample data'

    def handle(self, *args, **kwargs):
        if Student.objects.exists():
            self.stdout.write('Sample data already loaded.')
            return
        for s in STUDENTS:
            Student.objects.create(**s)
        s1 = Student.objects.first()
        s3 = Student.objects.filter(name="Sunil Jadhav").first()
        if s1:
            Complaint.objects.create(student=s1, student_name=s1.name, room=s1.room, hostel=s1.hostel,
                title="Window glass broken", complaint_type="Property Damage",
                description="Window glass in room G-01 was accidentally broken.",
                damage_amount=500, priority="High", status="Open")
        if s3:
            Complaint.objects.create(student=s3, student_name=s3.name, room=s3.room, hostel=s3.hostel,
                title="Ceiling fan damaged", complaint_type="Property Damage",
                description="Ceiling fan blade broke. Needs replacement.",
                damage_amount=800, priority="Normal", status="In Progress")
        self.stdout.write(self.style.SUCCESS(f'Loaded {len(STUDENTS)} students and 2 complaints.'))
