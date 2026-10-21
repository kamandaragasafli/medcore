from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('regions', '0006_specialization_code_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='specialization',
            name='code',
            field=models.CharField(
                blank=True,
                help_text='Qisa kod (mes: TE, GN, CA, SU)',
                max_length=20,
                null=True,
                unique=True,
                verbose_name='Kod',
            ),
        ),
    ]
