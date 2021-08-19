import discord
import os
from replit import db


client = discord.Client()

@client.event
async def on_ready():
  print("I'm ready. Logged in as {0.user}".format(client))
  db["game_values"] = {"created": False}

@client.event
async def on_message(message):
  if message.author == client.user:
    return
  
  #row = "┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼\n┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼\n┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼\n┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼\n┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼\n┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼\n┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼\n┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼\n┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼\n┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼\n┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼\n┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼\n┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼\n┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼\n┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼\n┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼\n┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼\n┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼\n┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼\n┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼"
  if message.content == "/help":
    msg = "This is a game test. For rules run /rules. To create a game run /createGame. To join the game type /join. To add an icon type /icon <emoji>. To start the game type /start."
    await message.channel.send(msg)

  if message.content == "/rules":
    msg = "To win, be the last to survive. You have three lives. Each round you get 5 mana. You can use mana to move, attack, or defend yourself. In addition, you can trade or gamble your mana."
    await message.channel.send(msg)

  if message.content == "/createGame":
    db["game_values"]["started"] = False
    db["game_values"]["created"] = True
    db["users"] = []
    msg = "Created a game. You need at least three players to start. To join the game type the command /join"
    await message.channel.send(msg)

  if message.content == "/join":
    if (not db["game_values"]["created"]):
      msg = "Sorry, but you must create a game before joining."
    elif (db["game_values"]["started"]):
      msg = "Sorry, but you cannot join as the game has already started"
    else:
      newPlayer = str(message.author)
      if newPlayer in db["users"].value:
        msg = "You have already joined the game"
      else:
        db["users"].append(newPlayer)
        db[newPlayer] = {}
        msg = "{0} joined the game. Add a emoji for your user by typing /icon <emoji>".format(message.author)
    await message.channel.send(msg)

  if message.content == "/playerList":
    if (not db["game_values"]["created"]):
      msg = "Sorry, but you must create a game before checking the playerList."
    else:
      msg = "Current Players: \n"
      for player in db["users"].value:
        msg += str(db[player]["icon"] + " " + player + "\n")
    await message.channel.send(msg)

  if message.content.startswith("/icon"):
    if (not db["game_values"]["created"]):
      msg = "Sorry, but you must create a game before changing your icon."
    elif (db["game_values"]["started"]):
      msg = "Sorry, but you cannot change your icon as the game has already started"
    elif str(message.author) not in db["users"].value:
      msg = "Sorry, but you must join the game before changing your icon."
    msg_list = list(message.content.split(" "))
    if len(msg_list) != 2:
      msg = "bad command. Need one argument /icon <emoji>"
    else:
      icon = msg_list[1]
      db[str(message.author)]["icon"] = icon
      msg = "Your new icon is " + icon

    await message.channel.send(msg)

  if message.content == "/start":
    if (not db["game_values"]["created"]):
      msg = "Sorry, but you must create a game before starting a game."
    elif (db["game_values"]["started"]):
      msg = "Sorry, but you cannot start a game as one has already started."
    msg = "The game is starting."
    await message.channel.send(msg)


bot_token = os.environ['bot_token']
client.run(bot_token)
