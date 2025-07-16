#!/usr/bin/env python3
import os
import json
import datetime
import yaml
import subprocess
import threading
import queue
import speech_recognition as sr
from llama_cpp import Llama

cfg = yaml.safe_load(open("config.yaml", encoding="utf-8"))   # <-- FIX

llm = Llama(
    model_path=cfg["model_path"],
    n_ctx=2048,
    verbose=False
)

def speak(text: str) -> None:
    subprocess.run(["espeak-ng", "-s", "160", "-v", "de", text])

def load_memory(lines: int = 10):
    if not os.path.exists(cfg["memory_file"]):
        return []
    with open(cfg["memory_file"], "r", encoding="utf-8") as f:
        mem = [json.loads(line) for line in f if line.strip()]
    return mem[-lines:]

def save_memory(role: str, text: str) -> None:
    with open(cfg["memory_file"], "a", encoding="utf-8") as f:
        json.dump(
            {
                "timestamp": datetime.datetime.utcnow().isoformat(),
                "role": role,
                "text": text
            },
            f,
            ensure_ascii=False
        )
        f.write("\n")

def listen(q: queue.Queue) -> None:
    r = sr.Recognizer()
    mic = sr.Microphone()
    with mic as source:
        r.adjust_for_ambient_noise(source, duration=1)
    while True:
        with mic as source:
            audio = r.listen(source, phrase_time_limit=5)
        try:
            text = r.recognize_google(audio, language="de-DE")
            q.put(text.strip())
        except sr.UnknownValueError:
            pass  # schweigend ignorieren

def main():
    q = queue.Queue()
    threading.Thread(target=listen, args=(q,), daemon=True).start()
    history = load_memory()
    print("Nira lauscht … (Sag 'Beenden' zum Stoppen)")
    while True:
        user = q.get()
        if "beenden" in user.lower():
            break
        history.append({"role": "user", "content": user})
        save_memory("user", user)

        prompt = cfg["system_prompt"] + "\n"
        for h in history[-6:]:
            prompt += f"{h['role']}: {h['content']}\n"
        prompt += "assistant:"

        response = llm(
            prompt,
            max_tokens=cfg["max_tokens"],
            temperature=cfg["temperature"]
        )["choices"][0]["text"].strip()
        print("Nira:", response)
        speak(response)
        history.append({"role": "assistant", "content": response})
        save_memory("assistant", response)

if __name__ == "__main__":
    main()