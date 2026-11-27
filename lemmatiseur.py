# -*- coding: utf-8 -*-
"""Lematização contextual (udpipe ou FreeLing) em vez do dicionário forma→lema.

O IRaMuTeQ identifica cada palavra por uma *chave* (a forma escrita) que aponta para
um único (lema, categoria). Este módulo anota o corpus com um analisador morfológico
e cria uma chave por leitura quando a mesma forma tem leituras diferentes:

    "un vino tinto"  → vino_nom  (lema vino,  nom)
    "ayer vino Juan" → vino_ver  (lema venir, ver)

As formas com uma só leitura no corpus mantêm a chave simples. Tudo o que vem depois
(segmentação, CHD, especificidades, similitude…) usa estas chaves sem alterações.

Analisadores:
    Udpipe(modelo, rpath)    — pacote R udpipe, modelos Universal Dependencies 2.5
    FreeLing(lingua, pasta)  — FreeLing 4.x (programa `analyze`), etiquetas EAGLES
    Stanza(lingua)           — Stanza (PyTorch), num ambiente Python próprio, via stanza_annotate.py

Uso: `build_parsed_corpus(infile, parametres, analisador)` em vez de `BuildFromAlceste(...)`.
"""
import codecs
import csv
import logging
import os
import subprocess
import tempfile
from collections import Counter, defaultdict, deque

from corpus import BuildFromAlceste, Uce, testetoile, testint

log = logging.getLogger('iramuteq.lemmatiseur')


def run_process(cmd, progress=None, event=None, detail=None, input=None, **kw):
    """subprocess.run com captura de texto; enquanto o processo corre chama progress(event, detail)
    cada 0,2 s, para a janela de progresso do IRaMuTeQ se manter viva e mostrar o que se faz."""
    if progress is None:
        return subprocess.run(cmd, input=input, capture_output=True, text=True, **kw)
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE if input is not None else None,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, **kw)
    pending = input
    while True:
        progress(event, detail)
        try:
            out, err = proc.communicate(pending, timeout=0.2)
            break
        except subprocess.TimeoutExpired:
            pending = None   # o resto da entrada continua a ser enviado por communicate
    return subprocess.CompletedProcess(cmd, proc.returncode, out, err)

TOOLS_DIR = os.path.join(os.path.expanduser('~'), '.iramuteq-tools')
UDPIPE_MODEL_DIR = os.path.join(os.path.expanduser('~'), '.iramuteq-udpipe')
FREELING_DIR = os.path.join(TOOLS_DIR, 'freeling-4.2.1')

# Pontuação que a segmentação do IRaMuTeQ usa como fronteira (ver decouperlist).
SEPARATORS = {'.', '?', '!', ':', ';', ','}
ELLIPSIS = {'...', '…'}


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
# Etiquetas EAGLES (FreeLing) → UPOS + traços
# ---------------------------------------------------------------------------
_EAGLES_DET = {'A': 'PronType=Art', 'D': 'PronType=Dem', 'P': 'Poss=Yes', 'I': 'PronType=Ind',
               'T': 'PronType=Int', 'E': 'PronType=Int', 'N': 'NumType=Card'}
_EAGLES_PRON = {'P': 'PronType=Prs', 'D': 'PronType=Dem', 'X': 'Poss=Yes', 'I': 'PronType=Ind',
                'R': 'PronType=Rel', 'T': 'PronType=Int', 'E': 'PronType=Int', 'N': 'PronType=Ind'}


def eagles_to_ud(tag):
    """'DA0MS0' → ('DET', 'PronType=Art|Definite=Def'); 'VMIS3S0' → ('VERB', ''); …"""
    t = tag.upper()
    c, s = t[:1], t[1:2]
    if c == 'N':
        return ('PROPN' if s == 'P' else 'NOUN'), ''
    if c == 'V':
        return ('AUX' if s in ('A', 'S') else 'VERB'), ''
    if c == 'A':
        return 'ADJ', ('NumType=Ord' if s == 'O' else '')
    if c == 'R':
        return 'ADV', ''
    if c == 'S':
        return 'ADP', ''
    if c == 'C':
        return ('SCONJ' if s == 'S' else 'CCONJ'), ''
    if c == 'D':
        feats = _EAGLES_DET.get(s, '')
        if s == 'A':
            feats += '|Definite=Def'
        return 'DET', feats
    if c == 'P':
        return 'PRON', _EAGLES_PRON.get(s, '')
    if c in ('Z', 'W'):
        return 'NUM', ''
    if c == 'I':
        return 'INTJ', ''
    if c == 'F':
        return 'PUNCT', ''
    return 'X', ''


