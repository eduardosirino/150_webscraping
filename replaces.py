# Abrir o arquivo de entrada e ler seu conteúdo
with open("text2.txt", 'r', encoding = 'utf-8') as arquivo_entrada:
    conteudo = arquivo_entrada.read()

# Substituir todos os "\n" por " "
conteudo_modificado = conteudo.replace("'', \n", "")
conteudo_modificado = conteudo_modificado.replace("'Comissão: 5%', \n", "")


# Escrever o conteúdo modificado no arquivo de saída
with open("text2.txt", 'w', encoding = 'utf-8') as arquivo_saida:
    arquivo_saida.write(conteudo_modificado)