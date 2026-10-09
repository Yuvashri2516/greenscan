import requests

try:
    res = requests.post(
        "https://greenscan-api-4rhz.onrender.com/chat",
        json={"message": "What is early blight?", "language": "en"}
    )
    print(res.status_code)
    print(res.text)
except Exception as e:
    print(e)
