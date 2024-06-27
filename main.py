from openai import OpenAI
from dotenv import load_dotenv
import os

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

def main():
    load_dotenv()

    caminho_audio = 'podcasts/hipsters_154_testes_short.mp3'
    nome_arquivo = 'hipsters_154_testes_short'
    url_podcast = 'https://rmwd.com.br'

    openai_key = os.getenv('API_OPENAI')
    openai = OpenAI(api_key=openai_key)
    
    
    modelo_whisper = 'whisper-1'
    transcricao_completa = ferramenta_ler_arquivo('texto_completo_hipsters_154_testes_short.txt')
    resumo_instagram = ferramenta_ler_arquivo('resumo_instagram_hipsters_154_testes_short.txt')
    hashtags = ferramenta_ler_arquivo('hastags_hipsters_154_testes_short.txt')

    resumo_imagem_instagram = openai_gpt_gerar_texto_imagem(resumo_instagram, nome_arquivo, openai)

if __name__ == "__main__":
    main()