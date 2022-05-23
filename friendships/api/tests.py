from friendships.models import Friendship
from rest_framework.test import APIClient
from testing.testcases import TestCase


FOLLOW_URL = '/api/friendships/{}/follow/'
UNFOLLOW_URL = '/api/friendships/{}/unfollow/'
FOLLOWERS_URL = '/api/friendships/{}/followers/'
FOLLOWINGS_URL = '/api/friendships/{}/followings/'


class FriendshipApiTests(TestCase):

    def setUp(self):
        self.anonymous_client = APIClient()

        self.kellynim = self.create_user('kellynim')
        self.kellynim_client = APIClient()
        self.kellynim_client.force_authenticate(self.kellynim)

        self.talenti = self.create_user('talenti')
        self.talenti_client = APIClient()
        self.talenti_client.force_authenticate(self.talenti)

        # create followings and followers for talenti
        for i in range(2):
            follower = self.create_user('talenti_follower{}'.format(i))
            Friendship.objects.create(from_user=follower, to_user=self.talenti)
        for i in range(3):
            following = self.create_user('talenti_following{}'.format(i))
            Friendship.objects.create(from_user=self.talenti, to_user=following)

    def test_follow(self):
        url = FOLLOW_URL.format(self.kellynim.id)


        response = self.anonymous_client.post(url)
        self.assertEqual(response.status_code, 403)

        response = self.talenti_client.get(url)
        self.assertEqual(response.status_code, 405)

        response = self.kellynim_client.post(url)
        self.assertEqual(response.status_code, 400)

        response = self.talenti_client.post(url)
        self.assertEqual(response.status_code, 201)

        response = self.talenti_client.post(url)
        self.assertEqual(response.status_code, 400)

        count = Friendship.objects.count()
        response = self.kellynim_client.post(FOLLOW_URL.format(self.talenti.id))
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Friendship.objects.count(), count + 1)

    def test_unfollow(self):
        url = UNFOLLOW_URL.format(self.kellynim.id)


        response = self.anonymous_client.post(url)
        self.assertEqual(response.status_code, 403)

        response = self.talenti_client.get(url)
        self.assertEqual(response.status_code, 405)

        response = self.kellynim_client.post(url)
        self.assertEqual(response.status_code, 400)

        Friendship.objects.create(from_user=self.talenti, to_user=self.kellynim)
        count = Friendship.objects.count()
        response = self.talenti_client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['deleted'], 1)
        self.assertEqual(Friendship.objects.count(), count - 1)

        count = Friendship.objects.count()
        response = self.talenti_client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['deleted'], 0)
        self.assertEqual(Friendship.objects.count(), count)

    def test_followings(self):
        url = FOLLOWINGS_URL.format(self.talenti.id)

        response = self.anonymous_client.post(url)
        self.assertEqual(response.status_code, 405)
        # get is ok
        response = self.anonymous_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['followings']), 3)

        ts0 = response.data['followings'][0]['created_at']
        ts1 = response.data['followings'][1]['created_at']
        ts2 = response.data['followings'][2]['created_at']
        self.assertEqual(ts0 > ts1, True)
        self.assertEqual(ts1 > ts2, True)
        self.assertEqual(
            response.data['followings'][0]['user']['username'],
            'talenti_following2',
        )
        self.assertEqual(
            response.data['followings'][1]['user']['username'],
            'talenti_following1',
        )
        self.assertEqual(
            response.data['followings'][2]['user']['username'],
            'talenti_following0',
        )

    def test_followers(self):
        url = FOLLOWERS_URL.format(self.talenti.id)
        # post is not allowed
        response = self.anonymous_client.post(url)
        self.assertEqual(response.status_code, 405)
        # get is ok
        response = self.anonymous_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['followers']), 2)

        ts0 = response.data['followers'][0]['created_at']
        ts1 = response.data['followers'][1]['created_at']
        self.assertEqual(ts0 > ts1, True)
        self.assertEqual(
            response.data['followers'][0]['user']['username'],
            'talenti_follower1',
        )
        self.assertEqual(
            response.data['followers'][1]['user']['username'],
            'talenti_follower0',
        )
