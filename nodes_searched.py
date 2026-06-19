from board import Board
import search, evaluation

search.search_iterative(Board(), evaluation.evaluate, 2)
print("after first think: ", search.nodes_visited)
search.search_iterative(Board(), evaluation.evaluate, 2)
print("after second think: ", search.nodes_visited)
