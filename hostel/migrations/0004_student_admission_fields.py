from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('hostel', '0003_academicyear_features'),
    ]
    operations = [
        migrations.AddField(
            model_name='student',
            name='university_admitted',
            field=models.BooleanField(default=False, help_text='Has university admission been confirmed?'),
        ),
        migrations.AddField(
            model_name='student',
            name='university_receipt_no',
            field=models.CharField(blank=True, max_length=50, help_text='University admission receipt number'),
        ),
        migrations.AddField(
            model_name='student',
            name='hostel_registered',
            field=models.BooleanField(default=False, help_text='Has hostel registration been done?'),
        ),
        migrations.AddField(
            model_name='student',
            name='hostel_receipt_no',
            field=models.CharField(blank=True, max_length=50, help_text='Hostel registration receipt number'),
        ),
        migrations.AddField(
            model_name='student',
            name='hostel_approved',
            field=models.BooleanField(default=False, help_text='Approved for hostel admission'),
        ),
        migrations.AlterField(
            model_name='student',
            name='phone',
            field=models.CharField(max_length=10),
        ),
    ]
