import pyaudio
import wave

class Recode():
    def __init__(self,usb_device_index = 2,filename = "demo.mp3",time=10):
        self.sample_rate = 16000
        self.duration = time
        self.frames = []
        self.filename=filename
        self.usb_device_index=usb_device_index

        self.p = pyaudio.PyAudio()
        self.stream=None
        self.stream = self.p.open(format=pyaudio.paInt16,
                        channels=1,
                        rate= self.sample_rate,
                        input=True,
                        input_device_index=usb_device_index,
                        frames_per_buffer=1024)
    
    def start_recode(self):
        self.frames = []
        # self.stream = self.p.open(format=pyaudio.paInt16,
        #                 channels=1,
        #                 rate= self.sample_rate,
        #                 input=True,
        #                 input_device_index=self.usb_device_index,
        #                 frames_per_buffer=1024)
        print("Start recording...")
        for _ in range(0, int( self.sample_rate / 1024 *  self.duration)):
            data =  self.stream.read(1024)
            self.frames.append(data)
        print("End of recording")

        # self.stream.stop_stream()
        # self.stream.close()
        # self.p.terminate()

        with wave.open(self.filename, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(self.p.get_sample_size(pyaudio.paInt16))
            wf.setframerate(self.sample_rate)
            wf.writeframes(b''.join(self.frames))

    def device_list(self):
        for i in range(self.p.get_device_count()):
            device_info = self.p.get_device_info_by_index(i)
            if device_info['maxInputChannels'] > 0:
                device_type = "内置麦克风"
                if 'USB' in device_info['name'].upper():
                    device_type = "USB麦克风"
                print(f"设备索引 {i}: {device_info['name']} - 类型: {device_type}")

        self.p.terminate()

if __name__=="__main__":
    r=Recode(2)
    r.device_list()      
    
# recode=Recode()
              
# recode.device_list()


# usb_device_index = 2  # 根据实际列表调整
# filename = "output.mp3"
# sample_rate = 44100
# duration = 6
# frames = []

# p = pyaudio.PyAudio()
# stream = p.open(format=pyaudio.paInt16,
#                 channels=1,
#                 rate=sample_rate,
#                 input=True,
#                 input_device_index=usb_device_index,
#                 frames_per_buffer=1024)

# print("开始录音...")
# for _ in range(0, int(sample_rate / 1024 * duration)):
#     data = stream.read(1024)
#     frames.append(data)
# print("录音结束")

# stream.stop_stream()
# stream.close()
# p.terminate()

# # 保存录音
# with wave.open(filename, 'wb') as wf:
#     wf.setnchannels(1)
#     wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
#     wf.setframerate(sample_rate)
#     wf.writeframes(b''.join(frames))