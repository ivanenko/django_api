from random import randrange
import sys
from time import sleep
import requests
import json
import uuid

API_URL = "http://localhost:8000"


def main(config_name):
    with open(config_name) as json_file:
        config = json.load(json_file)

    tokens = []
    post_ids = []

    # create users
    for i in range(0, config['number_of_users']):
        user_name = 'user_{}'.format(uuid.uuid4().hex[:10])
        token = create_user(user_name)
        tokens.append(token)

        # create users posts
        posts_number = randrange(1, config['max_posts_per_user'])
        for j in range(0, posts_number):
            post_id = create_users_post(token)
            post_ids.append(post_id)

    # randomly like posts
    likes_count = 0
    for token in tokens:
        like_number = randrange(0, config['max_likes_per_user'])
        for i in range(1, like_number):
            post_id = post_ids[randrange(0, len(post_ids))]
            if like_post(token, post_id):
                likes_count += 1

    print('users created: {}; total posts: {}; total likes: {}'.format(len(tokens), len(post_ids), likes_count))
    print('you can check likes analytics by url: {}/analytics/?date_from=2020-02-02&date_to=2020-10-25'.format(API_URL))


def create_user(user_name):
    user_data = {
        'username': user_name,
        'email': '{}@mail.ru'.format(user_name),
        'is_staff': False,
        'password': '123'
    }
    r = requests.post(API_URL + '/users/', data=user_data)
    if r.status_code >= 300:
        raise Exception('Error creating user: '+r.text)

    sleep(1)
    headers = {'Content-Type': 'application/json'}
    r = requests.post(API_URL + '/api-token-auth/', json={"username": user_name, "password": "123"}, headers=headers)
    if r.status_code >= 300:
        print(r.text)
        print(r.request.headers)
        print(r.request.body)
        raise Exception('Error getting auth token for user {}'.format(user_name))
    token = r.json()['token']

    print('user {} created with token {}'.format(user_name, token))
    return token


def create_users_post(token):
    post_data = {'text': 'post {}'.format(uuid.uuid4().hex), 'pub_date': '2020-02-02T02:02:00'}
    headers = {'Authorization': 'Token {}'.format(token)}
    r = requests.post(API_URL + '/posts/', data=post_data, headers=headers)
    if r.status_code >= 300:
        raise Exception('Error creating post')

    print('post created with id={}'.format(r.json()['id']))
    return r.json()['id']


def like_post(token, post_id):
    headers = {'Authorization': 'Token {}'.format(token)}
    r = requests.get(API_URL + '/posts/{}/like'.format(post_id), headers=headers)
    if r.status_code == 200:
        return True

# ==============================================
# main
# ==============================================
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('No config file specified.')
        print('Usage: >> python autobot.py conf.json')
        exit(1)

    main(sys.argv[1])




