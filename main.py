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

#first let's establish our working directory
os.chdir('C:\\Users\\bdwye\\Documents\\Python Scripts\\Youtube Shorts\\TikTok Voice\\tiktok-voice-main')

#start our reddit instance. Needed this to interact with the reddit api
reddit = praw.Reddit(
      client_id=""
      client_secret="",
      password="",
      user_agent="USERAGENT",
      username="boogiemen",
  )

def save_audio(ID, text, type):
  '''
  Takes the input text (string) and turns it into a .mp3 file in the correct folder
  '''
  client = ElevenLabs(
    api_key="", # Defaults to ELEVEN_API_KEY
  )

  audio = client.generate(
    text=text,
    voice="Adam",
    model="eleven_multilingual_v2"
  )

  #save the file to a different location if it's a comment file or a title file
  if type == 'comment':
    save(audio, f'Comment_Audios/{ID}.mp3')
  elif type == 'title':
    save(audio, f'Title_Audios/{ID}.mp3')

def postToReddit():
  '''
  Test for posting to reddit in r/test
  '''
  reddit.subreddit("test").submit("Test Submission", url="https://reddit.com")

def getAskredditPosts():
  '''
  returns a dictionary where the key is the url and the value is a list
  where the list is [title, id, top comment id, top comment text]
  '''
  postDict = {}

  #can change the limit to get more posts
  posts = reddit.subreddit('askreddit').top(time_filter='day', limit=3)
  
  for submission in posts:
    #don't want any NSFW posts
    if submission.over_18:
      continue

    postTitle = submission.title
    postID = submission.id

    #don't want any posts that i've already done
    f = open('redditIDs.txt', 'a+')
    f.seek(0)
    f1 = f.read()
    if postID in f1:
      continue
    
    #if we're proceeding, add the postID to my text file
    f.write(f'{postID}\n')
    f.close()
    
    postComments = {}

    length_commentAudios = 0
    i = 0

    #save the title audio. We want the length of the audio file to know how long to keep the screenshot up for
    save_audio(postID, postTitle, 'title')
    length_titleAudio = librosa.get_duration(path=f'Title_Audios/{postID}.mp3')

    #save the comment audio. Keep tabs on the length so our video doesn't end up too long
    while True:
      if len(submission.comments[i].body) > 200:
        continue
      save_audio(submission.comments[i].id, submission.comments[i].body, 'comment')

      length_commentAudios += librosa.get_duration(path=f'Comment_Audios/{submission.comments[i].id}.mp3')
      
      if length_commentAudios >45:
        break
      postComments[submission.comments[i].id] = submission.comments[i].body
      i+=1
    
    postDict[submission.url] = [postTitle, postID, length_titleAudio, postComments]
    
  return postDict

def makeVideo(postInfoDict):
  '''
  This function generates the video. Yeehaw!
  '''
  
  #silent clip to put between other clips so it's not too jumbled
  silentAudioClip = AudioFileClip('1sec_silence.mp3')
  
  #get screenshots of the URLs in the dictionary
  for url in postInfoDict.keys():
    getScreenshot(url, postInfoDict[url][1])

  #now we iterate through the reddit posts and make the videos
  for redditPost in postInfoDict.values():
    #get all the file locations appended into a list
    audio_files = []
    TitleAudio = f"Title_Audios/{redditPost[1]}.mp3"
    audio_files.append(TitleAudio)
    for commentKey in redditPost[3].keys():
      CommentAudio = f"Comment_Audios/{commentKey}.mp3"
      audio_files.append(CommentAudio)
    
    #now we need them all to be Audio clips
    audio_clips = []

    for file in audio_files:
      audio_clip = AudioFileClip(file) #convert to clip
      audio_clips.append(audio_clip) #add to list
      audio_clips.append(silentAudioClip) #add some silence for a nice spacer

    #concatenate them all into a single audio clip
    finalAudio = concatenate_audioclips(audio_clips)
    finalAudioLength = finalAudio.duration
    
    #export to a .mp3 file so we can use the WHISPER on it
    finalAudio.write_audiofile(f'Concatenated_Audios/{redditPost[1]}.mp3')

    #get a random start point for our minecraft video
    clip = VideoFileClip('Background_Minecraft_Video.mov')
    startTime = random.randint(0,12*60)
    videoClip = clip.subclip(t_start = startTime, t_end = startTime + finalAudioLength)
    
    #get our screenshot showing up for the right amount of time in the right place at the right size
    picClip1 = ImageClip(f'Screenshots/{redditPost[1]}.png').set_start(0).set_duration(redditPost[2]).set_pos(('center',500))
    picClip = resize(picClip1, width = 800, height = 300)

    #now we get the audio back into text form with timestamps to create subtitles
    model = whisper_timestamped.load_model("base")
    result = whisper_timestamped.transcribe(model, f'Concatenated_Audios/{redditPost[1]}.mp3')

    subs = [] #this will be a list of ALLLLLL the clips we want in our video. The order matters
    subs.append(videoClip) #add the minecraft
    subs.append(picClip) #add the screenshots

    #now add the subtitles
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


    #turn it all into a composite clip
    clip = CompositeVideoClip(subs)

    #export that shit
    clip.audio = finalAudio
    clip.write_videofile(f'Finished_Videos/{redditPost[1]}.mp4', fps=24)
  





def getScreenshot(url, postID):
  '''
  Saves a screenshot of the reddit post
  '''
  driver = webdriver.Chrome()
  
  driver.set_window_size(width=400, height=800)
  driver.get(url)
  driver.implicitly_wait(0.1)

  #find the element that contains the question, which contains the postID. handy!
  element = driver.find_element(By.ID, f't3_{postID}')

  element.screenshot(f'Screenshots/{postID}.png')

def main():
  makeVideo(getAskredditPosts())

if __name__ == '__main__':
    main()
