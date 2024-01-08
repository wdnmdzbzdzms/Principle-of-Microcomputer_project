import speech_recognition as sr
import Speaker
import RPi.GPIO as GPIO

    # 使用麦克风模块录制音频
def record_and_recognize():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(False)
    GPIO.setup(12, GPIO.OUT)
    GPIO.setup(11, GPIO.OUT)
    GPIO.output(12, GPIO.HIGH)
    GPIO.output(11, GPIO.LOW)
    # 初始化Recognizer类实例
    r = sr.Recognizer()
    while True:
        # time.sleep(2)
        with sr.Microphone() as source:
            print("请说话...")
            audio = r.listen(source)
        # 进行语音识别
        try:
            text=r.recognize_google(audio, language='zh-CN')
            print("你说的是: " + text)
            GPIO.output(11, GPIO.HIGH)
            GPIO.output(12, GPIO.LOW)   
            
            return text 
        except sr.UnknownValueError:
            print("无法识别音频，请重新说话...")
            Speaker.speak("无法识别音频，请三秒后重新说话")
            # time.sleep(2)
            continue
        except sr.RequestError as e:
            print("无法从Google Speech Recognition服务中获取数据; {0}，请重新说话...".format(e))
            Speaker.speak("无法从Google Speech Recognition服务中获取数据,请三秒后重新说话")
            # time.sleep(2)
            continue

    