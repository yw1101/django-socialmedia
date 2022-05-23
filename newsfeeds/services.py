from friendships.services import FriendshipService
from newsfeeds.models import NewsFeed

class NewsFeedService(object):

    @classmethod
    def fanout_to_followers(cls, tweet):
        newsfeeds = [
            NewsFeed(user = follower, tweet = tweet)
            for follower in FriendshipService.get_followers(tweet.user)
        ]
        #The user who tweets can see the tweets he/she created
        newsfeeds.append(NewsFeed(user = tweet.user, tweet = tweet))
        NewsFeed.objects.bulk_create(newsfeeds)
