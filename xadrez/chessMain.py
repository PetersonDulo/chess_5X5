
"""
responsavel por armazenar toda informacao acerca do corrente estado do jogo
determina os movimentos validos
"""

import pygame as p
import chessEngine
from xadrez import SmartMoveFinder

WIDTH = HEIGHT = 512  #
DIMENSION = 5  #dimensao do Tabuleiro
MAX_FPS = 15  # para animacao soa 15 frames por segundo
SQ_SIZE = HEIGHT // DIMENSION  #tamnho do quadrado
IMAGES = {}

''' 
inicializa um dicionario global de imagens que vai ser chamado na class main
'''
def CarregarImagens():
    pecas = ['bN', 'bR', 'bB', 'bQ', 'bK', 'bp', 'wR', 'wQ', 'wN', 'wB', 'wK', 'wp']
    for peca in pecas:
        IMAGES[peca] = p.transform.scale(p.image.load("../xadrez/images/"+peca+".png"), (SQ_SIZE, SQ_SIZE)) #recebe caminho e tamanho
    #podemos acessar a imagem dizendo IMAGES['wp']
    
'''
essa e a funcao principal para o nosso codigo. isso vai manejar as entradas do usuario
 a actualizar os graficos
'''

def main():
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    es = chessEngine.EstadoJogo()
    movimentosValidos = es.getMovimentosValidos()
    movimentoFeito = False  #falg para quando um movimento eh
    animate = False #para quando uma animacao deve se mover
    # print(str(es.tabuleiro)+"\33[1;2;31m teste \33[m")
    CarregarImagens()
    running = True
    sqSelected = () #armazena o ultimo click do usuario tuple(lin col)
    playerClicks = [] #guarda os clicks do jogador(duas tuplas:[(6,4),(4,4)])
    gameOver = False

    playerOne = False  #se um humano esta jogando com as brancas sera True se nao False
    playerTwo = False  #se um humano esta jogando com as pretas sera True se nao False

    while running:
        humanTurn = (es.whiteToMove and playerOne) or (not es.whiteToMove and playerTwo)
        for e in p.event.get():
            if e.type == p.QUIT:  #ablita o botao de fechar
                running = False
            #mouse
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver and humanTurn:
                    local = p.mouse.get_pos()  #(x,y) localizacao do mouse
                    col = local[0]//SQ_SIZE
                    lin = local[1]//SQ_SIZE
                    if sqSelected == (lin, col): #clicou no mesmo quadrado duas vezes
                        sqSelected = () #desceleciona
                        playerClicks = [] #limpa ou apaga
                    else:
                        sqSelected = (lin, col)
                        playerClicks.append(sqSelected) #adicionamos o primeiro e o segundo click
                    if len(playerClicks) == 2: #depois do segundo click
                        move = chessEngine.move(playerClicks[0], playerClicks[1], es.tabuleiro)
                        print(move.getChessNotation())
                        for i in range(len(movimentosValidos)):
                            if move == movimentosValidos[i]:
                                es.makeMove(movimentosValidos[i]) #faz movimentos
                                movimentoFeito = True
                                animate = True
                                sqSelected = () #desceleciona
                                playerClicks = []
                            if not movimentoFeito:
                                playerClicks = [sqSelected]
            #Teclado
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:  #desfaz quando 'z' eh precionado
                    es.desfasMovimento()
                    movimentoFeito = True
                    animate = False
                if e.key == p.K_r:  #restaura o tabuleiro
                    es = chessEngine.EstadoJogo()
                    movimentosValidos = es.getMovimentosValidos()
                    sqSelected = ()
                    playerClicks = []
                    movimentoFeito = False
                    animate = False

        #IA move Finder
        if not gameOver and not humanTurn:
            AIMove = SmartMoveFinder.findBestMove(es,movimentosValidos)
            if AIMove is None:
                AIMove = SmartMoveFinder.enconMovAleatorio(movimentosValidos)
            es.makeMove(AIMove)
            movimentoFeito = True
            animate = True

        if movimentoFeito:
            if animate:
                animateMove(es.moveLog[-1], screen, es.tabuleiro, clock)
            movimentosValidos = es.getMovimentosValidos()
            movimentoFeito = False
            animate = False

        desenhaEstadoJogo(screen, es, movimentosValidos, sqSelected)

        if es.checkMate:
            gameOver = True
            if es.whiteToMove:
                drawText(screen, "Pretas vencem por checkmate")
            else:
                drawText(screen, "Brancas vencem por checkmate")
        elif es.staleMate:
            gameOver = True
            drawText(screen, "Stalemate (afogamento)")

        clock.tick(MAX_FPS)
        p.display.flip()

