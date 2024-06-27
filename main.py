from openai import OpenAI
from dotenv import load_dotenv
import os

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

def main():
    load_dotenv()

    caminho_audio = 'podcasts/hipsters_154_testes_short.mp3'
    nome_arquivo = 'hipsters_154_testes_short'
    url_podcast = 'https://rmwd.com.br'

    openai_key = os.getenv('API_OPENAI')
    client = OpenAI(api_key=openai_key)
    
    
    modelo_whisper = 'whisper-1'
    transcricao_completa = openai_whisper_transcrever(caminho_audio, nome_arquivo, modelo_whisper, client)

if __name__ == "__main__":
    main()