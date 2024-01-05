# 150_webscraping
 
## Comandos:

### Cópia do projeto:
git clone https://github.com/eduardosirino/150_webscraping.git

### Instalação de dependências:
sudo apt-get update  
sudo apt-get upgrade  
sudo apt-get install xvfb  
sudo apt-get install chromium-chromedriver
sudo apt install python3-pip    
pip install logging  
pip install importlib  
pip install inspect  
pip install requests  
pip install bs4  
pip install selenium  
pip install pyvirtualdisplay  
pip install mysql  
pip install mysql-connector-python  

### Altera o Horário do servidor:
sudo timedatectl set-ntp true  
sudo timedatectl set-timezone America/Sao_Paulo  
timedatectl status - para ver se alterou corretamente  

### Executar o programa em segundo plano:
nohup python3 main.py &

### Pode ver se está executando com o:
ps aux | grep main.py

## Links para raspar:

### Problemas

#### Não será feito Scraping
1 - https://registradores.onr.org.br/ - não é leiloeiro  
2 - https://www.jusbrasil.com.br/acompanhamentos/processos - não é leiloeiro  
3 - http://www.jorgebrasil.lel.br/ - não é leiloeiro  
24 - https://www.mullerleiloes.com.br/ - mesmo número 4  
57 - https://www.tjsp.jus.br/auxiliaresjustica/auxiliarjustica/consultapublica - não é site de leilão  
128 - https://www.lancese.com.br/ - Mesmo site do 9  
126 - https://www.confiancaleiloes.com.br/ - mesmos resultados do 122  
54 - https://www.d1lance.com.br/ - mesmo do 105  
18 - https://nortonleiloes.com.br/externo/ - redireciona para o 43  
7 - https://www.kleiloes.com.br/ - mesmo do 103  





#### Estão com problemas e vou tentar de outras formas
  
16 - https://www.lessaleiloes.com.br/ - não pronto, deu erro (vou tentar com undetected ou selenium base depois)  
83 - https://www.norteleiloes.com.br/ - 403 com requests e erro com selenium  
71 - https://www.wrleiloes.com.br/ - não tem leilão cadastrado para criar o código  
37 - https://satoleiloes.com.br - problema grande - sem link para acesso a página do leilão  



### Falta
6 - https://www.trt12.jus.br/portal/areas/ascom/extranet/destaques/leiloes.jsp  
19 - https://leje.com.br/  
28 - https://www.centralsuldeleiloes.com.br/  
30 - https://www.freitasleiloeiro.com.br/  
33 - https://www.leilaovip.com.br/  
35 - https://kriegerleiloes.com.br/  
36 - https://seuimovelbb.com.br/  
45 - https://www.caixa.gov.br/voce/habitacao/imoveis-venda/Paginas/default.aspx  
47 - https://www.hastaleiloes.com.br/  
50 - https://www.balbinoleiloes.com.br/externo/  
51 - https://www.kronbergleiloes.com.br/  
52 - https://spencerleiloes.com.br/  
56 - https://www.banrisul.com.br/bob/link/bobw10hn_leiloes_comprar.aspx?secao_id=137  
59 - https://www.santanderimoveis.com.br/  
60 - https://imoveis.bancointer.com.br/  
61 - https://www.deonizialeiloes.com.br/externo/lotes/37947  
62 - https://www3.bcb.gov.br/CALCIDADAO/publico/exibirFormCorrecaoValores.do?method=exibirFormCorrecaoValores  
68 - https://www.gpleiloes.com.br//#/  
72 - https://www.hdleiloes.com.br/externo/  
73 - https://www.casaleiloeira.com.br/  
74 - https://www.leiloescentrooeste.com.br/externo/  
75 - https://www.alvaroleiloes.com.br/externo/  
78 - https://banco.bradesco/html/classic/produtos-servicos/leiloes/index.shtm  
80 - https://www.leilaovip.com.br/home  
81 - https://www.palaciodosleiloes.com.br/  
82 - https://www.leiloesbrasil.com.br/presite  
87 - https://www.vipleiloes.com.br/  
97 - https://www.bspleiloes.com.br/Principal.asp  
102 - https://www.leiloesjudiciaisrs.com.br/externo/  
115 - https://www.leiloesjudiciais.com.br/externo/  




