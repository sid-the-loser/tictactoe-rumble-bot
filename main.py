from nextcord import Interaction
from nextcord.ext import commands
import nextcord
import json

help_text = "Still working on it!"

open("help.json", "a").close() # makes a "help.json" file if it doesn't exist
print("help.json existance file checked")

open("scoreboard_data.json", "a").close() # makes a "scoreboard.json" file if it doesn't exist
print("scoreboard_data.json existance file checked")

open("board_data.json", "a").close() # makes a "board_data.json" file if it doesn't exist
print("board_data.json existance file checked")

data = open("help.json").read()

if data == "":
    data = {}
    f = open("help.json", "w")
    f.write("{}")
    f.close()
else:
    data = json.loads(data)

if data == {}:
    help_text = "Help command is under maintenance!"
else:
    help_text = "All the commands available are:\n\n"
    for cmd in data:
        help_text += f"**/{cmd}**: *{data[cmd]}*\n"

print("Loaded help.json!")

board_data = open("board_data.json").read()

if board_data == "":
    board_data = {}
    f = open("board_data.json", "w")
    f.write("{}")
    f.close()
else:
    board_data = json.loads(board_data)

print("Loaded board_data.json!")

scoreboard_data = open("scoreboard_data.json").read()

if scoreboard_data == "":
    scoreboard_data = {}
    f = open("scoreboard_data.json", "w")
    f.write("{}")
    f.close()
else:
    scoreboard_data = json.loads(scoreboard_data)

print("Loaded scoreboad_data.json")

intents = nextcord.Intents.default()
intents.members = True

bot = commands.Bot(intents=intents)

def place(board_id, position: int):
    global board_data
    placed = False
    board_id = str(board_id)

    if position > 0 and position < 10:
        if position < 4:
            ypos = 0
            xpos = position-1
        elif position < 7:
            ypos = 1
            xpos = position-4
        else:
            ypos = 2
            xpos = position-7

        if board_data[board_id]["board"][ypos][xpos] == 0:
            if board_data[board_id]["turn"]:
                board_data[board_id]["board"][ypos][xpos] = 1
            else:
                board_data[board_id]["board"][ypos][xpos] = 2

            placed = True
            board_data[board_id]["turn"] = not board_data[board_id]["turn"]

    return placed

def game_draw(board_id):
    global board_data
    board_id = str(board_id)
    board = board_data[board_id]["board"]

    for i in board:
        for j in i:
            if j == 0:
                return False
    else:
        return True

def game_ended(board_id):
    global board_data
    board_id = str(board_id)
    board = board_data[board_id]["board"]
    for n in range(1, 3):
        for x in range(3): # vertical |
            for y in range(3):
                if board[y][x] != n:
                    break
            else:
                return True
                
        for y in range(3):
            for x in range(3): # horizondal -
                if board[y][x] != n:
                    break
            else:
                return True
            
        for i in range(3): # diagonal \
            if board[i][i] != n:
                break
        else:
            return True
        
        for i in range(3): # diagonal /
            if board[i][2-i] != n:
                break
        else:
            return True

    return False

def generate3x3board():
    return [[0 for i in range(3)] for j in range(3)]

def get_board(board_id):
    board_id = str(board_id)
    current_board = board_data[board_id]["board"]
    text = ""
    for i in range(3):
        text += "|"
        for j in range(3):
            if current_board[i][j] == 1:
                text += "X"
            elif current_board[i][j] == 2:
                text += "O"
            else:
                text += "-"
            if j < 2:
                text += " "
        text += "|\n"
    return text

def save_board_data():
    global board_data
    f = open("board_data.json", "w")
    json.dump(board_data, f)
    f.close()
    print("Saved board data!")

def save_scoreboard_data():
    global scoreboard_data
    f = open("scoreboard_data.json", "w")
    json.dump(scoreboard_data, f)
    f.close()
    print("Saved scoreboard data!")

