import requests,json

response = requests.post("http://127.0.0.1:8000/emails/submit",json=json.dumps({
    "content":"test@abc123.xyz"
}))
