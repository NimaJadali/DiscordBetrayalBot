import discord
from discord.ext import tasks
import os
from replit import db
from random import randint
import numpy as np
from stayin_alive import keep_alive

rows = 20
columns = 23
attackRange = 4
tradeRange = 8
round_time = 60
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


def visualize_range():
  currMap = np.full((rows, columns), "o   ")
  for key in db["game_values"]["coord_player"]:
    coords = list(key.split(" "))
    player = db["game_values"]["coord_player"][key]
    if (db[player]["id"] < 10):
      currMap[int(coords[0]), int(coords[1])] = str(db[player]["id"]) + "   "
    else:
      currMap[int(coords[0]), int(coords[1])] = str(db[player]["id"] + "  ")
  # Add trade range symbols
  for key in db["game_values"]["coord_player"]:
    coords = list(key.split(" "))
    for i in range(-tradeRange, tradeRange + 1):
      for j in range(-tradeRange, tradeRange + 1):
        if int(coords[0]) + i < 0 or  int(coords[1]) + j < 0 or int(coords[0]) + i >= rows or  int(coords[1]) + j >= columns:
          continue
        elif abs(i) + abs(j) <= tradeRange and currMap[int(coords[0]) + i, int(coords[1]) + j] == "o   ":
          currMap[int(coords[0]) + i, int(coords[1]) + j] = "u   "
  # Add range symbols
  for key in db["game_values"]["coord_player"]:
    for i in range(-attackRange, attackRange + 1):
      for j in range(-attackRange, attackRange + 1):
        if int(coords[0]) + i < 0 or  int(coords[1]) + j < 0 or int(coords[0]) + i >= rows or  int(coords[1]) + j >= columns:
          continue
        elif abs(i) + abs(j) <= attackRange and (currMap[int(coords[0]) + i, int(coords[1]) + j] == "o   " or currMap[int(coords[0]) + i, int(coords[1]) + j] == "u   "):
          currMap[int(coords[0]) + i, int(coords[1]) + j] = "p   "

  currMap = np.concatenate((currMap, np.full((rows,1)," \n  ")), axis=1)
  currMapStr = "  " + currMap.astype('|S4').tobytes().decode('UTF-8')
  for key in db["game_values"]["coord_player"]:
    player = db["game_values"]["coord_player"][key]
    if (db[player]["id"] < 10):
      currMapStr = currMapStr.replace("  " + str(db[player]["id"]) + "  ", db[player]["icon"])
    else:
      currMapStr = currMapStr.replace("  " + str(db[player]["id"]) + " ", db[player]["icon"])
  return ". " + currMapStr[2:]


def playerInfo():
  msg = ""
  for player in db["user_username"]:
    msg += str(db[player]["icon"]) + " " + db["user_username"][player] + "  Coords: " + str(db[player]["location"].value) + "  Health: " + str(db[player]["health"]) + "  Defense: " + str(db[player]["defense"]) + "  Mana: " + str(db[player]["mana"]) + "\n"
  return msg


@tasks.loop(seconds = 1) # repeat after every 1 seconds
async def roundLoop():
  if not db["game_values"]["pause"]:
    if db["game_values"]["game_time"] % round_time == 0:
      for player in db["user_username"]:
        db[player]["mana"] += 5
      channel = client.get_channel(db["game_values"]["channel_id"])
      await channel.send("New Round!")
    db["game_values"]["game_time"] += 1


@client.event
async def on_ready():
  db.clear()
  print("I'm ready. Logged in as {0.user}".format(client))
  db["game_values"] = {"created": False, "wantingToEndGame": False, "usersWantingToEndgame": []}


