import chess
from copy import deepcopy

class LosingBoard:
	"""
	Wrapper for the python-chess Board class that encodes the rules of losing chess 
	(a.k.a. anti-chess, suicide chess). 

	The dynamics of the game are the same as regular chess. The rules are different.

	The rules:
	-> First player to lose all pieces wins.
	-> Attacking pieces must capture opponent's piece.
	-> Pawns are automatically promoted to Queens.
	"""

	def __init__(self, no_kings=False):
		self.board = chess.Board()

		self.piece_counts = { color: { 	
										chess.PAWN: 8,
										chess.ROOK: 2,
										chess.BISHOP: 2,
										chess.QUEEN: 1,
										chess.KING: 1,
										chess.KNIGHT: 2,
									}

							 for color in [chess.WHITE, chess.BLACK]
							}


	def getLegalMoves(self):
		"""
		Return list of all legal moves for a color given the current gamestate.
		Since the Board class knows whose turn it is, we need not take a color argument.
		"""

		legal_moves = []

		# get legal moves under normal chess rules
		chess_legal_moves = self.board.legal_moves

		# check for attacking positions
		# if one is found, we only include attacking moves among legal moves
		attacking = False
		for mv in chess_legal_moves:
			if self.board.piece_at(mv.to_square):
				legal_moves.append(mv)
				attacking = True

		if attacking:
			return legal_moves
		else:
			return list(chess_legal_moves)


	def move(self, mv):
		"""
		Push move mv to true board.
		"""

		p = self.board.piece_at(mv.to_square)

		# decrement count of pieces if one is captured
		if p:
			isWhite = str(p).isupper()
			self.piece_counts[isWhite][p.piece_type] -= 1

		self.board.push(mv)


	def generateSuccessor(self, mv):
		"""
		Generate successor board given move mv without modifying the true board.
		"""
		new_board = deepcopy(self)
		new_board.move(mv)
		return new_board


	def isGameOver(self):
		"""	
		Return true if all of one player's pieces have been consumed.
		"""

		for k in self.piece_counts:
			if sum(self.piece_counts[k].values()) == 0:
				return True
		return False

	def isDraw(self):
		"""
		Return true if there are only kings left.
		"""

		for color in [chess.WHITE, chess.BLACK]:
			if not sum(self.piece_counts[color].values()) == 1 and self.piece_counts[color][chess.KING] == 1:
				return False

		return True


	def __str__(self):

		return str(self.board)


