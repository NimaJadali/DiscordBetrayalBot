import discord
import os
from replit import db
from random import randint
import time
import numpy as np

rows = 20
columns = 23
attackRange = 4
tradeRange = 8
client = discord.Client()


def add(coords, direction):
  return coords[0] + direction[0], coords[1] + direction[1]


def visualize():
  currMap = np.full((rows, columns), "+   ")
  for key in db["game_values"]["coord_player"]:
    coords = list(key.split(" "))
    player = db["game_values"]["coord_player"][key]
    if (db[player]["id"] < 10):
      currMap[int(coords[0]), int(coords[1])] = str(db[player]["id"]) + "   "
    else:
      currMap[int(coords[0]), int(coords[1])] = str(db[player]["id"] + "  ")
  currMap = np.concatenate((currMap, np.full((rows,1)," \n  ")), axis=1)
  currMapStr = "  " + currMap.astype('|S4').tobytes().decode('UTF-8')
  for key in db["game_values"]["coord_player"]:
    player = db["game_values"]["coord_player"][key]
    if (db[player]["id"] < 10):
      currMapStr = currMapStr.replace("  " + str(db[player]["id"]) + "  ", db[player]["icon"])
    else:
      currMapStr = currMapStr.replace("  " + str(db[player]["id"]) + " ", db[player]["icon"])
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
    msg = "This is a game test. \n/rules shows the game rules. \n/createGame instantiates a game. \n/join to join the game type. \n/playerList gets the list of all the players. \n/icon <emoji> adds an icon type. \n/start to start the game. \n /endGame ends the current game and resets all the saved data. \n/move <direction> <distance> moves your character. Directions are \"left\",\"right\",\"up\", and \"down\". \n/attack <player> <damage> to attack a player if they are within range (4) dealing the specified damage. \n/deal <player> <amount> transfer a specified amount of money to an inrange (8) player.\n/defense <defense_amount> Give youself the specified amount of defense lasting only the current round.\map"
    await message.channel.send(msg)

  if message.content == "/rules":
    msg = "To win, be the last to survive. You have three hearts. Lose all your hearts and you die. \nEach round you get 5 mana. You can use mana to move, attack, or defend yourself. \nIn addition, you can trade or gamble your mana. \nYou cannot move out of bounds or where another player currently is. Each coordinate you move takes up one mana. \n Each quantity of attack and defense uses up one mana as well. Defense is like temporary health that only lasts a round.\n Both attacking (4) and dealing (8) have a maximum target range."
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
        db[newPlayer] = {"icon": newPlayer[0], 'id': db["game_values"]["player_count"], "health": 3, "defense": 3, "mana": 25}
        db["game_values"]["player_count"] += 1
        msg = "{0} joined the game. Add a emoji for your user by typing /icon <emoji>".format(message.author)
    await message.channel.send(msg)

  if message.content == "/playerList":
    if (not db["game_values"]["created"]):
      msg = "Sorry, but you must create a game before checking the playerList."
    else:
      msg = "Current Players: \n"
      if db["game_values"]["started"]:
        for player in db["users"].value:
          msg += str(db[player]["icon"]) + "  " + player + "  Coords: " + str(db[player]["location"].value) + "  Health: " + str(db[player]["health"]) + "  Defense: " + str(db[player]["defense"]) + "  Mana: " + str(db[player]["mana"]) + "\n"
      else:
        for player in db["users"].value:
          msg += str(db[player]["icon"]) + "  " + player + "\n"
      
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
    msg_list = list(message.content.split(" "))
    # Check the arguments 
    if len(msg_list) != 3:
      msg = "bad command. Need two argument /move <direction> <distance>. Directions are left, right, up, and down."
      fail = True
    try:
      dist = int(msg_list[2])
      fail = False
      if (dist < 0):
        fail = True
        msg = "Enter a positive integer you cheater"
    except:
      msg = "Enter an integer for the move distance"
      fail = True

    if (not db["game_values"]["created"]):
      msg = "Sorry, but you must create a game before doing this action."
    elif (not db["game_values"]["started"]):
      msg = "Sorry, but you must start a game before doing this action."
    elif str(message.author) not in db["users"].value:
      msg = "Sorry, but you must have joined the game before it started to do this action."
    elif dist > db[str(message.author)]["mana"]:
        msg = "Not enough mana. You have " + str(db[str(message.author)]["mana"]) + " mana."
    elif not fail:
      # Update Player Location
      if msg_list[1] == "left":
        direction = (0, -dist)
      elif msg_list[1] == "right":
        direction = (0, dist)
      elif msg_list[1] == "up":
        direction = (-dist, 0)
      elif msg_list[1] == "down":
        direction = (dist, 0)
      else:
        msg = "invalid direction"
        await message.channel.send(msg)
        return
      coords = db[str(message.author)]["location"]
      newCoords = add(coords, direction)
      if newCoords[0] < 0 or newCoords[1] < 0 or newCoords[0] > rows - 1 or newCoords[1] > columns - 1:
        msg = "Cannot move out of bounds"
      elif str(newCoords[0]) + " " + str(newCoords[1]) in db["game_values"]["coord_player"]:
        msg = "Cannot move to where a player already exists"
      else:
        db[str(message.author)]["mana"] -= dist
        del db["game_values"]["coord_player"][str(coords[0]) + " " + str(coords[1])]
        db["game_values"]["coord_player"][str(newCoords[0]) + " " + str(newCoords[1])] = str(message.author)
        db[str(message.author)]["location"] = newCoords
        # Visualize
        msg = visualize()
    await message.channel.send(msg)

  if message.content.startswith("/attack"):
    msg_list = list(message.content.split(" "))
    # Check the arguments 
    if len(msg_list) != 3:
      msg = "bad command. Need two argument /attack <player> <damage>. user /playerList for list of players."
      fail = True
    try:
      damage = int(msg_list[2])
      fail = False
      if (damage < 0):
        fail = True
        msg = "Enter a positive integer you cheater"
    except:
      msg = "Enter an integer for the damage"
      fail = True

    if (not db["game_values"]["created"]):
      msg = "Sorry, but you must create a game before doing this action."
    elif (not db["game_values"]["started"]):
      msg = "Sorry, but you must start a game before doing this action."
    elif str(message.author) not in db["users"].value:
      msg = "Sorry, but you must have joined the game before it started to do this action."
    elif msg_list[1] not in db["users"].value:
      msg = "Please enter a valid player name to attack. Type /playerList for all the available players"
    elif not fail:
      targetLoc = db[msg_list[1]]["location"].value
      attackerLoc = db[str(message.author)]["location"].value
      if attackRange < abs(attackerLoc[0] - targetLoc[0]) + abs(attackerLoc[1] - targetLoc[1]):
        msg = "Not in range to attack. Attack Range is 4."
      elif damage > db[str(message.author)]["mana"]:
        msg = "Not enough mana. You have " + str(db[str(message.author)]["mana"]) + " mana."
      else:
        db[str(message.author)]["mana"] -= damage
        remaining_damage = damage - db[msg_list[1]]["defense"]
        remaining_defense = db[msg_list[1]]["defense"] - damage
        if remaining_defense < 0:
          db[msg_list[1]]["defense"] = 0
          db[msg_list[1]]["health"] -= remaining_damage
          # Check if target died
        else:
          db[msg_list[1]]["defense"] = remaining_defense
        msg = "Attacked " + msg_list[1]
    await message.channel.send(msg)

  if message.content.startswith("/deal"):
    msg_list = list(message.content.split(" "))
    # Check the arguments 
    if len(msg_list) != 3:
      msg = "bad command. Need two argument /deal <player> <amount>. user /playerList for list of players."
      fail = True
    try:
      mana_amount = int(msg_list[2])
      fail = False
      if (mana_amount < 0):
        fail = True
        msg = "Enter a positive integer you cheater"
    except:
      msg = "Enter an integer for the transaction amount"
      fail = True

    if (not db["game_values"]["created"]):
      msg = "Sorry, but you must create a game before doing this action."
    elif (not db["game_values"]["started"]):
      msg = "Sorry, but you must start a game before doing this action."
    elif str(message.author) not in db["users"].value:
      msg = "Sorry, but you must have joined the game before it started to do this action."
    elif msg_list[1] not in db["users"].value:
      msg = "Please enter a valid player name to attack. Type /playerList for all the available players"
    elif not fail:
      targetLoc = db[msg_list[1]]["location"].value
      traderLoc = db[str(message.author)]["location"].value
      if tradeRange < abs(traderLoc[0] - targetLoc[0]) + abs(traderLoc[1] - targetLoc[1]):
        msg = "Not in range to make a deal. Deal Range is 8."
      elif mana_amount > db[str(message.author)]["mana"]:
        msg = "Not enough mana. You have " + str(db[str(message.author)]["mana"]) + " mana."
      else:
        db[str(message.author)]["mana"] -= mana_amount
        db[msg_list[1]]["mana"] += mana_amount
        msg = "Succesfully gave " + msg_list[1] + " " + str(mana_amount) + " mana."
    await message.channel.send(msg)

  if message.content.startswith("/defense"):
    msg_list = list(message.content.split(" "))
    # Check the arguments 
    if len(msg_list) != 2:
      msg = "bad command. Need two argument /defense <amount>."
      fail = True
    try:
      defense_amount = int(msg_list[1])
      fail = False
      if (defense_amount < 0):
        fail = True
        msg = "Enter a positive integer you cheater"
    except:
      msg = "Enter an integer for the transaction amount"
      fail = True

    if (not db["game_values"]["created"]):
      msg = "Sorry, but you must create a game before doing this action."
    elif (not db["game_values"]["started"]):
      msg = "Sorry, but you must start a game before doing this action."
    elif str(message.author) not in db["users"].value:
      msg = "Sorry, but you must have joined the game before it started to do this action."
    elif not fail:
      if defense_amount > db[str(message.author)]["mana"]:
        msg = "Not enough mana. You have " + str(db[str(message.author)]["mana"]) + " mana."
      else:
        db[str(message.author)]["mana"] -= defense_amount
        db[str(message.author)]["defense"] += defense_amount
        msg = "Succesfully increased your defense to " + str(defense_amount) + "."
    await message.channel.send(msg)

  if message.content == "/map":
    if (not db["game_values"]["created"]):
      msg = "Sorry, but you must create a game before doing this action."
    elif (not db["game_values"]["started"]):
      msg = "Sorry, but you must start a game before doing this action."
    else:
      msg = visualize()
    await message.channel.send(msg)

  if message.content.startswith("/echo"):
    print(message.content)
    await message.channel.send(message.content)

bot_token = os.environ['bot_token']
client.run(bot_token)
