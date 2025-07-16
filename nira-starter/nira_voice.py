#!/usr/bin/env python3
import os, json, yaml, datetime, speech_recognition as sr, subprocess, threading, queue
from llama_cpp import Llama
cfg = yaml.safe_load(open("config.yaml"))
llm = Llama(model_path=cfg["model_path"], n_ctx=2048, verbose=False)
def speak(text):
subprocess.run(["espeak-ng", "-s", "160", "-v", "de", text])
def load_memory(lines=10):
if not os.path.exists(cfg["memory_file"]):
return []
with open(cfg["memory_file"], "r") as f:
mem = [json.loads(l) for l in f]
return mem[-lines:]
def save_memory(role, text):
with open(cfg["memory_file"], "a") as f:
json.dump({"timestamp": str(datetime.datetime.utcnow()), "role": role, "text": text}, f)
f.write("\n")
def listen(q):
r = sr.Recognizer()
mic = sr.Microphone()
with mic as source:
r.adjust_for_ambient_noise(source)
while True:
with mic as source:
audio = r.listen(source, phrase_time_limit=5)
try:
text = r.recognize_google(audio, language="de-DE")
q.put(text)
except sr.UnknownValueError:
pass  # leise ignorieren
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
    prompt += "assistant: "

    response = llm(prompt, max_tokens=cfg["max_tokens"], temperature=cfg["temperature"])["choices"][0]["text"]
    response = response.strip()
    print("Nira:", response)
    speak(response)
    history.append({"role": "assistant", "content": response})
    save_memory("assistant", response)
if name == "main":
main()