import asyncio
import edge_tts

text = "林夏的手指停在门把手上，她知道，一旦打开，这个世界就再也回不去了。"

async def main():
    communicate = edge_tts.Communicate(
        text=text,
        voice="zh-CN-XiaoxiaoNeural"
    )
    await communicate.save("output.mp3")

asyncio.run(main())
