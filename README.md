#  Sincronização de Relógios com o Algoritmo de Cristian

Este projeto implementa um sistema distribuído de sincronização de relógios físicos utilizando o **algoritmo de Cristian**, com comunicação entre um servidor e múltiplos clientes simulada via containers Docker.

##  Descrição do Problema

A sincronização precisa de relógios em sistemas distribuídos é um desafio clássico da Computação. O algoritmo de Cristian permite alinhar os tempos dos clientes com um servidor de referência, considerando atrasos de rede.

### Objetivos

- Sincronizar os relógios de pelo menos 3 clientes com um servidor que obtém o tempo real via NTP.
- Calcular o tempo de ida e volta (RTT) para ajustar o tempo local.
- Realizar a sincronização de forma **gradual**, suavizando os ajustes.

##  Tecnologias Utilizadas

- Python
- Docker
- ntplib (consulta ao NTP)
- Threads e Sockets para comunicação

##  Arquitetura do Sistema

###  Servidor (NTPServer)

- Consulta o tempo real de `pool.ntp.org` a cada 30s.
- Responde às solicitações dos clientes com o timestamp atual.
- Utiliza um `threading.Lock` para garantir acesso seguro ao tempo.

###  Cliente (Client)

- Inicia com um desvio aleatório de tempo local.
- A cada 10s, solicita o tempo ao servidor.
- Calcula o RTT e aplica correções suaves ao seu relógio local.

##  Formato de Log

### Servidor

```log
-> Servidor NTP atualizado: 14:32:10.123
Tempo enviado para ('172.18.0.3', 37214): 14:32:12.456
