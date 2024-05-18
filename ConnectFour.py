import numpy as np
from bokeh.io import curdoc
from bokeh.models import ColumnDataSource, Button, Div, Select
from bokeh.layouts import column as bokeh_column, row as bokeh_row

from bokeh.plotting import figure
from easyAI import Negamax
from TwoPlayers import TwoPlayerGame
from Players import AI_Player, Human_Player
from bokeh.driving import linear
from functools import partial
import time

# Constants
width = 7
height = 6
len_win = 4
colors = ['white', 'yellow', 'red']

# Bokeh Setup
p = figure(x_range=(-0.5, width+0.5), y_range=(-0.5, height+0.5), 
           width=700, height=600, tools="", toolbar_location=None, styles={'transform': 'translate(50px, 10px)', 'border': '1px solid black', 'background-color': '#8B4513'})
p.grid.visible = False
p.axis.visible = False
p.background_fill_color = "#2C7B4A"

circles = ColumnDataSource(data=dict(x=[], y=[], color=[]))

# Initial Drawing of Circles
for row in range(height):
    for col in range(width):
        circles.data['x'].append(col + 0.5)
        circles.data['y'].append(row + 0.5)
        circles.data['color'].append(colors[0])

p.scatter('x', 'y', source=circles, size=50, color='color', line_color="black")

# Notification panel
notification_div = Div(text="Welcome to Connect Four!", width=200, height=100)
notification_div.styles = {'background-color': '#95BFB0','border': '1px solid black', 'color': 'white', 'text-align': 'center', 'font-size': '20px'}

class GameController(TwoPlayerGame):
    def __init__(self, players, board=None):
        self.players = players
        self.board = board if (board is not None) else np.zeros((height, width), dtype=int)
        self.current_player = 1

    def possible_moves(self):
        return [i for i in range(width) if self.board[:, i].min() == 0]
    
    def make_move(self, column):
        if self.board[5, column] != 0:
            return False
        line = np.argmax(self.board[:, column] == 0)
        self.board[line, column] = self.current_player
        return True

    def show(self):
        print('\n' + '\n'.join([
            ' '.join([['.', 'O', 'X'][self.board[height - 1 - j][i]] for i in range(width)]) for j in
            range(height)]))

    def check_winner(self, player):
        # Check horizontal, vertical, and diagonal lines for a win
        for row in range(height):
            for col in range(width - len_win + 1):
                if all(self.board[row, col + i] == player for i in range(len_win)):
                    return True

        for row in range(height - len_win + 1):
            for col in range(width):
                if all(self.board[row + i, col] == player for i in range(len_win)):
                    return True

        for row in range(height - len_win + 1):
            for col in range(width - len_win + 1):
                if all(self.board[row + i, col + i] == player for i in range(len_win)):
                    return True

        for row in range(len_win - 1, height):
            for col in range(width - len_win + 1):
                if all(self.board[row - i, col + i] == player for i in range(len_win)):
                    return True

        return False

    def loss_condition(self):
        return self.check_winner(self.opponent_index)

    def is_over(self):
        return self.check_winner(1) or self.check_winner(2) or (self.board.min() > 0)

    def scoring(self):
        return -100 if self.loss_condition() else 0

    def reset(self, players):
        self.__init__(players)

# Game Setup
game_started = False
algo_neg = Negamax(5)
human_player = Human_Player()
game = None
board = None
p.visible = False

def animate_fall(col, target_row, color, callback=None):
    """Animate a disc falling from the top to the target row."""
    current_y = height - 0.5
    final_y = target_row + 0.5
    disc = p.scatter(x=[col + 0.5], y=[current_y], color=[color], size=50, line_color="black")
    
    @linear()
    def update(step):
        nonlocal current_y
        if current_y > final_y and final_y > 0:
            current_y -= 1
            disc.data_source.data['y'] = [current_y]
            time.sleep(0.1)
        
    
    curdoc().add_periodic_callback(update, 50)


def update_board():
    circles.data['color'] = [colors[board[row, col]] for row in range(height) for col in range(width)]



