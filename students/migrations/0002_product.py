from django.db import migrations, models
from django.core.validators import MinValueValidator


class Migration(migrations.Migration):
    dependencies = [('students', '0001_initial')]

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_name', models.CharField(max_length=150)),
                ('product_no', models.CharField(max_length=50, unique=True)),
                ('price', models.DecimalField(decimal_places=2, max_digits=10, validators=[MinValueValidator(0)])),
                ('qty', models.PositiveIntegerField(default=0)),
            ],
            options={'ordering': ['product_name']},
        ),
    ]