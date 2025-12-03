import speech_recognition as sr
import time
try:
    import serial
    SERIAL_DISPONIVEL = True
except ImportError:
    SERIAL_DISPONIVEL = False
    print("Biblioteca 'serial' não encontrada. Rodando em MODO DE TESTE.")

# ===========================
# CONFIGURAÇÕES
# ===========================
ARDUINO_PORT = "COM3"
BAUD_RATE = 9600
MODO_TESTE = True  # MUDE PARA False QUANDO FOR USAR COM ARDUINO REAL

ser = None

# ===========================
# FUNÇÕES DO ARDUINO
# ===========================
def inicializar_conexao_arduino():
    """Tenta abrir a conexão serial com o Arduino."""
    global ser
    
    if MODO_TESTE:
        print("MODO DE TESTE ATIVADO - Simulando Arduino")
        print(f"Conexão Serial simulada em {ARDUINO_PORT}.")
        ser = "MODO_TESTE"
        return True
    
    if not SERIAL_DISPONIVEL:
        print("Biblioteca 'serial' não está instalada.")
        print("Execute: pip install pyserial")
        return False
    
    try:
        if ser is not None and hasattr(ser, 'is_open') and ser.is_open:
            ser.close()
            time.sleep(1)
        
        ser = serial.Serial(ARDUINO_PORT, BAUD_RATE, timeout=1)
        time.sleep(2)

        ser.reset_input_buffer()
        ser.reset_output_buffer()
        
        print(f"Conexão Serial estabelecida em {ARDUINO_PORT}.")
        return True

    except Exception as e:
        print(f"ERRO: Não foi possível conectar ao Arduino em {ARDUINO_PORT}.")
        print(f"Detalhes: {e}")
        return False


def enviar_para_arduino(sentimento):
    """Envia o código do sentimento pela porta Serial."""
    global ser

    # MAPEAMENTO CORRIGIDO
    codigo_sentimento = {
        'Positiva': '2',
        'Neutra': '3',
        'Negativa': '4'
    }

    codigo = codigo_sentimento.get(sentimento, '3')

    # MODO TESTE
    if MODO_TESTE or ser == "MODO_TESTE":
        print(f"[SIMULADO] Enviado para Arduino: Código '{codigo}' ({sentimento})")

        respostas = {
            '2': 'LED VERDE - Emoção POSITIVA',
            '3': 'LED BRANCO - Emoção NEUTRA',
            '4': 'LED VERMELHO - Emoção NEGATIVA'
        }

        time.sleep(0.2)
        print(f"[SIMULADO] Arduino respondeu: {respostas[codigo]}")
        return True

    # MODO REAL
    try:
        if not hasattr(ser, 'is_open') or not ser.is_open:
            print("Conexão fechada. Reconectando...")
            if not inicializar_conexao_arduino():
                return False
        
        ser.reset_input_buffer()
        ser.reset_output_buffer()

        ser.write(codigo.encode('utf-8'))
        ser.flush()

        print(f"Enviado para Arduino: Código '{codigo}' ({sentimento})")

        time.sleep(0.2)
        if ser.in_waiting > 0:
            resposta = ser.readline().decode('utf-8', errors='ignore').strip()
            print(f"Arduino respondeu: {resposta}")

        return True

    except Exception as e:
        print(f"Erro ao enviar dados: {e}")
        return False


# ===========================
# TRANSCRIÇÃO + ANÁLISE
# ===========================
def transcrever_e_analisar():
    """Captura áudio, transcreve e analisa sentimento."""
    r = sr.Recognizer()

    # Carrega modelo
    try:
        from prever_sentimento import prever_sentimento_carregado
    except ImportError:
        print("ERRO: Arquivo 'prever_sentimento.py' não encontrado!")
        print("Criando função de teste...")

        def prever_sentimento_carregado(texto):
            texto = texto.lower()
            if any(x in texto for x in ['bom', 'feliz', 'ótimo', 'excelente', 'alegre']):
                return 'Positiva'
            elif any(x in texto for x in ['ruim', 'triste', 'mal', 'péssimo', 'dor']):
                return 'Negativa'
            else:
                return 'Neutra'

    with sr.Microphone() as source:
        print("\n" + "="*50)
        print("MODO TESTE - LUZ DE HUMOR" if MODO_TESTE else "LUZ DE HUMOR")
        print("="*50)

        print("\nCalibrando ruído ambiente...")
        r.adjust_for_ambient_noise(source, duration=1)
        print("Pronto! Fale uma frase.\n")

        while True:
            try:
                print("-" * 50)
                print("Escutando você...")

                audio = r.listen(source, phrase_time_limit=10)

                print("Processando áudio...")
                frase = r.recognize_google(audio, language="pt-BR")

                print(f"Você disse: '{frase}'")

                sentimento = prever_sentimento_carregado(frase)
                print(f"Sentimento Previsto: {sentimento}")

                enviar_para_arduino(sentimento)
                print()

            except KeyboardInterrupt:
                print("\nEncerrado pelo usuário.")
                break

            except sr.UnknownValueError:
                print("Não entendi o áudio. Tente novamente.\n")

            except Exception as e:
                print(f"Erro inesperado: {e}\n")


# ===========================
# FECHAR CONEXÃO
# ===========================
def fechar_conexao():
    global ser

    if MODO_TESTE or ser == "MODO_TESTE":
        print("Modo de teste encerrado.")
        return

    if ser is not None and hasattr(ser, 'is_open') and ser.is_open:
        ser.close()
        print("Conexão serial fechada.")


# ===========================
# MAIN
# ===========================
if __name__ == "__main__":
    print("\n" + "="*50)
    print("RODANDO EM MODO DE TESTE" if MODO_TESTE else "MODO REAL")
    print("="*50 + "\n")

    try:
        if inicializar_conexao_arduino():
            transcrever_e_analisar()
    finally:
        fechar_conexao()