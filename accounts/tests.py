from accounts.models import UserProfile
from testing.testcases import TestCase


class UserProfileTests(TestCase):

    def test_profile_property(self):
        super(UserProfileTests, self).setUp()
        kellynim = self.create_user('kellynim')
        self.assertEqual(UserProfile.objects.count(), 0)
        p = kellynim.profile
        self.assertEqual(isinstance(p, UserProfile), True)
        self.assertEqual(UserProfile.objects.count(), 1)
