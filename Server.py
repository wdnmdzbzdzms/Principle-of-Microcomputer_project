# import time
import asyncio
from openai import OpenAI
from Speechin import record_and_recognize
import Speaker
import Tools
from MusicPlayer import MusicPlayer
import threading
import RPi.GPIO as GPIO
import time

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
                content = self._create_chat(message, msg_type)
                if msg_type == 'shutdown':
                    break
                elif msg_type == 'music':
                    Speaker.speak('请稍等')
                    player = MusicPlayer(content)
                    player_thread = threading.Thread(target=player.play)
                    player_thread.start()
                    # 主线程等待音乐播放完成
                    player_thread.join()
                elif msg_type == 'GPT':
                    msg_type_trans, content_trans  = content[1:-1].split(',')
                    msg_type_trans = msg_type_trans.replace("'", "")
                    print('[debug] gpt_load:'+ msg_type_trans)
                    msg = self._create_chat(content_trans, msg_type_trans)
                    if msg_type_trans == 'shutdown':
                        Speaker.speak('再见')
                        break
                    elif msg_type_trans == 'music':
                        Speaker.speak('请稍等')
                        player = MusicPlayer(msg)
                        player.play()
                        # player_thread = threading.Thread(target=player.play)
                        # player_thread.start()
                        # # 主线程等待音乐播放完成
                        # player_thread.join()
                    elif msg_type_trans == 'chat':
                        Speaker.speak(msg)
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
        print('[debug]green light on')
        message = record_and_recognize()
        print('[debug]red light on')
        if ('今天' in message) and ('天气' in message):
            reply, msg_type = Tools.get_weather()
            return reply, msg_type
        elif ('关机' in message) or ('退出' in message) or ('停止' in message):
            reply, msg_type = Tools.shutdown()
            return reply, msg_type
        elif ('播放' in message) or ('歌' in message):
            reply = message
            msg_type = 'music'
            return reply, msg_type
        elif ('聊天' in message) or ('对话' in message):
            reply = message
            msg_type = 'chat'
            return reply, msg_type
        elif ('开灯' in message) or ('关灯' in message):
            reply, msg_type = Tools.light(message)
            return reply, msg_type
        else:
            # 用gpt分析语义
            return message,'GPT'


    def _create_chat(self, message:str, msg_type:str):
        if msg_type == 'weather':
            completion = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "你是天气预报助手，根据天气信息，生成50字左右的穿衣提示"},
                {"role": "user", "content": message},
            ])
            content = completion.choices[0].message.content
            Speaker.speak(content)
            
        elif msg_type == 'light':
            Speaker.speak(message)
            content = message

        elif msg_type == 'GPT':
            completion = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "你是用户语义分析器，推测用户语句的含义，严格按照模板('type',value)格式返回内容。将用户信息分成以下五种情况：1.若用户询问天气信息，返回('weather',None); 2.若用户有播放歌曲的需求，找到一首满足用户需求的歌曲名,返回('music',name),其中name是歌曲名 3.用户想要你扮演某种角色跟他对话,返回('chat',character); 4.用户想要关机, 返回('shutdown',None)5.若其他含义，返回('other',None)"},
                {"role": "user", "content": message},
            ])
            content = completion.choices[0].message.content
            # print(content)
            # Speaker.speak(content)

        elif msg_type == 'music':
            completion = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "你是歌曲播放器助手，分析用户语义，返回一个满足用户需求的歌的歌名"},
                {"role": "user", "content": message},
            ])
            content = completion.choices[0].message.content
            if "《" in content and "》" in content:
                start_index = content.index("《") + 1
                end_index = content.index("》")
                
                content = content[start_index:end_index]  # 得到书名号中的内容 "Python编程"
            print('[debug]:'+ content)

        elif msg_type == 'shutdown':
            Speaker.speak('再见')
            content = '正在关机，再见'

        elif msg_type == 'chat':
            Speaker.speak('进入对话模式')
            messages_queue = []
            messages_queue.append({"role": "system", "content": '你是角色扮演机器人，理解用户对你的设定,按照用户期望的角色用中文与用户对话。有四种声音供你选择:0.默认;1.播音腔;2.东北话;3.陕西话;4.粤语；请必须按照(type,content)的格式返回消息(其中type是语言类型,content是返回用户的对话内容),例如：(2,俺是东北人)。若用户无语言需求返回(0,cotent)'})
            messages_queue.append({"role": "user", "content": message})
            while True:
                print('[debug]message_queue:' +messages_queue)
                message, message_type = self._get_speechin() # 检测说话信息
                messages_queue.append({"role": "user", "content": message})
                if message_type == 'shutdown':
                    content = '退出对话模式'
                    Speaker.speak(content)
                    break
                completion = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages = messages_queue)

                content = completion.choices[0].message.content
                # 根据用户需求改编语音播报类型
                response_type, response_content = content[1:-1].split(',')
                Speaker.speak(response_content, response_type)
                print(f'[debug]ChatGPT: {content}')
                messages_queue.append({"role": "assistant", "content": content})
        else: 
            content = '我不知道你在说什么'
        return content 
    
    