# -*- coding: utf-8 -*-
"""
Created on Sat May 11 22:47:55 2024

@author: bdwye
"""

from elevenlabs import play, save
from elevenlabs.client import ElevenLabs
import moviepy.Clip
import moviepy.editor
import praw
from selenium import webdriver
from selenium.webdriver.common.by import By
import os
import moviepy
import librosa
from moviepy.editor import *
import whisper
import whisper_timestamped
from moviepy.editor import *
from moviepy.video.fx.resize import resize
from moviepy.video.VideoClip import ImageClip
import random

os.chdir('C:\\Users\\bdwye\\Documents\\Python Scripts\\Youtube Shorts\\TikTok Voice\\tiktok-voice-main')

reddit = praw.Reddit(
      client_id="*******"
      client_secret="********",
      password="*******",
      user_agent="USERAGENT",
      username="boogiemen",
  )

def save_audio(ID, text, type):

  client = ElevenLabs(
    api_key="*******", # Defaults to ELEVEN_API_KEY
  )

  audio = client.generate(
    text=text,
    voice="Adam",
    model="eleven_multilingual_v2"
  )
  if type == 'comment':
    save(audio, f'Comment_Audios/{ID}.mp3')
  elif type == 'title':
    save(audio, f'Title_Audios/{ID}.mp3')

def postToReddit():
  
  reddit.subreddit("test").submit("Test Submission", url="https://reddit.com")

def getThreeAskredditPosts():
  '''
  returns a dictionary where the key is the url and the value is a list
  where the list is [title, id, top comment id, top comment text]
  '''
  postDict = {}

  posts = reddit.subreddit('askreddit').top(time_filter='day', limit=1)
  print(posts)
  for submission in posts:
    if submission.over_18:
      continue

    postTitle = submission.title
    postID = submission.id

    f = open('redditIDs.txt', 'r')
    f1 = f.read()
    print(f1)
    if postID in f1:
      print('found the post')
      continue
    f.close()
    
    f = open('redditIDs.txt', 'a+')
    f.write(f'{postID}\n')
    f.close()
    
  #   postComments = {}

  #   length_commentAudios = 0
  #   i = 0

  #   save_audio(postID, postTitle, 'title')
  #   length_titleAudio = librosa.get_duration(path=f'Title_Audios/{postID}.mp3')

  #   while True:
      
  #     save_audio(submission.comments[i].id, submission.comments[i].body, 'comment')

  #     length_commentAudios += librosa.get_duration(path=f'Comment_Audios/{submission.comments[i].id}.mp3')
      
  #     if length_commentAudios >45:
  #       break
  #     postComments[submission.comments[i].id] = submission.comments[i].body
  #     i+=1
    
  #   postDict[submission.url] = [postTitle, postID, length_titleAudio, postComments]
    
  # return postDict

def makeVideo(postInfoDict):
  silentAudioClip = AudioFileClip('1sec_silence.mp3')
  
  for url in postInfoDict.keys():
    getScreenshot(url, postInfoDict[url][1])

  for redditPost in postInfoDict.values():
    audio_files = []
    TitleAudio = f"Title_Audios/{redditPost[1]}.mp3"
    audio_files.append(TitleAudio)
    for commentKey in redditPost[3].keys():
      CommentAudio = f"Comment_Audios/{commentKey}.mp3"
      audio_files.append(CommentAudio)
    
    print(audio_files)
    audio_clips = []

    for file in audio_files:
      audio_clip = AudioFileClip(file)
      audio_clips.append(audio_clip)
      audio_clips.append(silentAudioClip)

    
    finalAudio = concatenate_audioclips(audio_clips)
    finalAudioLength = finalAudio.duration
    finalAudio.write_audiofile(f'Concatenated_Audios/{redditPost[1]}.mp3')

    clip = VideoFileClip('Background_Minecraft_Video.mov')
    startTime = random.randint(0,12*60)
    videoClip = clip.subclip(t_start = startTime, t_end = startTime + finalAudioLength)
    #need to subclip this
    
    picClip1 = ImageClip(f'Screenshots/{redditPost[1]}.png').set_start(0).set_duration(5).set_pos(('center',500))

    picClip = resize(picClip1, width = 800, height = 300)


    model = whisper_timestamped.load_model("base")
    result = whisper_timestamped.transcribe(model, f'Concatenated_Audios/{redditPost[1]}.mp3')

    subs = []
    subs.append(videoClip)
    subs.append(picClip)
    for segment in result['segments']:
        for word in segment['words']:
            text = word['text'].upper()
            start = word['start']
            end = word['end']
            duration = end - start
            # print([text, start, end])
            textClip = TextClip(text, fontsize=120, font='Arial-Bold', stroke_width=2, color= 'white', stroke_color='black', method='caption', align='center')
            textClip = textClip.set_start(start).set_duration(duration).set_pos(('center',1500))
            subs.append(textClip)


  
    clip = CompositeVideoClip(subs)


    clip.audio = finalAudio
    clip.write_videofile(f'Finished_Videos/{redditPost[1]}.mp4', fps=24)
  





def getScreenshot(url, postID):
  driver = webdriver.Chrome()
  # url = 'https://www.reddit.com/r/AskReddit/comments/1d8g3np/what_is_something_most_people_dont_know_can_kill/'
  driver.set_window_size(width=400, height=800)
  driver.get(url)
  driver.implicitly_wait(0.1)

  element = driver.find_element(By.ID, f't3_{postID}')

  element.screenshot(f'Screenshots/{postID}.png')

def testSaveAudio():
  redditDict = getThreeAskredditPosts()
  instance = list(redditDict.keys())[0]
  save_audio(redditDict.get(instance)[2], redditDict.get(instance)[3])

# clip = moviepy.editor.VideoFileClip('Background_Minecraft_Video.mov')

# newclip = clip.subclip('1:00', '2:00')
# newclip.write_videofile('Minute_Test.mp4')

# redditTest = reddit.submission("3g1jfi")
# print(redditTest.comments[1].body)

# print(getThreeAskredditPosts())

testdict = {'www.reddit.com/1234': ['this is a fake title',
                                    '1d90yxg',
                                    15,
                                    {'l76cvl5': 'fake comment 1',
                                     'l76gemj': 'fake comment 2'}]}

# makeVideo(getThreeAskredditPosts())
getThreeAskredditPosts()
