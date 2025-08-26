import os
import time
import schedule
from datetime import datetime
from pathlib import Path
import shutil
import logging
import json  # เพิ่ม import นี้
from json_to_nlu import JsonToNluConverter

# ตั้งค่า logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('model_training.log'),
        logging.StreamHandler()
    ]
)

class ModelTrainer:
    def __init__(self):
        self.models_dir = Path("models")
        self.cache_dir = Path(".rasa")
        self.data_dir = Path("data")
        self.json_path = self.data_dir / "questions.json"
        self.nlu_path = self.data_dir / "nlu.yml"
        self.keep_models = 2
        self.nlu_converter = JsonToNluConverter(self.json_path, self.nlu_path)

        # สร้างโฟลเดอร์หากไม่มี
        self.models_dir.mkdir(exist_ok=True)
        self.data_dir.mkdir(exist_ok=True)

    def train_model(self):
        """ฝึกโมเดลใหม่ด้วยคำสั่ง rasa train"""
        try:
            logging.info("Starting model training process...")
            start_time = datetime.now()
            
            # ตรวจสอบว่าไฟล์ JSON มีอยู่
            if not self.json_path.exists():
                self._create_default_questions_file()
                logging.warning(f"Created new questions.json at {self.json_path}")

            # แปลง questions.json เป็น nlu.yml
            logging.info("Converting JSON to NLU format...")
            if not self.nlu_converter.convert():
                raise Exception("JSON to NLU conversion failed")
            
            # ฝึกโมเดล
            logging.info("Training new model...")
            train_result = os.system("rasa train --quiet")
            if train_result != 0:
                raise Exception(f"Rasa train failed with exit code {train_result}")
            
            # จัดการโมเดลเก่า
            self.clear_old_models()
            self.clear_cache()
            
            duration = (datetime.now() - start_time).total_seconds()
            logging.info(f"Training completed in {duration:.2f} seconds")
            return True
            
        except Exception as e:
            logging.error(f"Training failed: {str(e)}")
            return False

    def _create_default_questions_file(self):
        """สร้างไฟล์ questions.json เริ่มต้นหากไม่มี"""
        default_content = {
            "version": "1.0",
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "total_examples": 0
            },
            "intents": {}
        }
        with open(self.json_path, 'w', encoding='utf-8') as f:
            json.dump(default_content, f, indent=2, ensure_ascii=False)

    def clear_old_models(self):
        """ลบโมเดลเก่า เหลือไว้เฉพาะล่าสุด"""
        try:
            if not self.models_dir.exists():
                return
                
            models = sorted(
                [f for f in os.listdir(self.models_dir) if f.endswith(".tar.gz")],
                key=lambda x: os.path.getmtime(self.models_dir / x),
                reverse=True
            )
            
            for old_model in models[self.keep_models:]:
                model_path = self.models_dir / old_model
                os.remove(model_path)
                logging.info(f"Removed old model: {old_model}")
        except Exception as e:
            logging.error(f"Failed to clear old models: {str(e)}")

    def clear_cache(self):
        """ลบ cache directory"""
        try:
            if self.cache_dir.exists():
                shutil.rmtree(self.cache_dir)
                logging.info("Cleared Rasa cache directory")
        except Exception as e:
            logging.error(f"Failed to clear cache: {str(e)}")

    def start_scheduler(self, interval_minutes: int = 15):
        """เริ่มการทำงานแบบ scheduled"""
        # ฝึกโมเดลทันทีที่เริ่ม
        self.train_model()
        
        # ตั้งเวลาให้ฝึกโมเดลตามช่วงเวลาที่กำหนด
        schedule.every(interval_minutes).minutes.do(self.train_model)
        
        logging.info(f"Scheduler started. Training every {interval_minutes} minutes...")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            logging.info("Scheduler stopped by user")

if __name__ == "__main__":
    trainer = ModelTrainer()
    trainer.start_scheduler(interval_minutes=15)