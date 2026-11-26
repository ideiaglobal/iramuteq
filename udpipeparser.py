# -*- coding: utf-8 -*-
"""Lematização contextual com udpipe (pacote R) em vez do dicionário forma→lema.

O IRaMuTeQ identifica cada palavra por uma *chave* (a forma escrita) que aponta para
um único (lema, categoria). Este módulo anota o corpus com um modelo Universal
Dependencies e cria uma chave por leitura quando a mesma forma tem leituras diferentes:

    "un vino tinto"  → vino_nom  (lema vino,  nom)
    "ayer vino Juan" → vino_ver  (lema venir, ver)

As formas com uma só leitura no corpus mantêm a chave simples. Tudo o que vem depois
(segmentação, CHD, especificidades, similitude…) usa estas chaves sem alterações.

Uso: `build_parsed_corpus(...)` em vez de `BuildFromAlceste(...)`.
"""
import codecs
import csv
import logging
import os
import subprocess
import tempfile
from collections import Counter, defaultdict, deque

from corpus import BuildFromAlceste, Uce, testetoile, testint

log = logging.getLogger('iramuteq.udpipe')

MODEL_DIR = os.path.join(os.path.expanduser('~'), '.iramuteq-udpipe')

# Pontuação que a segmentação do IRaMuTeQ usa como fronteira (ver decouperlist).
SEPARATORS = {'.', '?', '!', ':', ';', ','}
ELLIPSIS = {'...', '…'}

R_SCRIPT = r'''
args <- commandArgs(trailingOnly = TRUE)
suppressMessages(library(udpipe))
model <- udpipe_load_model(args[1])
d <- read.delim(args[2], header = FALSE, quote = "", comment.char = "", col.names = c("doc_id", "text"),
                colClasses = "character", encoding = "UTF-8")
x <- udpipe(d, object = model, parser = "none")
x <- x[, c("doc_id", "token_id", "token", "lemma", "upos", "feats")]
write.table(x, args[3], sep = "\t", quote = FALSE, row.names = FALSE, na = "", fileEncoding = "UTF-8")
'''


# ---------------------------------------------------------------------------
# Modelos
# ---------------------------------------------------------------------------
def find_model(name_or_path, model_dir=MODEL_DIR):
    """'galician-ctg' → ~/.iramuteq-udpipe/galician-ctg-ud-2.5-191206.udpipe (ou um caminho direto)."""
    if os.path.isfile(name_or_path):
        return os.path.abspath(name_or_path)
    if os.path.isdir(model_dir):
        found = sorted(f for f in os.listdir(model_dir) if f.startswith(name_or_path + '-') and f.endswith('.udpipe'))
        if found:
            return os.path.join(model_dir, found[-1])
    raise FileNotFoundError(
        'Modelo udpipe não encontrado: %s\nDescarregue-o com:\n'
        '  Rscript -e \'udpipe::udpipe_download_model("%s", model_dir="%s")\'' % (name_or_path, name_or_path, model_dir))


# ---------------------------------------------------------------------------
# Categorias UD → categorias do IRaMuTeQ (configuration/key.cfg)
# ---------------------------------------------------------------------------
def parse_feats(feats):
    out = {}
    for item in (feats or '').split('|'):
        if '=' in item:
            k, v = item.split('=', 1)
            out[k] = v
    return out


def ud_to_gram(upos, feats):
    """Converte UPOS (+ traços) numa categoria que já existe no key.cfg.

    Só usa categorias existentes, para a interface (KeyFrame) e o key.cfg continuarem válidos.
    Nomes próprios ficam em `nr`, como acontece hoje com as formas fora do dicionário.
    """
    f = parse_feats(feats)
    pron = f.get('PronType', '')
    if upos == 'NOUN':
        return 'nom'
    if upos == 'VERB':
        return 'ver'
    if upos == 'AUX':
        return 'aux'
    if upos == 'ADJ':
        return 'adj_num' if f.get('NumType') == 'Ord' else 'adj'
    if upos in ('ADV', 'PART'):
        return 'adv'
    if upos == 'ADP':
        return 'pre'
    if upos in ('CCONJ', 'SCONJ'):
        return 'con'
    if upos == 'NUM':
        return 'num'
    if upos == 'INTJ':
        return 'ono'
    if upos == 'DET':
        if pron == 'Art' or 'Definite' in f:
            return 'art_ind' if f.get('Definite') == 'Ind' else 'art_def'
        if f.get('Poss') == 'Yes':
            return 'adj_pos'
        if pron == 'Dem':
            return 'adj_dem'
        if pron == 'Int':
            return 'adj_int'
        if f.get('NumType') == 'Card':
            return 'adj_num'
        return 'adj_ind' if pron else 'art_def'   # sem traços (ex.: galician-ctg) — todos são suplementares
    if upos == 'PRON':
        if f.get('Poss') == 'Yes':
            return 'pro_pos'
        return {'Prs': 'pro_per', 'Dem': 'pro_dem', 'Rel': 'pro_rel', 'Ind': 'pro_ind',
                'Neg': 'pro_ind', 'Tot': 'pro_ind'}.get(pron, 'pro')
    if upos == 'SYM':
        return 'sw'
    return 'nr'   # PROPN, X, desconhecidos


