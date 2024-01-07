import pygame
import time

def play(filename):
    pygame.mixer.init()
    pygame.mixer.music.load(filename)  # 加载音乐文件
    pygame.mixer.music.play()                  # 播放
    pygame.mixer.music.set_volume(1.0)         # 设置音量
    
    time_list = []
    while True:
        now=pygame.mixer.music.get_pos()
        if not now in time_list:
            time_list.append(now)
        else:
            break
        time.sleep(1)
    pygame.mixer.music.stop()



def play_all_music(db):
    table = db.table("music")
    all_music = table.all()   # 查询所有乐曲

    print("歌单：")         # 列出歌单
    print("-"*30)
    for i in all_music:
        print(i.get('music_name'))
    print("-"*30)

    pygame.init()            # 初始化
    pygame.mixer.init()
    print("播放器就绪......") # 准备播放
    print("-"*30)

    for i in all_music:
        print("开始播放 {} ".format(i.get('music_name')))
        try:
            play("music/{}.mp3".format(i.get("music_id")))   # 根据id补全音乐文件路径
        except KeyboardInterrupt:  # Ctrl+C 引发的异常捕捉
            continue    # 下一个
    
    pygame.mixer.music.stop()