# ---------------------------------------------------------------------------
# Analisadores: annotate(blocks) → por bloco, [(forma, lema, upos, traços)]
# ---------------------------------------------------------------------------
def _find_rscript(rpath):
    return os.path.join(os.path.dirname(rpath), 'Rscript') if rpath else 'Rscript'


class Udpipe:
    """udpipe (pacote R), com um modelo Universal Dependencies."""
    name = 'udpipe'
    r_packages = ['udpipe']

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

    def __init__(self, model, rpath=None, model_dir=UDPIPE_MODEL_DIR, download=False, progress=None):
        self.rscript = _find_rscript(rpath)
        self.progress = progress
        try:
            self.model_path = self.find_model(model, model_dir)
        except FileNotFoundError:
            if not download or os.path.isfile(model):
                raise
            self.model_path = self.download_model(model, model_dir)

    def download_model(self, model, model_dir=UDPIPE_MODEL_DIR):
        """Descarrega um modelo UD 2.5 (3–20 MB) do repositório do pacote udpipe para model_dir."""
        os.makedirs(model_dir, exist_ok=True)
        log.info('udpipe: a descarregar o modelo %s para %s', model, model_dir)
        code = 'm <- udpipe::udpipe_download_model(commandArgs(TRUE)[1], model_dir = commandArgs(TRUE)[2]); ' \
               'if (isTRUE(m$download_failed[1])) quit(status = 1)'
        proc = run_process([self.rscript, '--vanilla', '-e', code, model, model_dir],
                           self.progress, 'download', model)
        if proc.returncode != 0:
            raise RuntimeError('udpipe: não foi possível descarregar o modelo %s:\n%s' % (model, proc.stderr[-2000:]))
        return self.find_model(model, model_dir)

    @staticmethod
    def find_model(name_or_path, model_dir=UDPIPE_MODEL_DIR):
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

    def describe(self):
        return {'parser': 'udpipe', 'parser_model': os.path.basename(self.model_path)}

    def annotate(self, blocks):
        """Anota todos os blocos numa só chamada ao R."""
        tmpdir = tempfile.mkdtemp(prefix='iraudpipe')
        fin, fout, fscript = (os.path.join(tmpdir, n) for n in ('in.tsv', 'out.tsv', 'annotate.R'))
        with open(fin, 'w', encoding='utf-8') as f:
            for i, block in enumerate(blocks):
                f.write('d%07i\t%s\n' % (i, ' '.join(block).replace('\t', ' ')))
        with open(fscript, 'w', encoding='utf-8') as f:
            f.write(self.R_SCRIPT)
        proc = run_process([self.rscript, '--vanilla', fscript, self.model_path, fin, fout],
                           self.progress, 'annotate', self.name)
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


class FreeLing:
    """FreeLing 4.x (programa `analyze`). Divide contrações e clíticos; junta nomes próprios (NER)."""
    name = 'freeling'
    r_packages = []
    progress = None   # progress(event, detail), ver run_process
    SENTINEL = 'Zzxqwj'   # frase-sentinela entre blocos, para os separar na saída

    def __init__(self, lang='gl', freeling_dir=FREELING_DIR, ner=True, multiwords=True):
        self.lang = lang
        self.dir = freeling_dir
        self.share = os.path.join(freeling_dir, 'share', 'freeling')
        self.cfg = os.path.join(self.share, 'config', '%s.cfg' % lang)
        self.analyze = os.path.join(freeling_dir, 'bin', 'analyze')
        if not os.path.isfile(self.analyze):
            raise FileNotFoundError('FreeLing não encontrado em %s (falta bin/analyze)' % freeling_dir)
        if not os.path.isfile(self.cfg):
            raise FileNotFoundError('FreeLing sem configuração para a língua "%s" (%s)' % (lang, self.cfg))
        self.options = ['--outlv', 'tagged', '--nodate', '--noquant']
        if not ner:
            self.options.append('--noner')
        if not multiwords:
            self.options.append('--noloc')

    def describe(self):
        return {'parser': 'freeling', 'parser_model': 'FreeLing %s (%s)' % (os.path.basename(self.dir), self.lang)}

    def annotate(self, blocks):
        sentinel = self.SENTINEL.lower()
        text = ''.join('%s\n%s .\n' % (' '.join(block), self.SENTINEL) for block in blocks)
        env = dict(os.environ, FREELINGSHARE=self.share,
                   LD_LIBRARY_PATH=os.pathsep.join(filter(None, [os.path.join(self.dir, 'lib'),
                                                                 os.environ.get('LD_LIBRARY_PATH')])))
        proc = run_process([self.analyze, '-f', self.cfg] + self.options, self.progress, 'annotate',
                           self.name, input=text, env=env)
        if proc.returncode != 0:
            raise RuntimeError('FreeLing falhou:\n' + proc.stderr[-3000:])
        docs, cur, skip_dot = [], [], False
        for line in proc.stdout.splitlines():
            parts = line.split(' ')
            if len(parts) < 3:
                continue
            token, lemma, tag = parts[0], parts[1], parts[2]
            if token.lower() == sentinel:
                docs.append(cur)
                cur, skip_dot = [], True
                continue
            if skip_dot and token == '.':
                skip_dot = False
                continue
            skip_dot = False
            upos, feats = eagles_to_ud(tag)
            cur.append((token, lemma, upos, feats))
        if len(docs) != len(blocks):
            raise RuntimeError('FreeLing: %i blocos anotados para %i blocos de texto' % (len(docs), len(blocks)))
        return docs


