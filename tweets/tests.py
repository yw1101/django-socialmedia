from datetime import timedelta
from utils.time_helpers import utc_now
from testing.testcases import TestCase
from tweets.models import TweetPhoto
from tweets.constants import TweetPhotoStatus
from utils.redis_client import RedisClient
from utils.redis_serializers import DjangoModelSerializer



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

    def test_cache_tweet_in_redis(self):
        tweet = self.create_tweet(self.kellynim)
        conn = RedisClient.get_connection()
        serialized_data = DjangoModelSerializer.serialize(tweet)
        conn.set(f'tweet:{tweet.id}', serialized_data)
        data = conn.get(f'tweet:not_exists')
        self.assertEqual(data, None)

        data = conn.get(f'tweet:{tweet.id}')
        cached_tweet = DjangoModelSerializer.deserialize(data)
        self.assertEqual(tweet, cached_tweet)
