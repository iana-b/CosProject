from django.db import migrations


def publish_existing(apps, schema_editor):
    apps.get_model('cosapp', 'Product').objects.update(status='published')


class Migration(migrations.Migration):

    dependencies = [
        ('cosapp', '0010_product_created_at_product_status_product_user_and_more'),
    ]

    operations = [
        migrations.RunPython(publish_existing, migrations.RunPython.noop),
    ]
