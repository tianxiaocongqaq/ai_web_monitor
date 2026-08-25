import os
import json
import hashlib
import requests
from bs4 import BeautifulSoup
from openai import OpenAI

DATA_DIR = "./data"
CONFIG_PATH = "config.json"
os.makedirs(DATA_DIR, exist_ok=True)

def load_config():
    if not os.path.exists(CONFIG_PATH):
        return {"openai_api_key": "YOUR_OPENAI_API_KEY", "tasks": []}
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_config(config):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

def fetch_page_text(url: str) -> str:
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    resp = requests.get(url, headers=headers, timeout=15)
    resp.encoding = resp.apparent_encoding or 'utf-8'
    soup = BeautifulSoup(resp.text, "html.parser")
    for element in soup(["script", "style", "nav", "footer"]):
        element.decompose()
    return soup.get_text(separator="\n", strip=True)

def add_monitor_task(task_id: str, name: str, url: str, prompt: str) -> dict:
    config = load_config()
    new_task = {"id": task_id, "name": name, "url": url, "prompt": prompt}
    existing = [t for t in config["tasks"] if t["id"] == task_id]
    if existing:
        config["tasks"].remove(existing[0])
    config["tasks"].append(new_task)
    save_config(config)
    return {"status": "success", "message": f"任务 [{name}] 已成功添加/更新。"}

def run_monitor_check(task_id: str = None) -> list:
    config = load_config()
    results = []
    tasks = config["tasks"]
    if task_id:
        tasks = [t for t in tasks if t["id"] == task_id]
        
    for task in tasks:
        tid = task["id"]
        cache_file = os.path.join(DATA_DIR, f"{tid}.hash")
        try:
            text = fetch_page_text(task["url"])
            current_hash = hashlib.md5(text.encode("utf-8")).hexdigest()
            last_hash = None
            if os.path.exists(cache_file):
                with open(cache_file, "r") as f:
                    last_hash = f.read().strip()
                    
            if current_hash != last_hash:
                client = OpenAI(
                    api_key=config.get("openai_api_key", os.getenv("OPENAI_API_KEY")),
                    base_url=config.get("openai_base_url", "https://api.openai.com/v1")
                )
                system_prompt = "你是一个网页内容变动分析助手。判断页面文本是否符合用户条件需求。"
                user_prompt = f"规则：{task['prompt']}\n\n最新文本：\n{text[:3000]}"
                
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.2
                )
                ai_output = response.choices[0].message.content
                with open(cache_file, "w") as f:
                    f.write(current_hash)
                    
                results.append({
                    "task_id": tid,
                    "task_name": task["name"],
                    "changed": True,
                    "ai_analysis": ai_output
                })
            else:
                results.append({
                    "task_id": tid,
                    "task_name": task["name"],
                    "changed": False,
                    "message": "页面内容无更新"
                })
        except Exception as e:
            results.append({"task_id": tid, "error": str(e)})
            
    return results