@client.event
async def on_message(message):
  if message.author == client.user:
    return

  if message.content == "!help":
    msg = "This is a game test. \nGameManagement Commands:\n!rules shows the game rules. \n!createGame instantiates a game. \n!join <Username> to join the game. \n!icon <emoji> adds an icon type. \n!start to start the game. \n !endGame ends the current game and resets all the saved data.\n\nInformation Commands:\n!playerList gets the list of all the players. \n!time shows the remaining time in the match. \n!pause to pause the round. \n!unpause to unpause the round. \n!map This shows the current layout. \n!range to get the range of all players. \n\n Gameplay Commands:\n!move <direction> <distance> moves your character. Directions are \"left\",\"right\",\"up\", and \"down\". \n!attack <player> <damage> to attack a player if they are within range (4) dealing the specified damage. \n!deal <player> <amount> transfer a specified amount of money to an inrange (8) player.\n!defend <defense_amount> Give youself the specified amount of defense lasting only the current round.\n!gamble <amount> to gamble the specified amount of mana. Be careful to only use positive integers."
    await message.channel.send(msg)

  if message.content == "!rules":
    msg = "To win, be the last to survive. You have three hearts. Lose all your hearts and you die. \nEach round you get 5 mana. You can use mana to move, attack, or defend yourself. \nIn addition, you can trade or gamble your mana. \nYou cannot move out of bounds or where another player currently is. Each coordinate you move takes up one mana. \n Each quantity of attack and defense uses up one mana as well. Defense is like temporary health that only lasts a round.\n Both attacking (4) and dealing (8) have a maximum target range."
    await message.channel.send(msg)

  if message.content == "!createGame":
    db["game_values"]["started"] = False
    db["game_values"]["created"] = True
    db["game_values"]["player_count"] = 0
    db["game_values"]["channel_id"] = message.channel.id
    db["user_username"] = {}
    db["username_user"] = {}
    db["deads"] = {}
    msg = "Created a game. You need at least three players to start. To join the game type the command !join <Username>"
    await message.channel.send(msg)

  if message.content.startswith("!join"):
    msg_list = list(message.content.split(" "))
    # Check the arguments 
    if len(msg_list) != 2:
      msg = "bad command. Need two argument !join <username>."
      await message.channel.send(msg)
      return
    if (not db["game_values"]["created"]):
      msg = "Sorry, but you must create a game before joining."
    elif (db["game_values"]["started"]):
      msg = "Sorry, but you cannot join as the game has already started"
    elif (msg_list[1] in db["username_user"]):
      msg = "Sorry, but that username is already taken."
    elif (not msg_list[1].isalnum()):
      msg = "Sorry, but the username can only contain letters and numbers."
    else:
      newPlayer = str(message.author)
      if newPlayer in db["user_username"]:
        msg = "You have already joined the game"
      else:
        db["user_username"][newPlayer] = msg_list[1]
        db["username_user"][msg_list[1]] = newPlayer
        db[newPlayer] = {"icon": newPlayer[0], 'id': db["game_values"]["player_count"], "actual_id": message.author.id, "health": 3, "defense": 3, "mana": 0, "alive": True}
        db["game_values"]["player_count"] += 1
        msg = "{0} joined the game as {1}. Now use !icon <emoji> to add an emoji icon.".format("<@" + str(message.author.id) + ">", msg_list[1])
    await message.channel.send(msg)

  if message.content == "!playerList":
    if (not db["game_values"]["created"]):
      msg = "Sorry, but you must create a game before checking the playerList."
    else:
      msg = "Current Players: \n"
      if db["game_values"]["started"]:
        for player in db["user_username"]:
          msg += str(db[player]["icon"]) + "  " + player + "  Username: " + db["user_username"][player] + "  Coords: " + str(db[player]["location"].value) + "  Health: " + str(db[player]["health"]) + "  Defense: " + str(db[player]["defense"]) + "  Mana: " + str(db[player]["mana"]) + "\n"
      else:
        for player in db["user_username"]:
          msg += str(db[player]["icon"]) + "  " + player + "  Username: " + db["user_username"][player] + "\n"
      
    await message.channel.send(msg)

  if message.content.startswith("!icon"):
    if (not db["game_values"]["created"]):
      msg = "Sorry, but you must create a game before changing your icon."
    elif (db["game_values"]["started"]):
      msg = "Sorry, but you cannot change your icon as the game has already started"
    elif str(message.author) not in db["user_username"]:
      msg = "Sorry, but you must join the game before changing your icon."
    else:
      msg_list = list(message.content.split(" "))
      if len(msg_list) != 2:
        msg = "bad command. Need one argument !icon <emoji>"
      else:
        icon = msg_list[1]
        db[str(message.author)]["icon"] = icon
        msg = "Your new icon is " + icon + ". Make sure it looks correct."
    await message.channel.send(msg)

  if message.content == "!start":
    temp = False
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
      for user in db["user_username"]:
        start_coords = str(randint(0, rows-1)) + " " + str(randint(0,columns-1))
        while start_coords in db["game_values"]["coord_player"]:
          start_coords = str(randint(0, rows-1)) + " " + str(randint(0,columns-1))
        db["game_values"]["coord_player"][start_coords] = user
        coords_list = list(start_coords.split(" "))
        db[user]["location"] = int(coords_list[0]), int(coords_list[1])
      # Visualize
      msg += "\n" + visualize()
      # Start First Round
      db["game_values"]["game_time"] = 0
      db["game_values"]["pause"] = False
      roundLoop.start()
      temp = True
    await message.channel.send(msg)
    if temp:
      msg = playerInfo()
      await message.channel.send(msg)

  if message.content == "!endGame":
    if (not db["game_values"]["created"]):
      msg = "Sorry, but you must create a game before ending a game."
    elif (not db["game_values"]["started"]):
      db.clear()
      db["game_values"] = {"created": False, "wantingToEndGame": False, "usersWantingToEndgame": []}
      msg = "Successfully ended the game"
    elif str(message.author) not in db["user_username"]:
      msg = "Sorry, but you must have joined the game to end the game."
    else:
      msg = "Are you sure you want to end the game? All the progress for everyone will be lost. At least two people must respond with \"yes\" for the game to end. If someone types \"no\" the game will continue."
      db["game_values"]["wantingToEndGame"] = True
    await message.channel.send(msg)
  
  if message.content == "yes" and db["game_values"]["wantingToEndGame"]:
    if str(message.author) not in db["user_username"]:
      msg = "Sorry, but you must have joined the game to vote."
    elif str(message.author) not in db["game_values"]["usersWantingToEndgame"].value:
      db["game_values"]["usersWantingToEndgame"].append(str(message.author))
    elif len(db["game_values"]["usersWantingToEndgame"]) == 2:
      db.clear()
      db["game_values"] = {"created": False, "wantingToEndGame": False, "usersWantingToEndgame": []}
      roundLoop.cancel()
      msg = "Successfully ended the game"
      await message.channel.send(msg)

  if message.content == "sudo yes" and db["game_values"]["wantingToEndGame"]:
    if str(message.author) not in db["user_username"]:
      msg = "Sorry, but you must have joined the game to vote."
    else:
      db.clear()
      db["game_values"] = {"created": False, "wantingToEndGame": False, "usersWantingToEndgame": []}
      roundLoop.cancel()
      msg = "Successfully ended the game"
      await message.channel.send(msg)

  if message.content == "no" and db["game_values"]["wantingToEndGame"]:
    if str(message.author) not in db["user_username"]:
      msg = "Sorry, but you must have joined the game to vote."
    db["game_values"]["usersWantingToEndgame"] = []
    db["game_values"]["wantingToEndGame"] = False
    msg = "Game not ended"
    await message.channel.send(msg)

  if message.content.startswith("!move"):
    msg_list = list(message.content.split(" "))
    # Check the arguments 
    if len(msg_list) != 3:
      msg = "bad command. Need two argument !move <direction> <distance>. Directions are left, right, up, and down."
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
    elif str(message.author) in db["deads"]:
      msg = "SpOoKy!"
    elif str(message.author) not in db["user_username"]:
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

  if message.content.startswith("!attack"):
    temp = False
    msg_list = list(message.content.split(" "))
    # Check the arguments 
    if len(msg_list) != 3:
      msg = "bad command. Need two argument !attack <player> <damage>. user !playerList for list of players."
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
    elif str(message.author) in db["deads"]:
      msg = "Bro you dead."
    elif str(message.author) not in db["user_username"]:
      msg = "Sorry, but you must have joined the game before it started to do this action."
    elif msg_list[1] not in db["username_user"]:
      msg = "Please enter a valid player username to attack. Type !playerList for all the available players"
    elif not fail:
      user = db["username_user"][msg_list[1]]
      targetLoc = db[user]["location"].value
      attackerLoc = db[str(message.author)]["location"].value
      if attackRange < abs(attackerLoc[0] - targetLoc[0]) + abs(attackerLoc[1] - targetLoc[1]):
        msg = "Not in range to attack "+ msg_list[1] + " (<@" + str(db[user]["actual_id"]) + ">). Attack Range is 4."
      elif damage > db[str(message.author)]["mana"]:
        msg = "Not enough mana. You have " + str(db[str(message.author)]["mana"]) + " mana."
      else:
        db[str(message.author)]["mana"] -= damage
        remaining_damage = damage - db[user]["defense"]
        remaining_defense = db[user]["defense"] - damage
        if remaining_defense < 0:
          db[user]["defense"] = 0
          db[user]["health"] -= remaining_damage
          # Check if target died
          if db[user]["health"] <= 0:
            db[user]["alive"] = False
            msg = db["user_username"][str(message.author)] + " (<@" + str(db[str(message.author)]["actual_id"]) + ">) " + " KILLED " + msg_list[1] + " (<@" + str(db[user]["actual_id"]) + ">)!"
            await message.channel.send(msg)
            deadPlayer = str(message.author)
            username = db["user_username"][deadPlayer]
            db["deads"][deadPlayer] = username
            del db["user_username"][deadPlayer]
            del db["username_user"][username]
            del db[deadPlayer]
            db["game_values"]["player_count"] -= 1
            if (db["game_values"]["player_count"] == 1):
              msg = db["user_username"][str(message.author)] + " won the game!!!"
              await message.channel.send(msg)
              roundLoop.cancel()
              db.clear()
              db["game_values"] = {"created": False, "wantingToEndGame": False, "usersWantingToEndgame": []}
            elif (db["game_values"]["player_count"] == 0):
              msg = username + " won, but at what cost?"
              await message.channel.send(msg)
              roundLoop.cancel()
              db.clear()
              db["game_values"] = {"created": False, "wantingToEndGame": False, "usersWantingToEndgame": []}
            return
        else:
          db[user]["defense"] = remaining_defense
        msg = db["user_username"][str(message.author)] + " (<@" + str(db[str(message.author)]["actual_id"]) + ">) " + " attacked " + msg_list[1] + " (<@" + str(db[str(message.author)]["actual_id"]) + ">) for " + str(damage) + " damage."
        temp = True
    await message.channel.send(msg)
    if temp:
      msg = playerInfo()
      await message.channel.send(msg)

  if message.content.startswith("!deal"):
    temp = False
    msg_list = list(message.content.split(" "))
    # Check the arguments 
    if len(msg_list) != 3:
      msg = "bad command. Need two argument !deal <player> <amount>. user !playerList for list of players."
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
    elif str(message.author) in db["deads"] and mana_amount != 666:
      msg = "If only you could make a deal with the devil... \n;)"
    elif str(message.author) in db["deads"]:
      if (randint(0,1) == 0):
        msg = "Nice try kid. Better luck next time."
      else:
        msg = "Your cries have been heard " + db["deads"][str(message.author)] + ".\nGood bye"
        for player in db["user_username"]:
          loss = np.random.normal(1,1)
          if loss < 0:
            loss = 0
          db[player]["mana"] -= loss
        del db["deads"][str(message.author)]
    elif str(message.author) not in db["user_username"]:
      msg = "Sorry, but you must have joined the game before it started to do this action."
    elif msg_list[1] not in db["username_user"]:
      msg = "Please enter a valid player name to attack. Type !playerList for all the available players"
    elif not fail:
      user = db["username_user"][msg_list[1]]
      targetLoc = db[user]["location"].value
      traderLoc = db[str(message.author)]["location"].value
      if tradeRange < abs(traderLoc[0] - targetLoc[0]) + abs(traderLoc[1] - targetLoc[1]):
        msg = "Not in range to make a deal. Deal Range is 8."
      elif mana_amount > db[str(message.author)]["mana"]:
        msg = "Not enough mana. You have " + str(db[str(message.author)]["mana"]) + " mana."
      else:
        db[str(message.author)]["mana"] -= mana_amount
        db[user]["mana"] += mana_amount
        msg = "Successfully gave " + msg_list[1] + " (<@" + str(db[str(user)]["actual_id"]) + ">) " + str(mana_amount) + " mana."
        temp = True
    await message.channel.send(msg)
    if temp:
      msg = playerInfo()
      await message.channel.send(msg)

  if message.content.startswith("!defend"):
    temp = False
    msg_list = list(message.content.split(" "))
    # Check the arguments 
    if len(msg_list) != 2:
      msg = "bad command. Need two argument !defend <amount>."
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
    elif str(message.author) in db["deads"]:
      msg = "You got nothing left to defend."
    elif str(message.author) not in db["user_username"]:
      msg = "Sorry, but you must have joined the game before it started to do this action."
    elif not fail:
      if defense_amount > db[str(message.author)]["mana"]:
        msg = "Not enough mana. You have " + str(db[str(message.author)]["mana"]) + " mana."
      else:
        db[str(message.author)]["mana"] -= defense_amount
        db[str(message.author)]["defense"] += defense_amount
        msg = "Successfully increased your defense to " + str(defense_amount) + "."
        temp = True
    await message.channel.send(msg)
    if temp:
      msg = playerInfo()
      await message.channel.send(msg)

  if message.content.startswith("!gamble"):
    temp = False
    msg_list = list(message.content.split(" "))
    # Check the arguments 
    if len(msg_list) != 2:
      msg = "bad command. Need two argument !gamble <amount>."
      fail = True
    try:
      gamble_amount = int(msg_list[1])
      fail = False
      if (gamble_amount < 0):
        fail = True
        msg = "are you sure?"
    except:
      msg = "Enter an integer for the transaction amount"
      fail = True

    if (not db["game_values"]["created"]):
      msg = "Sorry, but you must create a game before doing this action."
    elif (not db["game_values"]["started"]):
      msg = "Sorry, but you must start a game before doing this action."
    elif str(message.author) in db["deads"]:
      msg = "Ha! Nice try"
    elif str(message.author) not in db["user_username"]:
      msg = "Sorry, but you must have joined the game before it started to do this action."
    elif not fail:
      if gamble_amount > db[str(message.author)]["mana"]:
        msg = "Not enough mana. You have " + str(db[str(message.author)]["mana"]) + " mana."
      else:
        db[str(message.author)]["mana"] -= gamble_amount
        gain = round(np.random.normal(gamble_amount, gamble_amount/5))
        if gain < 0:
          gain = 0
        db[str(message.author)]["mana"] += gain
        if gain > gamble_amount:
          msg = "noice"
        else:
          msg = "lol unlucky dood"
        temp = True
    await message.channel.send(msg)
    if temp:
      msg = playerInfo()
      await message.channel.send(msg)

  if message.content == "!map":
    if (not db["game_values"]["created"]):
      msg = "Sorry, but you must create a game before doing this action."
    elif (not db["game_values"]["started"]):
      msg = "Sorry, but you must start a game before doing this action."
    else:
      msg = visualize()
    await message.channel.send(msg)

  if message.content == "!range":
    if (not db["game_values"]["created"]):
      msg = "Sorry, but you must create a game before doing this action."
    elif (not db["game_values"]["started"]):
      msg = "Sorry, but you must start a game before doing this action."
    else:
      msg = visualize_range()
    await message.channel.send(msg)

  if message.content == "!time":
    if (not db["game_values"]["created"]):
      msg = "Sorry, but you must create a game before doing this action."
    elif (not db["game_values"]["started"]):
      msg = "Sorry, but you must start a game before doing this action."
    else:
      msg = str(round_time - db["game_values"]["game_time"] % 60) + " seconds remain in the round!"
    await message.channel.send(msg)

  if message.content == "!pause":
    if (not db["game_values"]["created"]):
      msg = "Sorry, but you must create a game before doing this action."
    elif (not db["game_values"]["started"]):
      msg = "Sorry, but you must start a game before doing this action."
    else:
      db["game_values"]["pause"] = True
      msg = "Round paused"
    await message.channel.send(msg)

  if message.content == "!unpause":
    if (not db["game_values"]["created"]):
      msg = "Sorry, but you must create a game before doing this action."
    elif (not db["game_values"]["started"]):
      msg = "Sorry, but you must start a game before doing this action."
    else:
      db["game_values"]["pause"] = False
      msg = "Round unpaused"
    await message.channel.send(msg)


  if message.content.startswith("!echo"):
    print(message.content)
    await message.channel.send(message.content)

keep_alive()
bot_token = os.environ['bot_token']
client.run(bot_token)
