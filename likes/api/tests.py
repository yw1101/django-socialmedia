from testing.testcases import TestCase
from rest_framework.test import APIClient


LIKE_BASE_URL = '/api/likes/'
LIKE_CANCEL_URL = '/api/likes/cancel/'
COMMENT_LIST_API = '/api/comments/'
TWEET_LIST_API = '/api/tweets/'
TWEET_DETAIL_API = '/api/tweets/{}/'
NEWSFEED_LIST_API = '/api/newsfeeds/'


class LikeApiTests(TestCase):

    def setUp(self):
        self.clear_cache()
        self.kellynim, self.kellynim_client = self.create_user_and_client('kellynim')
        self.talenti, self.talenti_client = self.create_user_and_client('talenti')

    def test_tweet_likes(self):
        tweet = self.create_tweet(self.kellynim)
        data = {'content_type': 'tweet', 'object_id': tweet.id}

        # anonymous is not allowed
        response = self.anonymous_client.post(LIKE_BASE_URL, data)
        self.assertEqual(response.status_code, 403)

        # get is not allowed
        response = self.kellynim_client.get(LIKE_BASE_URL, data)
        self.assertEqual(response.status_code, 405)

        # wrong content_type
        response = self.kellynim_client.post(LIKE_BASE_URL, {
            'content_type': 'twitter',
            'object_id': tweet.id,
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual('content_type' in response.data['errors'], True)

        # wrong object_id
        response = self.kellynim_client.post(LIKE_BASE_URL, {
            'content_type': 'tweet',
            'object_id': -1,
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual('object_id'in response.data['errors'], True)


        # post success
        response = self.kellynim_client.post(LIKE_BASE_URL, data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(tweet.like_set.count(), 1)

        # duplicate likes
        self.kellynim_client.post(LIKE_BASE_URL, data)
        self.assertEqual(tweet.like_set.count(), 1)
        self.talenti_client.post(LIKE_BASE_URL, data)
        self.assertEqual(tweet.like_set.count(), 2)

    def test_comment_likes(self):
        tweet = self.create_tweet(self.kellynim)
        comment = self.create_comment(self.talenti, tweet)
        data = {'content_type': 'comment', 'object_id': comment.id}

        # anonymous is not allowed
        response = self.anonymous_client.post(LIKE_BASE_URL, data)
        self.assertEqual(response.status_code, 403)

        # get is not allowed
        response = self.kellynim_client.get(LIKE_BASE_URL, data)
        self.assertEqual(response.status_code, 405)

        # wrong content_type
        response = self.kellynim_client.post(LIKE_BASE_URL, {
            'content_type': 'coment',
            'object_id': comment.id,
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual('content_type' in response.data['errors'], True)

        # wrong object_id
        response = self.kellynim_client.post(LIKE_BASE_URL, {
            'content_type': 'comment',
            'object_id': -1,
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual('object_id'in response.data['errors'], True)

        # post success
        response = self.kellynim_client.post(LIKE_BASE_URL, data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(comment.like_set.count(), 1)

        # duplicate likes
        response = self.kellynim_client.post(LIKE_BASE_URL, data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(comment.like_set.count(), 1)
        self.talenti_client.post(LIKE_BASE_URL, data)
        self.assertEqual(comment.like_set.count(), 2)

    def test_cancel(self):
        tweet = self.create_tweet(self.kellynim)
        comment = self.create_comment(self.talenti, tweet)
        like_comment_data = {'content_type': 'comment', 'object_id': comment.id}
        like_tweet_data = {'content_type': 'tweet', 'object_id': tweet.id}
        self.kellynim_client.post(LIKE_BASE_URL, like_comment_data)
        self.talenti_client.post(LIKE_BASE_URL, like_tweet_data)
        self.assertEqual(tweet.like_set.count(), 1)
        self.assertEqual(comment.like_set.count(), 1)

        response = self.anonymous_client.post(LIKE_CANCEL_URL, like_comment_data)
        self.assertEqual(response.status_code, 403)

        response = self.kellynim_client.get(LIKE_CANCEL_URL, like_comment_data)
        self.assertEqual(response.status_code, 405)

        response = self.kellynim_client.post(LIKE_CANCEL_URL, {
            'content_type': 'wrong',
            'object_id': 1,
        })
        self.assertEqual(response.status_code, 400)

        response = self.kellynim_client.post(LIKE_CANCEL_URL, {
            'content_type': 'comment',
            'object_id': -1,
        })
        self.assertEqual(response.status_code, 400)

        response = self.talenti_client.post(LIKE_CANCEL_URL, like_comment_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['deleted'], 0)
        self.assertEqual(tweet.like_set.count(), 1)
        self.assertEqual(comment.like_set.count(), 1)

        response = self.kellynim_client.post(LIKE_CANCEL_URL, like_comment_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['deleted'], 1)
        self.assertEqual(tweet.like_set.count(), 1)
        self.assertEqual(comment.like_set.count(), 0)

        response = self.kellynim_client.post(LIKE_CANCEL_URL, like_tweet_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['deleted'], 0)
        self.assertEqual(tweet.like_set.count(), 1)
        self.assertEqual(comment.like_set.count(), 0)

        response = self.talenti_client.post(LIKE_CANCEL_URL, like_tweet_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['deleted'], 1)
        self.assertEqual(tweet.like_set.count(), 0)
        self.assertEqual(comment.like_set.count(), 0)

    def test_likes_in_comments_api(self):
        tweet = self.create_tweet(self.kellynim)
        comment = self.create_comment(self.kellynim, tweet)

        # test anonymous
        anonymous_client = APIClient()
        response = anonymous_client.get(COMMENT_LIST_API, {'tweet_id': tweet.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['comments'][0]['has_liked'], False)
        self.assertEqual(response.data['comments'][0]['likes_count'], 0)

        # test comments list api
        response = self.talenti_client.get(COMMENT_LIST_API, {'tweet_id': tweet.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['comments'][0]['has_liked'], False)
        self.assertEqual(response.data['comments'][0]['likes_count'], 0)
        self.create_like(self.talenti, comment)
        response = self.talenti_client.get(COMMENT_LIST_API, {'tweet_id': tweet.id})
        self.assertEqual(response.data['comments'][0]['has_liked'], True)
        self.assertEqual(response.data['comments'][0]['likes_count'], 1)

        # test tweet detail api
        self.create_like(self.kellynim, comment)
        url = TWEET_DETAIL_API.format(tweet.id)
        response = self.talenti_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['comments'][0]['has_liked'], True)
        self.assertEqual(response.data['comments'][0]['likes_count'], 2)

    def test_likes_in_tweets_api(self):
        tweet = self.create_tweet(self.kellynim)

        # test tweet detail api
        url = TWEET_DETAIL_API.format(tweet.id)
        response = self.talenti_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['has_liked'], False)
        self.assertEqual(response.data['likes_count'], 0)
        self.create_like(self.talenti, tweet)
        response = self.talenti_client.get(url)
        self.assertEqual(response.data['has_liked'], True)
        self.assertEqual(response.data['likes_count'], 1)

        # test tweets list api
        response = self.talenti_client.get(TWEET_LIST_API, {'user_id': self.kellynim.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['results'][0]['has_liked'], True)
        self.assertEqual(response.data['results'][0]['likes_count'], 1)

        # test newsfeeds list api
        self.create_like(self.kellynim, tweet)
        self.create_newsfeed(self.talenti, tweet)
        response = self.talenti_client.get(NEWSFEED_LIST_API)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['results'][0]['tweet']['has_liked'], True)
        self.assertEqual(response.data['results'][0]['tweet']['likes_count'], 2)

        # test likes details
        url = TWEET_DETAIL_API.format(tweet.id)
        response = self.talenti_client.get(url)
        self.assertEqual(len(response.data['likes']), 2)
        self.assertEqual(response.data['likes'][0]['user']['id'], self.kellynim.id)
        self.assertEqual(response.data['likes'][1]['user']['id'], self.talenti.id)

    def test_likes_count_with_cache(self):
        tweet = self.create_tweet(self.kellynim)
        self.create_newsfeed(self.kellynim, tweet)
        self.create_newsfeed(self.talenti, tweet)

        data = {'content_type': 'tweet', 'object_id': tweet.id}
        tweet_url = TWEET_DETAIL_API.format(tweet.id)
        for i in range(3):
            _, client = self.create_user_and_client('someone{}'.format(i))
            client.post(LIKE_BASE_URL, data)
            # check tweet api
            response = client.get(tweet_url)
            self.assertEqual(response.data['likes_count'], i + 1)
            tweet.refresh_from_db()
            self.assertEqual(tweet.likes_count, i + 1)

        self.talenti_client.post(LIKE_BASE_URL, data)
        response = self.talenti_client.get(tweet_url)
        self.assertEqual(response.data['likes_count'], 4)
        tweet.refresh_from_db()
        self.assertEqual(tweet.likes_count, 4)

        # check newsfeed api
        newsfeed_url = '/api/newsfeeds/'
        response = self.kellynim_client.get(newsfeed_url)
        self.assertEqual(response.data['results'][0]['tweet']['likes_count'], 4)
        response = self.talenti_client.get(newsfeed_url)
        self.assertEqual(response.data['results'][0]['tweet']['likes_count'], 4)

        # talenti canceled likes
        self.talenti_client.post(LIKE_BASE_URL + 'cancel/', data)
        tweet.refresh_from_db()
        self.assertEqual(tweet.likes_count, 3)
        response = self.talenti_client.get(tweet_url)
        self.assertEqual(response.data['likes_count'], 3)
        response = self.kellynim_client.get(newsfeed_url)
        self.assertEqual(response.data['results'][0]['tweet']['likes_count'], 3)
        response = self.talenti_client.get(newsfeed_url)
        self.assertEqual(response.data['results'][0]['tweet']['likes_count'], 3)
