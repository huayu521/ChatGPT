import os
from flask import Flask, render_template, request, url_for
import openai
import asyncio
import hashlib
import requests
import subprocess
import time
import json
import random

# 构建请求头
headers = {
    "Content-Type": "application/json",
    "Referer": "https://aigcfun.com/",
    "origin": "https://aigcfun.com"
}

# 构建URL
url = f"https://api.aigcfun.com/api/v1/text?key=FCM4CAEJZF62MWSZUA&signature=f5d35a81fe773f7b67024ac9937abb38bfc75f7e73d733a27431c52cbaf8376b"

pubkey = "FCM4CAEJZF62MWSZUA"

# 设置请求参数
model = "gpt-3.5-turbo-16k"
temperature = 0.5
max_tokens = 500
generated_text = ""

def generate_random_ip():
    ip = ".".join(str(random.randint(0, 255)) for _ in range(4))
    print(ip)
    return ip

def get_pubkey():
    global pubkey
    url = "https://api.aigcfun.com/fc/key"
    headers = {
    "Content-Type": "application/json",
    "Referer": "https://aigcfun.com/",
    "X-Forwarded-For": generate_random_ip()
        }
    
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        pubkey = data.get("data")
        if not pubkey:
            print("获取pubkey失败")
        else:
            print("pubkey: " + pubkey)
    else:
        print("请求失败，状态码：" + str(response.status_code))

# 函数用于生成签名
async def generate_signature(timestamp, your_qus):
    # 构造签名字符串
    signature_string = f"{timestamp}:{your_qus}:{pubkey}"
    
    # 使用SHA-256算法计算哈希值
    signature = hashlib.sha256(signature_string.encode()).hexdigest()
    print(signature)
    
    return signature

async def send_http_request(timestamp, your_qus):
    # 生成签名
    signature = await generate_signature(timestamp, your_qus)
    global generated_text
    
    # 构造请求头
    headers = {
        "Content-Type": "application/json",
        "Referer": "https://aigcfun.com/",
        "Origin": "https://aigcfun.com",
    }
    
    # 构造请求体
    messageChain1 = [{"role": "user", "content": your_qus}]
    data = {
        "messages": messageChain1,
        "tokensLength": len(your_qus) + 10,
        "model": "gpt-3.5-turbo-16k"
    }
    
    # 构造请求URL
    url = f"https://api.aigcfun.com/api/v1/text?key={pubkey}&signature={signature}"
    
    # 发送POST请求
    response = requests.post(url, headers=headers, json=data)
    
    # 处理响应
    if response.status_code == 200:
        try:
            print('成功....111')
            print(response.text)
            result = response.json()["choices"][0]["text"]
            print(result)
            generated_text = result
            print('成功....222')
            print(pubkey)
            get_pubkey()
            print('成功....333')
            print(pubkey)
            # 在这里可以对result进行进一步处理
        except Exception as e:
            print("未知错误:", e)
    else:
        print('访问失败了')

# 异步函数用于调用send_http_request
async def AIGCFUN(your_qus):
    # 弹出提示消息
    print("该线路较慢，请稍后...")
    
    # 获取当前时间戳
    now = int(time.time())
    print(now)
    
    # 发送HTTP请求并获取结果
    await send_http_request(now, your_qus)

app = Flask(__name__)
@app.route('/')
def home():
    image_url = url_for('static', filename='cycle.jpg')
    return render_template('index.html', image_url=image_url)

@app.route('/record', methods=['POST'])
def record():
    # 获取录音数据
    audio_file = request.files['audio_data']

    # 保存录音为MP3文件
    save_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'recorded_audio.mp3')
    audio_file.save(save_path)
    # save_path = '/Users/sense/openai-quickstart-node/run/92_1684398757.mp3'
        #翻译
        # global translate
    with open(save_path, 'rb') as file:
        response = openai.Audio.translate('whisper-1', file)
        translate = response['text']
        print(response)
        print(translate)

    return '录音已保存'

@app.route('/send', methods=['POST'])
def send():
    # 获取文本框中的信息
    message = request.form.get('message')
    global generated_text

    asyncio.run(AIGCFUN(message))
    print(generated_text)
    return generated_text

@app.route('/transcribe', methods=['POST'])
def transcribe():
    # 打开音频文件并读取二进制数据
    save_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'recorded_audio.mp3')
    with open(save_path, 'rb') as file:
        response = openai.Audio.transcribe('whisper-1', file)
        transcript = response['text']
        print(response)
    return transcript

@app.route('/translate', methods=['POST'])
def translate():
    # 打开音频文件并读取二进制数据
    save_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'recorded_audio.mp3')
    with open(save_path, 'rb') as file:
        response = openai.Audio.translate('whisper-1', file)
        translate = response['text']
        print(response)
    return translate

if __name__ == '__main__':
    app.run(host='localhost', port=8080)