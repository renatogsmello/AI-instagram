from openai import OpenAI
from dotenv import load_dotenv
import os
import requests
from pydub import AudioSegment
from PIL import Image
from instabot import Bot
import shutil

def openai_gpt_resumir_texto(transcricao_completa, nome_arquivo, openai):
    print('Resumindo com o gpt para um post no instagram...')

    prompt_sistema = """
    Assuma que você é um digital influencer digital e que está construíndo conteúdos das áreas de tecnologia em uma plataforma de áudio (podcast).

    Os textos produzidos devem levar em consideração uma peresona que consumirá os conteúdos gerados. Leve em consideração:

    - Seus seguidores são pessoas super conectadas da área de tecnologia, que amam consumir conteúdos relacionados aos principais temas da área de computação.
    - Você deve utilizar o gênero neutro na construção do seu texto
    - Os textos serão utilizados para convidar pessoas do instagram para consumirem seu conteúdo de áudio
    - O texto deve ser escrito em português do Brasil.

    """
    prompt_usuario = ". \nReescreva a transcrição acima para que possa ser postado como uma legenda do Instagram. Ela deve resumir o texto para chamada na rede social. Inclua hashtags"

    resposta = openai.chat.completions.create(
        model='gpt-3.5-turbo-16k',
        messages=[
            {
                "role": "system",
                "content": prompt_sistema
            },
            {
                "role": "user",
                "content": transcricao_completa + prompt_usuario
            }
        ],
        temperature = 0.6
    )

    resumo_instagram = resposta.choices[0].message.content

    with open(f'resumo_instagram_{nome_arquivo}.txt','w',encoding='utf-8') as arquivo_texto:
        arquivo_texto.write(resumo_instagram)

    return resumo_instagram


def openai_whisper_transcrever(caminho_audio, nome_arquivo,modelo_whisper, client):
    print('Estou transcrevendo com whisper...')

    audio = open(caminho_audio, 'rb')
    resposta = client.audio.transcriptions.create(
        
        model = modelo_whisper,
        file = audio
    )

    transcricao = resposta.text
    with open(f'texto_completo_{nome_arquivo}.txt','w',encoding='utf-8') as arquivo_texto:
        arquivo_texto.write(transcricao)

    return transcricao

def ferramenta_ler_arquivo(nome_arquivo):
    try:
        with open(nome_arquivo, 'r') as arquivo:
            return arquivo.read()
    except IOError as e:
        print(f'Erro no carregamento de arquivo: {e}')    

def openai_gpt_criar_hashtag(resumo_arquivo, nome_arquivo, openai):
    print('Gerando as hashtags...')

    prompt_sistema = """
    Assuma que você é um digital influencer digital e que está construíndo conteúdos das áreas de tecnologia em uma plataforma de áudio (podcast).

    Os textos produzidos devem levar em consideração uma peresona que consumirá os conteúdos gerados. Leve em consideração:

    - Seus seguidores são pessoas super conectadas da área de tecnologia, que amam consumir conteúdos relacionados aos principais temas da área de computação.
    - Você deve utilizar o gênero neutro na construção do seu texto
    - Os textos serão utilizados para convidar pessoas do instagram para consumirem seu conteúdo de áudio
    - O texto deve ser escrito em português do Brasil.
    - A saída deve conter 5 hashtags.

    """

    prompt_usuario =f'Aqui está um resumo de um texto "{resumo_arquivo}". Por favor, gere 5 hashtags que sejam relevantes para este texto e que possam ser publicadas no Instagram.  Por favor, faça isso em português do Brasil '


    resposta = openai.chat.completions.create(
        model='gpt-3.5-turbo',
        messages=[
            {
                "role": "system",
                "content": prompt_sistema
            },
            {
                "role": "user",
                "content": prompt_usuario
            }
        ],
        temperature = 0.6
    )

    hastags = resposta.choices[0].message.content
    with open(f'hastags_{nome_arquivo}.txt','w',encoding='utf-8') as arquivo_texto:
        arquivo_texto.write(hastags)

    return hastags

def openai_gpt_gerar_texto_imagem(resumo_instagram, nome_arquivo, openai):
    print('Gerando saida de texto para criação da imagem...')

    prompt_sistema = """

    - A saída deve ser uma única, do tamanho de um tweet, que seja capaz de descrever o conteúdo do texto para que possa ser transcrito como uma imagem.
    - Não inclua hashtags

    """

    prompt_usuario =  f'Reescreva o texto a seguir, em uma frase, para que descrever o texto abaixo em um tweet: {resumo_instagram}'


    resposta = openai.chat.completions.create(
            model='gpt-3.5-turbo-16k',
            messages=[
                {
                    "role": "system",
                    "content": prompt_sistema
                },
                {
                    "role": "user",
                    "content": prompt_usuario
                }
            ],
            temperature = 0.6
        )

    texto_para_imagem = resposta.choices[0].message.content

    with open(f'texto_para_imagem_{nome_arquivo}.txt','w',encoding='utf-8') as arquivo_texto:
        arquivo_texto.write(texto_para_imagem)

    return texto_para_imagem

def openai_dalle_gerar_imagem(resolucao, resumo_imagem, nome_arquivo, openai, qtd_imagens):
    print('Gerando imagem utilizando Dalle...')

    prompt_user = f'Uma pintura ultra futurista, textless, 3d que retrate: {resumo_imagem}'

    resposta = openai.images.generate(
        prompt= prompt_user,
        n = qtd_imagens,
        size=resolucao
    )

    return resposta.data

