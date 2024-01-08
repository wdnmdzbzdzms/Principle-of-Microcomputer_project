import os
import edge_tts
import asyncio
# import pyttsx3
# data路径
filepath = os.getcwd() + '/data'
voices = {
    '1': "zh-CN-YunyangNeural",#普通话
    '2': "zh-CN-liaoning-XiaobeiNeural",#东北
    '3': "zh-CN-shaanxi-XiaoniNeural",#陕西
    '4':"zh-HK-HiuGaaiNeural"#粤语
}
# 定义一个异步函数，该函数创建一个edge_tts.Communicate对象，并保存生成的语音到MP3文件
async def _txt2sound(message:str,name=None):
    # 设置语音的参数
    voice = select_voice(name, voices) # 语音的类型
    rate = '+0%' # 语音的速度
    volume = '+0%' # 语音的音量
    output_path = filepath+'/voice.wav' # 语音文件输出地址
    tts = edge_tts.Communicate(text=message, voice=voice, rate=rate, volume=volume)
    await tts.save(output_path)

def select_voice(name, voices_dict):
    if name is None:
        return 'zh-CN-YunyangNeural' 
    for key, value in voices_dict.items():
        if name in key:
            return value
    return 'zh-CN-YunyangNeural'
# 播放语音的函数
def _playsound():
    os.system('mplayer %s' % filepath+'/voice.wav')
    
# 如果这个脚本是直接运行的，而不是被导入的，那么就运行上面定义的异步函数
def speak(message: str,name=None):
    """
    Using the speaker to voice the message.

    Parameters:
    - message(str) 

    Returns:
    - None
    """
    loop = asyncio.get_event_loop_policy().get_event_loop()
    try:
        loop.run_until_complete(_txt2sound(message,name))
        # loop.run_in_executor(None, _playsound)
    finally:
        # loop.close()
        pass
    _playsound()
