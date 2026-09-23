from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [('students', '0002_product')]

    operations = [migrations.DeleteModel(name='Student')]