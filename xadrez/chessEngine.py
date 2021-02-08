
#Chess engine 
#responsavel pelas acoes do usuario pela apresentacao e corrente estado do jogo
#
MORD = 5
class EstadoJogo():
    def __init__(self):
        #O taboleiro eh 5x5 as letras representam o tipo de peça ex. "b" -black e "K" - King
        #"--" representa casas ou espacos vazios ou seja sem nenhuma peça
        self.tabuleiro = [
            ["bR", "bN", "bB", "bQ", "bK"],
            ["bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK"]]

        self.funcoesDeMovimento = {'p': self.getPeaMove, 'R': self.getRookMoves, 'N': self.getKnightMoves,
                                   'B': self.getBishopMoves, 'Q': self.getQueenMoves, 'K': self.getKingMoves}

        self.whiteToMove = True  # determina o turno do jogador
        self.moveLog = []
        self.wKingLocation = (4, 4)  # posicao inicial do rei no tabuleirio[5X5] ****
        self.bKingLocation = (0, 4)
        self.checkMate = False
        self.staleMate = False
        # self.enpassantPossible = ()  # cordenadas onde enpassant captura eh possivel
        self.currentCastlingRight = CastleRights(True, True, True, True)
        self.castleRightsLog = [CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks, self.currentCastlingRight.wqs, self.currentCastlingRight.bqs)]

    # tira a peca de uma posicao e poe em outra
    def makeMove(self, movimento):
        self.tabuleiro[movimento.inicioLinha][movimento.inicioColuna] = "--"
        self.tabuleiro[movimento.fimLinha][movimento.fimColuna] = movimento.pecaMovida
        self.moveLog.append(movimento)  # pode servir para voltar a jogada
        self.whiteToMove = not self.whiteToMove

        # actualiza a localizacao do rei
        if movimento.pecaMovida == 'wK':
            self.wKingLocation = (movimento.fimLinha, movimento.fimColuna)
        elif movimento.pecaMovida == 'bK':
            self.bKingLocation = (movimento.fimLinha, movimento.fimColuna)

        # promocao do peao
        if movimento.ehPeaPromovido:
            self.tabuleiro[movimento.fimLinha][movimento.fimColuna] = movimento.pecaMovida[0] + 'Q'

        # enpassant move
        # if movimento.ehEnpassantMove:
        #     self.tabuleiro[movimento.inicioLinha][movimento.fimColuna] = '--'  # Captura o peao
        # # actualiza enpassantPossible variavel
        # if movimento.pecaMovida[1] == 'p' and abs(movimento.inicioLinha - movimento.fimLinha) == 2:  # somente peaos q avancou 2 quadra.
        #     self.enpassantPossible = ((movimento.inicioLinha + movimento.fimLinha) // 2, movimento.inicioColuna)
        # else:
        #     self.enpassantPossible = ()

        #castle Move ...
        if movimento.isCastleMove:
            if movimento.fimColuna - movimento.inicioColuna == 2: #castle no lado do rei
                self.tabuleiro[movimento.fimLinha][movimento.fimColuna-1] = self.tabuleiro[movimento.fimLinha][movimento.fimColuna+1]
                self.tabuleiro[movimento.fimLinha][movimento.fimColuna+1] = "--" #apaga velha torre
            else: #castle no lado da raihna ou dama
                self.tabuleiro[movimento.fimLinha][movimento.fimColuna+1] = self.tabuleiro[movimento.fimLinha][movimento.fimColuna-2]
                self.tabuleiro[movimento.fimLinha][movimento.fimColuna-2] = "--" #apaga velha torre

        # actualiza castling a direira - quando a torre ou o rei se move
        self.updateCastleRights(movimento)
        self.castleRightsLog.append(
            CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks, self.currentCastlingRight.wqs,
                         self.currentCastlingRight.bqs))

    # desfaz o ultimo movimento feito
    def desfasMovimento(self):
        if len(self.moveLog) != 0:  # verifica se ja se fez algum movimento
            moves = self.moveLog.pop()
            self.tabuleiro[moves.inicioLinha][moves.inicioColuna] = moves.pecaMovida
            self.tabuleiro[moves.fimLinha][moves.fimColuna] = moves.pecaCapturada
            self.whiteToMove = not self.whiteToMove
            # actualiza a localizacao do rei
            if moves.pecaMovida == 'wK':
                self.wKingLocation = (moves.inicioLinha, moves.inicioColuna)
            elif moves.pecaMovida == 'bK':
                self.bKingLocation = (moves.inicioLinha, moves.inicioColuna)
            # # defaz en passant
            # if moves.ehEnpassantMove:
            #     self.tabuleiro[moves.fimLinha][moves.fimColuna] = '--'  # deixa o espaco me branco
            #     self.tabuleiro[moves.inicioLinha][moves.inicioColuna] = moves.pecaCapturada
            #     self.enpassantPossible = (moves.fimLinha, moves.fimColuna)
            # # desfaz 2 dois quadrados que o pea avancou
            # if moves.pecaMovida[1] == 'p' and abs(moves.inicioLinha - moves.fimLinha) == 2:
            #     self.enpassantPossible = ()

            # desfaz casling a direita
            self.castleRightsLog.pop()  # poe   ...Video 9
            newRights = self.castleRightsLog[-1]  # poe o corrente castle como ultimo na lista
            self.currentCastlingRight = CastleRights(newRights.wks, newRights.bks, newRights.wqs, newRights.bqs)
            # desfaz o movimento castle
            if moves.isCastleMove:
                if moves.fimColuna - moves.inicioColuna == 2: #castle no lado do rei
                    self.tabuleiro[moves.fimLinha][moves.fimColuna+1] = self.tabuleiro[moves.fimLinha][moves.fimColuna-1]
                    self.tabuleiro[moves.fimLinha][moves.fimColuna-1] = '--' #vota a por velha torre
                else: #castle no lado da raihna ou dama
                    self.tabuleiro[moves.fimLinha][moves.fimColuna-2] = self.tabuleiro[moves.fimLinha][moves.fimColuna+1]
                    self.tabuleiro[moves.fimLinha][moves.fimColuna+1] = '--' # volta a por velha torre

    # actualiza o castle a direira
    def updateCastleRights(self, movimento):
        if movimento.pecaMovida == 'wK':
            self.currentCastlingRight.wks = False
            self.currentCastlingRight.wqs = False
        elif movimento.pecaMovida == 'bK':
            self.currentCastlingRight.bks = False
            self.currentCastlingRight.bqs = False
        elif movimento.pecaMovida == 'wR':
            if movimento.inicioLinha == MORD - 1:
                if movimento.inicioColuna == 0:  # torre esquerda
                    self.currentCastlingRight.wqs = False
                elif movimento.inicioColuna == MORD - 1:  # torre direita
                    self.currentCastlingRight.wks = False
        elif movimento.pecaMovida == 'bR':
            if movimento.inicioLinha == 0:
                if movimento.inicioColuna == 0:  # torre esquerda
                    self.currentCastlingRight.bqs = False
                elif movimento.inicioColuna == MORD - 1:  # torre direita
                    self.currentCastlingRight.bks = False

    """
    Todos movimentos considerando os checks
    """

    def getMovimentosValidos(self):
        # for log in self.castleRightsLog:
        #     print(log.wks, log.bks, log.wks, log.bqs, end=",")
        # print()
        # tempEnpassantPossivel = self.enpassantPossible
        tempCastleRights = CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                        self.currentCastlingRight.wqs, self.currentCastlingRight.bqs) # copia dos castle a direita agora
        # 1.) gera todos possiveis movimentos
        moves = self.getTodosPossiveisMove()
        # if self.whiteToMove:
        #     self.getCastleMoves(self.wKingLocation[0], self.wKingLocation[1], moves)
        # else:
        #     self.getCastleMoves(self.bKingLocation[0], self.bKingLocation[1], moves)
        # 2.) para cada movim., faz um movimento
        for i in range(len(moves) - 1, -1, -1):
            self.makeMove(moves[i])
            # 3.) gera todos movimentos do oppenente
            # 4.) para cada movimento do oponente verifica se atacam o rei
            self.whiteToMove = not self.whiteToMove
            if self.inCheck():
                moves.remove(moves[i])  # 5.) se atacarem o rei nao sera um movimento valido
            self.whiteToMove = not self.whiteToMove
            self.desfasMovimento()
        if len(moves) == 0:  # esta em checkmate ou slatenate
            if self.inCheck():
                self.checkMate = True
            else:
                self.staleMate = True

        if self.whiteToMove:
        #     self.getCastleMoves(self.wKingLocation[0], self.wKingLocation[1], moves) #noa precisarei
        # else:
            self.getCastleMoves(self.bKingLocation[0], self.bKingLocation[1], moves)
        # self.enpassantPossible = tempEnpassantPossivel
        self.currentCastlingRight = tempCastleRights
        return moves

    """ determina se corrent jogador esta em check """

    def inCheck(self):
        if self.whiteToMove:
            return self.squareUnderAttack(self.wKingLocation[0], self.wKingLocation[1])
        else:
            return self.squareUnderAttack(self.bKingLocation[0], self.bKingLocation[1])

    """ determina se o oponente pode o quadrado lin, col """

    def squareUnderAttack(self, lin, col):
        self.whiteToMove = not self.whiteToMove  # troca para o turno do oponente
        oppMoves = self.getTodosPossiveisMove()
        self.whiteToMove = not self.whiteToMove  # troca devola
        for mover in oppMoves:
            if mover.fimLinha == lin and mover.fimColuna == col:  # quadrado sobre ataque
                return True
        return False

    """
    Todos movimentos sem considerar os checks
    """

    def getTodosPossiveisMove(self):
        movimentos = []
        for lin in range(len(self.tabuleiro)):  # numero de linhas
            for col in range(len(self.tabuleiro[lin])):  # numero de colunas em um linha
                turn = self.tabuleiro[lin][col][0]
                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    peca = self.tabuleiro[lin][col][1]
                    self.funcoesDeMovimento[peca](lin, col, movimentos)  # chama a funcao de movimento apropriada
        return movimentos

    """ 
        devolve todos movime. do pea localizado em uma linha,
        coluna e add esses move. na lista
    """

    def getPeaMove(self, lin, col, movimentos):
        if self.whiteToMove:  # movimento do peao branco
            if self.tabuleiro[lin - 1][col] == "--":  # peao avanca 1 quadrado
                movimentos.append(move((lin, col), (lin - 1, col), self.tabuleiro))
                if lin == 6 and self.tabuleiro[lin - 2][col] == "--":  # peao avanca dois quadrado
                    movimentos.append(move((lin, col), (lin - 2, col), self.tabuleiro))
            # Capturas
            if col - 1 >= 0:  # captura na esquerda
                if self.tabuleiro[lin - 1][col - 1][0] == 'b':  # captura peca (preta)
                    movimentos.append(move((lin, col), (lin - 1, col - 1), self.tabuleiro))
                # elif (lin - 1, col - 1) == self.enpassantPossible:
                #     movimentos.append(move((lin, col), (lin - 1, col - 1), self.tabuleiro, ehEnpassantMove=True))
            if col + 1 <= MORD - 1:  # captura pela direita
                if self.tabuleiro[lin - 1][col + 1][0] == 'b':  # captura peca (preta)
                    movimentos.append(move((lin, col), (lin - 1, col + 1), self.tabuleiro))
                # elif (lin - 1, col + 1) == self.enpassantPossible:
                #     movimentos.append(move((lin, col), (lin - 1, col + 1), self.tabuleiro, ehEnpassantMove=True))

        else:  # movimento do peao preto
            if self.tabuleiro[lin + 1][col] == "--":  # peao avanca 1 quadrado
                movimentos.append(move((lin, col), (lin + 1, col), self.tabuleiro))
                if lin == 1 and self.tabuleiro[lin + 2][col] == "--":  # peao avanca dois quadrado
                    movimentos.append(move((lin, col), (lin + 2, col), self.tabuleiro))
            # Capturas
            if col - 1 >= 0:  # captura na esquerda
                if self.tabuleiro[lin + 1][col - 1][0] == 'w':  # captura peca (preta)
                    movimentos.append(move((lin, col), (lin + 1, col - 1), self.tabuleiro))
                # elif (lin + 1, col - 1) == self.enpassantPossible:
                #     movimentos.append(move((lin, col), (lin + 1, col - 1), self.tabuleiro, ehEnpassantMove=True))
            if col + 1 <= MORD - 1:  # captura pela direita
                if self.tabuleiro[lin + 1][col + 1][0] == 'w':  # captura peca (preta)
                    movimentos.append(move((lin, col), (lin + 1, col + 1), self.tabuleiro))
                # elif (lin + 1, col + 1) == self.enpassantPossible:
                #     movimentos.append(move((lin, col), (lin + 1, col + 1), self.tabuleiro, ehEnpassantMove=True))

    """ 
        devolve todos movime. da torre localizado em uma linha,  
        coluna e add esses move. na lista
    """

    def getRookMoves(self, lin, col, movimentos):
        direcoes = ((-1, 0), (0, -1), (1, 0), (0, 1))
        adversarioCor = "b" if self.whiteToMove else "w"
        for d in direcoes:
            for i in range(1, MORD):  # intervalo de 1 a MORD  [MORDXMORD] ******
                fimDalinha = lin + d[0] * i
                fimDaColuna = col + d[1] * i
                if 0 <= fimDalinha < MORD and 0 <= fimDaColuna < MORD:  # *****[MORDXMORD]
                    pecaFinal = self.tabuleiro[fimDalinha][fimDaColuna]
                    if pecaFinal == "--":  # espaco vazio valido
                        movimentos.append(move((lin, col), (fimDalinha, fimDaColuna), self.tabuleiro))
                    elif pecaFinal[0] == adversarioCor:  # adversario peca valoda
                        movimentos.append(move((lin, col), (fimDalinha, fimDaColuna), self.tabuleiro))
                        break
                    else:  # peca da mesma cor
                        break
                else:
                    break

    """ 
        devolve todos movime. do Cavalo localizado em uma linha, 
        coluna e add esses move. na lista
    """

    def getKnightMoves(self, lin, col, movimentos):
        cavalo = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        aliadoCor = "w" if self.whiteToMove else "b"
        for m in cavalo:
            fimDalinha = lin + m[0]
            fimDaColuna = col + m[1]
            if 0 <= fimDalinha < MORD and 0 <= fimDaColuna < MORD:
                pecaFinal = self.tabuleiro[fimDalinha][fimDaColuna]
                if pecaFinal[0] != aliadoCor:
                    movimentos.append(move((lin, col), (fimDalinha, fimDaColuna), self.tabuleiro))

    """ 
        devolve todos movime. do bispo localizado em uma linha, 
        coluna e add esses move. na lista
    """

    def getBishopMoves(self, lin, col, movimentos):
        direcoes = ((-1, -1), (-1, 1), (1, -1), (1, 1))  # 4 diagonais
        adversarioCor = "b" if self.whiteToMove else "w"
        for d in direcoes:
            for i in range(1, MORD):  # intervalo de 1 a 8  [8X8] ******
                fimDalinha = lin + d[0] * i
                fimDaColuna = col + d[1] * i
                if 0 <= fimDalinha < MORD and 0 <= fimDaColuna < MORD:  # *****[8X8]
                    pecaFinal = self.tabuleiro[fimDalinha][fimDaColuna]
                    if pecaFinal == "--":  # espaco vazio valido
                        movimentos.append(move((lin, col), (fimDalinha, fimDaColuna), self.tabuleiro))
                    elif pecaFinal[0] == adversarioCor:  # adversario peca valoda
                        movimentos.append(move((lin, col), (fimDalinha, fimDaColuna), self.tabuleiro))
                        break
                    else:  # peca da mesma cor
                        break
                else:
                    break

    """ 
        devolve todos movime. da rainha localizado em uma linha, 
        coluna e add esses move. na lista
    """

    def getQueenMoves(self, lin, col, movimentos):
        self.getRookMoves(lin, col, movimentos)
        self.getBishopMoves(lin, col, movimentos)

    """ 
        devolve todos movime. do Rei localizado em uma linha, 
        coluna e add esses move. na lista
    """

    def getKingMoves(self, lin, col, movimentos):
        kingsMoves = ((-1, -1), (-1, 0), (-1, 1), (0, 1), (0, 1), (1, -1), (1, 0), (1, 1))
        aliadoCor = "w" if self.whiteToMove else "b"
        for i in range(8):
            fimDalinha = lin + kingsMoves[i][0]
            fimDaColuna = col + kingsMoves[i][1]
            if 0 <= fimDalinha < MORD and 0 <= fimDaColuna < MORD:  # *****[MORDXMORD]
                pecaFinal = self.tabuleiro[fimDalinha][fimDaColuna]
                if pecaFinal[0] != aliadoCor:
                    movimentos.append(move((lin, col), (fimDalinha, fimDaColuna), self.tabuleiro))


    """
    gera todos movimentos validos para o rei, e adiciona - os na lista
    """

    def getCastleMoves(self, lin, col, movimentos):
        if self.squareUnderAttack(lin, col):
            return  # nao pode se mover enquanto estiver em check
        # if (self.whiteToMove and self.currentCastlingRight.wks) or (not self.whiteToMove and self.currentCastlingRight.bks):
        #     self.getKingsideCastleMoves(lin, col, movimentos) #*** nao precisarei
        if (self.whiteToMove and self.currentCastlingRight.wqs) or (not self.whiteToMove and self.currentCastlingRight.bqs):
            self.getQueensideCastleMoves(lin, col, movimentos)

    # def getKingsideCastleMoves(self, lin, col, movimentos): #**nao precisarei
    #     if self.tabuleiro[lin][col + 1] == '--' and self.tabuleiro[lin][col + 2] == '--':
    #         if not self.squareUnderAttack(lin, col + 1) and not self.squareUnderAttack(lin, col + 2):
    #             movimentos.append(move((lin, col), (lin, col + 2), self.tabuleiro, isCastleMove=True))

    def getQueensideCastleMoves(self, lin, col, movimentos):
        if self.tabuleiro[lin][col - 1] == '--' and self.tabuleiro[lin][col - 2] == '--' and self.tabuleiro[lin][col - 3]:
            if not self.squareUnderAttack(lin, col - 1) and not self.squareUnderAttack(lin, col - 2):
                movimentos.append(move((lin, col), (lin, col - 2), self.tabuleiro, isCastleMove=True))