### Prontos
4 - http://www.mullerleiloes.com.br/ - PRONTO  
9 - https://lancese.com.br/ - PRONTO  
11 - https://www.francoleiloes.com.br/ - PRONTO  
14 - https://leilaosantos.com.br/ - PRONTO  
15 - https://leiloeirobonatto.com/ - PRONTO  
20 - https://www.rymerleiloes.com.br/ - PRONTO  
21 - https://www.lancejudicial.com.br/ - PRONTO  
26 - https://www.megaleiloes.com.br/ - PRONTO  
31 - https://www.vivaleiloes.com.br/ - PRONTO  
32 - https://www.biasileiloes.com.br/ - PRONTO  
34 - https://sanchesleiloes.com.br/externo/ - PRONTO  
43 - https://www.grandesleiloes.com.br/ - PRONTO  
48 - https://www.lancecertoleiloes.com.br/ - PRONTO  
55 - https://www.hastapublica.lel.br/leilao/lotes/imoveis - PRONTO  
58 - https://www.123leiloes.com.br/ - PRONTO  
65 - https://www.moraesleiloes.com.br/ - PRONTO  
67 - https://oleiloes.com.br/ - PRONTO  
70 - https://www.stefanellileiloes.com.br/ - PRONTO  
85 - https://www.globoleiloes.com.br/ - PRONTO  
86 - https://www.veronicaleiloes.com.br/ - PRONTO  
90 - https://www.delttaleiloes.com.br/home - PRONTO  
91 - https://www.krobelleiloes.com.br/ - PRONTO  
92 - https://mazzollileiloes.com.br/home - PRONTO  
93 - https://www.oesteleiloes.com.br/home - PRONTO  
104 - https://www.portellaleiloes.com.br/ - PRONTO  
114 - https://rochaleiloes.com.br/ - PRONTO  
116 - https://www.centraljudicial.com.br/ - PRONTO  
119 - https://www.simonleiloes.com.br/ - PRONTO  
121 - https://www.nogarileiloes.com.br/ - PRONTO  
123 - https://www.trileiloes.com.br/ - PRONTO  
130 - https://www.alfaleiloes.com/ - PRONTO  
127 - https://www.wspleiloes.com.br/ - PRONTO  
99 - https://www.nordesteleiloes.com.br/ - PRONTO  
5 - https://www.fidalgoleiloes.com.br/ - PRONTO  
95 - https://www.damianileiloes.com.br/home - PRONTO  
8 - https://joaoemilio.com.br/ - PRONTO  
38 - https://www.cravoleiloes.com.br/ - PRONTO  
94 - https://www.topleiloes.com.br/ - PRONTO  
12 - https://www.valerioiaminleiloes.com.br/ - PRONTO  
39 - https://www.renovarleiloes.com.br/ - PRONTO  
41 - https://www.agenciadeleiloes.com.br/ - PRONTO  
40 - https://www.portalzuk.com.br/ - PRONTO  
42 - https://www.superbid.net/ - PRONTO  
49 - https://www.tonialleiloes.com.br/ - PRONTO  
96 - https://www.pimentelleiloes.com.br/ - PRONTO  
100 - https://www.leilaobrasil.com.br/ - PRONTO  
101 - https://www.saraivaleiloes.com.br/ - PRONTO  
106 - https://www.kcleiloes.com.br/ - PRONTO  
107 - https://www.patiorochaleiloes.com.br/ - PRONTO  
108 - https://ccjleiloes.com.br/ - PRONTO  
124 - https://faleiloes.com.br/ - PRONTO  
120 - https://www.leilaopernambuco.com.br/ - PRONTO  
112 - https://www.nsleiloes.lel.br/ - PRONTO  
110 - https://www.nasarleiloes.com.br/ - PRONTO  
111 - https://www.pecinileiloes.com.br/ - PRONTO  
113 - https://www.montenegroleiloes.com.br/ - PRONTO  
118 - https://www.agostinholeiloes.com.br/ - PRONTO  
 122 - https://www.e-leiloeiro.com.br/ - PRONTO  
 64 - https://www.machadoleiloes.com.br/ - PRONTO  
89 - https://www.maxxleiloes.com.br/ - PRONTO  
129 - https://www.jeleiloes.com.br/ - PRONTO  
125 - https://sfrazao.com.br/index.php - PRONTO  
103 - https://www.kleiloes.com.br/ - PRONTO  
105 - https://www.d1lance.com.br/proximos_leiloes/1/1/ - PRONTO  
88 - https://www.hastavip.com.br/ - PRONTO  
27 - https://www.frazaoleiloes.com.br/ - PRONTO  
13 - https://peterlongoleiloes.com.br/ - PRONTO  
84 - https://www.lbleiloes.com.br/ - PRONTO  
79 - https://www.milanleiloes.com.br/ - PRONTO  
23 - https://www.rauppleiloes.com.br/ - PRONTO  
53 - https://www.clicleiloes.com.br/ - PRONTO  
66 - https://www.patricialeiloeira.com.br/ - PRONTO (pwleiloes)  
77 - https://www.rjleiloes.com.br/ - PRONTO  
76 - https://www.fabiobarbosaleiloes.com.br/externo/ - PRONTO  
44 - https://hammer.lel.br/ - PRONTO  
22 - https://www.mpleilao.com.br/ - PRONTO  
17 - https://www.scholanteleiloes.com.br/ - PRONTO  
46 - https://www.3torresleiloes.com.br/ - PRONTO  
29 - https://www.santamarialeiloes.com.br/ - PRONTO  
69 - https://www.baldisseraleiloeiros.com.br/ - PRONTO  
63 - https://www.nakakogueleiloes.com.br/ - PRONTO  
98 - https://www.psnleiloes.com.br/ - PRONTO  
117 - https://www.maxterleiloes.com.br/home -  PRONTO
109 - https://gestordeleiloes.com.br/home - PRONTO (sem leilão cadastrado agora, porém o site é igual a outros)
25 - https://www.sold.com.br/ - PRONTO  
10 - https://www.leiloes.com.br/ - PRONTO (pestana)  