class Stanza:
    """Stanza (Stanford NLP), num ambiente Python próprio (PyTorch). Modelos UD recentes."""
    name = 'stanza'
    r_packages = []
    progress = None   # progress(event, detail), ver run_process
    HELPER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'stanza_annotate.py')

    def __init__(self, lang='gl', python=os.path.join(TOOLS_DIR, 'stanza-venv', 'bin', 'python'),
                 model_dir=os.path.join(TOOLS_DIR, 'stanza_resources'), package=None):
        if not os.path.isfile(python):
            raise FileNotFoundError('Python com o Stanza não encontrado: %s' % python)
        self.lang, self.python, self.model_dir, self.package = lang, python, model_dir, package

    def describe(self):
        return {'parser': 'stanza', 'parser_model': 'Stanza %s%s' % (self.lang, '/' + self.package if self.package else '')}

    def annotate(self, blocks):
        import json
        req = {'lang': self.lang, 'model_dir': self.model_dir, 'package': self.package,
               'texts': [' '.join(b) for b in blocks]}
        proc = run_process([self.python, '-I', self.HELPER], self.progress, 'annotate', self.name,
                           input=json.dumps(req))
        if proc.returncode != 0:
            raise RuntimeError('Stanza falhou:\n' + proc.stderr[-3000:])
        docs = [[tuple(w) for w in doc] for doc in json.loads(proc.stdout)]
        if len(docs) != len(blocks):
            raise RuntimeError('Stanza: %i blocos anotados para %i blocos de texto' % (len(docs), len(blocks)))
        return docs


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
            # alguns tokenizadores (ex.: Stanza gl/ctg) deixam o ponto final colado: "pan." → "pan" + "."
            trailing = ''
            if len(token) > 1 and token[-1] in SEPARATORS and token[:-1].strip(''.join(SEPARATORS)):
                token, trailing = token.rstrip(''.join(SEPARATORS)), token[-1]
                lemma = lemma.rstrip(''.join(SEPARATORS))
            form = clean_token(token)
            if form:
                gram = ud_to_gram(upos, feats)
                lem = clean_token(lemma) or form
                if form.isdigit():
                    gram, lem = 'num', form
                seq.append(Reading(form, lem, gram))
            if trailing:
                seq.append(trailing)
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
            raise RuntimeError('os blocos anotados não correspondem ao texto lido (uci %i)' % iduci)
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


def build_parsed_corpus(infile, parametres, analyser, dlg=None):
    """Anota o corpus com `analyser` (Udpipe ou FreeLing) e constrói-o. Devolve (corpus, ambiguidades)."""
    blocks = read_blocks(infile, parametres['encoding'], parametres.get('ucimark', 0))
    log.info('%s: %i blocos', analyser.name, len(blocks))
    docs = analyser.annotate(blocks)
    readings = to_readings(docs)
    key, lexique, ambiguous = build_keys(readings)
    parsed = deque()
    for block, seq in zip(blocks, readings):
        parsed.append((block, [t if isinstance(t, str) else key(t) for t in seq]))

    parametres = dict(parametres)
    parametres.update(analyser.describe())
    parametres.update({'expressions': 0, 'lem': 1})
    builder = BuildFromAlcesteParsed(infile, parametres, lexique, parsed, dlg=dlg)
    write_ambiguities(os.path.join(parametres['pathout'], 'ambiguidades.csv'), ambiguous)
    return builder.corpus, ambiguous
