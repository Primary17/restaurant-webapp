from django.test import TestCase

from users.models import User


class UserStaffSyncTests(TestCase):
    def test_customer_is_not_staff(self):
        user = User.objects.create_user(
            username='cust',
            password='pass',
            role=User.ROLE_CUSTOMER,
        )
        self.assertFalse(user.is_staff)

    def test_staff_role_sets_is_staff(self):
        user = User.objects.create_user(
            username='staff1',
            password='pass',
            role=User.ROLE_STAFF,
        )
        self.assertTrue(user.is_staff)

    def test_admin_role_sets_is_staff(self):
        user = User.objects.create_user(
            username='admin1',
            password='pass',
            role=User.ROLE_ADMIN,
        )
        self.assertTrue(user.is_staff)

    def test_role_change_updates_is_staff_on_save(self):
        user = User.objects.create_user(
            username='promoted',
            password='pass',
            role=User.ROLE_CUSTOMER,
        )
        user.role = User.ROLE_STAFF
        user.save()
        user.refresh_from_db()
        self.assertTrue(user.is_staff)
