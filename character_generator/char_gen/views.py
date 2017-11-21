import numpy as np
import os
import time
import glob
import threading
import json
import shutil
from django.core.files.storage import FileSystemStorage
from PIL import Image
from django.shortcuts import render
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from char_gen.AlgoritmoGenetico import AlgoritmoGenetico
from char_gen.TiposCruzamento import TiposCruzamento
from random import randrange

# Create your views here.
def index(request):
    return render(request, 'char_gen/index.html')

#Esta funcao recebe a imagem de upload, cria os diretorios a serem usados pela sessao,
#recorta a imagem em imagens individuais baseadas nos tamanhos informados no formulario
#principal e inicializa as variaveis de sessao.
def imagens(request):
    if not request.session.session_key:
        request.session.save()

    tmp_diretorio = os.path.join(os.path.dirname(__file__), 'static/char_gen/tmp')
    img_tmp_diretorio = os.path.join(tmp_diretorio, request.session.session_key)

    if not os.path.isdir(img_tmp_diretorio):
        os.mkdir(img_tmp_diretorio)
        os.mkdir(img_tmp_diretorio + '/base')
        os.mkdir(img_tmp_diretorio + '/geradas')
    else:
        files = glob.glob(img_tmp_diretorio + '/*.png')

        for f in files:
            os.remove(f)

    request.session['sec-minima'] = request.POST['sec-minima']
    request.session['sec-maxima'] = request.POST['sec-maxima']
    request.session['num-geracoes'] = request.POST['num-geracoes']
    arquivo_imagem = request.FILES['imagem']
    fs = FileSystemStorage()
    filename = fs.save(img_tmp_diretorio + '/base/base.png', arquivo_imagem)
    request.session['tamanho'] = [int(request.POST['largura']), int(request.POST['altura'])]
    request.session['escala-entrada'] = int(request.POST['escala-entrada'])
    request.session['escala-saida'] = int(request.POST['escala-saida'])
    imagens_array = get_imagens_array(img_tmp_diretorio + '/base/base.png', request.session['tamanho'])
    imagens_url = []

    for i in range(0, len(imagens_array)):
        imagem_nome = str(i) + '.png'
        imagem_nova = imagens_array[i].resize([imagens_array[i].size[0] * request.session['escala-entrada'], imagens_array[i].size[1] * request.session['escala-entrada']], Image.NEAREST)
        imagem_nova.save(img_tmp_diretorio + '/' + imagem_nome)
        imagens_url.append('char_gen/tmp/' + request.session.session_key + '/' + imagem_nome)

    return render(request, 'char_gen/imagens.html', {'imagens_url': imagens_url})

#Esta funcao recebe os indices das imagens selecionadas pelo usuario que serao ignoradas pelo
#algoritmo de cruzamento
@ensure_csrf_cookie
def receber_ignoradas(request):
    global thread_ativa
    thread_ativa = False
    request.session['cruzamento_terminado'] = '0'
    request.session['imagens_ignoradas'] = request.POST['imagens_ignoradas'].split(',')
    return HttpResponse('OK')

#Esta funcao cria a thread que ira realizar o cruzamento das imagens
def cruzar(request):
    global thread_ativa

    if not thread_ativa:
        global cruzando
        cruzando = '1'
        t = threading.Thread(target=crossover, args=[request])
        t.start()
    
    return render(request, 'char_gen/cruzar.html')

#Esta funcao retorna o status do servidor com relacao ao cruzamento.
#O sistema requisita atraves de uma requisicao AJAX o status em
#intervalos de tempo predefinidos
def is_cruzando(request):
    global cruzando

    if cruzando == '1':
        request.session['cruzamento_terminado'] = '0'
    elif cruzando == '0':
        request.session['cruzamento_terminado'] = '1'

    return HttpResponse(request.session['cruzamento_terminado'])


#Esta funcao retorna o caminho das imagens geradas para a requisicao AJAX.
#Apos isso, gera uma thread que esperara 5 minutos antes de excluir as imagens geradas
def get_geradas(request):
    dir_raiz = os.path.dirname(__file__)
    tmp_diretorio = os.path.join(dir_raiz, 'static/char_gen/tmp')
    img_tmp_diretorio = os.path.join(tmp_diretorio, request.session.session_key)
    im_geradas_dir = os.path.join(img_tmp_diretorio, 'geradas')
    dir_geradas = []

    for nome in glob.glob(im_geradas_dir + '/*.png'):
        dir_geradas.append('/static/char_gen/tmp/' + request.session.session_key + '/geradas/' + os.path.basename(nome))
    
    resposta_dir_geradas = ', '.join(dir_geradas)
    t = threading.Thread(target=limpa_sessao, args=[request])
    t.start()

    return HttpResponse(resposta_dir_geradas)

