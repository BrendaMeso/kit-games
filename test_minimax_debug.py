from advsearch.your_agent.minimax import minimax_move


class DebugState:
    """
    Estado artificial para testar minimax sem depender de Othello ou TTTM.

    Cada estado tem:
    - name: nome só para debug
    - player: jogador da vez, 'B' ou 'W'
    - children: dicionário move -> próximo estado
    - terminal: se é folha
    - value: valor terminal/heurístico do ponto de vista do jogador raiz
    """

    def __init__(self, name, player="B", children=None, terminal=False, value=None):
        self.name = name
        self.player = player
        self.children = children or {}
        self.terminal = terminal
        self.value = value

    def legal_moves(self):
        return list(self.children.keys())

    def next_state(self, move):
        return self.children[move]

    def is_terminal(self):
        return self.terminal

    def winner(self):
        return None


def debug_eval(state, root_player):
    """
    Função de avaliação artificial.
    Aqui o valor já está guardado no estado.
    """
    if state.value is None:
        return 0
    return state.value


def run_test(name, test_func):
    print(f"\n=== {name} ===")
    try:
        test_func()
        print("OK")
    except AssertionError as e:
        print("FALHOU:", e)


def test_unica_jogada():
    """
    Se só existe uma jogada, minimax deve retornar essa jogada.
    """

    root = DebugState(
        "root",
        player="B",
        children={
            (0, 0): DebugState("terminal", player="W", terminal=True, value=1)
        }
    )

    move = minimax_move(root, -1, debug_eval)

    assert move == (0, 0), f"Esperado (0, 0), recebido {move}"


def test_max_escolhe_maior_valor():
    """
    Raiz é MAX.
    Entre valor +1 e valor -1, deve escolher +1.
    """

    root = DebugState(
        "root",
        player="B",
        children={
            (0, 0): DebugState("win", player="W", terminal=True, value=1),
            (1, 0): DebugState("lose", player="W", terminal=True, value=-1),
        }
    )

    move = minimax_move(root, -1, debug_eval)

    assert move == (0, 0), f"Esperado (0, 0), recebido {move}"


def test_min_escolhe_pior_para_max():
    """
    Testa alternância MAX/MIN.

    Jogada A leva a um nó MIN com filhos +1 e -1.
    Como MIN escolhe o menor, valor de A = -1.

    Jogada B leva a um nó MIN com filhos 0 e 0.
    Valor de B = 0.

    MAX deve escolher B, pois 0 > -1.
    """

    node_a = DebugState(
        "A",
        player="W",
        children={
            (0, 0): DebugState("A1", player="B", terminal=True, value=1),
            (1, 0): DebugState("A2", player="B", terminal=True, value=-1),
        }
    )

    node_b = DebugState(
        "B",
        player="W",
        children={
            (0, 0): DebugState("B1", player="B", terminal=True, value=0),
            (1, 0): DebugState("B2", player="B", terminal=True, value=0),
        }
    )

    root = DebugState(
        "root",
        player="B",
        children={
            (0, 0): node_a,
            (1, 0): node_b,
        }
    )

    move = minimax_move(root, -1, debug_eval)

    assert move == (1, 0), f"Esperado (1, 0), recebido {move}"


def test_limite_de_profundidade():
    """
    Testa se max_depth funciona.

    Com max_depth = 1, o algoritmo deve avaliar os sucessores diretamente,
    sem descer mais.
    """

    node_a = DebugState("A", player="W", terminal=False, value=5)
    node_b = DebugState("B", player="W", terminal=False, value=2)

    root = DebugState(
        "root",
        player="B",
        children={
            (0, 0): node_a,
            (1, 0): node_b,
        }
    )

    move = minimax_move(root, 1, debug_eval)

    assert move == (0, 0), f"Esperado (0, 0), recebido {move}"


def test_poda_alfa_beta():
    """
    Testa se a poda alfa-beta evita avaliar um ramo desnecessário.

    Estrutura:

          MAX
         /   \
        A     B
       MIN   MIN
      /  \   /  \
     10 10  0  ERRO

    Depois de avaliar A, MAX já tem alpha = 10.
    Ao entrar em B, MIN encontra 0.
    Como 0 <= alpha, o segundo filho de B deve ser podado.

    Se o algoritmo avaliar o nó "ERRO", o teste falha.
    """

    def eval_with_prune_check(state, root_player):
        if state.name == "ERRO":
            raise AssertionError("A poda falhou: avaliou um nó que deveria ter sido podado.")
        return state.value

    node_a = DebugState(
        "A",
        player="W",
        children={
            (0, 0): DebugState("A1", player="B", terminal=True, value=10),
            (1, 0): DebugState("A2", player="B", terminal=True, value=10),
        }
    )

    node_b = DebugState(
        "B",
        player="W",
        children={
            (0, 0): DebugState("B1", player="B", terminal=True, value=0),
            (1, 0): DebugState("ERRO", player="B", terminal=True, value=999),
        }
    )

    root = DebugState(
        "root",
        player="B",
        children={
            (0, 0): node_a,
            (1, 0): node_b,
        }
    )

    move = minimax_move(root, -1, eval_with_prune_check)

    assert move == (0, 0), f"Esperado (0, 0), recebido {move}"


if __name__ == "__main__":
    run_test("Teste 1: única jogada", test_unica_jogada)
    run_test("Teste 2: MAX escolhe maior valor", test_max_escolhe_maior_valor)
    run_test("Teste 3: MIN escolhe pior para MAX", test_min_escolhe_pior_para_max)
    run_test("Teste 4: limite de profundidade", test_limite_de_profundidade)
    run_test("Teste 5: poda alfa-beta", test_poda_alfa_beta)