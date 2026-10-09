import asyncio
from chatbot import get_chat_response

async def main():
    print("Testing Language Detection")
    context = {"disease_name": "tomato_Early blight", "display_name": "Tomato Early Blight", "confidence": 95.0, "severity_level": "Moderate"}
    
    tests = [
        ("en", "How can I protect my tomato plants from early blight?"),
        ("en", "எனக்கு உதவி வேண்டும்"), # Tamil question with EN button
        ("en", "टमाटर के पौधों को अर्ली ब्लाइट से कैसे बचाएं?"), # Hindi question with EN button
        ("ta", "What should I do now?"), # English question with TA button
        ("hi", " வானிலை இதை பாதிக்குமா?"), # Tamil question with HI button
        ("ta", "movie"), # Unrelated question in english with TA button
        ("en", "how much spray"), # Dosage in English
        ("hi", "spray amount?"), # Dosage in English with HI button
    ]
    
    for btn_lang, msg in tests:
        res = await get_chat_response(message=msg, language=btn_lang, context=context)
        print(f"\n[Input ({btn_lang} button)]: {msg}")
        print(f"[Output]: {res['reply'][:100]}...")

if __name__ == "__main__":
    asyncio.run(main())