# ---------------------------------------------------------------------------
# Leitura dos blocos de texto (mesmo agrupamento que BuildFromAlceste.read_corpus)
# ---------------------------------------------------------------------------
def read_blocks(infile, encoding, ucimark=0):
    """Blocos de linhas que read_corpus vai entregar a treattxt, pela mesma ordem."""
    testuci = testetoile if ucimark == 0 else testint
    blocks, txt, in_text = [], [], False
    with codecs.open(infile, 'r', encoding) as f:
        for line in f:
            line = line.rstrip('\n\r')
            if testuci(line) or line.startswith('-*'):
                if txt:
                    blocks.append(txt)
                    txt = []
                in_text = in_text or testuci(line)
            elif line.strip() != '' and in_text:
                txt.append(line)
    if txt:
        blocks.append(txt)
    return blocks


# ---------------------------------------------------------------------------
# Anotação
# ---------------------------------------------------------------------------
def annotate(blocks, model_path, rscript):
    """Anota todos os blocos numa só chamada ao R. Devolve, por bloco, [(forma, lema, upos, feats)]."""
    tmpdir = tempfile.mkdtemp(prefix='iraudpipe')
    fin, fout, fscript = (os.path.join(tmpdir, n) for n in ('in.tsv', 'out.tsv', 'annotate.R'))
    with open(fin, 'w', encoding='utf-8') as f:
        for i, block in enumerate(blocks):
            text = ' '.join(block).replace('\t', ' ')
            f.write('d%07i\t%s\n' % (i, text))
    with open(fscript, 'w', encoding='utf-8') as f:
        f.write(R_SCRIPT)
    proc = subprocess.run([rscript, '--vanilla', fscript, model_path, fin, fout], capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError('udpipe falhou:\n' + proc.stderr)

    docs = [[] for _ in blocks]
    with open(fout, encoding='utf-8', newline='') as f:
        reader = csv.reader(f, delimiter='\t', quoting=csv.QUOTE_NONE)
        next(reader)
        for doc_id, token_id, token, lemma, upos, feats in reader:
            if '-' in token_id or '.' in token_id:
                continue   # token de várias palavras (ex.: gl "do" = de + o): ficam as palavras sintáticas
            docs[int(doc_id[1:])].append((token, lemma, upos, feats))
    return docs


# ---------------------------------------------------------------------------
# Chaves e dicionário do corpus
# ---------------------------------------------------------------------------
def clean_token(s):
    s = '_'.join(s.lower().split()).strip('_')   # o IRaMuTeQ trata "_x_" como forma suplementar especial
    return '' if '$' in s else s                    # '$' marca o fim do texto na segmentação (decouperlist)


class Reading:
    __slots__ = ('form', 'lemma', 'gram')

    def __init__(self, form, lemma, gram):
        self.form, self.lemma, self.gram = form, lemma, gram


def to_readings(docs):
    """Tokens anotados → leituras (ou separadores de pontuação, como strings)."""
    out = []
    for doc in docs:
        seq = []
        for token, lemma, upos, feats in doc:
            if upos == 'PUNCT':
                if token in SEPARATORS:
                    seq.append(token)
                elif token in ELLIPSIS:
                    seq.append('£$£')
                continue
            form = clean_token(token)
            if not form:
                continue
            gram = ud_to_gram(upos, feats)
            lem = clean_token(lemma) or form
            if form.isdigit():
                gram, lem = 'num', form
            seq.append(Reading(form, lem, gram))
        out.append(seq)
    return out


def build_keys(readings_docs):
    """Decide a chave de cada leitura e o lema de cada chave, com base em todo o corpus.

    - forma com uma só leitura (lema, categoria)  → chave = forma
    - forma ambígua                              → forma_categoria, ou forma_lema se a categoria não chegar
    - lema com várias categorias (ex.: bajo adj / bajo pre) → lema_categoria, para não se juntarem
    Devolve (função leitura→chave, lexique {chave: [lema, categoria]}, ambiguidades).
    """
    by_form = defaultdict(Counter)
    lemma_grams = defaultdict(set)
    for seq in readings_docs:
        for r in seq:
            if isinstance(r, Reading):
                by_form[r.form][(r.lemma, r.gram)] += 1
                lemma_grams[r.lemma].add(r.gram)

    def lemma_key(lemma, gram):
        return lemma if len(lemma_grams[lemma]) == 1 else '%s_%s' % (lemma, gram)

    key_of = {}
    ambiguous = {}
    for form, readings in by_form.items():
        if len(readings) == 1:
            (lemma, gram), = readings
            key_of[(form, lemma, gram)] = form
            continue
        ambiguous[form] = readings
        grams = Counter(g for _, g in readings)
        lemmas = Counter(l for l, _ in readings)
        for lemma, gram in readings:
            if grams[gram] == 1:
                key = '%s_%s' % (form, gram)
            elif lemmas[lemma] == 1:
                key = '%s_%s' % (form, lemma)
            else:
                key = '%s_%s_%s' % (form, lemma, gram)
            key_of[(form, lemma, gram)] = key

    lexique = {}
    for (form, lemma, gram), key in key_of.items():
        lexique[key] = [lemma_key(lemma, gram), gram]
    return (lambda r: key_of[(r.form, r.lemma, r.gram)]), lexique, ambiguous


def write_ambiguities(path, ambiguous):
    with open(path, 'w', encoding='utf-8', newline='') as f:
        w = csv.writer(f, delimiter=';')
        w.writerow(['forma', 'leituras', 'lema', 'categoria', 'ocorrencias'])
        for form in sorted(ambiguous, key=lambda k: -sum(ambiguous[k].values())):
            for (lemma, gram), n in ambiguous[form].most_common():
                w.writerow([form, len(ambiguous[form]), lemma, gram, n])


# ---------------------------------------------------------------------------
# Construção do corpus
# ---------------------------------------------------------------------------
class BuildFromAlcesteParsed(BuildFromAlceste):
    """BuildFromAlceste em que cada bloco de texto chega já anotado (fila `self.parsed`)."""

    def __init__(self, infile, parametres_corpus, lexique, parsed, dlg=None):
        self.parsed = parsed   # deque de (linhas originais, [chaves e separadores])
        BuildFromAlceste.__init__(self, infile, parametres_corpus, lexique, {}, dlg=dlg)

    def treattxt(self, txt, iduce, idpara, iduci):
        lines, tokens = self.parsed.popleft()
        if lines != txt:
            raise RuntimeError('udpipe: os blocos anotados não correspondem ao texto lido (uci %i)' % iduci)
        if self.corpus.ucis[-1].paras == []:
            idpara += 1
        # a segmentação do IRaMuTeQ corre sobre a sequência de chaves (com a pontuação como fronteira)
        ucetxt = self.make_uces(' '.join(tokens), self.corpus.parametres['douce'])
        for uce in ucetxt:
            iduce += 1
            self.corpus.ucis[-1].uces.append(Uce(iduce, idpara, iduci))
            self.c.execute('INSERT INTO uces VALUES(?,?);', (repr(iduce), uce))
            for word in uce.split():
                self.last += 1
                self.corpus.add_word(word)
        if self.last > self.lim:
            self.backup_uce()
            self.last = 0
        return iduce, idpara


def build_parsed_corpus(infile, parametres, model, rscript, dlg=None):
    """Anota o corpus com udpipe e constrói-o. Devolve (corpus, nº de formas ambíguas)."""
    model_path = find_model(model)
    blocks = read_blocks(infile, parametres['encoding'], parametres.get('ucimark', 0))
    log.info('udpipe: %i blocos, modelo %s', len(blocks), model_path)
    docs = annotate(blocks, model_path, rscript)
    readings = to_readings(docs)
    key, lexique, ambiguous = build_keys(readings)
    parsed = deque()
    for block, seq in zip(blocks, readings):
        parsed.append((block, [t if isinstance(t, str) else key(t) for t in seq]))

    parametres = dict(parametres)
    parametres.update({'parser': 'udpipe', 'udpipe_model': os.path.basename(model_path),
                       'expressions': 0, 'lem': 1})
    builder = BuildFromAlcesteParsed(infile, parametres, lexique, parsed, dlg=dlg)
    corpus = builder.corpus
    write_ambiguities(os.path.join(parametres['pathout'], 'ambiguidades.csv'), ambiguous)
    return corpus, ambiguous
