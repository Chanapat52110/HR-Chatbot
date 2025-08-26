import os
import threading
import logging
from train_scheduler import ModelTrainer
from rasa.core.agent import Agent
from rasa.shared.utils.io import json_to_string
import time

# ตั้งค่า logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('system.log'),
        logging.StreamHandler()
    ]
)

class ChatbotSystem:
    def __init__(self):
        self.trainer = ModelTrainer()
        self.agent = None
        self.running = False

    def start_training_scheduler(self):
        """เริ่มการฝึกโมเดลตามตารางเวลา"""
        self.trainer.start_scheduler()

    def load_rasa_agent(self):
        """โหลด Rasa agent"""
        try:
            # หาโมเดลล่าสุด
            model_files = sorted(
                [f for f in os.listdir("models") if f.endswith(".tar.gz")],
                key=lambda x: os.path.getmtime(os.path.join("models", x)),
                reverse=True
            )
            
            if not model_files:
                logging.error("No model files found in models directory")
                return False
            
            latest_model = os.path.join("models", model_files[0])
            logging.info(f"Loading model: {latest_model}")
            
            self.agent = Agent.load(latest_model)
            return True
        except Exception as e:
            logging.error(f"Failed to load Rasa agent: {str(e)}")
            return False

    def start(self):
        """เริ่มการทำงานของระบบ"""
        self.running = True
        
        # เริ่ม training scheduler ใน thread แยก
        scheduler_thread = threading.Thread(
            target=self.start_training_scheduler,
            daemon=True,
            name="TrainingScheduler"
        )
        scheduler_thread.start()
        
        # โหลด Rasa agent
        if not self.load_rasa_agent():
            logging.error("Failed to initialize Rasa agent. Exiting.")
            return
        
        logging.info("System is running. Training will happen automatically every 15 minutes.")
        
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            logging.info("Shutting down system...")
            self.running = False

if __name__ == "__main__":
    system = ChatbotSystem()
    system.start()