def ferramenta_download_imagem(nome_arquivo, imagem_gerada, qtd_imagens = 1):
    lista_nome_imagens = []
    try:
        for contador_imagens in range(0, qtd_imagens):
            caminho = imagem_gerada[contador_imagens].url
            imagem = requests.get(caminho)
            with open(f'{nome_arquivo}_{contador_imagens}.png','wb') as arquivo_imagem:
                arquivo_imagem.write(imagem.content)

            lista_nome_imagens.append(f'{nome_arquivo}_{contador_imagens}.png')
        return lista_nome_imagens
    except:
        print('Ocorreu um erro')
        return None

def ferramenta_transcrever_audio_em_partes(caminho_audio, nome_arquivo):
    print('Iniciando cortes ...')

    audio = AudioSegment.from_mp3(caminho_audio)

    cinco_minutos = 5 * 60 * 1000

    contador_pedaco = 1
    arquivos_exportados = []

    while len(audio) > 0:
        pedaco = audio[:cinco_minutos]
        nome_pedaco_audio = f'{nome_arquivo}_parte_{contador_pedaco}.mp3'
        pedaco.export(nome_pedaco_audio, format='mp3')
        arquivos_exportados.append(nome_pedaco_audio)
        audio = audio[cinco_minutos:]
        contador_pedaco += 1

    return arquivos_exportados

def openai_whisper_transcrever_em_partes(caminho_audio, nome_arquivo,modelo_whisper, client):
    print('Estou transcrevendo com whisper...')

    lista_arquivos_audio = ferramenta_transcrever_audio_em_partes(caminho_audio, nome_arquivo)
    lista_pedacos_audio = []
    for um_pedaco_audio in lista_arquivos_audio:
        audio = open(um_pedaco_audio, 'rb')

        resposta = client.audio.transcriptions.create(
            
            model = modelo_whisper,
            file = audio
        )

        transcricao = resposta.text
        lista_pedacos_audio.append(transcricao)

    transcricao = ''.join(lista_pedacos_audio)


    with open(f'texto_completo_{nome_arquivo}.txt','w',encoding='utf-8') as arquivo_texto:
        arquivo_texto.write(transcricao)

    return transcricao

def selecionar_imagem(lista_nome_imagens):
    return lista_nome_imagens[int(input("Qual imagem você deseja selecionar, informe o número do sufixo da imagem ? "))]

def ferramenta_converter_png_para_jpeg(caminho_imagem_escolhida, nome_arquivo):
    img_png = Image.open(caminho_imagem_escolhida)
    img_png.save(caminho_imagem_escolhida.split('.')[0]+".jpg")

    return caminho_imagem_escolhida.split(".")[0] + ".jpg"

def postar_instagram(caminho_imagem, texto, user, password):
    if os.path.exists('config'):
        shutil.rmtree('config')
    
    bot = Bot()
    bot.login(username=user, password=password)

    resposta = bot.upload_photo(caminho_imagem, caption=texto)

def confirmacao_postagem(caminho_imagem_convertida, legenda_postagem ):
    print(f'\n Caminho Imagem: {caminho_imagem_convertida}')
    print(f'\n Legenda: {legenda_postagem}')
    
    print("\n\nDeseja postar os dados acima no seu instagram? Digite 's' para sim e 'n' para não.")
    return input()

def ferramenta_conversao_binario_string(texto):
    if isinstance(texto, bytes):
       return str(texto.decode())
    return texto


def main():
    load_dotenv()

    caminho_audio = 'podcasts/hipsters_154_testes_short.mp3'
    nome_arquivo = 'hipsters_154_testes_short'
    url_podcast = 'https://rmwd.com.br'
    resolucao = '1024x1024'
    qtd_imagens = 4
    usuario_instagram = os.getenv('USER_INSTAGRAM')
    senha_instagram = os.getenv('PASSWORD_INSTAGRAM')
   
    openai_key = os.getenv('API_OPENAI')
    openai = OpenAI(api_key=openai_key)
    
    openai.images.generate
    modelo_whisper = 'whisper-1'
    transcricao_completa = ferramenta_ler_arquivo('texto_completo_hipsters_154_testes_short.txt')
    #transcricao_completa = openai_whisper_transcrever_em_partes(caminho_audio, nome_arquivo,modelo_whisper, openai)
    resumo_instagram = openai_gpt_resumir_texto(str(transcricao_completa), nome_arquivo, openai)
    hashtags = openai_gpt_criar_hashtag(resumo_instagram, nome_arquivo, openai)
    resumo_imagem_instagram = openai_gpt_gerar_texto_imagem(resumo_instagram, nome_arquivo, openai)

    imagem_gerada = openai_dalle_gerar_imagem(resolucao, resumo_imagem_instagram, nome_arquivo, openai,qtd_imagens)
    lista_imagens_geradas = ferramenta_download_imagem(nome_arquivo, imagem_gerada, qtd_imagens)
    caminho_imagem_escolhida = selecionar_imagem(lista_imagens_geradas)
    caminho_imagem_convertida = ferramenta_converter_png_para_jpeg(caminho_imagem_escolhida, nome_arquivo)

    legenda_imagem = f'O conteúdo da postagem abaixo foi feita com Python e ferramentas da OpenAi \n {ferramenta_conversao_binario_string(resumo_instagram)} \n {ferramenta_conversao_binario_string(hashtags)}'

    if confirmacao_postagem(caminho_imagem_convertida, legenda_imagem).lower()  == 's':
        
        postar_instagram(caminho_imagem_convertida,legenda_imagem, usuario_instagram, senha_instagram)


if __name__ == "__main__":
    main()