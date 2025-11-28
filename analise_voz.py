import speech_recognition as sr
import time
import serial 
from prever_sentimento import prever_sentimento_carregado 


# ===========================
# CONFIGURAÇÕES DO ARDUINO
# ===========================
ARDUINO_PORT = "COM3"       # ajuste para sua porta
BAUD_RATE = 9600
ser = None


# ===========================
# FUNÇÕES DO ARDUINO
# ===========================

def inicializar_conexao_arduino():
    """Tenta abrir a conexão serial com o Arduino."""
    global ser
    try:
        ser = serial.Serial(ARDUINO_PORT, BAUD_RATE, timeout=1)
        time.sleep(2)  # tempo para estabilizar
        print(f"Conexão Serial estabelecida em {ARDUINO_PORT}.")
        return ser
    except serial.SerialException as e:
        print(f"ERRO: Não foi possível conectar ao Arduino em {ARDUINO_PORT}.")
        print(f"Verifique a porta COM. Detalhes: {e}")
        return None


def enviar_para_arduino(sentimento):
    """Envia o código do sentimento pela porta Serial aberta."""
    global ser
    
    if ser is None or not ser.is_open:
        print("Conexão serial não está ativa. Tentando reconectar...")
        inicializar_conexao_arduino()
        if ser is None or not ser.is_open:
            print("Falha ao enviar o comando. Conexão inativa.")
            return

    codigo_sentimento = {
        'Negativo': '0',
        'Neutro': '1',
        'Positivo': '2'
    }

    codigo = codigo_sentimento.get(sentimento, '1')  # padrão = Neutro

    try:
        ser.write(codigo.encode())
        print(f"Enviado para Arduino: Código {codigo} ({sentimento})")
        time.sleep(0.1)
    except serial.SerialTimeoutException:
        print("Erro de timeout ao enviar dados para o Arduino.")
    except Exception as e:
        print(f"Erro inesperado ao enviar dados: {e}")


# ===========================
# TRANSCRIÇÃO + ANÁLISE
# ===========================

def transcrever_e_analisar():
    r = sr.Recognizer()
    
    with sr.Microphone() as source:
        print("\n______________________________________________________________________")
        print("\nBem vindo ao Luz de Humor")
        print("\n______________________________________________________________________")

        print("\nCalibrando ruído ambiente...")
        r.adjust_for_ambient_noise(source, duration=1) 
        print("Pronto! Fale uma frase para análise.")

        while True:
            try:
                print("\nEstamos escutando você...")
                audio = r.listen(source, phrase_time_limit=10)

                textodafala = r.recognize_google(audio, language="pt-BR")
                
                print(f"Você disse: {textodafala}")
                
                sentimento = prever_sentimento_carregado(textodafala)
                print(f"Sentimento Previsto: {sentimento}")

                enviar_para_arduino(sentimento)
                
            except sr.WaitTimeoutError:
                time.sleep(3)
            
            except sr.UnknownValueError:
                print("Não foi possível entender o áudio.")
                
            except sr.RequestError as e:
                print(f"Erro na API do Google Speech: {e}")
                
            except KeyboardInterrupt:
                print("\nAplicação encerrada pelo usuário.")
                break


# ===========================
# INÍCIO DO PROGRAMA
# ===========================
if __name__ == "__main__":
    inicializar_conexao_arduino()
    transcrever_e_analisar()
