#!/usr/bin/env python3
import os
import json
import datetime
import yaml
from llama_cpp import Llama

# === CONFIG LADEN ===
try:
    with open("config.yaml", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
except Exception as e:
    print(f"[ERROR] Konnte config.yaml nicht laden: {e}")
    exit(1)

# === LLM INITIALISIERUNG ===
try:
    llm = Llama(
        model_path=cfg["model_path"],
        n_ctx=cfg.get("context_length", 2048),
        verbose=False
    )
except Exception as e:
    print(f"[ERROR] Konnte das Modell nicht laden: {e}")
    exit(1)

# === MEMORY HANDLING ===
def load_memory(lines=10):
    if not os.path.exists(cfg["memory_file"]):
        return []
    try:
        with open(cfg["memory_file"], "r", encoding="utf-8") as f:
            mem = [json.loads(line) for line in f if line.strip()]
        return mem[-lines:]
    except Exception as e:
        print(f"[WARNUNG] Fehler beim Laden des Memory-Logs: {e}")
        return []

def save_memory(role: str, text: str):
    try:
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
    except Exception as e:
        print(f"[WARNUNG] Fehler beim Speichern des Memory-Logs: {e}")

# === FEEDBACK-LOOP ===
def feedback_loop(response: str):
    feedback = input("War die Antwort gut? (y/n): ").strip().lower()
    if feedback == "n":
        with open("feedback_log.txt", "a", encoding="utf-8") as f:
            f.write(f"[BAD] {datetime.datetime.utcnow().isoformat()} → {response}\n")

# === CHAT ===
def chat():
    history = load_memory(lines=cfg.get("history_limit", 6))
    print("💬 Nira ist bereit. Schreibe 'exit' oder 'quit' zum Beenden.")

    while True:
        user = input("\nDu: ").strip()
        if user.lower() in {"exit", "quit", "bye"}:
            print("👋 Nira: Bis bald.")
            break

        history.append({"role": "user", "content": user})
        save_memory("user", user)

        # Prompt aufbauen
        prompt = cfg["system_prompt"] + "\n"
        for h in history[-cfg.get("history_limit", 6):]:
            prompt += f"{h['role']}: {h['content']}\n"
        prompt += "assistant:"

        try:
            result = llm(
                prompt,
                max_tokens=cfg["max_tokens"],
                temperature=cfg["temperature"]
            )
            response = result["choices"][0]["text"].strip()
        except Exception as e:
            print(f"[ERROR] Fehler bei LLM-Antwort: {e}")
            continue

        print("Nira:", response)
        history.append({"role": "assistant", "content": response})
        save_memory("assistant", response)

        if cfg.get("enable_feedback", False):
            feedback_loop(response)

# === START ===
if __name__ == "__main__":
    chat()
