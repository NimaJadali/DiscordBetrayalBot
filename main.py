import discord
import os
from replit import db
from random import randint
import time
import numpy as np

rows = 20
columns = 23

client = discord.Client()


def add(coords, direction):
  return coords[0] + direction[0], coords[1] + direction[1]


def visualize():
  print(time.time())
  currMap = np.full((rows, columns), "+   ")
  for key in db["game_values"]["coord_player"]:
    coords = list(key.split(" "))
    player = db["game_values"]["coord_player"][key]
    if (db[player]["id"] < 10):
      currMap[int(coords[0]), int(coords[1])] = str(db[player]["id"]) + "   "
    else:
      currMap[int(coords[0]), int(coords[1])] = str(db[player]["id"] + "  ")
  currMap = np.concatenate((currMap, np.full((rows,1)," \n  ")), axis=1)
  print(time.time())
  print(currMap)
  currMapStr = "  " + currMap.astype('|S4').tobytes().decode('UTF-8')
  for key in db["game_values"]["coord_player"]:
    player = db["game_values"]["coord_player"][key]
    if (db[player]["id"] < 10):
      currMapStr = currMapStr.replace("  " + str(db[player]["id"]) + "  ", db[player]["icon"])
    else:
      currMapStr = currMapStr.replace("  " + str(db[player]["id"]) + " ", db[player]["icon"])
  print(len(currMapStr))
  return ". " + currMapStr[2:]


@client.event
async def on_ready():
  print("I'm ready. Logged in as {0.user}".format(client))
  db.clear()
  db["game_values"] = {"created": False, "wantingToEndGame": False, "usersWantingToEndgame": []}


@client.event
async def on_message(message):
  if message.author == client.user:
    return

  if message.content == "/help":
    msg = "This is a game test. For rules run /rules. To create a game run /createGame. To join the game type /join. To add an icon type /icon <emoji>. To start the game type /start."
    await message.channel.send(msg)

  if message.content == "/rules":
    msg = "To win, be the last to survive. You have three lives. Each round you get 5 mana. You can use mana to move, attack, or defend yourself. In addition, you can trade or gamble your mana."
    await message.channel.send(msg)

  if message.content == "/createGame":
    db["game_values"]["started"] = False
    db["game_values"]["created"] = True
    db["game_values"]["player_count"] = 0
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
        db[newPlayer] = {"icon": newPlayer[0], 'id': db["game_values"]["player_count"]}
        db["game_values"]["player_count"] += 1
        msg = "{0} joined the game. Add a emoji for your user by typing /icon <emoji>".format(message.author)
    await message.channel.send(msg)

  if message.content == "/playerList":
    if (not db["game_values"]["created"]):
      msg = "Sorry, but you must create a game before checking the playerList."
    else:
      msg = "Current Players (icon - playerName): \n"
      for player in db["users"].value:
        msg += str(db[player]["icon"]) + " - " + player + "\n"
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
    elif (db["game_values"]["player_count"] < 1):
      msg = "Sorry, but you need more players to start the game."
    else:
      msg = "The game is starting."
      db["game_values"]["started"] = True
      # Put all the players into random locations
      db["game_values"]["coord_player"] = {}
      for user in db["users"].value:
        start_coords = str(randint(0, rows-1)) + " " + str(randint(0,columns-1))
        while start_coords in db["game_values"]["coord_player"]:
          start_coords = str(randint(0, rows-1)) + " " + str(randint(0,columns-1))
        db["game_values"]["coord_player"][start_coords] = user
        coords_list = list(start_coords.split(" "))
        db[user]["location"] = int(coords_list[0]), int(coords_list[1])
      # Visualize
      msg += "\n" + visualize()
      # Start First Round
      print(len(msg))
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
      # Update Player Location
      if msg_list[1] == "left":
        direction = (0, -int(msg_list[2]))
      elif msg_list[1] == "right":
        direction = (0, int(msg_list[2]))
      elif msg_list[1] == "up":
        direction = (-int(msg_list[2]), 0)
      elif msg_list[1] == "down":
        direction = (int(msg_list[2]), 0)
      #TODO: CHECK IF OUT OF BOUNDS OR IF USED BY OTHER PLAYER
      coords = db[str(message.author)]["location"]
      del db["game_values"]["coord_player"][str(coords[0]) + " " + str(coords[1])]
      newCoords = add(coords, direction)
      db["game_values"]["coord_player"][str(newCoords[0]) + " " + str(newCoords[1])] = str(message.author)
      db[str(message.author)]["location"] = newCoords
      # Visualize
      msg = visualize()
      # 
    await message.channel.send(msg)

bot_token = os.environ['bot_token']
client.run(bot_token)
