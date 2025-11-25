import speech_recognition as sr
import time
import serial 
from prever_sentimento import prever_sentimento_carregado 


# ---  TRANSCRIÇÃO E PREVISÃO EM TEMPO REAL ---

def transcrever_e_analisar():
    r = sr.Recognizer()
    
    with sr.Microphone() as source:
        print("\n______________________________________________________________________")
        print("\nBem vindo ao Luz de Humor")
        print("\n______________________________________________________________________")

        print("\nCalibrando ruido ambiente...")
        r.adjust_for_ambient_noise(source, duration=1) 
        print("Pronto! Fale uma frase para analise.")

        while True:
            try:
                print("\nEstamos escutando você...")
                audio = r.listen(source, phrase_time_limit=10)

                textodafala = r.recognize_google(audio, language="pt-BR")
                
                print(f"Voce disse: {textodafala}")
                
                # Analise de Sentimento usando a funcao importada
                sentimento = prever_sentimento_carregado(textodafala)
                
                print(f"Sentimento Previsto: {sentimento}")
                
                # Envio para o Arduino
                enviar_para_arduino(sentimento)
                
            except sr.WaitTimeoutError:
                time.sleep(3) 
            
            except sr.UnknownValueError:
                print("Nao foi possivel entender o audio.")
                
            except sr.RequestError as e:
                print(f"Erro na requisicao da API do Google Speech: {e}")
                
            except KeyboardInterrupt:            
                print("\n Aplicacao encerrada pelo usuario.")
                break

if __name__ == "__main__":
    transcrever_e_analisar()