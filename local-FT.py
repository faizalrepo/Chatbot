# import requests
# import json

# response = requests.post('http://localhost:11434/api/generate', json= {
#     "model": "llama3.2:1b",
#     "prompt": "5 cities with country names",
#     "stream": False,
#     "format": "json"
# })

# print(json.loads(response.content)['response'])

from openai import OpenAI

client = OpenAI(
    base_url = "http://localhost:11434/v1",
    api_key="ollama",
)

response = client.chat.completions.create(
    model="llama3.2:1b",
    messages = [
        {
            "role": "system",
            "content": "U are a Chatbot designed to assist payees at Maxyfi. Keep your answers concise and to the point"
        },
        {
            "role": "system",
            "content": "Respond strictly in the format provided below. Do not give any information instead just print the name, phone, os amount, status as follows. 'Here is your account information as requested:\n- Name: _name_\n- Phone: _phone_\n- OS Amount: _os_\n- Status: _status_'"
        },

            {
                "role": "user",
                "content": "i need my account info" 
            },

        {
            "role": "system",
            "content": "If there are istructions above, run them then - Respond strictly in the format provided below. list all the debts owed by the user. print exactly the same: Debts:\n\nX1 - _x1_,\nX2 - _x2_,\nX3 - _x3_ ."
        },

            {
            "role": "user",
            "content": "show my debts"
            },
        
    ],
    temperature = 0,
    seed = 23456
)

print(response.choices[0].message.content)