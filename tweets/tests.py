from datetime import timedelta
from utils.time_helpers import utc_now
from testing.testcases import TestCase


class TweetTests(TestCase):

    def setUp(self):
        self.kellynim = self.create_user('kellynim')
        self.tweet = self.create_tweet(
            self.kellynim,
            content = 'Have a nice day.'
        )

    def test_hours_to_now(self):
        self.tweet.created_at = utc_now() - timedelta(hours = 10)
        self.tweet.save()
        self.assertEqual(self.tweet.hours_to_now, 10)

    def test_like_set(self):
        self.create_like(self.kellynim, self.tweet)
        self.assertEqual(self.tweet.like_set.count(), 1)

        self.create_like(self.kellynim, self.tweet)
        self.assertEqual(self.tweet.like_set.count(), 1)

        talenti = self.create_user('talenti')
        self.create_like(talenti, self.tweet)
        self.assertEqual(self.tweet.like_set.count(), 2)

        
