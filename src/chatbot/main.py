from google import genai
from google.genai import types

client = genai.Client(api_key='AIzaSyDPBGRJ1sj2NMI7M-Qji5fnoI5J6nWhxgs')
chat = client.chats.create(model="gemini-2.5-flash")

print("Simple chat test")
userinput = input("User : ")

while userinput != 'endchat':
    response = chat.send_message(userinput)
    print("Databot : " + response.text)
    userinput = input("User : ")