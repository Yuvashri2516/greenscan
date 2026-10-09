import requests

res1 = requests.post("https://greenscan-api-4rhz.onrender.com/chat", json={'message': 'hello'})
print("EN:", res1.json())

res2 = requests.post("https://greenscan-api-4rhz.onrender.com/chat", json={'message': 'வணக்கம்'})
print("TA:", res2.json()['reply'])

res3 = requests.post("https://greenscan-api-4rhz.onrender.com/chat", json={'message': 'नमस्ते'})
print("HI:", res3.json()['reply'])
