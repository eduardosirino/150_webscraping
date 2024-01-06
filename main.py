import os
import time
import logging
import platform
import threading
import subprocess
from datetime import datetime
from auxiliar import update_db
from scraping import *  # noqa: F403


funcoes_leilao = [
    francoleiloes, mullerleiloes, lancese, leilaosantos, leiloeirobonatto, rymerleiloes, grupolance, megaleiloes, vivaleiloes, biasileiloes, sanchesleiloes, grandesleiloes, lancecertoleiloes,   # noqa: F405
    hastapublica, leiloes123, moraesleiloes, oleiloes, stefanellileiloes, globoleiloes, veronicaleiloes, delltaleiloes, krobelleiloes, mazzollileiloes, oesteleiloes, nordesteleiloes,   # noqa: F405
    portellaleiloes, rochaleiloes, centraljudicial, simonleiloes, nogarileiloes, trileiloes, alfaleiloes, wspleiloes,fidalgoleiloes, damianileiloes, joaoemilio, cravoleiloes, topleiloes,   # noqa: F405
    valerioiaminleiloes, renovarleiloes, agenciadeleiloes, portalzuk, superbid, tonialleiloes, pimentelleiloes, leilaobrasil, saraivaleiloes, kleiloes, kcleiloes, patiorochaleiloes, ccjleiloes,   # noqa: F405
    faleiloes, leilaopernambuco, nsleiloes, nasarleiloes, pecinileiloes, montenegroleiloes, agostinholeiloes, eleiloero, machadoleiloes, maxxleiloes, sfrazao, jeleiloes, d1lance, hastavip,   # noqa: F405
    frazaoleiloes, peterlongoleiloes, lbleiloes, milanleiloes, rauppleiloes, pwleiloes, clicleiloes, rjleiloes,fabiobarbosaleiloes, hammer, mpleilao, scholanteleiloes, trestorresleiloes,  # noqa: F405
    santamarialeiloes, baldisseraleiloeiros, nakakogueleiloes, psnleiloes, maxterleiloes, gestordeleiloes, sold, pestanaleiloes, hdleiloes  # noqa: F405
]

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
    delay_incremento = 120  # 60 segundos de atraso entre cada chamada de função
    for funcao in funcoes_leilao:
        threading.Thread(target=chamar_funcao_com_delay, args=(funcao, delay)).start()
        delay += delay_incremento

def fazer_git_pull():
    subprocess.run(["git", "-C", "/home/ubuntu/150_webscraping/", "pull"])

def excluir_arquivo_log(nome_arquivo):
    try:
        if os.path.exists(nome_arquivo):
            os.remove(nome_arquivo)
            print(f"Arquivo de log {nome_arquivo} excluído com sucesso.")
        else:
            print(f"Arquivo de log {nome_arquivo} não encontrado.")
    except Exception as e:
        print(f"Erro ao excluir o arquivo de log: {e}")

def main():
    while True:
        agora = datetime.now()
        if agora.hour == 1 and agora.minute == 0 and 0 <= agora.second <= 59 and agora.weekday() in [0, 2, 4]:  # Segunda, Quarta, Sexta
            logging.info(f"Pull concluído em {agora.day}/{agora.month}/{agora.year} - {agora.hour}:{agora.minute}:{agora.second}")
            fazer_git_pull()
            excluir_arquivo_log("meu_log.log")
        if agora.hour == 3 and agora.minute == 0 and 0 <= agora.second <= 59 and agora.weekday() in [0, 2, 4]:
            if platform.system() == "Windows":
                os.system('cls')
            else:
                os.system('clear')
            logging.info(f"Coletando dados em {agora.day}/{agora.month}/{agora.year} - {agora.hour}:{agora.minute}:{agora.second}")
            executar_leiloes()
        time.sleep(60)  # Espera 1 minuto antes de verificar novamente

if __name__ == "__main__":
    main()
