import game
import chess
import chess_agents
import evaluation
import losing_board

from copy import deepcopy
from scipy.stats import binom

class StatsGenerator:
	"""
	Class for running experiments to compare agents with different attributes.
	"""
	def __init__(self, sig_level, max_iter=30, null_p=.5, stop_at_significance=False):

		self.sig_level = sig_level
		self.null_p = null_p
		self.max_iter = max_iter
		self.stop_at_significance = stop_at_significance

	def compare_agents(self, a1, a2, board, verbose=False):
		"""
		Run 30 games between a1 and a2, randomly assigning color and
		recording the results of each game.
		"""
		a1_victory_history = []

		for i in range(self.max_iter):
			tmp_board = deepcopy(board)
			winning_agent = None
			if i % 2 == 0:
				g = game.Game(tmp_board, a1, a2, get_stats=True)
				winning_agent = g.play(max_turns=200)
			else:
				g = game.Game(tmp_board, a2, a1, get_stats=True)
				winning_agent = g.play(max_turns=200)
			if winning_agent == chess.WHITE:
				a1_victory_history.append(True)
			else:
				a1_victory_history.append(False)

			# check if significance has been reached, excluding true draws (with no winner)
			no_draws = [a for a in a1_victory_history if a is not None]
			n = len(no_draws)
			x = sum(no_draws)
			p_val = binom.cdf(x, n, self.null_p)
			if self.stop_at_significance:
				if p_val < self.sig_level/2 or p_val > 1 - self.sig_level/2:
					if sum(no_draws) < len(no_draws)/2:
						self.print_results(a2, a1, no_draws, p_val)
						return a2, [not a for a in a1_victory_history], p_val
					else:
						self.print_results(a1, a2, no_draws, p_val)
						return a1, a1_victory_history, p_val

		self.print_results(a1, a2, a1_victory_history, p_val)
		return a1, a1_victory_history, p_val


	def print_results(self, win_agent, lose_agent, history, p):

		if p > .5:
			p = 1 - p

		print
		print win_agent.__class__.__name__ + " with evaluator '" + str(win_agent.eval_func.im_class)[11:] + "' and depth " + str(win_agent.depth)
		print "wins " + str(sum(history)) + " out of " + str(len(history)) + " games against"
		print lose_agent.__class__.__name__ + " with evaluator '" + str(lose_agent.eval_func.im_class)[11:] + "' and depth " + str(lose_agent.depth)
		print "p-value: " + str(p)
		print
		if p > self.sig_level:
			print "No significant difference found."

		print
		return


if __name__ == "__main__":

	anti_pawn = evaluation.AntiPawn()
	counter = evaluation.WeightedPieceCount()

	a1 = chess_agents.AlphaBetaAgent(color=chess.WHITE, eval_func=counter.evaluate, depth=1, ant_eval_func=anti_pawn.evaluate)
	a2 = chess_agents.AlphaBetaAgent(color=chess.BLACK, eval_func=anti_pawn.evaluate, depth=1, ant_eval_func=counter.evaluate)
	board = losing_board.LosingBoard(no_kings=False)

	s = StatsGenerator(.05, max_iter=30)
	out = s.compare_agents(a1, a2, board)