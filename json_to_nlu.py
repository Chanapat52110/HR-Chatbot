import json
import yaml
from pathlib import Path
import logging

# ตั้งค่า logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class JsonToNluConverter:
    def __init__(self, json_path: Path, nlu_path: Path):
        self.json_path = json_path
        self.nlu_path = nlu_path

    def convert(self) -> bool:
        """แปลงไฟล์ JSON เป็น NLU format ที่ Rasa รองรับ"""
        try:
            # โหลดข้อมูลจาก JSON
            logger.info(f"📂 Reading JSON from: {self.json_path}")
            with open(self.json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # ตรวจสอบโครงสร้างพื้นฐาน
            if not isinstance(data, dict) or "intents" not in data:
                raise ValueError("❌ Invalid JSON structure: missing 'intents' key")

            # สร้างโครงสร้าง NLU
            nlu_data = {
                "version": "3.1",
                "nlu": []
            }

            for intent, intent_data in data["intents"].items():
                if not isinstance(intent_data, dict) or "examples" not in intent_data:
                    logger.warning(f"⚠️ Skipped invalid intent format: {intent}")
                    continue

                examples = [
                    f"- {example['text']}"
                    for example in intent_data["examples"]
                    if isinstance(example, dict) and "text" in example
                ]

                if examples:
                    nlu_data["nlu"].append({
                        "intent": intent,
                        "examples": "\n".join(examples)
                    })
                    logger.info(f"✅ Processed intent: {intent} ({len(examples)} examples)")

            # เขียน YAML ไฟล์
            logger.info(f"📝 Writing NLU data to: {self.nlu_path}")
            with open(self.nlu_path, 'w', encoding='utf-8') as f:
                yaml.dump(nlu_data, f, allow_unicode=True, sort_keys=False)

            logger.info("✅ Conversion completed successfully.")
            return True

        except Exception as e:
            logger.error(f"❌ Conversion error: {str(e)}")
            return False
