import discord
import os
from replit import db

rows = 17
columns = 36

client = discord.Client()

@client.event
async def on_ready():
  print("I'm ready. Logged in as {0.user}".format(client))
  db.clear()
  db["game_values"] = {"created": False, "wantingToEndGame": False, "usersWantingToEndgame": []}

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
        db[newPlayer] = {"icon": newPlayer[0]}
        msg = "{0} joined the game. Add a emoji for your user by typing /icon <emoji>".format(message.author)
    await message.channel.send(msg)

  if message.content == "/playerList":
    if (not db["game_values"]["created"]):
      msg = "Sorry, but you must create a game before checking the playerList."
    else:
      msg = "Current Players (icon - playerName): \n"
      for player in db["users"].value:
        msg += str(db[player]["icon"] + " - " + player + "\n")
    await message.channel.send(msg)

  if message.content.startswith("/icon"):
    if (not db["game_values"]["created"]):
      msg = "Sorry, but you must create a game before changing your icon."
    elif (db["game_values"]["started"]):
      msg = "Sorry, but you cannot change your icon as the game has already started"
    elif str(message.author) not in db["users"].value:
      msg = "Sorry, but you must join the game before changing your icon."
    else:
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
    else:
      msg = "The game is starting."
      db["game_values"]["started"] = True
      # Put all the players into random locations
      for user in db["users"].value:
        db[user]["location"] = (8, 18)
      # Visualize
      visualize()
      # Start First Round
    await message.channel.send(msg)

  if message.content == "/endGame":
    if (not db["game_values"]["created"]):
      msg = "Sorry, but you must create a game before ending a game."
    elif (not db["game_values"]["started"]):
      db.clear()
      db["game_values"] = {"created": False, "wantingToEndGame": False, "usersWantingToEndgame": []}
      msg = "Successfully ended the game"
    else:
      msg = "Are you sure you want to end the game? All the progress for everyone will be lost. At least two people must respond with \"yes\" for the game to end. If someone types \"no\" the game will continue."
      db["game_values"]["wantingToEndGame"] = True
    await message.channel.send(msg)
  
  if message.content == "yes" and db["game_values"]["wantingToEndGame"]:
    if str(message.author) not in db["game_values"]["usersWantingToEndgame"].value:
      db["game_values"]["usersWantingToEndgame"].append(str(message.author))
    if len(db["game_values"]["usersWantingToEndgame"]) == 2:
      db.clear()
      db["game_values"] = {"created": False, "wantingToEndGame": False, "usersWantingToEndgame": []}
      msg = "Successfully ended the game"

  if message.content.startswith("/move"):
    if (not db["game_values"]["created"]):
      msg = "Sorry, but you must create a game before doing this action."
    elif (not db["game_values"]["started"]):
      msg = "Sorry, but you must start a game before doing this action."
    elif str(message.author) not in db["users"].value:
      msg = "Sorry, but you must have joined the game before it started to do this action."
    else:
      msg_list = list(message.content.split(" "))
      if len(msg_list) != 3:
        msg = "bad command. Need two argument /move <direction> <distance>. Directions are left, right, up, and down."
      print(db[str(message.author)]["location"])
      # Update Player Location
      if msg_list[1] == "left":
        direction = (0, -int(msg_list[2]))
      elif msg_list[1] == "right":
        direction = (0, int(msg_list[2]))
      elif msg_list[1] == "up":
        direction = (-int(msg_list[2]), 0)
      elif msg_list[1] == "down":
        direction = (int(msg_list[2]), 0)
      db[str(message.author)]["location"] = add(db[str(message.author)]["location"], direction)
      print(db[str(message.author)]["location"])
      # Visualize
      msg = visualize(db[str(message.author)]["location"])
      # 
    await message.channel.send(msg)

bot_token = os.environ['bot_token']
client.run(bot_token)

def add(coords, direction):
  return coords[0] + direction[0], coords[1] + direction[1]

def visualize(temp):
  currMap = ""
  for i in range(rows):
    for j in range(columns):
      if (i,j) == temp:
        "0"
      else:
        currMap += "┼"
    currMap += "\n"
  return currMap
