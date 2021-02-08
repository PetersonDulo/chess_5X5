import random

pontuacaoPeca = {"K": 0, "Q": 10, "R": 5, "B": 3, "N": 3, "p": 1}
CHECKMATE = 1000
STALEMATE = 0
#as pretas tentam tornar o valor o mais negativo possivel  e as brancas o mais positivo possivel
"""
    return um movimento aleatorio
"""
def enconMovAleatorio(movimentosValidos):
    return movimentosValidos[random.randint(0, len(movimentosValidos)-1)]
"""
    encontra o melhor movimento
"""
def findBestMove(es, movimentosValidos):
    turnMultiplier = 1 if es.whiteToMove else -1
    opponentMinMaxScore = CHECKMATE  #  ... para depois maximizar ou tentar o resultado o mais positivo possivel
    jogadorMelhorMove = None
    random.shuffle(movimentosValidos)
    for playerMove in movimentosValidos:
        es.makeMove(playerMove)
        opponentsMoves = es.getMovimentosValidos()
        opponentMaxPontuacao = -CHECKMATE
        for opponentsMove in opponentsMoves:
            es.makeMove(opponentsMove)
            if es.checkMate:
                pontuacao = -turnMultiplier * CHECKMATE
            elif es.staleMate:
                pontuacao = STALEMATE
            else:
                pontuacao = -turnMultiplier * scoreMaterial(es.tabuleiro)
            if pontuacao > opponentMaxPontuacao:
                opponentMaxPontuacao = pontuacao
            es.desfasMovimento()
        if opponentMaxPontuacao < opponentMinMaxScore:
            opponentMinMaxScore = opponentMaxPontuacao
            jogadorMelhorMove = playerMove
        es.desfasMovimento()
    return jogadorMelhorMove

"""
faz a pontuacao do tabuleiro baseando se no material(pecas em campo)
"""
def scoreMaterial(Tabuleiro):
    pontuacao = 0
    for lin in Tabuleiro:
        for quadrado in lin:
            if quadrado[0] == 'W':
                pontuacao +=pontuacaoPeca[quadrado[1]]
            elif quadrado[0] == 'b':
                pontuacao -= pontuacaoPeca[quadrado[1]]
    return pontuacao