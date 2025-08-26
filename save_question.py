import json
from pathlib import Path
from typing import Dict, List, Optional
import yaml
import os
from datetime import datetime

class QuestionManager:
    def __init__(self, json_path: str = "C:\KOSEN\PBL3\chat_bot_model\data\questions.json", nlu_path: str = "data/nlu.yml"):
        self.json_path = Path(json_path)
        self.nlu_path = Path(nlu_path)
        self.ensure_files_exist()
    
    def ensure_files_exist(self):
        """สร้างไฟล์ถ้ายังไม่มี"""
        # สำหรับไฟล์ JSON
        if not self.json_path.exists():
            self.json_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.json_path, 'w', encoding='utf-8') as f:
                json.dump({
                    "version": "1.0",
                    "metadata": {
                        "created_at": datetime.now().isoformat(),
                        "last_updated": datetime.now().isoformat(),
                        "total_examples": 0
                    },
                    "intents": {}
                }, f, ensure_ascii=False, indent=2)
        
        # สำหรับไฟล์ NLU
        if not self.nlu_path.exists():
            self.nlu_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.nlu_path, 'w', encoding='utf-8') as f:
                yaml.dump({
                    "version": "3.1",
                    "nlu": []
                }, f, allow_unicode=True)
    
    def add_question(self, intent: str, question: str, confidence: Optional[float] = None):
        """เพิ่มคำถามใหม่พร้อมบันทึก metadata"""
        data = self.load_json_data()
        
        # ทำความสะอาดคำถาม
        cleaned_question = question.strip()
        if not cleaned_question:
            return False
        
        # ตรวจสอบว่าไม่มีคำถามนี้อยู่แล้ว
        if intent not in data["intents"]:
            data["intents"][intent] = {
                "examples": [],
                "metadata": {
                    "count": 0,
                    "last_added": None
                }
            }
        
        # ตรวจสอบคำถามซ้ำ
        existing_questions = [ex["text"].lower() for ex in data["intents"][intent]["examples"]]
        if cleaned_question.lower() not in existing_questions:
            new_question = {
                "text": cleaned_question,
                "added_at": datetime.now().isoformat(),
                "confidence": confidence,
                "source": "user"
            }
            data["intents"][intent]["examples"].append(new_question)
            data["intents"][intent]["metadata"]["count"] += 1
            data["intents"][intent]["metadata"]["last_added"] = datetime.now().isoformat()
            data["metadata"]["total_examples"] += 1
            data["metadata"]["last_updated"] = datetime.now().isoformat()
            
            self.save_json_data(data)
            self.update_nlu_file()
            return True
        return False
    
    def load_json_data(self) -> Dict:
        """โหลดข้อมูลจากไฟล์ JSON"""
        with open(self.json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def save_json_data(self, data: Dict):
        """บันทึกข้อมูลลงไฟล์ JSON"""
        with open(self.json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def update_nlu_file(self):
        """อัปเดตไฟล์ nlu.yml จากข้อมูลใน JSON"""
        json_data = self.load_json_data()
        
        nlu_data = {
            "version": "3.1",
            "nlu": []
        }
        
        for intent, intent_data in json_data["intents"].items():
            examples = "\n".join([f"- {ex['text']}" for ex in intent_data["examples"]])
            nlu_data["nlu"].append({
                "intent": intent,
                "examples": examples
            })
        
        with open(self.nlu_path, 'w', encoding='utf-8') as f:
            yaml.dump(nlu_data, f, allow_unicode=True, sort_keys=False)
    
    def get_all_questions(self) -> Dict[str, List[str]]:
        """ดึงคำถามทั้งหมด"""
        data = self.load_json_data()
        return {
            intent: [ex["text"] for ex in intent_data["examples"]]
            for intent, intent_data in data["intents"].items()
        }

# ตัวอย่างการใช้งาน
if __name__ == "__main__":
    manager = QuestionManager()
    manager.add_question("greet", "สวัสดีตอนบ่าย", confidence=0.4)