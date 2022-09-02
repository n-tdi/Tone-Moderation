from tabnanny import check
import torch
import json
from transformers import AutoTokenizer, AutoModelForSequenceClassification

tokenizer = AutoTokenizer.from_pretrained("pysentimiento/bertweet-hate-speech")

model = AutoModelForSequenceClassification.from_pretrained("pysentimiento/bertweet-hate-speech")

with open('./config.json') as f:
  data = json.load(f)
  for c in data['botConfig']:
     print('Token: ' + c['token'])

def rank(text: str):
    inputs = tokenizer(text, return_tensors="pt")
    with torch.no_grad():
        logits = model(**inputs).logits
        
    return {'hateful': logits[0][0].item(), 'targeted': logits[0][1].item(), 'aggressive': logits[0][2].item()}

def checks(rank):
    flagged = False
    print(rank)
    if rank['hateful'] > 1 and rank['targeted'] > 1 and rank['aggressive'] > -1.5:
        flagged = True
        
    return flagged

import discord

intents = discord.Intents.default()
intents.members = True
intents.messages = True

class MyClient(discord.Client):
    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))

    async def on_message(self, message):
        if checks(rank(message.content)):
            await message.delete()

client = MyClient(intents=intents)
client.run(c['token'])