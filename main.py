from openai import OpenAI
from dotenv import load_dotenv
import os
import requests
from pydub import AudioSegment

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


def main():
    load_dotenv()

    caminho_audio = 'podcasts/hipsters_154_testes_short.mp3'
    nome_arquivo = 'hipsters_154_testes_short'
    url_podcast = 'https://rmwd.com.br'
    resolucao = '1024x1024'
    qtd_imagens = 4

    openai_key = os.getenv('API_OPENAI')
    openai = OpenAI(api_key=openai_key)
    
    openai.images.generate
    modelo_whisper = 'whisper-1'
    #transcricao_completa = ferramenta_ler_arquivo('texto_completo_hipsters_154_testes_short.txt')
    transcricao_completa = openai_whisper_transcrever_em_partes(caminho_audio, nome_arquivo,modelo_whisper, openai)
    #resumo_instagram = ferramenta_ler_arquivo('resumo_instagram_hipsters_154_testes_short.txt')
    #hashtags = ferramenta_ler_arquivo('hastags_hipsters_154_testes_short.txt')
    #resumo_imagem_instagram = ferramenta_ler_arquivo('resumo_instagram_hipsters_154_testes_short.txt')

    #imagem_gerada = openai_dalle_gerar_imagem(resolucao, resumo_imagem_instagram, nome_arquivo, openai,qtd_imagens)
    #ferramenta_download_imagem(nome_arquivo, imagem_gerada, qtd_imagens)

if __name__ == "__main__":
    main()