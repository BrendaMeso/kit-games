from typing import Tuple, Union
from .board import Board

class GameState:

    game_name = "Tic-Tac-Toe Misere"

    def __init__(self, board: Board, player: str):
        self.board = board
        self.player = player

    def is_terminal(self) -> bool: # um estado é terminal se o tabuleiro estiver cheio ou se houver um vencedor (ou seja, se um jogador tiver perdido)
        # entao jogo acabou 
        return self.board.is_full() or self.winner() is not None

    def is_legal_move(self, move: Tuple[int, int]) -> bool:     # principal regra de jogo: não pode colocar uma peça em um local já ocupado, e deve estar dentro dos limites do tabuleiro
        """
        Checks whether the given move (x, y) is legal in this state.
        """
        col, row = move
        return 0 <= row < 3 and 0 <= col < 3 and self.board.is_empty(row, col) 

    def legal_moves(self) -> set: # retorna todas as jogadas legais disponíveis no estado atual do jogo
        moves = set()
        for row in range(3):
            for col in range(3):
                if self.is_legal_move((col, row)):
                    moves.add((col, row))
        return moves

    def winner(self) -> Union[str, None]:
        loser = self.board.check_loser()
        if loser == 'B':
            return 'W'
        elif loser == 'W':
            return 'B'
        else:
            return None

    def get_board(self) -> Board:
        return self.board

    def copy(self) -> 'GameState': 
        new_state = GameState(self.board.copy(), self.player)
        return new_state

    def next_state(self, move: Tuple[int, int]) -> 'GameState': # essencial para busca com adversario,
        # recebe um movimento e retorna o estado resultante após aplicar esse movimento
        # seria a função sucessora no contexto de busca, mas aqui é específico para jogos de adversário, onde o movimento é aplicado e o jogador é alternado
        if not self.is_legal_move(move):
            raise ValueError("Invalid move.")
        
        new_state = self.copy()
        col, row = move
        new_state.board.place_marker(self.player, row, col)

        # Toggle the player for the next move
        new_state.player = 'B' if self.player == 'W' else 'W'

        return new_state
