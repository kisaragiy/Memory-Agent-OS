import asyncio
import edge_tts
import os
import subprocess
import argparse
import re

OUTPUT_DIR = "output"

# 1️⃣ 解析 speaker + text
def split_sentences(text):
    pattern = r'(林夏|陈默|旁白)[:：](.*?)(?=(林夏|陈默|旁白)[:：]|$)'
    matches = re.findall(pattern, text)

    result = []
    for m in matches:
        speaker = m[0]
        content = m[1].strip()
        if content:
            result.append({"speaker": speaker, "text": content})

    return result


# 2️⃣ voice 映射（关键）
VOICE_MAP = {
    "林夏": "zh-CN-XiaoxiaoNeural",
    "陈默": "zh-CN-YunxiNeural",
    "旁白": "zh-CN-XiaoyiNeural"
}


# 3️⃣ 生成音频（关键升级）
async def generate_audio(text, speaker, index):
    voice = VOICE_MAP.get(speaker, "zh-CN-XiaoxiaoNeural")

    print(f"[TTS] {speaker} -> {voice} : {text}")

    communicate = edge_tts.Communicate(
        text=text,
        voice=voice
    )

    filename = os.path.abspath(f"{OUTPUT_DIR}/audio_{index}.mp3")
    await communicate.save(filename)
    return filename


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--text", type=str, required=True)
    args = parser.parse_args()

    text = args.text.strip()
    if not text:
        print("输入为空")
        return

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    scenes = split_sentences(text)

    print("解析结果:", scenes)
    print("句子数量:", len(scenes))

    audio_files = []

    for i, item in enumerate(scenes):
        speaker = item["speaker"]
        sentence = item["text"]

        print(f"生成 {speaker}: {sentence}")

        file = await generate_audio(sentence, speaker, i)
        audio_files.append(file)

    file_list_path = os.path.abspath(f"{OUTPUT_DIR}/list.txt")

    with open(file_list_path, "w") as f:
        for file in audio_files:
            f.write(f"file '{file}'\n")

    final_output = os.path.abspath(f"{OUTPUT_DIR}/final.mp3")

    subprocess.run([
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", file_list_path,
        "-c", "copy",
        final_output
    ])

    print("完成:", final_output)


if __name__ == "__main__":
    asyncio.run(main())
