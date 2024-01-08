import re
import requests
from datetime import datetime
from bs4 import BeautifulSoup
import RPi.GPIO as GPIO
import time

def get_weather():
        """
        Get the weather of the current city.

        Parameters:
        - None

        Returns:
        str: The weather information of current city.
        """
        
        headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit'
                                '/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safar'
                                'i/537.36',
        }

        res2 = requests.get('http://tianqi.moji.com/', headers=headers)

        # 使用html.parser解释获取的res2.text的html文本
        soup = BeautifulSoup(res2.text, "html.parser")
        # print(soup)

        # 解析文本，获得温度、湿度等具体值
        temp = soup.find('div', attrs={'class': 'wea_weather clearfix'}).em.getText()
        weather = soup.find('div', attrs={'class': 'wea_weather clearfix'}).b.getText()
        sd = soup.find('div', attrs={'class': 'wea_about clearfix'}).span.getText()
        sd_num = re.search(r'\d+', sd).group()
        # sd = sd.replace(sd_num, sd_num_zh)
        wind = soup.find('div', attrs={'class': 'wea_about clearfix'}).em.getText()
        aqi = soup.find('div', attrs={'class': 'wea_alert clearfix'}).em.getText()
        aqi_num = re.search(r'\d+', aqi).group()
        # aqi = aqi.replace(aqi_num, aqi_num_zh)
        info = soup.find('div', attrs={'class': 'wea_tips clearfix'}).em.getText()
        sd = sd.replace(' ', '百分之').replace('%', '')
        aqi = 'aqi' + aqi

        today = datetime.now().date().strftime('%Y年%m月%d日')
        message = '今天是%s,天气%s,温度%s摄氏度,%s,%s,%s,%s' % \
                (today, weather, temp, sd, wind, aqi, info)
        return message, 'weather'

def light(message):
        """
        Control the light.

        Parameters:
        - message: What user's say.

        Returns:
        str: The light information.
        """
        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)
        GPIO.setup(11, GPIO.OUT)
        GPIO.setup(12, GPIO.OUT)
        if '开灯' in message:
                message = '灯已打开'
                GPIO.output(11, GPIO.HIGH)
        elif '关灯' in message:
                message = '灯已关闭'
                GPIO.output(11, GPIO.LOW)
        msg_type = 'light'
        return message, msg_type

def shutdown():
        message = ''
        msg_type = 'shutdown'
        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)
        GPIO.setup(11, GPIO.OUT)
        GPIO.setup(12, GPIO.OUT)
        GPIO.output(12, GPIO.LOW)
        GPIO.output(11, GPIO.LOW)
        return message, msg_type