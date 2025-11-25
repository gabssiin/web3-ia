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


def inicializar_conexao_arduino():
    """Tenta abrir a conexão serial com o Arduino."""
    global ser
    try:
        # Tenta conectar
        ser = serial.Serial(ARDUINO_PORT, BAUD_RATE, timeout=1)
        # Necessário esperar um pouco para o Arduino resetar e a comunicação estabilizar
        time.sleep(2)
        print(f"Conexão Serial estabelecida em {ARDUINO_PORT}.")
        return ser
    except serial.SerialException as e:
        print(f"ERRO: Nao foi possivel conectar ao Arduino em {ARDUINO_PORT}.")
        print(f"Verifique se o Arduino esta conectado e a porta COM esta correta. Detalhes: {e}")
        return None

def enviar_para_arduino(sentimento):
    """Envia o código do sentimento pela porta Serial aberta."""
    global ser
    
    if ser is None or not ser.is_open:
        print("Aviso: Conexao serial nao esta ativa. Tentando re-conectar...")
        inicializar_conexao_arduino()
        if ser is None or not ser.is_open:
             print("Falha ao enviar o comando. Conexao serial inativa.")
             return

    codigo_sentimento = {'Negativo': '0', 'Neutro': '1', 'Positivo': '2'}
    # Se o sentimento não for reconhecido, assume '1' (Neutro)
    codigo = codigo_sentimento.get(sentimento, '1') 
    
    try:
        ser.write(codigo.encode())
        print(f"Enviado para Arduino: Codigo {codigo} ({sentimento})")
        # Pequena pausa para garantir que o Arduino leu o dado
        time.sleep(0.1) 
    except serial.SerialTimeoutException:
        print("Erro de timeout ao enviar dados para o Arduino.")
    except Exception as e:
        print(f"Erro inesperado ao enviar dados: {e}")