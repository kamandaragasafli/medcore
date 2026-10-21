from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('regions', '0005_clinic_address_optional'),
    ]

    operations = [
        migrations.AddField(
            model_name='specialization',
            name='code',
            field=models.CharField(
                blank=True,
                help_text='Qisa kod (mes: TE, GN, NP)',
                max_length=10,
                null=True,
                unique=True,
                verbose_name='Kod',
            ),
        ),
        migrations.AddField(
            model_name='specialization',
            name='description',
            field=models.TextField(blank=True, null=True, verbose_name='Tesvir'),
        ),
    ]