"""quadrado selecionado muda de cor"""
def highlightSquares(screen, es, movimentosValidos, sqSelected):
    if sqSelected != ():
        lin, col = sqSelected
        if es.tabuleiro[lin][col][0] == ('w' if es.whiteToMove else 'b'):  #eh a peca que pode ser movida
            #destaca o quadrado selecionado
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100) #tranparencia valores de 0 a 255
            s.fill(p.Color('blue'))
            screen.blit(s, (col*SQ_SIZE, lin*SQ_SIZE))
            #destaca o quadrado selecionado
            s.fill(p.Color('yellow'))  #Cor
            for moves in movimentosValidos:
                if moves.inicioLinha == lin and moves.inicioColuna == col:
                    screen.blit(s, (moves.fimColuna*SQ_SIZE, moves.fimLinha*SQ_SIZE))

"""
reponsavel pelos graficos no corrente estado de jogo
"""
def desenhaEstadoJogo(screen, es, movimentosValidos, sqSelected):
    desenhaTabuleiro(screen)
    highlightSquares(screen, es, movimentosValidos, sqSelected)
    desenhaPecas(screen, es.tabuleiro) #desenha as pecas nesses quadrados

#desenha quadrados no tabuleiro
def desenhaTabuleiro(screen):
    """ Cor do tabuleiro"""
    global colors
    colors = [p.Color("white"), p.Color("gray")]
    for lin in range(DIMENSION):
        for col in range(DIMENSION):
            cor = colors[((lin + col) % 2)]
            p.draw.rect(screen, cor, p.Rect(col*SQ_SIZE, lin*SQ_SIZE, SQ_SIZE, SQ_SIZE))

#adciona pecas destacando ou movendo sugerindo
def desenhaPecas(screen,tabuleiro):
    for lin in range(DIMENSION):
        for col in range(DIMENSION):
            peca = tabuleiro[lin][col]
            if peca != "--": #nao espaco vazio
                screen.blit(IMAGES[peca], p.Rect(col*SQ_SIZE, lin*SQ_SIZE, SQ_SIZE, SQ_SIZE))

def  animateMove(moves, screen, tabuleiro, clock):
    global colors
    dR = moves.fimLinha - moves.inicioLinha
    dC = moves.fimColuna - moves.inicioColuna
    framePorQuadrado = 10  #frama para mover um quadrado
    frameCount = (abs(dR)+abs(dC)) * framePorQuadrado
    for frame in range(frameCount + 1):
        lin, col = (moves.inicioLinha + dR * frame / frameCount, moves.inicioColuna + dC * frame / frameCount)
        desenhaTabuleiro(screen)
        desenhaPecas(screen, tabuleiro)
        #apaga a peca movida para o fim do quadrado
        color = colors[(moves.fimLinha + moves.fimColuna) % 2]
        fimQuadrado = p.Rect(moves.fimColuna*SQ_SIZE, moves.fimLinha*SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, fimQuadrado)
        #desenha peca capturada nos retanglos
        if moves.pecaCapturada != "--":
            screen.blit(IMAGES[moves.pecaCapturada], fimQuadrado)
        #desenha peca se movendo
        screen.blit(IMAGES[moves.pecaMovida], p.Rect(col * SQ_SIZE, lin * SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(60)

def drawText (screen, text):
    font = p.font.SysFont("Helvitca", 32, True, False)
    textObject = font.render(text, 0, p.Color('Gray'))
    textLocation = p.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH/2 - textObject.get_width()/2, HEIGHT/2 - textObject.get_height()/2)
    screen.blit(textObject, textLocation)
    textObject = font.render(text, 0, p.Color('Black'))
    screen.blit(textObject, textLocation.move(2, 2))

if __name__ == "__main__":
    main()
