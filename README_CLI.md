# `iracli.py`: IRaMuTeQ sem interface

Constrói o corpus **uma vez** e corre sobre ele as análises de texto pedidas, a partir da linha de comandos. Não abre janelas e não precisa de wxPython.

```bash
python3 iracli.py corpus.txt --lang galician --out resultados/            # só a CHD (omissão)
python3 iracli.py corpus.txt -a stat,chd,spec,simi,nuvem --spec-var tema  # várias análises
python3 iracli.py --help
```

## Análises (`-a`)

| Nome | Análise da interface | Pacotes R |
|---|---|---|
| `stat` | Statistics: totais, hápax, lei de Zipf, tamanho dos segmentos | — |
| `chd` | Clustering → Reinert's Method | Matrix, cluster, ape, ca (+ irlba) |
| `spec` | Specificities and CA, por variável | ca (+ textometry com `hypergeo`) |
| `simi` | Similarities Analysis | igraph, proxy, Matrix (+ sna, intergraph, network com o layout `frutch`; + rgexf com `gexf`) |
| `nuvem` | WordCloud | wordcloud |

O CLI verifica os pacotes R antes de começar. Se faltar algum, indica o comando de instalação.

## Opções

**Gerais**

| Opção | Omissão | Descrição |
|---|---|---|
| `--lang` | `portuguese` | Idioma do dicionário (french, english, galician, …, other) |
| `--dictionary` | — | Dicionário próprio (`forma<TAB>lema<TAB>categoria`) |
| `--out` | pasta do corpus | Onde se cria `<corpus>_corpus_N/` |
| `--no-lem` | — | Não lematizar |
| `--rpath` | `R` no PATH | Executável R |

**`chd`**

| Opção | Omissão | Descrição |
|---|---|---|
| `--chd-classes` | 10 | Classes terminais da fase 1 |
| `--chd-mode` | `simple-st` | `simple-st`, `double-rst` ou `simple-text` |
| `--chd-min-segments` | 0 | Mínimo de segmentos por classe (0 = automático) |
| `--chd-max-actives` | 20000 | Máximo de formas ativas |
| `--chd-rst1`, `--chd-rst2` | 12, 14 | Tamanhos dos RST (só `double-rst`) |
| `--chd-svd` | `svdR` | `svdR` ou `irlba` (mais rápido em corpus grandes) |

**`spec`**

| Opção | Omissão | Descrição |
|---|---|---|
| `--spec-var` | a única variável, se só houver uma | Variável (`tema`) ou lista de modalidades (`tema_mar,tema_escola`) |
| `--spec-index` | `chi2` | `chi2` ou `hypergeo` (a lei hipergeométrica exige o pacote R `textometry`) |
| `--spec-min-freq` | 10 | Frequência mínima das formas |
| `--spec-forms` | `todas` | `todas`, `ativas` ou `suplementares` |

**`simi`**

| Opção | Omissão | Descrição |
|---|---|---|
| `--simi-words` | 100 | Número de formas mais frequentes a incluir |
| `--simi-index` | `cooccurrence` | Também `Jaccard`, `Ochiai`, `binomial`, … (os 28 índices da interface) |
| `--simi-format` | `png` | `png` ou `gexf` (para o Gephi) |
| `--simi-layout` | `frutch` | `frutch`, `kawa`, `graphopt`, `circle`, `random` |
| `--simi-no-tree` | — | Não reduzir à árvore máxima |
| `--simi-communities [ALG]` | — | Detetar e colorir comunidades, com halo. Algoritmos: `edge-betweenness` (omissão), `fastgreedy`, `label-propagation`, `leading-eigenvector`, `multilevel`, `optimal`, `spinglass`, `walktrap` |
| `--simi-svg` | — | Gráfico em SVG |

**`nuvem`**

| Opção | Omissão | Descrição |
|---|---|---|
| `--nuvem-forms` | `ativas` | `ativas`, `suplementares` ou `todas` |
| `--nuvem-max-words` | 600 | Número máximo de palavras |
| `--nuvem-size` | 800 | Largura e altura, em píxeis |
| `--nuvem-svg` | — | Gráfico em SVG |

Os restantes parâmetros vêm de `configuration/*.cfg` ou dos mesmos valores por omissão que os diálogos da interface usam.

## Resultados

São as mesmas pastas que a interface cria e podem ser abertas nela (*Open an analysis*):

```
<corpus>_corpus_1/           corpus.db, formes.db, uces.db, Corpus.cira
├── <corpus>_stat_1/         glob.txt, total.csv, hapax.csv, zipf.png, segments_size.png
├── <corpus>_alceste_1/      profiles.csv, antiprofiles.csv, chisqtable.csv, dendro1.png, AFC2D*.png …
├── <corpus>_spec_1/         tablespecf.csv, tablespect.csv, banalites.csv, afcf_*.png, afct_*.png …
├── <corpus>_simitxt_1/      graph_simi_1.png (ou web_1/gexf.gexf)
└── <corpus>_wordcloud_1/    nuage_1.png
```

