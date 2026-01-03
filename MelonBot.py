# 導入Discord.py模組
import discord
from googletrans import Translator
import os
from dotenv import load_dotenv
import emoji
import asyncio

load_dotenv() 

# client是跟discord連接，intents是要求機器人的權限
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents = intents)

CANTONESE_KEYWORDS = [
    "喺", "咁", "嘅", "佢", "佢哋", "我哋","哋",
    "冇", "嚟", "嗰", "啲", "咗", "呢", "好勁",
    "點解", "乜", "咩", "仲", "晒"
]

def contains_cantonese(text: str) -> bool:
    return any(word in text for word in CANTONESE_KEYWORDS)

# 建立翻譯器
translator = Translator()

# 指定頻道
ALLOWED_CHANNELS = {
    1434742197642592298,  #閒聊
    1434752955407405126   #開會
}

def is_only_emoji(text: str) -> bool:
    # 去除空白與換行
    stripped = text.strip()
    if not stripped:
        return False

    # 移除所有 emoji
    text_without_emoji = emoji.replace_emoji(stripped, replace="")

    # 如果移除後只剩空白，代表原本全是 emoji
    return text_without_emoji.strip() == ""

ready_once = False

# 調用event函式庫
@client.event
# 當機器人完成啟動
async def on_ready():
    global ready_once
    if ready_once:
        return
    ready_once = True
    print(f"機器人已上線：{client.user}")

@client.event
async def on_message(message):
    # 只允許特定頻道
    if message.channel.id not in ALLOWED_CHANNELS:
        return
    
    # 忽略機器人自己的訊息
    if message.author.bot:
        return

    text = message.content.strip()

    # 空訊息不處理
    if not text:
        return
    
    #emoji不處理
    if is_only_emoji(text):
        return  # 只有 emoji，直接 return
    
    try:
        # googletrans 有速率限制 → 稍微放慢
        await asyncio.sleep(0.3)

        # 偵測語言
        detected = translator.detect(text)
        lang = detected.lang

        # 只翻譯英文
        if lang == "en":
            result = translator.translate(text, src="en", dest="zh-tw")
            #print("英 ➜ 繁體中文：")
        # 粵語特徵字 → 繁體中文
        elif contains_cantonese(text):
            result = translator.translate(text, dest="zh-tw")
            #print("翻粵語 ➜ 繁體中文：")
        else:
            return
        
        await message.reply(
            f"🤖：{result.text}"
        )

    except Exception as e:
        print("翻譯錯誤：", e)


#機器人的TOKEN
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
client.run(DISCORD_TOKEN)