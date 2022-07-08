from friendships.models import Friendship
from rest_framework.test import APIClient
from testing.testcases import TestCase
from friendships.api.paginations import FriendshipPagination
from friendships.services import FriendshipService
from utils.paginations import EndlessPagination


FOLLOW_URL = '/api/friendships/{}/follow/'
UNFOLLOW_URL = '/api/friendships/{}/unfollow/'
FOLLOWERS_URL = '/api/friendships/{}/followers/'
FOLLOWINGS_URL = '/api/friendships/{}/followings/'


class FriendshipApiTests(TestCase):

    def setUp(self):
        super(FriendshipApiTests, self).setUp()
        self.kellynim = self.create_user('kellynim')
        self.kellynim_client = APIClient()
        self.kellynim_client.force_authenticate(self.kellynim)

        self.talenti = self.create_user('talenti')
        self.talenti_client = APIClient()
        self.talenti_client.force_authenticate(self.talenti)

        # create followings and followers for talenti
        for i in range(2):
            follower = self.create_user('talenti_follower{}'.format(i))
            self.create_friendship(follower, self.talenti)
        for i in range(3):
            following = self.create_user('talenti_following{}'.format(i))
            self.create_friendship(self.talenti, following)

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

        before_count = FriendshipService.get_following_count(self.kellynim.id)
        response = self.kellynim_client.post(FOLLOW_URL.format(self.talenti.id))
        self.assertEqual(response.status_code, 201)
        after_count = FriendshipService.get_following_count(self.kellynim.id)
        self.assertEqual(after_count, before_count + 1)

    def test_unfollow(self):
        url = UNFOLLOW_URL.format(self.kellynim.id)


        response = self.anonymous_client.post(url)
        self.assertEqual(response.status_code, 403)

        response = self.talenti_client.get(url)
        self.assertEqual(response.status_code, 405)

        response = self.kellynim_client.post(url)
        self.assertEqual(response.status_code, 400)

        self.create_friendship(self.talenti, self.kellynim)
        before_count = FriendshipService.get_following_count(self.talenti.id)
        response = self.talenti_client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['deleted'], 1)
        after_count = FriendshipService.get_following_count(self.talenti.id)
        self.assertEqual(after_count, before_count - 1)

        before_count = FriendshipService.get_following_count(self.talenti.id)
        response = self.talenti_client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['deleted'], 0)
        after_count = FriendshipService.get_following_count(self.talenti.id)
        self.assertEqual(after_count, before_count)

    def test_followings(self):
        url = FOLLOWINGS_URL.format(self.talenti.id)

        response = self.anonymous_client.post(url)
        self.assertEqual(response.status_code, 405)
        # get is ok
        response = self.anonymous_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 3)

        ts0 = response.data['results'][0]['created_at']
        ts1 = response.data['results'][1]['created_at']
        ts2 = response.data['results'][2]['created_at']
        self.assertEqual(ts0 > ts1, True)
        self.assertEqual(ts1 > ts2, True)
        self.assertEqual(
            response.data['results'][0]['user']['username'],
            'talenti_following2',
        )
        self.assertEqual(
            response.data['results'][1]['user']['username'],
            'talenti_following1',
        )
        self.assertEqual(
            response.data['results'][2]['user']['username'],
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
        self.assertEqual(len(response.data['results']), 2)

        ts0 = response.data['results'][0]['created_at']
        ts1 = response.data['results'][1]['created_at']
        self.assertEqual(ts0 > ts1, True)
        self.assertEqual(
            response.data['results'][0]['user']['username'],
            'talenti_follower1',
        )
        self.assertEqual(
            response.data['results'][1]['user']['username'],
            'talenti_follower0',
        )


    def test_followers_pagination(self):
        page_size = EndlessPagination.page_size
        friendships = []
        for i in range(page_size * 2):
            follower = self.create_user('kellynim_follower{}'.format(i))
            friendship = self.create_friendship(follower, self.kellynim)
            friendships.append(friendship)
            if follower.id % 2 == 0:
                self.create_friendship(self.talenti, follower)

        url = FOLLOWERS_URL.format(self.kellynim.id)
        self._pagination_until_the_end(url, 2, friendships)

        # anonymous hasn't followed any users
        response = self.anonymous_client.get(url)
        for result in response.data['results']:
            self.assertEqual(result['has_followed'], False)

        # talenti has followed users with even id
        response = self.talenti_client.get(url)
        for result in response.data['results']:
            has_followed = (result['user']['id'] % 2 == 0)
            self.assertEqual(result['has_followed'], has_followed)

    def test_followings_pagination(self):
        page_size = EndlessPagination.page_size
        friendships = []
        for i in range(page_size * 2):
            following = self.create_user('kellynim_following{}'.format(i))
            friendship = self.create_friendship(self.kellynim, following)
            friendships.append(friendship)
            if following.id % 2 == 0:
                self.create_friendship(self.talenti, following)

        url = FOLLOWINGS_URL.format(self.kellynim.id)
        self._pagination_until_the_end(url, 2, friendships)

        # anonymous hasn't followed any users
        response = self.anonymous_client.get(url)
        for result in response.data['results']:
            self.assertEqual(result['has_followed'], False)

        # talenti has followed users with even id
        response = self.talenti_client.get(url)
        for result in response.data['results']:
            has_followed = (result['user']['id'] % 2 == 0)
            self.assertEqual(result['has_followed'], has_followed)

        # kellynim has followed all his following users
        response = self.kellynim_client.get(url)
        for result in response.data['results']:
            self.assertEqual(result['has_followed'], True)

        last_created_at = friendships[-1].created_at
        response = self.kellynim_client.get(url, {'created_at__gt': last_created_at})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 0)

        new_friends = [self.create_user('big_v{}'.format(i)) for i in range(3)]
        new_friendships = []
        for friend in new_friends:
            new_friendships.append(self.create_friendship(from_user = self.kellynim, to_user = friend))
        response = self.kellynim_client.get(url, {'created_at__gt': last_created_at})
        self.assertEqual(len(response.data['results']), 3)
        for result, friendship in zip(response.data['results'], reversed(new_friendships)):
            self.assertEqual(result['created_at'], friendship.created_at)



    # def _test_friendship_pagination(self, url, page_size, max_page_size):
    #     response = self.anonymous_client.get(url, {'page': 1})
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(len(response.data['results']), page_size)
    #     self.assertEqual(response.data['total_pages'], 2)
    #     self.assertEqual(response.data['total_results'], page_size * 2)
    #     self.assertEqual(response.data['page_number'], 1)
    #     self.assertEqual(response.data['has_next_page'], True)
    #
    #     response = self.anonymous_client.get(url, {'page': 2})
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(len(response.data['results']), page_size)
    #     self.assertEqual(response.data['total_pages'], 2)
    #     self.assertEqual(response.data['total_results'], page_size * 2)
    #     self.assertEqual(response.data['page_number'], 2)
    #     self.assertEqual(response.data['has_next_page'], False)
    #
    #     response = self.anonymous_client.get(url, {'page': 3})
    #     self.assertEqual(response.status_code, 404)
    #
    #     # test user can not customize page_size exceeds max_page_size
    #     response = self.anonymous_client.get(url, {'page': 1, 'size': max_page_size + 1})
    #     self.assertEqual(len(response.data['results']), max_page_size)
    #     self.assertEqual(response.data['total_pages'], 2)
    #     self.assertEqual(response.data['total_results'], page_size * 2)
    #     self.assertEqual(response.data['page_number'], 1)
    #     self.assertEqual(response.data['has_next_page'], True)
    #
    #     # test user can customize page size by param size
    #     response = self.anonymous_client.get(url, {'page': 1, 'size': 2})
    #     self.assertEqual(len(response.data['results']), 2)
    #     self.assertEqual(response.data['total_pages'], page_size)
    #     self.assertEqual(response.data['total_results'], page_size * 2)
    #     self.assertEqual(response.data['page_number'], 1)
    #     self.assertEqual(response.data['has_next_page'], True)


    def _pagination_until_the_end(self, url, expect_pages, friendships):
        results, pages = [], 0
        response = self.anonymous_client.get(url)
        results.extend(response.data['results'])
        pages += 1
        while response.data['has_next_page']:
            self.assertEqual(response.status_code, 200)
            last_item = response.data['results'][-1]
            response = self.anonymous_client.get(url, {
                'created_at__lt': last_item['created_at'],
            })
            results.extend(response.data['results'])
            pages += 1

        self.assertEqual(len(results), len(friendships))
        self.assertEqual(pages, expect_pages)
        for result, friendship in zip(results, friendships[::-1]):
            self.assertEqual(result['created_at'], friendship.created_at)
