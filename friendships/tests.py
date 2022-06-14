from friendships.models import Friendship
from friendships.services import FriendshipService
from testing.testcases import TestCase


class FriendshipServiceTests(TestCase):

    def setUp(self):
        self.clear_cache()
        self.kellynim = self.create_user('kellynim')
        self.talenti = self.create_user('talenti')

    def test_get_followings(self):
        user1 = self.create_user('user1')
        user2 = self.create_user('user2')
        for to_user in [user1, user2, self.talenti]:
            Friendship.objects.create(from_user = self.kellynim, to_user = to_user)

        user_id_set = FriendshipService.get_following_user_id_set(self.kellynim.id)
        self.assertSetEqual(user_id_set, {user1.id, user2.id, self.talenti.id})

        Friendship.objects.filter(from_user = self.kellynim, to_user = self.talenti).delete()
        user_id_set = FriendshipService.get_following_user_id_set(self.kellynim.id)
        self.assertSetEqual(user_id_set, {user1.id, user2.id})
