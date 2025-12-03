import speech_recognition as sr
import time
import serial 
from prever_sentimento import prever_sentimento_carregado 

# ===========================
# CONFIGURAÇÕES DO ARDUINO
# ===========================
ARDUINO_PORT = "COM3"  # AJUSTE AQUI para sua porta
BAUD_RATE = 9600
ser = None

# ===========================
# FUNÇÕES DO ARDUINO
# ===========================
def inicializar_conexao_arduino():
    """Tenta abrir a conexão serial com o Arduino."""
    global ser
    try:
        if ser is not None and ser.is_open:
            ser.close()
            time.sleep(1)
        
        ser = serial.Serial(ARDUINO_PORT, BAUD_RATE, timeout=1)
        time.sleep(2)  # Tempo para estabilizar a conexão
        
        # Limpa o buffer
        ser.reset_input_buffer()
        ser.reset_output_buffer()
        
        print(f" Conexão Serial estabelecida em {ARDUINO_PORT}.")
        
        # Lê mensagem inicial do Arduino
        time.sleep(0.5)
        if ser.in_waiting > 0:
            msg = ser.readline().decode('utf-8', errors='ignore').strip()
            print(f"Arduino diz: {msg}")
        
        return True
    except serial.SerialException as e:
        print(f" ERRO: Não foi possível conectar ao Arduino em {ARDUINO_PORT}.")
        print(f"  Verifique se a porta está correta e se o Arduino está conectado.")
        print(f"  Detalhes: {e}")
        return False

def enviar_para_arduino(sentimento):
    """Envia o código do sentimento pela porta Serial."""
    global ser
    
    if ser is None or not ser.is_open:
        print(" Conexão serial não está ativa. Tentando reconectar...")
        if not inicializar_conexao_arduino():
            print("Falha ao enviar o comando. Conexão inativa.")
            return False
    
    codigo_sentimento = {
        'Negativo': '4',
        'Neutro': '3',
        'Positivo': '2'
    }
    
    codigo = codigo_sentimento.get(sentimento, '3')  # padrão = Neutro
    
    try:
        # Limpa buffers antes de enviar
        ser.reset_input_buffer()
        ser.reset_output_buffer()
        
        # Envia o código
        ser.write(codigo.encode('utf-8'))
        ser.flush()  # Garante que foi enviado
        
        print(f"→ Enviado para Arduino: Código '{codigo}' ({sentimento})")
        
        # Aguarda resposta do Arduino
        time.sleep(0.2)
        if ser.in_waiting > 0:
            resposta = ser.readline().decode('utf-8', errors='ignore').strip()
            print(f"← Arduino respondeu: {resposta}")
        
        return True
        
    except serial.SerialTimeoutException:
        print(" Erro de timeout ao enviar dados para o Arduino.")
        return False
    except Exception as e:
        print(f" Erro inesperado ao enviar dados: {e}")
        return False

# ===========================
# TRANSCRIÇÃO + ANÁLISE
# ===========================
def transcrever_e_analisar():
    """Captura áudio, transcreve e analisa sentimento."""
    r = sr.Recognizer()
    
    with sr.Microphone() as source:
        print("\n" + "="*50)
        print("          BEM-VINDO AO LUZ DE HUMOR")
        print("="*50)
        print("\n Calibrando ruído ambiente...")
        r.adjust_for_ambient_noise(source, duration=1) 
        print("✓ Pronto! Fale uma frase para análise de sentimento.\n")
        print("(Pressione Ctrl+C para sair)\n")
        
        while True:
            try:
                print("-" * 50)
                print(" Escutando você...")
                
                audio = r.listen(source, phrase_time_limit=10)
                
                print(" Processando áudio...")
                textodafala = r.recognize_google(audio, language="pt-BR")
                
                print(f" Você disse: '{textodafala}'")
                
                sentimento = prever_sentimento_carregado(textodafala)
                print(f" Sentimento Previsto: {sentimento}")
                
                sucesso = enviar_para_arduino(sentimento)
                
                if not sucesso:
                    print(" Falha ao comunicar com Arduino. Tentando novamente...")
                
                print()  # Linha em branco para separação
                
            except sr.WaitTimeoutError:
                print(" Timeout - Nenhum áudio detectado.")
                time.sleep(1)
            
            except sr.UnknownValueError:
                print(" Não foi possível entender o áudio. Tente novamente.")
                
            except sr.RequestError as e:
                print(f" Erro na API do Google Speech: {e}")
                print("   Verifique sua conexão com a internet.")
                
            except KeyboardInterrupt:
                print("\n\n Aplicação encerrada pelo usuário.")
                break
                
            except Exception as e:
                print(f"Erro inesperado: {e}")

# ===========================
# LIMPEZA E ENCERRAMENTO
# ===========================
def fechar_conexao():
    """Fecha a conexão serial com segurança."""
    global ser
    if ser is not None and ser.is_open:
        try:
            ser.close()
            print("Conexão serial fechada.")
        except Exception as e:
            print(f"Erro ao fechar conexão: {e}")

# ===========================
# INÍCIO DO PROGRAMA
# ===========================
if __name__ == "__main__":
    try:
        if inicializar_conexao_arduino():
            transcrever_e_analisar()
        else:
            print("\nNão foi possível iniciar. Verifique a conexão com o Arduino.")
    finally:
        fechar_conexao()
        
        
        
        
        