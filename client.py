import socket
import time
import logging
import random
from threading import Thread, Lock
import os
from datetime import datetime

# Configuração do logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

class Client:
    def __init__(self, client_id, host_servidor='ntp-server', porta=8000):
        # Inicializa o cliente com ID, host do servidor, porta e configurações iniciais
        self.client_id = client_id
        self.host_servidor = host_servidor
        self.porta = porta
        self.tempo_local = time.time() + random.uniform(-10, 10)  # Tempo local com desvio aleatório
        self.lock = Lock()  # Lock para sincronização de threads
        self.executando = True  # Flag para controle da execução do cliente

    def sincronizar_com_servidor(self):
        # Método para sincronizar o tempo local com o servidor
        while self.executando:
            try:
                # Cria um socket para comunicação com o servidor
                socket_cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                socket_cliente.connect((self.host_servidor, self.porta))
                
                # Recebe mensagem inicial do servidor (descarta)
                socket_cliente.recv(1024).decode()
                tempo_inicial = time.time()  # Tempo de envio da requisição
                #socket_cliente.send(f"GET_TIME,{self.client_id}".encode())
                socket_cliente.send("GET_TIME".encode())  # Solicita o tempo ao servidor
                
                # Recebe o tempo do servidor
                tempo_servidor = float(socket_cliente.recv(1024).decode())
                tempo_final = time.time()  # Tempo de recebimento da resposta
                
                # Calcula o RTT (tempo de ida e volta) e o atraso estimado
                rtt = tempo_final - tempo_inicial
                atraso = rtt / 2
                tempo_estimado_servidor = tempo_servidor + atraso  # Tempo estimado do servidor

                with self.lock:  # Bloqueia a thread para ajustar o tempo local
                    diferenca_tempo = tempo_estimado_servidor - self.tempo_local  # Diferença entre relógios
                    if abs(diferenca_tempo) > 0.1:  # Ajusta apenas se a diferença for significativa
                        ajuste = diferenca_tempo / 10  # Ajuste gradual de 10% da diferença
                        self.tempo_local += ajuste
                        # Converte o timestamp para datetime e formata com milissegundos
                        dt = datetime.fromtimestamp(self.tempo_local)
                        logger.info(f"Cliente {self.client_id} ajustado: {dt.strftime('%H:%M:%S.%f')[:-3]} (dif_t: {diferenca_tempo:.3f}s, RTT: {rtt:.3f}s)")
                
                socket_cliente.close()  # Fecha o socket após a comunicação
            except Exception as e:
                # Loga erros que possam ocorrer durante a sincronização
                logger.error(f"Cliente {self.client_id} erro: {e}")
            time.sleep(10)  # Aguarda 10 segundos antes de enviar a próxima requisição

    def start(self):
        # Método para iniciar o cliente e exibir o tempo inicial
        dt = datetime.fromtimestamp(self.tempo_local)
        logger.info(f"Cliente {self.client_id} iniciado com tempo: {dt.strftime('%H:%M:%S.%f')[:-3]}")
        # Inicia a thread para sincronização com o servidor
        Thread(target=self.sincronizar_com_servidor, daemon=True).start()

if __name__ == "__main__":
    # Obtém o ID do cliente a partir de uma variável de ambiente ou usa um padrão
    client_id = os.getenv("CLIENT_ID", "Client-0")
    client = Client(client_id)  # Cria uma instância do cliente
    client.start()  # Inicia o cliente
    try:
        while True:
            time.sleep(1)  # Mantém o programa rodando
    except KeyboardInterrupt:
        # Finaliza o cliente ao receber uma interrupção do teclado
        client.executando = False
        logger.info(f"Cliente {client_id} encerrado.")