def make_move(column):
    if not game.is_over() and game.current_player == 1:
        if game.make_move(column):
            game.show()
            animate_fall(column, np.argmax(game.board[:, column] == 0) - 1, colors[1])
            #update_board()
            if game.is_over():
                if game.check_winner(1):
                    notification_div.text = "Game over! You won!"
                elif game.check_winner(2):
                    notification_div.text = "Game over! AI won!"
                else:
                    notification_div.text = "Game over! It's a draw!"
            else:
                game.switch_player()
                notification_div.text = "Waiting For AI...!"
                # Sau khi người chơi đã thực hiện xong bước đi, gọi AI để thực hiện bước đi của mình sau 2 giây
                curdoc().add_timeout_callback(partial(make_ai_move, column), 2000)

def make_ai_move(column):
    ai_move = game.players[1].ask_move(game)
    game.make_move(ai_move)
    game.show()
    animate_fall(ai_move, np.argmax(game.board[:, ai_move] == 0) - 1, colors[2])
    #update_board()
    if game.is_over():
        if game.check_winner(1):
            notification_div.text = "Game over! You won!"
        elif game.check_winner(2):
            notification_div.text = "Game over! AI won!"
        else:
            notification_div.text = "Game over! It's a draw!"
    else:
        game.switch_player()
        notification_div.text = "Your turn!"



def on_click(event):
    col = int(event.x)
    if 0 <= col < width:
        make_move(col)
# Add a mouse click event
p.on_event('tap', on_click)


def start_game():
    global game_started, game, board
    game_started = True
    start_button.visible = False
    p.visible = True
    game = GameController([human_player, AI_Player(algo_neg)])
    board = game.board
    update_board()
    notification_div.text = "Game started! Your turn!"

# Add a button to start the game
start_button = Button(label="Start Game", width=200, height=50, button_type="success")
start_button.on_click(start_game)

# Add a reset button
reset_button = Button(label="Reset", width=150, height=50, button_type="primary", styles={'transform': 'translate(25px, 0px)'})
def reset_game():
    global game, board
    game.reset([human_player, AI_Player(algo_neg)])
    board = game.board
    update_board()
    notification_div.text = "Welcome to Connect Four!"

reset_button.on_click(reset_game)

# Difficulty options
difficulty_select = Select(title="Difficulty", options=["Easy", "Medium", "Hard"], value="Medium", styles={'color': 'white', 'font-size': '15px'})

def update_difficulty(attr, old, new):
    if new == "Easy":
        algo_neg.depth = 3
    elif new == "Medium":
        algo_neg.depth = 5
    elif new == "Hard":
        algo_neg.depth = 7

difficulty_select.on_change('value', update_difficulty)

from bokeh.layouts import column, row, gridplot

# Image
image_div = Div(text="<img src='https://tse2.mm.bing.net/th?id=OIP.8YELn0KiSXXEgbZraTqtugHaHa&pid=Api&P=0&h=180' width='100' height='100'>", width=200, height=100, styles={'transform': 'translate(50px, 5px)'})

# Title
title_div = Div(text="""
<h1 style="
    text-align: center; 
    color: white; 
    font-family: 'Arial Black', Gadget, sans-serif;
    font-size: 25px;
    text-shadow: 3px 3px 5px black;
">Connect Four</h1>""", width=200, height=50)

# Arrange plots and widgets in layouts
buttons_column = bokeh_column(image_div, start_button, reset_button, difficulty_select, notification_div, sizing_mode='scale_width')


# Create a column layout for buttons and notification_div
buttons_and_notification_layout = column(image_div, title_div, start_button, reset_button, difficulty_select, notification_div)
buttons_and_notification_layout.styles = {'background-color': '#1E5938','border': '1px solid black', 'transform': 'translate(20px, 20px)'}

# Arrange plots and widgets in layouts
grid_layout = gridplot([[row(buttons_and_notification_layout, p)]], toolbar_location=None, sizing_mode='scale_width', merge_tools=False)
curdoc().add_root(grid_layout)
curdoc().title = "Connect Four with Bokeh"