def add_score(user_id):
    global scoreboard_data
    user_id = str(user_id)

    if user_id not in scoreboard_data:
        scoreboard_data[user_id] = 1
    else:
        scoreboard_data[user_id] += 1

def sorted_score():
    scores = []
    for user_id in scoreboard_data:
        scores.append([scoreboard_data[user_id], user_id])
    scores = sorted(scores, reverse=True)
    for i in range(len(scores)):
        scores[i] = [scores[i][1], scores[i][0]]
    return scores

def get_score(user_id):
    user_id = str(user_id)
    scores = sorted_score()
    count = 0
    
    for data in scores:
        count += 1
        if data[0] == user_id:
            break
    else:
        return False
    
    return [scoreboard_data[user_id], count]

@bot.event
async def on_ready():
    print("Bot online!")
    await bot.change_presence(activity=nextcord.Game("Tic-Tac-Toe RUMBLE!"))

@bot.slash_command(name="help", description="Helps you know more about the bot")
async def help(interaction: Interaction):
    await interaction.response.send_message(help_text, ephemeral=True)

@bot.slash_command(name="play", description="Marks a position in the board")
async def play(interaction: Interaction, position: int):
    global board_data
    await interaction.response.defer()

    board_id = str(interaction.guild_id)

    if board_id not in board_data:
        board_data[board_id] = {
            "board": generate3x3board(),
            "turn": True,
            "last_player": 0
        }

    user_id = interaction.user.id

    if board_data[board_id]["last_player"] != user_id:
        placed = place(board_id, position)
    else:
        placed = False
        
    if placed:
        message = f"<@{user_id}> placed a marking at {position}...\n\n{get_board(board_id)}"
        board_data[board_id]["last_player"] = user_id
        if game_ended(board_id):
            message += f"\n\n**<@{user_id}> won!**"
            board_data[board_id] = {
                "board": generate3x3board(),
                "turn": True,
                "last_player": 0
            }
            add_score(user_id)
            save_scoreboard_data()
        elif game_draw(board_id):
            message += f"\n\n**Game draw!**"
            board_data[board_id] = {
                "board": generate3x3board(),
                "turn": True,
                "last_player": 0
            }

        save_board_data()
        ephemeral = False

    elif board_data[board_id]["last_player"] == user_id:
        message = "You can't place another marking right now, please let another player play!"
        ephemeral = True
    
    elif not placed:
        message = f"Can't place at {position} since it is already occupied"
        ephemeral = True

    else:
        message = "HUH?"

    await interaction.followup.send(message)
    

@bot.slash_command(name="see", description="To see the board")
async def see(interaction: Interaction):
    await interaction.response.defer(ephemeral=True)

    board_id = str(interaction.guild_id)
    if board_id not in board_data:
        await interaction.followup.send("Nobody on the server has initiated a game yet!?")
    else:
        await interaction.followup.send(get_board(board_id))

@bot.slash_command(name="myscore", description="To see your score and your place on the scoreboard")
async def myscore(interaction: Interaction):
    await interaction.response.defer(ephemeral=True)

    user_id = interaction.user.id
    user_data = get_score(user_id)
    if user_data:
        await interaction.followup.send(f"Your score is: {user_data[0]}\nYou're at place: {user_data[1]} on the scoreboard!")
    else:
        await interaction.followup.send(f"You're not even on the leaderboard")

@bot.slash_command(name="top10", description="See who the top ten players are on the scoreboard")
async def top10(interaction: Interaction):
    await interaction.response.defer(ephemeral=True)
    
    user_datas = sorted_score()
    if len(user_datas) > 0:
        text = "Top 10 players are:\n\n"

        for data in user_datas[:10 if len(user_datas) >= 10 else len(user_datas)]:
            text += f"- <@{data[0]}>: {data[1]}\n"
    else:
        text = "Scoreboard has not been occupied yet!"
    
    await interaction.followup.send(text)

bot.run("KEY HERE")