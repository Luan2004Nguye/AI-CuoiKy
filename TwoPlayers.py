import abc
from abc import ABC
from copy import deepcopy


class TwoPlayerGame(ABC):
    @abc.abstractmethod
    def possible_moves(self):
        pass

    @abc.abstractmethod
    def make_move(self, move):
        pass

    @abc.abstractmethod
    def is_over(self):
        pass

    @property
    def opponent_index(self):
        return 2 if (self.current_player == 1) else 1

    @property
    def player(self):
        return self.players[self.current_player - 1]

    @property
    def opponent(self):
        return self.players[self.opponent_index - 1]

    def switch_player(self):
        self.current_player = self.opponent_index

    def copy(self):
        return deepcopy(self)

    def get_move(self):
        """
        Method for getting a move from the current player. If the player is an
        AI_Player, then this method will invoke the AI algorithm to choose the
        move. If the player is a Human_Player, then the interaction with the
        human is via the text terminal.
        """
        return self.player.ask_move(self)

    def play_move(self, move):
        """
        Method for playing one move with the current player. After making the move,
        the current player will change to the next player.

        Parameters
        -----------

        move:
          The move to be played. ``move`` should match an entry in the ``.possibles_moves()`` list.
        """
        result = self.make_move(move)
        self.switch_player()
        return result
