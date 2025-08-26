from dotenv import load_dotenv
load_dotenv() 
import json
import os
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from langdetect import detect
from rasa_sdk.events import SlotSet

class ActionDetectAndRespondMultilang(Action):
    def name(self) -> Text:
        return "action_detect_and_respond_multilang"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        message_text = tracker.latest_message.get('text', '')
        intent = tracker.latest_message['intent'].get('name')
        confidence = tracker.latest_message['intent'].get('confidence', 0.0)

        # Detect language
        try:
            lang = detect(message_text)
        except Exception:
            lang = 'en'

        language = 'EN'
        if lang.startswith('th'):
            language = 'TH'
        elif lang.startswith('ja'):
            language = 'JA'

        # Load local responses
        response_path = r"C:\KOSEN\PBL3\chat_bot_model\data\responses.json"
        try:
            with open(response_path, "r", encoding="utf-8") as file:
                responses = json.load(file)
        except Exception:
            dispatcher.utter_message(text={
                "TH": "ขออภัย โหลดข้อมูลไม่ได้ค่ะ",
                "JA": "申し訳ありませんが、データを読み込めませんでした。",
                "EN": "Sorry, failed to load data."
            }.get(language, "Sorry, failed to load data."))
            return []

        # Try to get response from local file
        response_text = responses.get(intent, {}).get(language)

        # If confidence ต่ำหรือไม่มี response ให้ตอบ fallback message ตามภาษา
        if confidence < 0.6 or not response_text:
            fallback_messages = {
                "TH": "เรื่องของแม่มึงค่ะอีดอก ถามใหม่ดิ อีบ้า~ หรือจะลองเลือกคำถามจากตัวอย่างก็ได้นะจ๊ะ",
                "JA": "あんたの質問、マジでわからないわよバカ！もう一回言ってみなさいよ、アホか！それかサンプル質問選びなさいよね〜",
                "EN": "Girl, that question is totally cray-cray! Try again, silly~ or pick from the sample questions, honey!"
            }
            response_text = fallback_messages.get(language, fallback_messages["EN"])

        dispatcher.utter_message(text=response_text)
        return [SlotSet("detected_language", language)]
