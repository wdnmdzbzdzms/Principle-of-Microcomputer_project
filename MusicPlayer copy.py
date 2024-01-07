from Speechin import record_and_recognize
import pygame
import requests
import jsonpath
import os
import threading
import time
import queue

class MusicPlayer:
    def __init__(self,name):
        pygame.mixer.init()
        self.paused = False
        self.recover =False
        self.ifpause =False
        self.command_queue = command_queue
        download_music(name)
        # print('[debug musicplayer]',os.getcwd() + '/data/music.mp3')
        

    def play(self,result):
        pygame.mixer.music.load(r'/home/kanno/Desktop/personal_folder/EE351/project2_byzzx_1217/data/music.mp3')
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            # 在这里加入一些等待时间，以避免无限循环过于密集
            time.sleep(1)

            # 检查主程序传递的指令队列
            try:
                command = self.command_queue.get_nowait()
                if command == 'pause' and not self.ifpause:
                    self.ifpause = True
                    pygame.mixer.music.pause()
                    print("[debug]music is paused")
                elif command == 'resume' and self.ifpause:
                    self.ifpause = False
                    pygame.mixer.music.unpause()
                    print('[debug]music resumed')
            except queue.Empty:
                pass
        print("[debug]music playback completed")
                
            
def _song_download(url,title,author):
    # 创建文件夹
    # os.makedirs("music",exist_ok=True)
    path = 'music\{}.mp3'.format(title)
    print('歌曲:{0}-{1},正在下载...'.format(title,author))
    # 下载（这种读写文件的下载方式适合少量文件的下载）
    content = requests.get(url).content
    print('[debug]now:'+os.getcwd()+'/data/music.mp3')
    with open(os.getcwd() + '/data/music.mp3',mode='wb') as f:
        f.write(content)
    print('下载完毕,{0}-{1},请试听'.format(title,author))

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

