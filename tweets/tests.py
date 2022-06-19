from datetime import timedelta
from utils.time_helpers import utc_now
from testing.testcases import TestCase
from tweets.models import TweetPhoto
from tweets.constants import TweetPhotoStatus


class TweetTests(TestCase):

    def setUp(self):
        self.clear_cache()
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

    def test_create_photo(self):
        photo = TweetPhoto.objects.create(
            tweet = self.tweet,
            user = self.kellynim,
        )
        self.assertEqual(photo.user, self.kellynim)
        self.assertEqual(photo.status, TweetPhotoStatus.PENDING)
        self.assertEqual(self.tweet.tweetphoto_set.count(), 1)
