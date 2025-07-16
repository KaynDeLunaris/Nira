#!/usr/bin/env python3
import os, json, datetime, yaml
from llama_cpp import Llama
cfg = yaml.safe_load(open("config.yaml"))
llm = Llama(model_path=cfg["model_path"], n_ctx=2048, verbose=False)
def load_memory(lines=10):
if not os.path.exists(cfg["memory_file"]):
return []
with open(cfg["memory_file"], "r") as f:
mem = [json.loads(l) for l in f]
return mem[-lines:]   # nur letzte N Zeilen, sonst wird’s zu lang
def save_memory(role, text):
with open(cfg["memory_file"], "a") as f:
json.dump({"timestamp": str(datetime.datetime.utcnow()), "role": role, "text": text}, f)
f.write("\n")
def chat():
history = load_memory()
while True:
user = input("\nDu: ")
if user.lower() in {"exit", "quit", "bye"}:
break
history.append({"role": "user", "content": user})
save_memory("user", user)
prompt = cfg["system_prompt"] + "\n"
for h in history[-6:]:   # 6 letzte Nachrichten als Kontext
prompt += f"{h['role']}: {h['content']}\n"
prompt += "assistant: "

response = llm(prompt, max_tokens=cfg["max_tokens"], temperature=cfg["temperature"])["choices"][0]["text"]
response = response.strip()
print("Nira:", response)
history.append({"role": "assistant", "content": response})
save_memory("assistant", response)
if name == "main":
chat()