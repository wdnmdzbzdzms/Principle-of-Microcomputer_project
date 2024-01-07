from Speechin import record_and_recognize
import subprocess
import pygame
import requests
import jsonpath
import os
import threading
import time

class MusicPlayer:
    def __init__(self,name):
        pygame.mixer.init()
        self.paused = False
        self.recover =False
        self.ifpause =False
        # print('[debug musicplayer]',os.getcwd() + '/data/music.mp3')
        download_music(name)
        pygame.mixer.music.load(r'/home/kanno/Desktop/personal_folder/EE351/project2_byzzx_1217/data/music.mp3')

    def play(self):
        
        pygame.mixer.music.play()
        

        while pygame.mixer.music.get_busy():
            print("[debug]music is playing")
            # time.sleep(0.5)
            text=record_and_recognize()
            if '暂停' in text:
                if not self.ifpause:
                    self.ifpause = True
                    pygame.mixer.music.pause()
                    print("[debug]music is pause")
            if '恢复' in text:
                if self.ifpause:
                    self.ifpause = False
                    pygame.mixer.music.unpause()
                    print('[debug]music unpause')
                
            
def _song_download(url,title,author):
    input_path = os.getcwd() + '/data/binary_music.mp3'
    output_path = os.getcwd() + '/data/music.mp3'
    print('歌曲:{0}-{1},正在下载...'.format(title,author))
    # 下载（这种读写文件的下载方式适合少量文件的下载）
    content = requests.get(url).content
    # print('[debug]now:'+os.getcwd()+'/data/music.mp3')
    with open(input_path, mode='wb') as f:
        f.write(content)

    # 将二进制MP3文件转为标准MP3文件
    ffmpeg_command = ['sudo','ffmpeg', '-i', input_path, output_path]
    subprocess.run(ffmpeg_command)

def _get_music_name(name):
    """
    搜索歌曲名称
    :return:
    """
    # name = input("请输入歌曲名称:")
    # print("1.网易云:netease\n2.QQ:qq\n3.酷狗:kugou\n4.酷我:kuwo\n5.百度:baidu\n6.喜马拉雅:ximalaya")
    # platfrom = input("输入音乐平台类型:")
    platfrom = 'qq'
    # print("-------------------------------------------------------")
    url = 'https://music.liuzhijin.cn/'
    headers = {
        "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36",
        # 判断请求是异步还是同步
        "x-requested-with":"XMLHttpRequest",
    }
    param = {
        "input":name,
        "filter":"name",
        "type":platfrom,
        "page": 1,
    }
    res = requests.post(url=url,data=param,headers=headers)
    json_text = res.json()

    title = jsonpath.jsonpath(json_text,'$..title')
    author = jsonpath.jsonpath(json_text,'$..author')
    url = jsonpath.jsonpath(json_text, '$..url')
    if title:
        songs = list(zip(title,author,url))
        for s in songs:
            print(s[0],s[1],s[2])
        print("-------------------------------------------------------")
        # index = int(input("请输入您想下载的歌曲版本:"))
        index = 1
        _song_download(url[index],title[index],author[index])
    else:
        print("对不起，暂无搜索结果!")

def download_music(name):
    _get_music_name(name)

