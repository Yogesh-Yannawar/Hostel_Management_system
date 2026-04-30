from django.db import migrations, models
import hostel.models


class Migration(migrations.Migration):

    dependencies = [
        ('hostel', '0005_alter_leave_contact_during_leave_and_more'),
    ]

    operations = [
        # Add CET marks obtained field
        migrations.AddField(
            model_name='student',
            name='cet_marks_obtained',
            field=models.CharField(
                blank=True, max_length=6,
                validators=[hostel.models.validate_marks],
                help_text='CET marks obtained'
            ),
        ),
        # Add CET marks total field
        migrations.AddField(
            model_name='student',
            name='cet_marks_total',
            field=models.CharField(
                blank=True, max_length=6,
                validators=[hostel.models.validate_marks],
                help_text='CET total marks'
            ),
        ),
        # Make university_receipt_no compulsory (remove blank=True), provide default
        migrations.AlterField(
            model_name='student',
            name='university_receipt_no',
            field=models.CharField(
                max_length=50,
                default='',
                help_text='University admission receipt number'
            ),
            preserve_default=False,
        ),
        # Make hostel_receipt_no compulsory (remove blank=True), provide default
        migrations.AlterField(
            model_name='student',
            name='hostel_receipt_no',
            field=models.CharField(
                max_length=50,
                default='',
                help_text='Hostel registration receipt number'
            ),
            preserve_default=False,
        ),
        # Allow hostel to be blank — filled later via Hostel Details step
        migrations.AlterField(
            model_name='student',
            name='hostel',
            field=models.CharField(
                max_length=50,
                blank=True,
                default='',
                choices=[
                    ('Boys Hostel 1','Boys Hostel 1'),
                    ('Boys Hostel 2','Boys Hostel 2'),
                    ('Boys Hostel 3','Boys Hostel 3'),
                    ('Boys Hostel 4','Boys Hostel 4'),
                ]
            ),
        ),
    ]
