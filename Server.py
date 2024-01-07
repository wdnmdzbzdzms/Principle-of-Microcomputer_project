# import time
import asyncio
from openai import OpenAI
from Speechin import record_and_recognize
import Speaker
import Tools
from MusicPlayer import MusicPlayer
import threading

start_key = '你好'
pause_key = '暂停'
class Server:
    def __init__(self):
        with open('.env', 'r') as f:
            for line in f:
                # 忽略注释和空行
                if line.startswith("#") or line.strip() == "":
                    continue
                # 解析键值对
                key, value = line.strip().split("=", 1)
                if key == 'OPENAI_API_KEY':
                    self.client = OpenAI(api_key=value)
    
    def run(self):
        try:
            while start_key not in record_and_recognize():
                pass
            Speaker.speak("我在")
            while True:
                message,msg_type = self._get_speechin() # 检测说话信息
                # print('[debug]', msg_type)
                content = self._create_chat(message, msg_type)
                # asyncio.run(self.listen_pause())
                if msg_type == 'shutdown':
                    break
                elif msg_type == 'music':
                    player = MusicPlayer(content)
                    player_thread = threading.Thread(target=player.play)
                    player_thread.start()
                    # 主线程等待音乐播放完成
                    player_thread.join()
            # asyncio.run(self.listen_pause())
        except KeyboardInterrupt:
            print('[debug]ctrl+c')
    


        


    def _get_speechin(self):
        """
        Detect and clarify the user's command.

        Parameters:
        - None

        Returns:
        message: What user's say.
        msg_type: Type of user's message.
        """
        message = record_and_recognize()
        if ('今天' in message) and ('天气' in message):
            reply, msg_type = Tools.get_weather()
            return reply, msg_type
        elif ('关机' in message) or ('退出' in message):
            reply, msg_type = Tools.shutdown()
            return reply, msg_type
        elif ('播放' in message) or ('歌' in message):
            reply = message
            msg_type = 'music'
            return reply, msg_type
        else:
            return message,'GPT'


    def _create_chat(self, message:str, msg_type:str):
        if msg_type == 'weather':
            completion = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "你是天气预报助手，尽量简短的给出穿衣提示"},
                {"role": "user", "content": message},
            ])
            content = completion.choices[0].message.content
            Speaker.speak(content)
            
        elif msg_type == 'GPT':
            completion = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "你是一个语音助手，请简要回答用户问题"},
                {"role": "user", "content": message},
            ])
            content = completion.choices[0].message.content
            Speaker.speak(content)

        elif msg_type == 'music':
            completion = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "通过用户的输入内容，返回一首歌的歌名"},
                {"role": "user", "content": message},
            ])
            content = completion.choices[0].message.content
            print('[debug]:'+ content)

        elif msg_type == 'shutdown':
            content = '正在关机，再见'
            
        else: 
            content = '我不知道你在说什么'

        return content 
    
    