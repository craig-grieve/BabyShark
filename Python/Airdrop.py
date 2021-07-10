import requests
from telethon import TelegramClient, sync
import time
import os
from dotenv import load_dotenv
import csv
BASEDIR = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(BASEDIR, '.env'))

# Sharky P, Bone Shark want's to be notified

class CSV:
    FILENAME = ''

    def __init__(self, filename, data):
        self.FILENAME = filename
        self._write(data)

    def _write(self, data):
        with open(self.FILENAME, 'a+', newline='') as fd:
            writer=csv.writer(fd)
            for item in data:
                writer.writerow(item)
            print('Writing {}'.format(len(data)))
            fd.close()



class Twitter:
    # API Rate limit: 1 per minute (15 in 15 mins)
    # https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/follow-search-get-users/api-reference/get-followers-list

    TARGET = 'BabySharkToken'
    BEARER = os.getenv('TWITTER_BEARER_TOKEN')
    FOLLOWERS_NEXT_CURSOR = '-1'  # Starts with -1 to get the first NEXT Cursor value which is provided after the first run
    RETWEET_NEXT_CURSOR = '-1'
    RUNS = 0
    RETWEET_RUNS = 0
    TWEET_ID = ''


    def __init__(self, followers, retweets, tweet_id):
        print('Twitter Init')
        self.RUNS = int(1 + (followers / 200)) # To not get caught out by the rate limit
        self.RETWEET_RUNS = int(1 + (retweets / 100)) # To not get caught out by the rate limit
        self.TWEET_ID = tweet_id
        print('Will run for {} minutes'.format(self.RUNS))
        self._loop()


    def create_headers(self):
        headers = {"Authorization": "Bearer {}".format(self.BEARER)}
        # print(headers)

        return headers


    def _request_followers(self):
        # Example: https://github.com/twitterdev/Twitter-API-v2-sample-code/blob/master/Recent-Search/recent_search.py

        endpoint = 'https://api.twitter.com/1.1/followers/list.json?cursor=' + str(self.FOLLOWERS_NEXT_CURSOR) + '&screen_name=' + self.TARGET + '&skip_status=true&include_user_entities=false&count=200'
        r = requests.request("GET", endpoint, headers=self.create_headers())

        if r.status_code != 200:
            raise Exception(r.status_code, r.text)
        else:
            jsn = r.json()

            self.FOLLOWERS_NEXT_CURSOR = jsn['next_cursor']

            # print(jsn['users'])
            # print(jsn['next_cursor'])
            # print(r.json())
            return jsn

    def _request_retweets(self):
        endpoint = 'https://api.twitter.com/1.1/statuses/retweeters/ids.json?cursor=' + str(self.RETWEET_NEXT_CURSOR) + '&id=' + self.TWEET_ID + '&count=100&stringify_ids=true'
        print(endpoint)
        r = requests.request("GET", endpoint, headers=self.create_headers())

        if r.status_code != 200:
            raise Exception(r.status_code, r.text)
        else:
            jsn = r.json()

            self.RETWEET_NEXT_CURSOR = jsn['next_cursor']

            # print(jsn['users'])
            # print(jsn['next_cursor'])
            # print(r.json())
            return jsn



    def _get_followers(self, users):
        # Retrives the users from the json object and outputs the screen_name to an array
        output = []
        for user in users['users']:
            output.append([user['screen_name'], user['id']])
            # print("user['screen_name']")

        #print(len(output))

        # SAVE to CSV
        print('Writing Followers')
        CSV(os.path.join(BASEDIR, 'data/twitter_users.csv'), output)

        return output


    def _get_retweets(self, users):
        output = []

        for user in users['ids']:
            output.append([user])
            # print("user['screen_name']")

        print('Writing Retweet Ids')
        CSV(os.path.join(BASEDIR, 'data/twitter_tweet_{}.csv'.format(self.TWEET_ID)), output)



    def _loop(self):
        print('Starting Twitter Loop')

        for _ in range(self.RUNS):
            req = self._request_followers()
            self._get_followers(req)

            time.sleep(60)

        for _ in range(self.RETWEET_RUNS):
            req = self._request_retweets()
            self._get_retweets(req)

            time.sleep(15)

        print('Ending Twitter Loop')



class Telegram:
    API_ID = os.getenv('TELEGRAM_API_ID')
    API_HASH = os.getenv('TELEGRAM_API_HASH')
    TARGET = 'BabySharkToken'
    CLIENT = ""

    def __init__(self):
        print('Telegram Init')
        self.CLIENT = TelegramClient('TGSession', self.API_ID, self.API_HASH).start()
        channels = self._get_channels()

        users = self._get_users(channels[self.TARGET])



    def _get_channels(self):

        channels = {d.entity.username: d.entity
                    for d in self.CLIENT.get_dialogs()
                    if d.is_channel}

        return channels

    def _get_users(self, channel):
        # get all the users and print them
        users = []
        for u in self.CLIENT.get_participants(channel):
            users.append([u.username])

            # print(u)
            # print(u.id, u.first_name, u.last_name, u.username)

        print(len(users))
        CSV(os.path.join(BASEDIR, 'data/telegram_users.csv'), output)

        # print(users[1:10])


# Add follower count, retweet count and tweet id

Twitter(200, 200, '1409573612441505796') # Provide the number of twitter followers to run for
Telegram()