def nova_sessao(request):
    dir_raiz = os.path.dirname(__file__)
    tmp_diretorio = os.path.join(dir_raiz, 'static/char_gen/tmp')
    img_tmp_diretorio = os.path.join(tmp_diretorio, request.session.session_key)
    shutil.rmtree(img_tmp_diretorio)

    del request.session['sec-minima']
    del request.session['sec-maxima']
    del request.session['num-geracoes']
    del request.session['tamanho']
    del request.session['escala-entrada']
    del request.session['escala-saida']
    del request.session['cruzamento_terminado']
    del request.session['imagens_ignoradas']

    return render(request, 'char_gen/index.html')

def limpa_sessao(request):
    time.sleep(300)
    dir_raiz = os.path.dirname(__file__)
    tmp_diretorio = os.path.join(dir_raiz, 'static/char_gen/tmp')
    img_tmp_diretorio = os.path.join(tmp_diretorio, request.session.session_key)
    shutil.rmtree(img_tmp_diretorio)

    del request.session['sec-minima']
    del request.session['sec-maxima']
    del request.session['num-geracoes']
    del request.session['tamanho']
    del request.session['escala-entrada']
    del request.session['escala-saida']
    del request.session['cruzamento_terminado']
    del request.session['imagens_ignoradas']

    return HttpResponse('OK')

#Funcao de suporte para a funcao imagens
def get_imagens_array(nome_arquivo, tamanho):
    imagem = Image.open(nome_arquivo).convert('RGB')
    im_rgb_array = np.array(imagem)
    count = 0
    imagens_array = []

    for lin in range(0, int(im_rgb_array.shape[0] / tamanho[1])):
        for col in range(0, int(im_rgb_array.shape[1] / tamanho[0])):
            imagem_matriz = np.zeros((tamanho[1], tamanho[0], 3), dtype=np.uint8)

            for i in range(0, im_rgb_array.shape[2]):
                comeco = [lin * tamanho[1], col * tamanho[0]]
                fim = [comeco[0] + tamanho[1], comeco[1] + tamanho[0]]
                imagem_matriz[:,:,i] = im_rgb_array[comeco[0]:fim[0], comeco[1]:fim[1], i]

            imagens_array.append(Image.fromarray(imagem_matriz, 'RGB'))

            count += 1

    return imagens_array


#Funcao da thread que realiza o cruzamento das imagens.
def crossover(request):
    #print('Iniciando thread')
    
    global thread_ativa
    thread_ativa = True

    tamanho = [request.session['tamanho'][0] * request.session['escala-entrada'], request.session['tamanho'][1] * request.session['escala-entrada']]
    total_pixels = tamanho[0] * tamanho[1]
    TAMANHOS_SECCAO_CROMOSSOMO = []
    NUM_GENERACOES = int(request.session['num-geracoes'])
    SECCAO_MINIMA = float(request.session['sec-minima'])
    SECCAO_MAXIMA = float(request.session['sec-maxima'])
    tipo_cruzamento = TiposCruzamento.TROCA
    filtro = [175, 175, 175]

    for x in range(2, total_pixels):
        if total_pixels % x == 0:
            if x >= total_pixels * SECCAO_MINIMA and x <= total_pixels * SECCAO_MAXIMA:
                TAMANHOS_SECCAO_CROMOSSOMO.append(x)

    #Ler os sprites
    imagens_array =[]
    imagens_ignoradas = []

    for nome in request.session['imagens_ignoradas']:
        imagens_ignoradas.append(nome + '.png')

    dir_raiz = os.path.dirname(__file__)
    tmp_diretorio = os.path.join(dir_raiz, 'static/char_gen/tmp')
    img_tmp_diretorio = os.path.join(tmp_diretorio, request.session.session_key)

    for file in glob.glob(img_tmp_diretorio + '/*.png'):
        if not os.path.basename(file) in imagens_ignoradas:
            imagem = Image.open(file).convert('RGB')
            array_im = np.asarray(imagem).astype(np.uint8)
            imagens_array.append(array_im)
    
    for x in range(0, NUM_GENERACOES):
        index_seccao = randrange(0, len(TAMANHOS_SECCAO_CROMOSSOMO))
        tamanho_seccao = TAMANHOS_SECCAO_CROMOSSOMO[index_seccao]
        #print('Tamanho da secção: ' + str(tamanho_seccao))
        algoritmo = AlgoritmoGenetico(imagens_array, tamanho, tamanho_seccao)
        algoritmo.cruzar(tipo_cruzamento)
        imagens_array = algoritmo.get_imagens_array_gerado(filtro)
    
    for x in range(0, len(imagens_array)):
        imagem = Image.fromarray(imagens_array[x], 'RGB')
        imagem_nova = imagem.resize([imagem.size[0] * request.session['escala-saida'], imagem.size[1] * request.session['escala-saida']], Image.NEAREST)
        imagem_nova.save(img_tmp_diretorio + '/geradas/' + str(x) + '.png')

    global cruzando
    cruzando = '0'
    
    #print('Finalizando thread')
