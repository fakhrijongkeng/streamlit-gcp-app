# %%
from tabnanny import check
import requests # library to interact with API
import pandas as pd
import numpy as np
import time
from datetime import datetime
import re
from datetime import date # converting timestamp to date time format
import warnings
import streamlit as st
# %%
# Class ttapi will crete an object where it can process all of the API mining tasks
class ttapi:
    def __init__(self, By='username', ChallengeHashtag='',Count='', Url='', ChallengeId='', Username='', secUid = '', Id='', HasNext = False, NextPageId='', Source = '', Tag = '',videoId = '', MasterDataFrame = pd.DataFrame(), list_id = [], list_username = []):
        self.By = By 
        self.Username = Username # Feed (id and username), profile, followers, following
        self.Id = Id
        self.Source = Source
        self.HasNext = HasNext
        self.NextPageId = NextPageId
        self.Tag = Tag
        self.MasterDataFrame = MasterDataFrame
        self.secUid = secUid
        self.videoId = videoId
        self.Count = Count
        self.Url = Url
        self.Status = True
        self.ChallengeId = ChallengeId
        self.ChallengeHashtag = ChallengeHashtag
        self.headers = {
                "X-RapidAPI-Key": "7917528e84mshd5a15bfaa29b022p17b723jsn080203dddd0c",
                "X-RapidAPI-Host": "tiktok-scraper7.p.rapidapi.com"
        }
        self.querystring = {}
        self.querystring['user_id'] = self.Id
        self.querystring['unique_id'] = self.Username
        self.querystring['count'] = self.Count
        self.querystring['secUid'] = self.secUid
        self.querystring['video_id'] = self.videoId
        self.querystring['url'] = self.Url
        self.querystring['cursor'] = self.NextPageId
        self.querystring['challenge_id'] = self.ChallengeId
        self.querystring['challenge_name'] = self.ChallengeHashtag
        self.summary = ''

    # CreateAPIURL() is url creator which handles entry error before an API request is sent
    def CreateAPIURL(self):
        print('Creating API URL')
        url_rapidapi = 'https://tiktok-scraper7.p.rapidapi.com/'
        # Condtion for miner
        url_tail = self.Source
        if self.Source == 'feed' and self.By == 'username' or self.By == 'id':
            url_tail = 'user/posts'
        elif self.Source == 'profile' and self.By == 'username':
            url_tail = 'user/info'
        elif self.Source == 'comment' and self.By == 'url':
            url_tail = 'comment/list'
        elif self.Source == 'challenge' and self.By == 'hashtag':
            self.getID()
            url_tail = 'challenge/info'
        elif self.Source == 'challenge_posts' and self.By == 'challenge_id':
            url_tail = 'challenge/posts'
        # handling error
        if self.By == 'id' and self.Id == '' and self.Source != 'challenge':
            print('Your ID is empty')
            return
        elif self.By == 'username' and self.Username == '':
            print('Your username is empty')
            return
        elif self.Source == 'feed' and self.By == 'hashtag':
            print('You cannot get feed data with hashtag')
            return
        elif self.Source == 'profile' and self.By == 'id':
            print('You cannot get profile data with id')
            return
        elif self.Source == 'comment' and self.By == 'id':
            print('You cannot get comment data with id')
            return

        else:
            url_output = url_rapidapi + url_tail
            self.url = url_output
            self.summary = f'API URL created: {url_output} \n'
            print('API URL sucessfully been created')


    # GetAPIData() is a function to get data from RapidAPI which will return Instagram public data
    def GetAPIData(self):
        self.querystring['cursor'] = self.NextPageId
        retry = 0
        check = True
        while check:
            try:
                print('Mining data from API')
                response = requests.request("GET", self.url, headers=self.headers, params=self.querystring).json()
                self.Status = response['msg']

            except:
                while retry < 3:
                    # print(response['msg'])
                    print('retrying 3 times, wait 60 seconds..')
                    time.sleep(60)
                    retry = retry + 1
                print('Mining failed')
                self.Status = False
                self.summary = self.summary + f'API data capture sucess: {self.Status} (There is an error)) \n'

            else:
                self.ApiData = response
                if self.ApiData['msg'] == False :
                    print('\nretrying to get data...\n')
                    retry += 1
                    if retry >= 2 :
                        self.HasNext = False
                        break

                else :
                    if self.Source == 'feed' and self.By == 'username' or self.By == 'id':
                        self.NextPageId = self.ApiData['data']['cursor']
                        self.HasNext = self.ApiData['data']['hasMore']
                    elif self.Source == 'challenge_posts' and self.By == 'challenge_id':
                        self.NextPageId = self.ApiData['data']['cursor']
                        self.HasNext = self.ApiData['data']['hasMore']
                    elif self.Source == 'comment' and self.By == 'url':
                        self.NextPageId = self.ApiData['data']['cursor']
                        self.HasNext = self.ApiData['data']['hasMore']    
                    self.Status = self.ApiData['msg']
                    self.summary = self.summary + f'API data capture sucess: {self.Status} \n'
                    print('Data sucessfully have been mined')
                    check = False

    # Function to get id from username input
    def getID(self):            
        # Call API
        print('Getting user ID')
        check = True
        retry = 0
        while check and retry < 2:
            try: 
                # this function can get from challenge
                if self.Source == 'challenge' and self.By == 'hashtag':
                    response = requests.request("GET", 'https://tiktok-scraper7.p.rapidapi.com/challenge/info', headers=self.headers, params=self.querystring).json()
                self.ApiData = response
                if self.ApiData['msg'] == 'challenge is failed! Please check challenge_name or challenge_id.' :
                    print('\nretrying to get id...\n')
                    retry += 1
            except :
                retry = retry + 1
                print(f'retrying {retry}/3 times, wait 60 seconds..')
                time.sleep(5) 
                print(response)

                if retry == 3 :
                    # break
                    return print('Mining failed')

            else :
                try :
                    if self.Source == 'feed' or self.Source == 'profile' and self.By == 'username':
                        self.Id = response['data']['user']['id']
                        self.secUid = response['data']['user']['secUid']
                        self.querystring['user_id'] = str(self.Id)
                        self.querystring['secUid'] = str(self.secUid)
                        self.summary = self.summary + f'User ID: {self.Id} \n'
                        print('User ID have been captured')
                        check=False
                    elif self.Source == 'challenge' and self.By == 'hashtag':
                        self.ChallengeId = response['data']['id']
                        self.querystring['challenge_id'] = str(self.ChallengeId)
                        self.summary = self.summary + f'Challenge ID: {self.Id} \n'
                        print('Challenge ID have been captured')
                        check=False
                except : 
                    pass
                

    # Creating an object of .DataFrame
    def APIDataToDataFrame(self):
        print('Creating dataframe')
        data_frame = pd.DataFrame()
        if self.Status == 'success' :
            # mining FEED data
            if self.Source == 'feed':
                mention_pattern = r'@([A-Za-z0-9_]+)'
                hashtag_pattern = r'#([A-Za-z0-9_]+)'
                self.df = pd.json_normalize(self.ApiData['data']['videos'])
                if len(self.ApiData['data']['videos']) < 2:
                    return print('this user has no content')
                data_frame['content_id'] = self.df['video_id']
                data_frame['description'] = self.df['title']
                data_frame['date_created'] = pd.to_datetime(self.df['create_time'], unit='s')
                data_frame['duration'] = self.df['duration']
                data_frame['digg'] = self.df['digg_count']
                data_frame['share'] = self.df['share_count']
                data_frame['comment'] = self.df['comment_count']
                data_frame['download'] = self.df['download_count']
                data_frame['collect'] = self.df['collect_count']
                data_frame['play'] = self.df['play_count']
                data_frame['is_ad'] = self.df['is_ad']
                data_frame['music_title'] = self.df['music_info.title']
                data_frame['author_id'] = self.df['author.id']
                data_frame['author_nickname'] = self.df['author.nickname']
                data_frame['mentions'] = self.df['title'].str.findall(mention_pattern).apply(lambda x: ', '.join(x) if x else None)
                data_frame['hashtag'] = self.df['title'].str.findall(hashtag_pattern).apply(lambda x: ', '.join(x) if x else None)                
                data_frame['username'] = self.df['author.unique_id']
                data_frame['thumbnail'] = self.df['cover']
            
            # Mining Comment Data
            if self.Source == 'comment':
                self.df = pd.json_normalize(self.ApiData['data']['comments'])               
                data_frame['comment_id'] = self.df['id']               
                data_frame['username'] =  self.df['user.unique_id']                               
                data_frame['full_name'] = self.df['user.nickname'] 
                data_frame['comment_text'] = self.df['text'] 
                data_frame['likes'] = self.df['digg_count']
                data_frame['reply'] = self.df['reply_total']
                data_frame['date_created'] = pd.to_datetime(self.df['create_time'], unit='s')               
                data_frame['post_url'] = self.Url
            
            # Mining Challenge(Hashtag) Data
            if self.Source == 'challenge_posts':
                self.df = pd.json_normalize(self.ApiData['data']['videos'])
                data_frame['content_id'] = self.df['video_id']
                data_frame['region'] = self.df['region']
                data_frame['description'] = self.df['title']
                data_frame['date_created'] = pd.to_datetime(self.df['create_time'], unit='s')
                data_frame['duration'] = self.df['duration']
                data_frame['username'] = self.df['author.unique_id']
                data_frame['author_id'] = self.df['author.id']
                data_frame['author_nickname'] = self.df['author.nickname']           
                data_frame['music_id'] = self.df['music_info.id']
                data_frame['music_title'] = self.df['music_info.title']
                data_frame['like'] = self.df['digg_count']
                data_frame['share'] = self.df['share_count']
                data_frame['comment'] = self.df['comment_count']
                data_frame['save'] = self.df['collect_count']
                data_frame['play'] = self.df['play_count']
                data_frame['is_ad'] = self.df['is_ad']
                data_frame['thumbnail'] = self.df['cover']
                data_frame['challenge_hashtag'] = self.ChallengeHashtag
            
            # Mining Profile Data
            if self.Source == 'profile':
                self.df = pd.json_normalize(self.ApiData['data'])
                data_frame['id'] = self.df['user.id']
                data_frame['unique_id'] = self.df['user.uniqueId']
                data_frame['nickname'] = self.df['user.nickname']
                data_frame['avatar'] = self.df['user.avatarThumb']
                data_frame['signature'] = self.df['user.signature']
                data_frame['verified'] = self.df['user.verified']
                data_frame['secUid'] = self.df['user.secUid']
                data_frame['ftc'] = self.df['user.ftc']
                data_frame['relation'] = self.df['user.relation']
                data_frame['open_favorite'] = self.df['user.openFavorite']
                data_frame['private_account'] = self.df['user.privateAccount']
                data_frame['secret'] = self.df['user.secret']
                data_frame['is_ad_virtual'] = self.df['user.isADVirtual']
                data_frame['followers'] = self.df['stats.followerCount']
                data_frame['following'] = self.df['stats.followingCount']
                data_frame['heart'] = self.df['stats.heart']
                data_frame['heart_count'] = self.df['stats.heartCount']
                data_frame['video_count'] = self.df['stats.videoCount']
                data_frame['digg_count'] = self.df['stats.diggCount']

            # Information prompt
            nrows = len(data_frame)
            self.summary = self.summary + f'Dataframe mined: {nrows} rows \n'
            self.DataFrame = data_frame
            print('Data frame succesfully have been created')
        else : 
            print("Got no data!")

    def AppendToMasterDataFrame(self):
        print('Adding data to master dataframe')
        if len(self.MasterDataFrame) == 0:
            self.MasterDataFrame = self.DataFrame
        else:
            self.MasterDataFrame = self.MasterDataFrame.append(self.DataFrame, ignore_index=True)
        print('Data have been added to master dataframe')
        self.summary = self.summary + f'Master dataframe: {len(self.MasterDataFrame)} rows \n'
     
