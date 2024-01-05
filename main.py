import os
import time
import logging
import platform
import threading
import subprocess
from datetime import datetime
from auxiliar import update_db
import importlib
import inspect

modulo = importlib.import_module("scraping")
funcoes_leilao = {nome: getattr(modulo, nome) for nome in dir(modulo) if inspect.isfunction(getattr(modulo, nome))}

# Configura o logging
logging.basicConfig(filename='meu_log.log', level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(threadName)s : %(message)s')


def chamar_funcao_com_delay(funcao, delay):
    time.sleep(delay)
    for tentativa in range(10):
        try:
            data = funcao()
            if len(data) > 0:
                update_db(data)
                break
        except Exception as e:
            logging.error(f"Erro ao executar {funcao.__name__}: {e}")
            time.sleep(5)

def executar_leiloes():
    delay = 0
    delay_incremento = 60  # 60 segundos de atraso entre cada chamada de função
    for nome_funcao, funcao in funcoes_leilao.items():
        threading.Thread(target=chamar_funcao_com_delay, args=(funcao, delay)).start()
        delay += delay_incremento

def fazer_git_pull():
    subprocess.run(["git", "-C", "/home/ubuntu/150_webscraping/", "pull"])

def main():
    while True:
        agora = datetime.now()
        if agora.hour == 1 and agora.minute == 0 and 0 <= agora.second <= 59 and agora.weekday() in [0, 2, 4]:  # Segunda, Quarta, Sexta
            logging.info(f"Pull concluído em {agora.day}/{agora.month}/{agora.year} - {agora.hour}:{agora.minute}:{agora.second}")
            fazer_git_pull()
        if agora.hour == 14 and agora.minute == 10 and 0 <= agora.second <= 59 and agora.weekday() in [0, 2, 4]:
            if platform.system() == "Windows":
                os.system('cls')
            else:
                os.system('clear')
            logging.info(f"Coletando dados em {agora.day}/{agora.month}/{agora.year} - {agora.hour}:{agora.minute}:{agora.second}")
            executar_leiloes()
        time.sleep(60)  # Espera 1 minuto antes de verificar novamente

if __name__ == "__main__":
    main()
