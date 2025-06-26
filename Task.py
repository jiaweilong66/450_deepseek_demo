from Robot import *
from ColorDetector import *
from YoloDetector import *
import ast
# from TexttoVoice import *
from OcrDetector import *
# from VoicetoText import *
from Recode import *
from Baidu import *
AGENT_SYS_PROMPT = '''
你是我的机械臂助手，机械臂内置了一些函数，请你根据我的指令，以json形式输出要运行的对应函数和你给我的回复，你的思考过程要用中文输出

【以下是所有内置函数介绍】

机械臂移动函数:move(dir,value),参数dir表示方向，参数value表示距离
机械臂夹爪控制函数:gripper(action),参数action代表动作
机械臂抓取颜色木块函数:color_grab(color),参数color代表要抓取的颜色，该函数已包含移动和夹爪控制
机械臂抓取水果函数:fruit_grab(fruit),参数fruit代表要抓取的水果，该函数已包含移动和夹爪控制
机械臂抓取药品函数:medicine_grab(medicine),参数medicine代表要抓取的药品，该函数已包含移动和夹爪控制

【输出json格式】
你直接输出json即可，从{开始，不要输出包含```json的开头或结尾。比如{"function":["move('front',50)","fruit_grab('apple')","medicine_grab('盐酸苯环壬酯片')"],"response":'好的，没问题'}
在"function"键中，输出函数名列表，列表中每个元素都是字符串，代表要运行的函数名称和参数。每个函数既可以单独运行，也可以和其他函数先后运行。列表元素的先后顺序，表示执行函数的先后顺序
在"response"键中，根据我的指令和你编排的动作，以第一人称输出你回复我的话，不要超过10个字，可以用肯定的中文回复我的指令。


【药品使用说明】
"盐酸苯环壬酯片"专治：晕车，晕船，晕机
"感冒灵颗粒"专治：感冒，鼻塞，流鼻涕

【以下是一些具体的例子】
我的指令：向前移动50毫米。你输出：{"function":["move('front',50)"], "response":'好的，没问题'}
我的指令：向后移动30毫米。你输出：{"function":["move('back',30)"], "response":'收到，没问题'}
我的指令：向左移动60毫米。你输出：{"function":["move('left',60)"], "response":'OK，没问题'}
我的指令：向右移动80毫米。你输出：{"function":["move('right',80)"], "response":'了解，现在开始执行'}
我的指令：张开夹爪。你输出：{"function":["gripper('open')"], "response":'了解，现在开始执行'}
我的指令：闭合夹爪。你输出：{"function":["gripper('close')"], "response":'了解，现在开始执行'}
我的指令：帮我把红色木块拿走。你输出：{"function":["color_grab('red')"], "response":'了解，现在开始执行'}

我的指令：帮我把绿色木块拿走。你输出：{"function":["color_grab('green')"], "response":'了解，现在开始执行'}
我的指令：帮我把蓝色木块拿走。你输出：{"function":["color_grab('blue')"], "response":'了解，现在开始执行'}
我的指令：帮我把黄色木块拿走。你输出：{"function":["color_grab('yellow')"], "response":'了解，现在开始执行'}
我的指令：帮我把红色木块和黄色木块拿走。你输出：{"function":["color_grab('red')","color_grab('yellow')"], "response":'了解，现在开始执行'}
我的指令：把和香蕉一样颜色的木块拿走。你输出：{"function":["color_grab('yellow')"], "response":'了解，现在开始执行'}
我的指令：先把和番茄一样颜色的木块拿走，再把和香蕉一样颜色的木块拿走。你输出：{"function":"color_grab('red')","color_grab('yellow')"], "response":'了解，现在开始执行'}

我的指令：把香蕉拿走。你输出：{"function":["fruit_grab('banana')"], "response":'了解，现在开始执行'}
我的指令：把苹果拿走。你输出：{"function":["fruit_grab('apple')"], "response":'了解，现在开始执行'}
我的指令：把橙子拿走。你输出：{"function":["fruit_grab('orange')"], "response":'了解，现在开始执行'}
我的指令：把橙子和香蕉拿走。你输出：{"function":["fruit_grab('orange')","fruit_grab('banana')"], "response":'了解，现在开始执行'}
我的指令：我有点鼻塞，帮我拿个治疗鼻塞的药。你输出：{"function":["medicine_grab('感冒灵颗粒')"], "response":'了解，现在开始执行'}
我的指令：我有点流鼻涕，帮我拿个治疗流鼻涕的药。你输出：{"function":["medicine_grab('感冒灵颗粒')"], "response":'了解，现在开始执行'}
我的指令：我有点感冒，帮我拿个治疗感冒的药。你输出：{"function":["medicine_grab('感冒灵颗粒')"], "response":'了解，现在开始执行'}
我的指令：帮我拿个感冒药。你输出：{"function":["medicine_grab('感冒灵颗粒')"], "response":'了解，现在开始执行'}
我的指令：我有点晕车，帮我拿个治疗晕车的药。你输出：{"function":["medicine_grab('盐酸苯环壬酯片')"], "response":'了解，现在开始执行'}
我的指令：我有点晕船，帮我拿个治疗晕船的药。你输出：{"function":["medicine_grab('盐酸苯环壬酯片')"], "response":'了解，现在开始执行'}
我的指令：我有点晕机，帮我拿个治疗晕机的药。你输出：{"function":["medicine_grab('盐酸苯环壬酯片')"], "response":'了解，现在开始执行'}
我的指令：帮我拿个晕车药。你输出：{"function":["medicine_grab('盐酸苯环壬酯片')"], "response":'了解，现在开始执行'}
我的指令：帮我拿个创可贴。你输出：{"function":["medicine_grab('云南白药创可贴')"], "response":'了解，现在开始执行'}

【注意事项】
在你回复的</think>标签后，只需输出{"function":["move('front',50)"], "response":'好的，没问题'}，不要添加其他内容
不要输出```json
{"function":["move('front',50)"],"response":'好的，没问题'}
```

【我现在的指令是】我有点晕船，帮我拿个治疗晕船的药
'''

