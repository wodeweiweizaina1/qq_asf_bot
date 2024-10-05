import asyncio
import websockets
import json
import requests
import os
# 配置 WebSocket 和 ASF API 的相关信息
NAPCAT_WS_URL = os.environ.get('NAPCAT_WS_URL')
TARGET_USER_ID = os.environ.get('TARGET_USER_ID')
ASF_API_URL = os.environ.get('ASF_API_URL')
ASF_API_KEY = os.environ.get('ASF_API_KEY')



# 发送消息给指定用户
async def send_message_to_user(user_id, message):
    async with websockets.connect(NAPCAT_WS_URL) as ws:
        # 构造发送消息的 JSON 数据
        data = {
            "action": "send_msg",
            "params": {
                "user_id": user_id,
                "message": message
            }
        }
        await ws.send(json.dumps(data))

# 调用 ASF 的 play API
def asf_play(botname, gameid):
    url = f"{ASF_API_URL}/Command"
    headers = {
        "Authentication": ASF_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "Command": f"play {botname} {gameid}"
    }
    response = requests.post(url, headers=headers, json=payload)
    return response.json()

# 调用 ASF 的 stop API (实际上是 play 0 命令)
def asf_stop(botname):
    url = f"{ASF_API_URL}/Command"
    headers = {
        "Authentication": ASF_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "Command": f"play {botname} 0"
    }
    response = requests.post(url, headers=headers, json=payload)
    return response.json()

# 调用 ASF 的 redeem API
def asf_redeem(botname, key):
    url = f"{ASF_API_URL}/Command"
    headers = {
        "Authentication": ASF_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "Command": f"redeem {botname} {key}"
    }
    response = requests.post(url, headers=headers, json=payload)
    return response.json()

# 处理接收到的消息
async def handle_message(message):
    try:
        msg_data = json.loads(message)
        user_id = str(msg_data.get("user_id"))
        msg_content = msg_data.get("message")

        # 只处理来自指定用户的消息
        if user_id == TARGET_USER_ID:
            if msg_content.startswith("asf play"):
                parts = msg_content.split()
                if len(parts) == 4:
                    botname = parts[2]
                    gameid = parts[3]
                    # 调用 ASF 的 play API
                    result = asf_play(botname, gameid)
                    # 把结果发送给用户
                    await send_message_to_user(user_id, f"ASF Play Result: {result}")
            elif msg_content.startswith("asf stop"):
                parts = msg_content.split()
                if len(parts) == 4:
                    botname = parts[2]
                    # 调用 ASF 的 stop API (实际上是 play 0)
                    result = asf_stop(botname)
                    # 把结果发送给用户
                    await send_message_to_user(user_id, f"ASF Stop Result: {result}")
            elif msg_content.startswith("asf"):
                parts = msg_content.split()
                if len(parts) == 3:
                    botname = parts[1]
                    key = parts[2]
                    # 调用 ASF 的 redeem API
                    result = asf_redeem(botname, key)
                    # 把结果发送给用户
                    await send_message_to_user(user_id, f"ASF Redeem Result: {result}")

    except Exception as e:
        print(f"Error handling message: {e}")

# 监听 WebSocket 消息
async def listen_to_ws():
    async with websockets.connect(NAPCAT_WS_URL) as ws:
        while True:
            try:
                message = await ws.recv()
                await handle_message(message)
            except websockets.ConnectionClosed:
                print("Connection closed, attempting to reconnect...")
                await asyncio.sleep(5)
                await listen_to_ws()  # 尝试重新连接
            except Exception as e:
                print(f"Error: {e}")

# 主函数
async def main():
    await listen_to_ws()

# 运行事件循环
if __name__ == "__main__":
    asyncio.run(main())


