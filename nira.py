#!/usr/bin/env python3
import os
import json
import datetime
import yaml
from llama_cpp import Llama

cfg = yaml.safe_load(open("config.yaml", encoding="utf-8"))   # <-- FIX: expliziter UTF-8

llm = Llama(
    model_path=cfg["model_path"],
    n_ctx=2048,
    verbose=False
)

def load_memory(lines=10):
    if not os.path.exists(cfg["memory_file"]):
        return []
    with open(cfg["memory_file"], "r", encoding="utf-8") as f:   # <-- FIX
        mem = [json.loads(line) for line in f if line.strip()]   # <-- FIX: leere Zeilen ignorieren
    return mem[-lines:]

def save_memory(role: str, text: str):
    with open(cfg["memory_file"], "a", encoding="utf-8") as f:   # <-- FIX
        json.dump(
            {
                "timestamp": datetime.datetime.utcnow().isoformat(),
                "role": role,
                "text": text
            },
            f,
            ensure_ascii=False   # <-- FIX: Umlaute erhalten
        )
        f.write("\n")

def chat():
    history = []
    while True:
        user = input("\nDu: ").strip()
        if user.lower() in {"exit", "quit", "bye"}:
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
            temperature=cfg["temperature"],
            stop=["\nDu:", "\nUser:", "\nassistant:", "assistant:"]
        )["choices"][0]["text"].strip()
        print("Nira:", response)
        history.append({"role": "assistant", "content": response})
        save_memory("assistant", response)

if __name__ == "__main__":
    chat()