from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hostel', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='receipt_number',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AlterField(
            model_name='complaint',
            name='description',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='complaint',
            name='damage_amount',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=10, null=True),
        ),
    ]
