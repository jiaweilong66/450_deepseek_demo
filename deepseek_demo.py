from openai import OpenAI

import numpy as np
from Task import *



class DeepSeek():
    def __init__(self,url="http://127.0.0.1:11434/v1"):
        self.client = OpenAI(
            base_url=url,  
            api_key="ollama"  
        )
        
    def ask_ollama_openai_stream(self,prompt, model="deepseek-r1:7b"):
        # 启用流式响应
        response = self.client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        stream=True  # 启用流式输出
    )
    
        # 逐块处理响应
        full_response = ""
        for chunk in response:
            if chunk.choices[0].delta.content:  # 检查是否有内容
                text = chunk.choices[0].delta.content
                print(text, end="", flush=True)  # 逐词打印
                full_response += text
        # for chunk in response:
        #     content = chunk.choices[0].delta.content
        #     if content:
        #         full_response += content
        return full_response.split("</think>")[-1]
        
        # return full_response.replace("<think>", "").replace("</think>", "").strip()

    def convert_punctuation(self,text):
        # 创建中英文标点映射表（包含全角/半角情况）
        punctuation_map = {
            '“': '"',  # 中文双引号（左）
            '”': '"',  # 中文双引号（右）
            '‘': "'",  # 中文单引号（左）
            '’': "'",  # 中文单引号（右）
            '，': ',',  # 中文逗号
            '（': '(',  # 中文括号（左）
            '）': ')',  # 中文括号（右）
            '【': '[',  # 扩展：中文方括号
            '】': ']',  # 扩展：中文方括号
            '；': ';',  # 扩展：中文分号
            '：': ':',  # 扩展：中文冒号
        }
        
        # 创建转换表（处理ASCII码映射）
        trans_table = str.maketrans(punctuation_map)
        
        # 执行批量替换
        return text.translate(trans_table)
    

deepseek=DeepSeek()    

if __name__=="__main__":
    while 1 :
        try:
            AGENT_PROMPT=input("按下回车键开始录音:")
            recode.start_recode()
            
            AGENT_PROMPT=bd.recognize_audio()
            
            res = deepseek.ask_ollama_openai_stream(AGENT_SYS_PROMPT+AGENT_PROMPT)
            answer =deepseek.convert_punctuation(res)
            # print("answer=",answer)
            task(answer)
            print()
            # break
        except SyntaxError as e:
            print("二次解析")
            try:
                tmp_answer=answer.split("```json")[1].split("```")[0]
                task(tmp_answer)
            except :
                print("推理出错，重新录入指令")
                






        
        
