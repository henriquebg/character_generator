import numpy as np
import math


#Classe que implementa os cromossomos utilizados pelo algoritmo genetico
class Cromossomo(object):
    genes = None

    def __init__(self):
        self.genes = ''


    #Esta funcao converte uma matriz unidimensional em uma cadeia de
    #caracteres ASCII com um offset de +33 na tabela ASCII
    #Isso significa que todas as cores em R, G e B serao normalizadas
    #de 0 a 255 para 0 a 32. Isso resulta em cores diferentes, porem
    #continuam fieis as originais.
    def criar_genes(self, imagem_array):
        for x in range(0, imagem_array.shape[0]):
            for y in range(0, imagem_array.shape[1]):
                norm = (round(imagem_array[x][y] / 255, 1)) * 32
                self.genes += str(chr(int(norm) + 33))


    def get_genes(self, index, tamanho):
        return self.genes[index : index + tamanho]


    def set_genes(self, index, gene):
        self.genes[index] = gene


    def add_genes(self, genes):
        self.genes += genes


    def get_tamanho(self):
        return len(self.genes)
    

    #Esta funcao converte a cadeia de genes (uma string de caracteres) em um array
    #unidimensional com valores de 0 a 255.
    def para_array(self, tamanho_da_linha):
        if len(self.genes) % tamanho_da_linha != 0:
            raise Exception("O tamanho dos genes não é divisivel pelo tamanho das linhas.")
        else:
            imagem_array = []

            for x in range(0, int(len(self.genes) / tamanho_da_linha)):
                current_index = x * tamanho_da_linha
                end_index = current_index + tamanho_da_linha
                linha = self.genes[current_index : end_index]
                imagem_linha = [0] * len(linha)

                for y in range(0, len(linha)):
                    desnorm = ((ord(linha[y]) - 33) / 32) * 255
                    imagem_linha[y] = int(desnorm)
                
                imagem_array.append(imagem_linha)
            
            return np.array(imagem_array, np.uint8)
