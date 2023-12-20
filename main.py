import os
import threading
import time
from datetime import datetime
import subprocess
from scraping import update_db, mullerleiloes, lancese, francoleiloes, leilaosantos, leiloeirobonatto, rymerleiloes, grupolance, megaleiloes, vivaleiloes, biasileiloes, sanchesleiloes, grandesleiloes, lancecertoleiloes, hastapublica, leiloes123, moraesleiloes, oleiloes, stefanellileiloes, globoleiloes, veronicaleiloes, delltaleiloes, krobelleiloes, mazzollileiloes, oesteleiloes, nordesteleiloes, portellaleiloes, rochaleiloes, centraljudicial, simonleiloes, nogarileiloes, trileiloes, alfaleiloes, wspleiloes, fidalgoleiloes, damianileiloes, joaoemilio, cravoleiloes, topleiloes, valerioiaminleiloes, renovarleiloes, agenciadeleiloes, portalzuk, superbid, tonialleiloes, pimentelleiloes, leilaobrasil, saraivaleiloes, kcleiloes, patiorochaleiloes, ccjleiloes, faleiloes, leilaopernambuco, nsleiloes, nasarleiloes, pecinileiloes, montenegroleiloes, agostinholeiloes, eleiloero

# Lista de funções a serem chamadas
funcoes_leilao = [
    mullerleiloes, lancese, francoleiloes, leilaosantos, leiloeirobonatto, rymerleiloes,
    grupolance, megaleiloes, vivaleiloes, biasileiloes, sanchesleiloes, grandesleiloes,
    lancecertoleiloes, hastapublica, leiloes123, moraesleiloes, oleiloes, stefanellileiloes,
    globoleiloes, veronicaleiloes, delltaleiloes, krobelleiloes, mazzollileiloes,
    oesteleiloes, nordesteleiloes, portellaleiloes, rochaleiloes, centraljudicial,
    simonleiloes, nogarileiloes, trileiloes, alfaleiloes, wspleiloes, fidalgoleiloes,
    damianileiloes, joaoemilio, cravoleiloes, topleiloes, valerioiaminleiloes, renovarleiloes,
    agenciadeleiloes, portalzuk, superbid, tonialleiloes, pimentelleiloes, leilaobrasil,
    saraivaleiloes, kcleiloes, patiorochaleiloes, ccjleiloes, faleiloes, leilaopernambuco,
    nsleiloes, nasarleiloes, pecinileiloes, montenegroleiloes, agostinholeiloes, eleiloero
]

def chamar_funcao_com_delay(funcao, delay):
    time.sleep(delay)
    for tentativa in range(10):
        try:
            data = funcao()
            if len(data) > 0:
                update_db(data, funcao.__name__)
                break
        except Exception as e:
            print(f"Erro ao executar {funcao.__name__}: {e}")
            time.sleep(5)

def executar_leiloes():
    delay = 0
    delay_incremento = 10  # 10 segundos de atraso entre cada chamada de função
    for funcao in funcoes_leilao:
        threading.Thread(target=chamar_funcao_com_delay, args=(funcao, delay)).start()
        delay += delay_incremento

def fazer_git_pull():
    subprocess.run(["git", "-C", "/150_webscraping/", "pull"])

def main():
    while True:
        agora = datetime.now()
        if agora.hour == 1 and agora.minute == 0 and agora.weekday() in [0, 2, 4]:  # Segunda, Quarta, Sexta
            fazer_git_pull()
        if agora.hour == 9 and agora.minute == 30 and agora.weekday() in [0, 2, 4]:
            os.system("clear")
            executar_leiloes()
        time.sleep(60)  # Espera 1 minuto antes de verificar novamente

if __name__ == "__main__":
    main()