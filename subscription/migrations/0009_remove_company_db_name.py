# Generated manually for single-DB deployment

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subscription', '0008_backup_backupsettings'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='company',
            name='db_name',
        ),
        migrations.AlterField(
            model_name='company',
            name='tax_number',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='VOEN'),
        ),
    ]
