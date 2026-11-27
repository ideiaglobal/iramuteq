# IRaMuTeQ — versão com linha de comandos e lematização contextual

Esta é uma versão modificada do [IRaMuTeQ](http://www.iramuteq.org) (*Interface de R pour les Analyses Multidimensionnelles de Textes et de Questionnaires*), de Pierre Ratinaud. Parte do ramo `3.0` do [repositório original](https://gitlab.huma-num.fr/pratinaud/iramuteq) (versão 0.8 alpha 7) e acrescenta:

- **Linha de comandos** (`iracli.py`): constrói o corpus e corre as análises de texto sem abrir a interface.
- **Lematização contextual** com três analisadores: [udpipe](https://cran.r-project.org/package=udpipe), [FreeLing](https://github.com/TALP-UPC/FreeLing) e [Stanza](https://stanfordnlp.github.io/stanza/). Cada ocorrência recebe o lema e a categoria do seu contexto, em vez de um lema fixo por forma.
- **Seletor de língua alargado**: além das línguas com dicionário do IRaMuTeQ, mostra as línguas que os analisadores tratam (66 com o udpipe, até 104 no total).

O ramo principal é `cli-minimo`. O ramo `3.0` é o original, sem alterações, para comparação.

Este repositório não é o oficial. As mudanças não foram propostas ao autor.

## O que muda

### Linha de comandos

```bash
python3 iracli.py corpus.txt --lang galician -a stat,chd,spec --spec-var tema
python3 iracli.py corpus.txt --lang ca --parser udpipe -a chd,simi,nuvem
python3 iracli.py --help
```

Análises disponíveis: estatísticas (`stat`), classificação hierárquica descendente de Reinert (`chd`), especificidades e AFC (`spec`), análise de similitudes (`simi`) e nuvem de palavras (`nuvem`). Não precisa de wxPython. A documentação completa está em [README_CLI.md](README_CLI.md).

### Lematização contextual

Na interface, o diálogo de configuração do corpus tem uma opção **Contextual** no campo *Dicionário*, com a escolha do analisador e, quando há mais de um, do modelo. Na linha de comandos, usa-se `--parser udpipe`, `--parser freeling` ou `--parser stanza`.

| Analisador | Línguas | Instalação |
|---|---|---|
| udpipe | 66 (modelos UD 2.5) | pacote R `udpipe`; o modelo da língua descarrega-se sozinho na primeira utilização, para `~/.iramuteq-udpipe` |
| FreeLing 4.2.1 | 13 | à parte, compilado, em `~/.iramuteq-tools/freeling-4.2.1` |
| Stanza | 100 | à parte, num ambiente Python próprio (`~/.iramuteq-tools/stanza-venv`) |

A lematização contextual distingue, por exemplo, o espanhol *vino* nome (`vino`) de *vino* verbo (`venir`), ou o catalão *pot* nome (`pot`) de *pot* verbo (`poder`). A qualidade depende do modelo e do tipo de texto: os modelos treinados com imprensa falham mais em textos coloquiais.

Os modelos UD 2.5 do udpipe têm licença **CC BY-NC-SA 4.0** (uso não comercial).

### Seletor de língua

- Primeiro aparecem as línguas com dicionário do IRaMuTeQ (as 11 originais, mais o latim e o romeno, cujos dicionários já existiam). Depois aparecem as línguas que algum analisador trata nesta máquina e, no fim, "Outra língua".
- Cada língua aparece pelo seu nome na própria língua e pelo código ISO: *Galego (gl)*, *Català (ca)*, *Ελληνικά (el)*.
- Uma linha de estado indica o que existe para a língua (`dicionário · udpipe · FreeLing (língua não instalada) · Stanza`).
- Os corpus e preferências antigos continuam a funcionar: as 11 línguas originais mantêm a chave interna (`french`, `galician`…).

### Outras mudanças

- A verificação dos pacotes R no arranque inclui o `udpipe`.
- Durante o descarregamento de um modelo udpipe, a janela de progresso avisa o utilizador. Já não fica congelada enquanto o analisador trabalha.
- Correção da exportação GEXF (`Rscripts/Rgraph.R`): as versões recentes do pacote R `rgexf` exigem a transparência das cores entre 0 e 1.
- Os textos novos estão traduzidos para francês, português, espanhol e italiano. Acrescenta-se o ficheiro `.po` italiano.

## Instalação

Requisitos, como no IRaMuTeQ original: Python 3 com wxPython 4 (só para a interface) e R com os pacotes `ca`, `gee`, `ape`, `igraph`, `proxy`, `wordcloud`, `irlba`, `textometry`, `sna`, `network`, `intergraph` e `rgl`. Para a lematização contextual com udpipe, acrescenta-se:

```r
install.packages("udpipe")
```

Testado em Debian 13 com Python 3.13, wxPython 4.2.3 e R 4.5.0.

```bash
git clone https://github.com/ideiaglobal/iramuteq.git
cd iramuteq
python3 iramuteq.py    # interface gráfica
python3 iracli.py --help   # linha de comandos
```

## Ficheiros novos

| Ficheiro | Função |
|---|---|
| `iracli.py` | linha de comandos |
| `lemmatiseur.py` | anotação com udpipe, FreeLing e Stanza, e construção do corpus a partir da anotação |
| `lemmaconf.py` | analisadores e modelos por língua, deteção do que está instalado |
| `stanza_annotate.py` | chamada ao Stanza no ambiente Python próprio |
| `corpuslangs.py`, `corpuslangs_data.py` | registo das línguas do seletor |
| `README_CLI.md` | documentação da linha de comandos e da lematização contextual |

Alguns ficheiros citados no `README_CLI.md` (avaliação do galego, geração da lista de línguas) estão num diretório de trabalho à parte, `iramuteq-analise/`, que não faz parte deste repositório.

## Licença e autoria

O IRaMuTeQ é software livre, distribuído sob a licença GNU GPL (ver `gpl-2.0.txt`). Autor original: Pierre Ratinaud, LERASS, Université de Toulouse. As modificações deste repositório seguem a mesma licença.