class CastleRights():
        def __init__(self, wks, bks, wqs, bqs):
            self.wks = wks
            self.bks = bks
            self.wqs = wqs
            self.bqs = bqs

class move():
        # mapas chavas para valores
        # chave: valor
        # mapear o tabuleiro
        ranksToRows = {"1": MORD - 1, "2": 6, "3": 5, "4": 4,
                       "5": 3, "6": 2, "7": 1, "8": 0}
        rowsToRanks = {v: k for k, v in ranksToRows.items()}  # adicionado ao dicionario de forma reversa ou na ordem inversa
        filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3,
                       "e": 4, "f": 5, "g": 6, "h": MORD - 1}
        colsTofiles = {v: k for k, v in filesToCols.items()}  # mesma coisa

        def __init__(self, inicioSq, fimSq, tabuleiro, ehEnpassantMove=False, isCastleMove=False):
            self.inicioLinha = inicioSq[0]
            self.inicioColuna = inicioSq[1]
            self.fimLinha = fimSq[0]
            self.fimColuna = fimSq[1]
            self.pecaMovida = tabuleiro[self.inicioLinha][self.inicioColuna]
            self.pecaCapturada = tabuleiro[self.fimLinha][self.fimColuna]

            # promocao do peao
            self.ehPeaPromovido = (self.pecaMovida == 'wp' and self.fimLinha == 0) or (self.pecaMovida == 'bp' and self.fimLinha == MORD - 1)
            # enpassant
            # self.ehEnpassantMove = ehEnpassantMove
            # if self.ehEnpassantMove:
            #     self.pecaCapturada = 'wp' if self.pecaMovida == 'bp' else 'bp'
            # castle move
            self.isCastleMove = isCastleMove
            self.moveID = self.inicioLinha * 1000 + self.inicioColuna * 100 + self.fimLinha * 10 + self.fimColuna

            # super().__init__()

        """
        Overriting metodos iguais
        """

        def __eq__(self, value):
            if isinstance(value, move):
                return self.moveID == value.moveID
            return False

        # notacao do xadrez para as jogadas realizadas
        def getChessNotation(self):
            return self.getRankFile(self.inicioLinha, self.inicioColuna) + self.getRankFile(self.fimLinha, self.fimColuna)

        def getRankFile(self, linha, coluna):
            return self.colsTofiles[coluna] + self.rowsToRanks[linha]