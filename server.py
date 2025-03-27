import socket 
import time
import logging
import ntplib
from threading import Thread, Lock
from datetime import datetime

# Configuração logging 
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

class NTPServer: 
    def __init__(self, host='0.0.0.0', porta=8000):
        # Inicializa o servidor com o host e porta especificados
        self.host = host
        self.porta = porta
        # Cria um cliente NTP para obter o tempo
        self.cliente_ntp = ntplib.NTPClient()
        # Cria um lock para sincronizar o acesso ao tempo
        self.lock = Lock()
        # Obtém o tempo inicial do servidor NTP
        self.tempo_atual = self.obter_tempo_ntp()

    def obter_tempo_ntp(self):
        # Obtém o tempo atual de um servidor NTP
        try:
            resposta = self.cliente_ntp.request('pool.ntp.org')
            return resposta.tx_time  # Retorna o timestamp do tempo NTP
        except Exception as e:
            # Loga um erro caso não consiga obter o tempo NTP
            logger.error(f"Erro ao obter tempo NTP: {e}")
            return time.time()  # Retorna o tempo local em caso de erro

    def atualizar_tempo_periodicamente(self):
        # Atualiza o tempo do servidor periodicamente
        while True:
            with self.lock:  # Garante que apenas uma thread pode acessar o recurso por vez
                self.tempo_atual = self.obter_tempo_ntp()
                # Converte o timestamp para datetime e formata com milissegundos
                dt = datetime.fromtimestamp(self.tempo_atual)
                logger.info(f"->Servidor NTP atualizado: {dt.strftime('%H:%M:%S.%f')[:-3]}\n")
            time.sleep(30)  # Aguarda 30 segundos antes de atualizar novamente

    def start(self):  # Inicia o servidor
        # Cria um socket para comunicação
        socket_servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Associa o socket ao host e porta
        socket_servidor.bind((self.host, self.porta))
        # Configura o socket para aceitar até 5 conexões simultâneas
        socket_servidor.listen(5)
        logger.info(f"Servidor NTP rodando em {self.host}:{self.porta}\n")

        # Inicia uma thread para atualizar o tempo periodicamente
        Thread(target=self.atualizar_tempo_periodicamente, daemon=True).start()

        while True:
            # Aguarda conexões dos clientes
            socket_cliente, endereco = socket_servidor.accept()
            # Inicia uma thread para tratar a conexão com o cliente
            Thread(target=self.tratar_cliente, args=(socket_cliente, endereco)).start()

    def tratar_cliente(self, socket_cliente, endereco):
        # Trata a comunicação com um cliente
        try:
            # Envia uma mensagem inicial para o cliente
            socket_cliente.send("REQUEST_TIME".encode())
            # Recebe a solicitação do cliente
            dados = socket_cliente.recv(1024).decode()
            if dados == "GET_TIME":  # Verifica se o cliente pediu o tempo
                with self.lock:  # Garante acesso thread-safe ao tempo
                    tempo_servidor = self.tempo_atual
                # Envia o tempo atual para o cliente
                socket_cliente.send(str(tempo_servidor).encode())
                # Loga o tempo enviado para o cliente
                dt = datetime.fromtimestamp(tempo_servidor)
                logger.info(f"Tempo enviado para {endereco}: {dt.strftime('%H:%M:%S.%f')[:-3]}\n") 
        except Exception as e:
            # Loga erros ocorridos durante a comunicação com o cliente
            logger.error(f"Erro com o cliente {endereco}: {e}")
        finally:
            # Fecha a conexão com o cliente
            socket_cliente.close()

if __name__ == "__main__":
    # Cria uma instância do servidor e inicia
    server = NTPServer()
    server.start()
