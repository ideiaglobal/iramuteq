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
| `--parser` | `dicionario` | `dicionario`, `udpipe`, `freeling` ou `stanza` (ver a secção seguinte) |
| `--udpipe-model` | — | Modelo udpipe: nome (`spanish-ancora`, `galician-treegal`…) ou caminho |
| `--freeling-lang` | deduzida de `--lang` | Língua do FreeLing (`gl`, `es`, `pt`…) |
| `--freeling-dir` | `~/.iramuteq-tools/freeling-4.2.1` | Pasta de instalação do FreeLing |
| `--stanza-lang` | deduzida de `--lang` | Língua do Stanza (`gl`, `es`, `pt`…) |
| `--stanza-package` | o padrão da língua | Modelo do Stanza (ex.: `treegal`, `ctg`) |
| `--freeling-no-ner` | — | Não juntar nomes próprios compostos (`Xosé_Luís_Barreiro`) |
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

## Lematização contextual: udpipe, FreeLing e Stanza (experimental)

O dicionário do IRaMuTeQ associa cada forma a **um só** lema e categoria. Com `--parser udpipe`, `--parser freeling` ou `--parser stanza`, o corpus é anotado por um analisador morfológico, e cada ocorrência recebe o lema e a categoria do seu contexto:

- **udpipe:** modelos [Universal Dependencies](https://universaldependencies.org) através do pacote R [udpipe](https://cran.r-project.org/package=udpipe).
- **Stanza:** [Stanza](https://stanfordnlp.github.io/stanza/), num ambiente Python próprio (`~/.iramuteq-tools/stanza-venv`, com PyTorch). É chamado através de `stanza_annotate.py`.
- **FreeLing:** [FreeLing](https://github.com/TALP-UPC/FreeLing) 4.2.1, programa `analyze`, com etiquetas EAGLES convertidas para UD. A instalação no Debian 13 está descrita em `iramuteq-analise/avaliacao_gl/RESULTADOS.md`.

```bash
python3 iracli.py corpus.txt --lang galician --parser freeling -a chd,spec --spec-var tema
```

```bash
python3 iracli.py corpus.txt --parser udpipe --udpipe-model spanish-ancora -a chd,spec --spec-var tema
```

**Modelos.** Os modelos são procurados em `~/.iramuteq-udpipe/` pelo nome; também se pode dar o caminho de um ficheiro `.udpipe`. Para descarregar um modelo:

```bash
Rscript -e 'udpipe::udpipe_download_model("galician-treegal", model_dir="~/.iramuteq-udpipe")'
```

Os modelos UD 2.5 do udpipe têm licença **CC BY-NC-SA 4.0** (uso não comercial).

### Como funciona (`lemmatiseur.py`)

1. **Leitura dos blocos.** Lê os blocos de texto com o mesmo agrupamento do `read_corpus`: as linhas entre marcas `****` e `-*`.
2. **Anotação.** Anota todos os blocos **numa só chamada** ao analisador, a partir do texto original, com maiúsculas e pontuação:
   - classe `Udpipe`: uma chamada ao R com `udpipe(..., parser = "none")`;
   - classe `FreeLing`: uma chamada ao `analyze`, com uma frase-sentinela entre os blocos para os separar na saída, e sem reconhecimento de datas e quantidades.

   - classe `Stanza`: uma chamada ao `stanza_annotate.py` no ambiente do Stanza, com os blocos em JSON.

   Para acrescentar outro analisador basta uma classe com `annotate(blocos)` e `describe()`. As palavras que chegam com o ponto final colado (*pan.*) são divididas em palavra + separador.
3. **Conversão das categorias.** Converte as categorias UD (UPOS + traços) nas que já existem no `key.cfg`, sem acrescentar categorias novas:
   - `NOUN`→`nom`, `VERB`→`ver`, `ADP`→`pre`;
   - `DET` com `Definite=Def`→`art_def`;
   - `PRON` com `PronType=Dem`→`pro_dem`;
   - `PROPN`→`nr`, como hoje acontece com as formas fora do dicionário.
4. **Chaves.** Cria uma **chave por leitura** só quando a mesma forma tem leituras diferentes no corpus. Por exemplo, `vino_nom` (lema *vino*) e `vino_ver` (lema *venir*). As formas com uma só leitura ficam com a chave simples.
5. **Lemas com várias categorias.** Quando um lema aparece com mais de uma categoria (*bajo* adj./prep.), recebe também um sufixo. Assim, as duas leituras não se juntam num lema cuja categoria seria a da primeira forma encontrada.
6. **Construção do corpus.** O `BuildFromAlcesteParsed` (subclasse de `BuildFromAlceste`) só substitui o `treattxt`. A segmentação, as bases de dados e todas as análises continuam inalteradas.
7. **Ficheiro de ambiguidades.** Escreve `ambiguidades.csv` na pasta do corpus: forma, leituras e ocorrências. O `Corpus.cira` regista o analisador (`parser`) e o modelo usado (`parser_model`).

**Decisões desta primeira versão:**

- **Contrações.** São divididas nas palavras sintáticas (gl. *do* → *de* + *o*), porque assim os artigos e as preposições ficam suplementares.
- **Concordanciador.** Mostra as chaves, com o sufixo das formas ambíguas, por exemplo `vino_ver`.
- **Expressões e dicionário externo.** O dicionário de expressões (`expression_XX.txt`) não é aplicado. A opção de dicionário externo nas análises deixa de fazer sentido.

### Na interface gráfica (FreeLing)

Ao abrir um corpus de texto (*Abrir um corpus de texto* / *Ouvrir un corpus texte*), o campo **Dicionário** do diálogo de configuração tem uma terceira opção: **FreeLing (contextual)**.

- **Quando a opção está disponível:** só fica ativa se o FreeLing estiver instalado e tiver dados para a língua escolhida. Ao lado aparece a língua e a pasta (por exemplo `gl - ~/.iramuteq-tools/freeling-4.2.1`). Caso contrário aparece a razão: "não instalado" ou "língua não disponível no FreeLing".
- **Dicionário de expressões:** com a opção escolhida, a caixa "Usar o dicionário de expressões" fica desmarcada e desativada. Ao voltar ao dicionário, o valor anterior é reposto.
- **Corpus criado:** abre-se e analisa-se como qualquer outro. O `Corpus.cira` regista `parser = freeling`, `freeling_lang` e `freeling_path`.
- **Pasta do FreeLing:** fica na preferência `freeling_path` do `iramuteq.cfg`. Vazia, usa `~/.iramuteq-tools/freeling-4.2.1`.

Código envolvido:

- `dialog.py` (`CorpusPref`): opção, ativação conforme a língua e parâmetros `parser`, `freeling_lang`, `freeling_path`.
- `corpus.py` (`Builder`): com `parser = freeling`, constrói o corpus com `lemmatiseur.build_parsed_corpus`.
- `freelingconf.py`: localização do FreeLing e línguas disponíveis. Fica num módulo próprio para o `dialog.py` não importar o `corpus.py`, o que criaria uma importação circular.
- `locale/{fr_FR,pt_PT,es_ES}`: traduções dos três textos novos.

Para correr a interface no Debian 13:

```bash
sudo apt install python3-wxgtk4.0 python3-xlrd
python3 iramuteq.py
```

### Testes (corpus sintéticos com frases gramaticais, 200 textos, 4 temas)

**Espanhol (`spanish-ancora`).** O corpus tem *vino* nome no tema "bebida" (400 ocorrências) e *vino* verbo no tema "llegada" (400).

| | Dicionário | udpipe |
|---|---|---|
| Leituras de *vino* | 800 × `vino/nom` | **400 `vino/nom` + 400 `venir/ver`** (100 % certo) |
| Especificidade de *vino* em bebida / llegada | +51 / **+56** | **+245** / −34 |
| Especificidade de *venir* em llegada | — | **+248** |
| CHD | *vino* caracteriza a classe de bebida e as duas de chegada | *vino* só na de bebida (χ² 362); *venir* nas de chegada |

Outros erros do dicionário que o udpipe evita: *casa* → `casar`. Erros do udpipe: *crianza* → `crianzar/ver` 8 vezes, e o primeiro verbo de algumas frases com maiúscula (*Dámelo* → NOUN).

**Galego (`galician-ctg`, `galician-treegal`).** O corpus tem *como* verbo (*comer*, 400 ocorrências) e *como* conjunção (400).

| | Léxico | ctg | treegal |
|---|---|---|---|
| *como* | 800 × `adv` | 800 × `pro` | 619 `adv` + 181 `con`, **nunca *comer*** |
| *sobre* prep. / nome (frases isoladas) | sempre `sobrar/ver` | ✔ ADP / NOUN | ✔ ADP / NOUN |
| Erros de lema vistos | — | *peixe*→`peixar`, *caldo*→`calr`, *polbo*→`polbir`, *veu*→`ver` | *peixe*→VERB, *viño*→`vo`, *mañá*→`mañ/aux`, *veu*→`ver` |

**FreeLing (`--parser freeling`), nos mesmos corpus:**

| | udpipe | FreeLing |
|---|---|---|
| es: *vino* (400 nome + 400 verbo) | **400 + 400** (100 %) | 479 `vino/nom` + 321 `venir/ver` (79 verbos lidos como nome) |
| es: especificidade de *vino* em bebida / llegada | 245 / −34 | 178 / −6 |
| gl: *como* (400 *comer* + 400 conjunção) | treegal: 619 `adv` + 181 `con` | 800 × `pro_rel`, **nunca *comer*** |

Na comparação alargada com texto real (`iramuteq-analise/avaliacao_gl/RESULTADOS.md`), o FreeLing é o melhor analisador para galego: 73 % no conjunto de ambiguidades e cerca de 97 % na distinção ativa/suplementar no TreeGal.

**Conclusão.** A integração funciona: a ambiguidade passa da anotação para todas as análises sem alterar o resto do IRaMuTeQ. A qualidade depende do analisador e da língua:
- **Espanhol:** o melhor foi o udpipe com o modelo AnCora.
- **Galego:** o melhor nas ambiguidades foi o FreeLing; o Stanza-treegal foi o melhor no texto corrido. Os modelos udpipe UD 2.5 são fracos.
- **Limite comum:** nenhum resolve as leituras raras, como *como* = *comer*.

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

Além da correção acima, que é independente do CLI, o código da aplicação **não foi alterado**. A lematização contextual está num módulo novo, `lemmatiseur.py`. O `iracli.py`:

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
