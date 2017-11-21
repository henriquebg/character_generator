import sys
import numpy as np
from random import randrange
from char_gen.Cromossomo import Cromossomo
from char_gen.TiposCruzamento import TiposCruzamento
from collections import Counter
from PIL import Image

#Classe que implementa o algoritmo genetico em si
class AlgoritmoGenetico(object):
    isValido = None
    cromossomos = None
    tamanho_seccao = None
    cromossomos_gerados = None
    tamanho_imagem = None

    #Inicializando os atributos e testando se todas as imagens inseridas
    #possuem as mesmas dimensoes nas tres camadas R (Red), G (Green) e B (Blue).
    #Nesta etapa as matrizes tridimensionais do tipo numpy sao convertidas em
    #objetos Cromossomo.
    def __init__(self, imagens_array, tamanho_imagens, tamanho_seccao):
        self.isValido = True
        self.cromossomos = []
        self.tamanho_seccao = tamanho_seccao
        self.cromossomos_gerados = []
        self.tamanho_imagem = tamanho_imagens
        
        for x in range(0, len(imagens_array)):
            for y in range(0, imagens_array[x].shape[2]):
                if imagens_array[x][:,:,y].shape[0] == self.tamanho_imagem[1] and imagens_array[x][:,:,y].shape[1] == self.tamanho_imagem[0]:
                    self.isValido &= True
                else:
                    self.isValido &= False

        if self.isValido:
            for x in range(0, len(imagens_array)):
                cromossomos_imagem = []

                for y in range(0, imagens_array[x].shape[2]):
                    cromossomo_im = Cromossomo()
                    cromossomo_im.criar_genes(imagens_array[x][:,:,y])
                    cromossomos_imagem.append(cromossomo_im)

                self.cromossomos.append(cromossomos_imagem)
            
            self.criar_referencia_avaliacao(imagens_array)
        else:
            raise Exception("O tamanho das imagens devem ser iguais")


    #Esta funçao ainda nao esta em uso, mas sera utilizada em futuras implementacoes
    #Ela cria uma imagem de referencia que sera utilizada para avaliar se a imagem gerada
    #e aceitavel ou nao. Esta imagem referencia e gerada a partir da moda de todas as imagens
    #do array passado no construtor.
    def criar_referencia_avaliacao(self, imagens_array):
        moda_array = np.zeros((self.tamanho_imagem[1], self.tamanho_imagem[0], 3), dtype=np.uint8)
        count = 0
        for dim in range(0, imagens_array[0].shape[2]):
            for lin in range(0, imagens_array[0].shape[0]):
                for col in range(0, imagens_array[0].shape[1]):
                    index_array = []

                    for index in range(0, len(imagens_array)):
                        index_array.append(imagens_array[index][lin,col,dim])
                        count += 1              
                
                    data = Counter(index_array)
                    moda_index = data.most_common(1)
                    moda_array[lin,col,dim] = moda_index[0][0]
        

    #Este algoritmo de cruzamento apresenta duas tecnicas de cruzamento: A de troca de genes e a de media
    #Na troca de genes, ele simplesmente pega uma seccao da amostra atual e troca com a seccao de mesmo tamanho
    #e posicao de uma amostra aleatoria. Alem da amostra ser aleatoria, o algoritmo tambem define de forma aleatoria
    #se vai manter a seccao da amostra principal ou se vai trocar com o da amostra aleatoria
    #Ja a tecnica da media simplesmente acha a media entre as duas seccoes (amostra atual e aleatoria)
    #No sistema, somente o algoritmo de troca esta sendo utilizado no momento.
    def cruzar(self, tipo_cruzamento):

        for x in range(0, len(self.cromossomos)):
            if self.cromossomos[x][0].get_tamanho() % self.tamanho_seccao != 0:
                raise Exception("O tamanho da secção do crossover deve ser divisível pelo tamanho dos cromossomos.")
            else:
                novos_genes = [''] * 3
                
                for y in range(0, int(self.cromossomos[x][0].get_tamanho() / self.tamanho_seccao)):
                    index_cromossomo_2 = randrange(0, len(self.cromossomos) - 1)
                    cromossomo_2 = []
                    
                    for i in range(0, len(self.cromossomos[index_cromossomo_2])):
                        cromossomo_2.append(self.cromossomos[index_cromossomo_2][i])
                    
                    current_index = y * self.tamanho_seccao
                    					
                    if tipo_cruzamento == TiposCruzamento.TROCA:
                        crossover_selector = randrange(0,100) % 2

                        if crossover_selector == 0:
                            for i in range(0, len(self.cromossomos[x])):
                                gene = self.cromossomos[x][i].get_genes(current_index, self.tamanho_seccao)
                                novos_genes[i] += gene
                        else:
                            for i in range(0, len(cromossomo_2)):
                                gene = cromossomo_2[i].get_genes(current_index, self.tamanho_seccao)
                                novos_genes[i] += gene

                    elif tipo_cruzamento == TiposCruzamento.MEDIA:                    
                        for i in range(0, len(self.cromossomos[x])):
                            gene1 = self.cromossomos[x][i].get_genes(current_index, self.tamanho_seccao)
                            gene2 = cromossomo_2[i].get_genes(current_index, self.tamanho_seccao)

                            for j in range (0, len(gene1)):
                                novos_genes[i] += str(chr(int((ord(gene1[j]) + ord(gene2[j])) / 2)))                    

                cromossomos_im = []

                for i in range(0, len(novos_genes)):
                    cromossomo_comp = Cromossomo()
                    cromossomo_comp.add_genes(novos_genes[i])
                    cromossomos_im.append(cromossomo_comp)

                self.cromossomos_gerados.append(cromossomos_im)


    #Esta funcao retorna as imagens geradas em forma de um array de matrizes Numpy tridimensionais
    #Aqui ha a conversao dos objetos Cromossomos em matrizes tridimensionais. Entao elas sao armazenadas
    #em um array que sera retornado.
    def get_imagens_array_gerado(self, filtro):
        imagens_array_gerado = []
        
        for x in range(0, len(self.cromossomos_gerados)):
            imagem_array = np.zeros((self.tamanho_imagem[1], self.tamanho_imagem[0], 3), dtype=np.uint8)

            for y in range(0, len(self.cromossomos_gerados[x])):
                imagem_array[:,:,y] = self.cromossomos_gerados[x][y].para_array(self.tamanho_imagem[0])

            for i in range(0, self.tamanho_imagem[1]):
                for j in range(0, self.tamanho_imagem[0]):
                    if imagem_array[i, j, 0] > filtro[0] and imagem_array[i, j, 1] > filtro[1] and imagem_array[i, j, 2] > filtro[2]:
                        imagem_array[i, j, 0] = 255
                        imagem_array[i, j, 1] = 255
                        imagem_array[i, j, 2] = 255
                
      
            imagens_array_gerado.append(imagem_array)

        return imagens_array_gerado