# Function to regex mentions (@) from a string
def username_string(x):
    list = re.findall(r'\B@[._a-z0-9]{3,24}', x)
    string = "" 
    
    if len(list) > 1:
        for l in list: 
            string += l + " "
    else:
        for l in list: 
            string += l

    return string.strip()

def hashtag_string(x):
    output = list_to_string(re.findall(r"#(\w+)", x))
    return output

def list_to_string(s): 
    string = "" 
    
    for ele in s: 
        string += f'{ele}, '   

    return string 

def check_error(x):
    try:
        x
    except:
        return ''
    else:
        return x

warnings.filterwarnings("ignore")

####################### OOP FOR CALL API #######################

def fetch_tiktok_content(username: str, count: int = 20) -> pd.DataFrame:
    tt = ttapi(
        By='username', 
        Username=username, 
        Count=count, 
        Source='feed'
    )

    tt.CreateAPIURL()
    try :
        tt.GetAPIData()
        tt.APIDataToDataFrame()
            
        # Error handling for when the username is correct, but the user does't have any content
        return tt.DataFrame
    except : 
        return print('Failed to fetch tiktok content')

def fetch_tiktok_profile(username: str) -> pd.DataFrame:
    tt = ttapi(
        By='username', 
        Username=username, 
        Source='profile'
    )

    tt.CreateAPIURL()
    try :
        tt.GetAPIData()
        tt.APIDataToDataFrame()
            
        # Error handling for when the username is correct, but the user does't have any content
        return tt.DataFrame
    except : 
        return print('Failed to fetch tiktok content')

@st.cache_data(ttl='1h')
def fetch_tiktok_content_cached(username: str, count: int = 20) -> pd.DataFrame:
    return fetch_tiktok_content(username, count)

@st.cache_data(ttl='1h')
def fetch_tiktok_profile_cached(username: str) -> pd.DataFrame:
    return fetch_tiktok_profile(username)