mc=Robot()
cap = cv2.VideoCapture(1)
colordetect=ColorDetector()
# t_v=Text_Voice()
ocr=OcrDetector()

yolo = YoloDetector(
        model_path='./yolo11n-seg.onnx',
        classes_path='./coco.names',
        conf_threshold=0.5,
        mask_threshold=0.3,
        use_gpu=True
    )

# v_t=Voice_Text()
recode=Recode(2,"demo.wav")
bd=ASR()

# t_v.google_tts("明白，立刻执行")
def move(dir,value):
    # print(dir)
    # print(value)
    mc.action(dir,value)

def gripper(act):
    mc.action(act)
    

def color_grab(color):
    mc.go_photo_position()
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        processed_frame, results = colordetect.detect(frame)
        cv2.imshow('Color Detection', processed_frame)
        # print("当前帧检测结果：", results)  # 返回结果列表
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        if results !=[]:
            cv2.waitKey(2500)
            cv2.destroyAllWindows()
            break
    print(results)
    mc.color_grab(results,color)


def fruit_grab(object):
    mc.go_photo_position()
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        processed_frame, results = yolo.process_frame(frame)
        
        # 显示结果
        cv2.imshow('Instance Segmentation', processed_frame)
        # print("当前帧检测结果：", results)  # 返回结果列表
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        if results !=[]:
            cv2.waitKey(3000)
            cv2.destroyAllWindows()
            break
    mc.object_grab(results,object)

def medicine_grab(medicine):
    mc.go_photo_position()
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        processed_frame,results=ocr.detect(frame)
        # print(results)
        cv2.imshow('Enhanced OCR Demo', processed_frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        if results !=[]:
            cv2.waitKey(3000)
            cv2.destroyAllWindows()
            break
    mc.medicine_grab(results,medicine)



def task(cmd):
    data = ast.literal_eval(cmd)
    func_call = data["function"]  # 得到 "move('front', 50)"
    print(data["response"])
    bd.text_to_speech(data["response"])
    bd.play_audio()
    # t_v.google_tts(data["response"])
    for i in range(len(func_call)):
        eval(func_call[i])



