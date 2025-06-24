from aip import AipSpeech
from Recode import *
import pygame
from API_Key import *
# 替换成你的应用信息
# APP_ID = '119086778'
# API_KEY = 'Nnhi8XxnmAyemK3lSykMwltz'
# SECRET_KEY = 'curDmKdqJoad5xZ8yM7I5F6AOLj4EHPM'


class ASR():
    def __init__(self):
        self.client = AipSpeech(APP_ID, API_KEY, SECRET_KEY)
        pygame.mixer.init()
    def recognize_audio(self,file_path='./demo.wav'):
        """识别本地音频文件"""
        # 读取音频文件（支持pcm/wav/amr格式）
        with open(file_path, 'rb') as f:
            audio_data = f.read()
        
        # 调用语音识别接口
        # 参数说明：音频数据、格式、采样率、语言模型（1537=中文普通话）
        result = self.client.asr(audio_data, 'wav', 16000, {
            'dev_pid': 1537,  # 中文普通话模型
        })
        
        # 解析结果
        if result['err_no'] == 0:
            print(result['result'])
            return result['result'][0]
        else:
            print(f"识别失败！错误码: {result['err_no']}, 错误信息: {result['err_msg']}")
            return None
    def text_to_speech(self,text, output_file="output.wav"):
        # 语音合成参数配置
        result = self.client.synthesis(
            text,         # 要合成的文本 (UTF-8)
            'zh',         # 语言：中文
            1,            # 普通话发音人（0-女声，1-男声）
            {
                'vol': 5,       # 音量 (0-15)
                'spd': 5,       # 语速 (0-9)
                'pit': 5,       # 音调 (0-9)
                'per': 4,       # 发音人选择（见下方备注）
                'aue': 6        # 音频格式 6=mp3
            }
        )

        # 合成成功返回音频二进制，错误返回dict
        if not isinstance(result, dict):
            with open(output_file, 'wb') as f:
                f.write(result)
            print(f'语音合成成功，已保存至: {output_file}')
            return True
        else:
            print('合成失败:', result['err_msg'])
            return False
    
    def play_audio(self,file="output.wav"):
        
        pygame.mixer.music.load(file)
        pygame.mixer.music.play()
        # 等待播放结束
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        pygame.mixer.music.unload()



if __name__=="__main__":
    s=ASR()
    s.recognize_audio("./demo.wav")
    # s.text_to_speech("广东英德")
    # s.play_audio("./output.wav")