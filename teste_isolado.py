"""
SIMULADOR DE ARDUINO - Porta Serial Virtual
Execute este script ANTES de executar seu código principal.
Ele simulará as respostas do Arduino.
"""

import socket
import threading
import time

HOST = 'localhost'
PORT = 5000

def simular_arduino(conn, addr):
    """Simula o comportamento do Arduino."""
    print(f"✓ Arduino Virtual conectado de {addr}")
    
    # Envia mensagem inicial (como o Arduino faz)
    mensagem_inicial = "Arduino pronto! Aguardando comandos...\n"
    conn.send(mensagem_inicial.encode('utf-8'))
    
    led_status = {
        'verde': False,
        'vermelho': False,
        'branco': False
    }
    
    while True:
        try:
            # Recebe dados
            data = conn.recv(1024)
            if not data:
                break
            
            codigo = data.decode('utf-8').strip()
            
            if codigo == '2':  # Positivo
                led_status = {'verde': True, 'vermelho': False, 'branco': False}
                resposta = "LED VERDE - Emocao POSITIVA\n"
                print(f"🟢 LED VERDE ACESO - Código recebido: '{codigo}'")
                
            elif codigo == '4':  # Negativo (seu código usa '4')
                led_status = {'verde': False, 'vermelho': True, 'branco': False}
                resposta = "LED VERMELHO - Emocao NEGATIVA\n"
                print(f"🔴 LED VERMELHO ACESO - Código recebido: '{codigo}'")
                
            elif codigo == '3':  # Neutro (seu código usa '3')
                led_status = {'verde': False, 'vermelho': False, 'branco': True}
                resposta = "LED BRANCO - Emocao NEUTRA\n"
                print(f"⚪ LED BRANCO ACESO - Código recebido: '{codigo}'")
                
            else:
                resposta = f"Codigo invalido recebido: {codigo}\n"
                print(f"❌ Código inválido: '{codigo}'")
            
            # Envia resposta
            conn.send(resposta.encode('utf-8'))
            time.sleep(0.1)
            
        except Exception as e:
            print(f"Erro: {e}")
            break
    
    print("✗ Conexão fechada")
    conn.close()

def iniciar_servidor():
    """Inicia o servidor que simula o Arduino."""
    print("="*60)
    print("       SIMULADOR DE ARDUINO - PORTA SERIAL VIRTUAL")
    print("="*60)
    print(f"Servidor rodando em {HOST}:{PORT}")
    print("Aguardando conexão do seu código Python...")
    print("="*60)
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen()
        
        while True:
            conn, addr = s.accept()
            thread = threading.Thread(target=simular_arduino, args=(conn, addr))
            thread.daemon = True
            thread.start()

if __name__ == "__main__":
    try:
        iniciar_servidor()
    except KeyboardInterrupt:
        print("\n\n👋 Simulador encerrado pelo usuário")
    except Exception as e:
        print(f"Erro ao iniciar servidor: {e}")