Código de saída: `0` correu tudo bem; `1` houve uma análise com erro; `3` faltam pacotes R.

Uma análise só é dada como bem-sucedida se o R não registou erros **e** o ficheiro de resultado esperado existe (`zipf.png`, `profiles.csv`, `tablespecf.csv`, `graph_simi_*`/`gexf.gexf`, `nuage_*`).

## Verificação

Testado em 2026-11-26 com Python 3, R 4.5.0 e sem wxPython. O corpus de teste era sintético, em português: 80 textos, 4 temas, a variável `*tema_*`.

| Análise | Estado |
|---|---|
| `stat` | ✔ 80 textos, 8160 ocorrências, gráficos de Zipf e de tamanho dos segmentos |
| `chd` | ✔ 5 classes, 64,6 % dos segmentos classificados. Escola, política e saúde ficaram em classes puras; o tema mar dividiu-se em duas |
| `spec` (`chi2`) | ✔ As formas mais específicas de cada modalidade correspondem ao tema (aula/professor, rede/praia, votar/eleição, hospital/tratamento) |
| `spec --spec-index hypergeo` | ✔ Mesmos temas (escola: aula, professor; política: votar, eleição; …) |
| `nuvem` | ✔ `nuage_1.png` |
| `simi --simi-layout kawa` | ✔ Os 4 temas formam 4 grupos no grafo. Com `--simi-communities multilevel`, 5 comunidades coloridas, com halo. Testado também `--simi-index Jaccard` |
| `simi` com layout `frutch` (omissão) | ✔ `graph_simi_1.png` |
| `simi --simi-format gexf` | ✔ `web_1/gexf.gexf` com 55 nós e 54 arestas. Com `--simi-communities fastgreedy`, 5 cores distintas. Só funcionou depois da correção em `Rgraph.R` descrita abaixo |
| Corrida completa `-a stat,chd,spec,simi,nuvem` | ✔ Código de saída 0 |

Pacotes R instalados para estes testes: `ape` 5.8.1, `proxy` 0.4.29, `textometry` 0.1.7, `sna` 2.8, `intergraph` 2.0.4, `network` 1.20.0, `rgexf` 0.17.0.

## Correção ao código da aplicação

**`Rscripts/Rgraph.R`**: as funções `simi.to.gexf` e a exportação GEXF da AFC passavam ao `write.gexf` a transparência das cores entre 0 e 255. O `rgexf` atual (testado: 0.17.0) exige um valor entre 0 e 1 e para com o erro *The color specification for nodes is out of range*. A correção divide essa coluna por 255, em duas linhas. Este defeito afeta também a interface gráfica com versões recentes do `rgexf`, por isso é candidato a ser proposto ao projeto original.

## Como funciona

Além da correção acima, que é independente do CLI, o código da aplicação **não foi alterado**. O `iracli.py`:

1. Regista um *import hook* que responde a `import wx` (e `wx.*`) com classes substitutas sem efeitos. Faz o mesmo para `xlrd`, quando falta. Assim importam sem erro os módulos que misturam interface e cálculo.
2. Cria um objeto `Headless` com os atributos da janela principal que as análises leem: `ConfigPath`, `DictPath`, `RscriptsPath`, `pref`, `RPath`, `TEMPDIR`, `history`, `lexique`.
3. Constrói o corpus com `BuildFromAlceste` e abre-o com `conn_all()`.
4. Corre cada análise com `dlg=False`. Onde a classe original depende de um diálogo, uma subclasse pequena substitui só esse passo:
   - `CliLexico`: a lista de modalidades, que vinha do `OptLexi`.
   - `CliSimiTxt`: a seleção das N formas mais frequentes, que vinha do `PrepSimi`.
   - `CliWordCloud`: as opções, que vinham do `PrefWordCloud`; aqui todas as formas ficam selecionadas, em vez do `SelectColumn`.

## Limites conhecidos

- Na aplicação, a `BugReport` apaga `Rerror` depois de mostrar o erro numa janela. Por isso, o `Headless` guarda os erros do R num registo próprio (`r_errors`). Sem isso, um erro do R passaria despercebido no CLI.

- Os textos gerados pela aplicação (`glob.txt`, `RAPPORT.txt`) saem na língua da interface definida em `configuration/iramuteq.cfg` (francês, por omissão).
- A saída do R aparece no terminal, porque `exec_rcode` não a captura.
- Ainda não incluídas: distância de Labbé, subcorpus e as análises sobre matrizes.
