from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('hostel', '0002_student_receipt_number_complaint_optional'),
    ]

    operations = [
        migrations.CreateModel(
            name='AcademicYear',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(help_text='e.g. 2025-2026', max_length=20, unique=True)),
                ('start_year', models.IntegerField()),
                ('end_year', models.IntegerField()),
                ('is_current', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={'ordering': ['-start_year']},
        ),
        migrations.AddField(
            model_name='student',
            name='academic_year',
            field=models.ForeignKey(
                blank=True, null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='students',
                to='hostel.academicyear',
            ),
        ),
        migrations.AddField(
            model_name='leave',
            name='certificate',
            field=models.FileField(blank=True, null=True, upload_to='leave_certificates/'),
        ),
    ]
