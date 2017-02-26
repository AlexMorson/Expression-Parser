import os

import discord

import expressionParser
import renderer

async def sendExpression(expression, channel):
    parsedExpression = expressionParser.Expression(expression)
    expressionImage = renderer.renderExpression(parsedExpression)
    expressionImage.save("temp.png")
    await client.send_file(channel, "temp.png")
    os.remove("temp.png")

client = discord.Client()

@client.event
async def on_ready():
    print("Logged in as", client.user.name)

@client.event
async def on_message(message):
    if message.content.startswith("!parse"):
        try:
            expression = message.content[len("!parse"):]
            await sendExpression(expression, message.channel)
        except Exception as e:
            print(e)
            await client.send_message(message.channel, "I can't understand the expression :frowning:")
    
client.run("token")
