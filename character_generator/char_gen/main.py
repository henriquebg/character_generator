import numpy as np
from PIL import Image
from AlgoritmoGenetico import AlgoritmoGenetico
from random import randrange
import imageio

NOME_ARQUIVO = 'final_fantasy_6.png'
TAMANHO = [18, 25]
IMAGENS_IGNORADAS = [99, 98]
ESCALA_IMAGEM = 4

imagens_gif = []
DEBUG_GERACOES_GIF = False
DEBUG_GERACOES_IMAGEM = False

NUM_GENERACOES = 10
SECCAO_MINIMA = 1 / 8
SECCAO_MAXIMA = 1 / 2


def main():
    total_pixels = TAMANHO[1] * TAMANHO[0]
    TAMANHOS_SECCAO_CROMOSSOMO = []

    for x in range(2, total_pixels):
        if total_pixels % x == 0:
            if x >= total_pixels * SECCAO_MINIMA and x <= total_pixels * SECCAO_MAXIMA:
                TAMANHOS_SECCAO_CROMOSSOMO.append(x)

    print(TAMANHOS_SECCAO_CROMOSSOMO)
    imagens_array = get_imagens_array(NOME_ARQUIVO, TAMANHO, IMAGENS_IGNORADAS)
    #imagens_array = get_imagens_array(NOME_ARQUIVO, TAMANHO, [99, 98])
    #imagens_array = get_imagens_array(NOME_ARQUIVO, TAMANHO, [151, 152, 153, 154, 155, 156, 157, 158, 159])
    #imagens_array = get_imagens_array(NOME_ARQUIVO, TAMANHO, [53, 54, 55, 56, 57, 58, 59])

    for x in range(0, NUM_GENERACOES):
        if DEBUG_GERACOES_GIF:
            buffer_para_gif(imagens_array, x)

        index_seccao = randrange(0, len(TAMANHOS_SECCAO_CROMOSSOMO))
        tamanho_seccao = TAMANHOS_SECCAO_CROMOSSOMO[index_seccao]
        print('Tamanho da secção: ' + str(tamanho_seccao))
        algoritmo = AlgoritmoGenetico(imagens_array, TAMANHO, tamanho_seccao)
        algoritmo.cruzar()
        imagens_array = algoritmo.get_imagens_array_gerado()

    if DEBUG_GERACOES_GIF:
        imageio.mimsave('img_sprites/debug/imagens.gif', imagens_gif)

    for x in range(0, len(imagens_array)):
        imagem = Image.fromarray(imagens_array[x], 'RGB')
        imagem_nova = imagem.resize([imagem.size[0] * ESCALA_IMAGEM, imagem.size[1] * ESCALA_IMAGEM], Image.NEAREST)
        imagem_nova.save('img_sprites/resultado' + str(x) + '.png')


def get_imagens_array(nome_arquivo, tamanho, imagens_ignoradas):
    imagem = Image.open(nome_arquivo).convert('RGB')
    im_rgb_array = np.array(imagem)
    count = 0
    imagens_array = []

    for lin in range(0, int(im_rgb_array.shape[0] / tamanho[1])):
        for col in range(0, int(im_rgb_array.shape[1] / tamanho[0])):
            if count not in imagens_ignoradas:
                imagem_matriz = np.zeros((tamanho[1], tamanho[0], 3), dtype=np.uint8)

                for i in range(0, im_rgb_array.shape[2]):
                    comeco = [lin * tamanho[1], col * tamanho[0]]
                    fim = [comeco[0] + tamanho[1], comeco[1] + tamanho[0]]
                    imagem_matriz[:,:,i] = im_rgb_array[comeco[0]:fim[0], comeco[1]:fim[1], i]
                    #print("")
                    #print(imagem_matriz)

                imagens_array.append(imagem_matriz)
            else:
                print('Imagem ignorada: ' + str(count))
            count += 1

    print('Total de imagens carregadas: ' + str(len(imagens_array)))
    return imagens_array

def buffer_para_gif(imagens_array, geracao):
    imagens_geracao = []

    for x in range(0, len(imagens_array)):
        imagem = Image.fromarray(imagens_array[x], 'RGB')
        imagem = imagem.resize([imagem.size[0] * ESCALA_IMAGEM, imagem.size[1] * ESCALA_IMAGEM], Image.NEAREST)
        imagens_geracao.append(imagem)
        
    total_width = TAMANHO[0] * ESCALA_IMAGEM * 10
    qtde_height = int(len(imagens_geracao) / 10) + 1
    max_height = TAMANHO[1] * ESCALA_IMAGEM * qtde_height
    nova_imagem = Image.new('L', (total_width, max_height))
    x_offset = 0
    y_count = 0
    count = 0

    for x in range(0, len(imagens_geracao)):
        nova_imagem.paste(imagens_geracao[x], (x_offset, y_count * TAMANHO[1] * ESCALA_IMAGEM))
        x_offset += TAMANHO[0] * ESCALA_IMAGEM

        if x % 10 == 0 and x > 0:
            x_offset = 0
            y_count += 1

    for x in range(0, 15):
        imagens_gif.append(np.asarray(nova_imagem, np.uint8))
    
    if DEBUG_GERACOES_IMAGEM:
        nova_imagem.save('img_sprites/debug/geracao' + str(geracao) + '.png')

if __name__ == "__main__":
    main()
