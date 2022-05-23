from newsfeeds.models import NewsFeed
from friendships.models import Friendship
from rest_framework.test import APIClient
from testing.testcases import TestCase


NEWSFEEDS_URL = '/api/newsfeeds/'
POST_TWEETS_URL = '/api/tweets/'
FOLLOW_URL = '/api/friendships/{}/follow/'


class NewsFeedApiTests(TestCase):

    def setUp(self):
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

    def test_list(self):

        response = self.anonymous_client.get(NEWSFEEDS_URL)
        self.assertEqual(response.status_code, 403)

        response = self.kellynim_client.post(NEWSFEEDS_URL)
        self.assertEqual(response.status_code, 405)

        response = self.kellynim_client.get(NEWSFEEDS_URL)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['newsfeeds']), 0)

        self.kellynim_client.post(POST_TWEETS_URL, {'content': 'Hello World'})
        response = self.kellynim_client.get(NEWSFEEDS_URL)
        self.assertEqual(len(response.data['newsfeeds']), 1)

        self.kellynim_client.post(FOLLOW_URL.format(self.talenti.id))
        response = self.talenti_client.post(POST_TWEETS_URL, {
            'content': 'Hello Twitter',
        })
        posted_tweet_id = response.data['id']
        response = self.kellynim_client.get(NEWSFEEDS_URL)
        self.assertEqual(len(response.data['newsfeeds']), 2)
        self.assertEqual(response.data['newsfeeds'][0]['tweet']['id'], posted_tweet_id)
