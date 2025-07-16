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
        verbose=False,
    )
except Exception as e:
    print(f"[ERROR] Konnte das Modell nicht laden: {e}")
    exit(1)


# === MEMORY HANDLING ===
def load_memory():
    if not os.path.exists(cfg["memory_file"]):
        return []
    try:
        with open(cfg["memory_file"], "r", encoding="utf-8") as f:
            mem = [json.loads(line) for line in f if line.strip()]
        return mem
    except Exception as e:
        print(f"[WARNUNG] Fehler beim Laden des Memory-Logs: {e}")
        return []

def save_memory(role: str, content: str, used=False):
    try:
        with open(cfg["memory_file"], "a", encoding="utf-8") as f:
            json.dump(
                {
                    "timestamp": datetime.datetime.utcnow().isoformat(),
                    "role": role,
                    "content": content,
                    "used": used,
                },
                f,
                ensure_ascii=False,
            )
            f.write("\n")
    except Exception as e:
        print(f"[WARNUNG] Fehler beim Speichern des Memory-Logs: {e}")

def rewrite_memory(entries):
    try:
        with open(cfg["memory_file"], "w", encoding="utf-8") as f:
            for entry in entries:
                json.dump(entry, f, ensure_ascii=False)
                f.write("\n")
    except Exception as e:
        print(f"[WARNUNG] Fehler beim Überschreiben des Memory-Logs: {e}")

# === FEEDBACK-LOOP ===
def feedback_loop(response: str):
    feedback = input("War die Antwort gut? (y/n): ").strip().lower()
    if feedback == "n":
        with open("feedback_log.txt", "a", encoding="utf-8") as f:
            f.write(f"[BAD] {datetime.datetime.utcnow().isoformat()} → {response}\n")

# === CHAT ===
def chat():
    print("💬 Nira ist nun Wach. Schreibe 'exit' oder 'quit' zum Beenden.\n")

    while True:
        user = input("Du: ").strip()
        if user.lower() in {"exit", "quit", "bye"}:
            break

        # Lade komplette History
        history = load_memory()

        # Speichere neue User-Eingabe mit used=False
        save_memory("user", user, used=False)
        history.append({
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "role": "user",
            "content": user,
            "used": False
        })

        # Trenne schon beantwortete (used=True) und neue User-Nachrichten (used=False)
        answered_msgs = [h for h in history if h.get("used", False)]
        new_user_msgs = [h for h in history if h["role"] == "user" and not h.get("used", False)]

        # Prompt zusammenbauen:
        prompt = cfg["system_prompt"].strip() + "\n\n"

        for h in answered_msgs:
            role = h["role"]
            content = h.get("content") or ""
            if role == "user":
                prompt += f"User: {content}\n"
            elif role == "nira":
                prompt += f"Nira: {content}\n"

        for h in new_user_msgs:
            prompt += f"User: {h['content']}\n"

        prompt += "Nira: "

        # Antwort generieren
        response = llm(
            prompt, max_tokens=cfg["max_tokens"], temperature=cfg["temperature"]
        )["choices"][0]["text"].strip()

        print("Nira:", response)

        # Neue Nira-Antwort speichern (initial used=False)
        save_memory("nira", response, used=False)
        history.append({
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "role": "nira",
            "content": response,
            "used": False
        })

        # Direkt alle neuen User- und Nira-Nachrichten auf used=True setzen
        for entry in history:
            if (entry["role"] == "user" or entry["role"] == "nira") and not entry.get("used", False):
                entry["used"] = True

        # Memory-Log komplett neu schreiben mit updated Status
        rewrite_memory(history)
    print("💬 Nira ist nun Wach. Schreibe 'exit' oder 'quit' zum Beenden.\n")

    while True:
        user = input("Du: ").strip()
        if user.lower() in {"exit", "quit", "bye"}:
            break

        # Lade komplette History
        history = load_memory()

        # Speichere neue User-Eingabe mit used=False
        save_memory("user", user, used=False)
        history.append({"timestamp": datetime.datetime.utcnow().isoformat(), "role": "user", "content": user, "used": False})

        # Trenne schon beantwortete (used=True) Nachrichten (egal Rolle)
        answered_msgs = [h for h in history if h.get("used", False)]

        # Neue User-Nachrichten (used=False)
        new_user_msgs = [h for h in history if h["role"] == "user" and not h.get("used", False)]

        # Wichtig: Neue Nira-Nachrichten mit used=False NICHT in Prompt aufnehmen

        # Prompt zusammenbauen:
        prompt = cfg["system_prompt"].strip() + "\n\n"

        # 1. alle bereits beantworteten Nachrichten (user + nira, used=True)
        for h in answered_msgs:
            role = h["role"]
            content = h.get("content") or ""
            if role == "user":
                prompt += f"User: {content}\n"
            elif role == "nira":
                prompt += f"Nira: {content}\n"

        # 2. alle neuen User-Nachrichten (used=False)
        for h in new_user_msgs:
            prompt += f"User: {h['content']}\n"

        prompt += "Nira: "

        # Antwort generieren
        response = llm(
            prompt, max_tokens=cfg["max_tokens"], temperature=cfg["temperature"]
        )["choices"][0]["text"].strip()

        print("Nira:", response)

        # Neue Nira-Antwort speichern (used=False, noch nicht als verwendet markiert)
        save_memory("nira", response, used=False)
        history.append({"timestamp": datetime.datetime.utcnow().isoformat(), "role": "nira", "content": response, "used": False})

        # Alle gerade verarbeiteten User-Nachrichten auf used=True setzen
        for entry in history:
            if entry in new_user_msgs:
                entry["used"] = True

        # Alle bisher unbenutzten Nira-Antworten auf used=True setzen (damit sie im Kontext landen)
        for entry in history:
            if entry["role"] == "nira" and not entry.get("used", False):
                entry["used"] = True

        # Memory-Log komplett neu schreiben mit aktualisiertem Status
        rewrite_memory(history)

# === START ===
if __name__ == "__main__":
    chat()
