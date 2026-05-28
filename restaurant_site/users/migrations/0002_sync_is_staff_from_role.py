from django.db import migrations


def sync_is_staff_from_role(apps, schema_editor):
    User = apps.get_model('users', 'User')
    for user in User.objects.all():
        if user.is_superuser:
            continue
        expected = user.role in ('staff', 'admin')
        if user.is_staff != expected:
            user.is_staff = expected
            user.save(update_fields=['is_staff'])


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(sync_is_staff_from_role, migrations.RunPython.noop),
    ]
