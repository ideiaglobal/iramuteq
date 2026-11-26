#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""IRaMuTeQ em linha de comandos: corpus → análises de texto, sem interface.

Uso:
    python3 iracli.py corpus.txt --lang galician --out resultados/          # só CHD
    python3 iracli.py corpus.txt -a stat,chd,spec,simi,nuvem --spec-var tema
    python3 iracli.py --help

Não altera o código da aplicação: instala um módulo `wx` substituto (sem
efeitos) antes de importar os módulos do IRaMuTeQ, e entrega às análises um
objeto `Headless` com os atributos que a janela principal lhes forneceria.
As análises correm com `dlg=False`, o que já evita os diálogos de parâmetros.
"""
import argparse
import importlib.abc
import importlib.machinery
import logging
import os
import shutil
import sys
import tempfile
import types
from configparser import RawConfigParser  # stdlib, antes de o configparser local entrar no caminho

APPLI_PATH = os.path.dirname(os.path.realpath(__file__))
if APPLI_PATH not in sys.path:   # também com `python3 -I`, que não acrescenta a pasta do script
    sys.path.insert(0, APPLI_PATH)


# ---------------------------------------------------------------------------
# 1. wx substituto
# ---------------------------------------------------------------------------
_STUB_CLASSES = {}


def _stub_class(qualname):
    """Uma classe substituta distinta por nome (permite herança múltipla de wx.*)."""
    if qualname not in _STUB_CLASSES:
        _STUB_CLASSES[qualname] = _StubMeta(qualname.rsplit('.', 1)[-1], (_Stub,), {'__qualname__': qualname})
    return _STUB_CLASSES[qualname]


class _StubMeta(type):
    """Qualquer atributo de uma classe substituta é outra classe substituta."""
    def __getattr__(cls, name):
        if name.startswith('__') and name.endswith('__'):
            raise AttributeError(name)
        return _stub_class(cls.__qualname__ + '.' + name)

    def __or__(cls, other):
        return 0
    __ror__ = __and__ = __rand__ = __or__


class _Stub(metaclass=_StubMeta):
    """Pode ser instanciada, herdada, chamada e consultada sem fazer nada."""
    def __init__(self, *args, **kwargs):
        pass

    def __getattr__(self, name):
        if name.startswith('__') and name.endswith('__'):
            raise AttributeError(name)
        return _Stub()

    def __call__(self, *args, **kwargs):
        return _Stub()

    def __bool__(self):
        return False

    def __iter__(self):
        return iter(())

    def __contains__(self, item):
        return False

    def __int__(self):
        return 0
    __index__ = __int__

    def __or__(self, other):
        return 0
    __ror__ = __and__ = __rand__ = __or__


class _StubModule(types.ModuleType):
    def __getattr__(self, name):
        if name.startswith('__') and name.endswith('__'):
            raise AttributeError(name)
        return _stub_class(self.__name__ + '.' + name)


class _StubFinder(importlib.abc.MetaPathFinder, importlib.abc.Loader):
    """Responde a `import wx` (e `wx.qualquer.coisa`) com módulos substitutos."""
    def __init__(self, roots):
        self.roots = set(roots)

    def find_spec(self, fullname, path, target=None):
        if fullname.split('.')[0] in self.roots:
            return importlib.machinery.ModuleSpec(fullname, self, is_package=True)
        return None

    def create_module(self, spec):
        module = _StubModule(spec.name)
        module.__path__ = []
        return module

    def exec_module(self, module):
        pass


# Dependências só usadas por funções que o CLI não chama (xlrd: abrir matrizes .xls).
OPTIONAL_MODULES = ('xlrd',)


def install_headless_wx():
    """O wx é sempre substituído; os módulos opcionais só quando não estão instalados."""
    import importlib.util
    roots = ['wx'] + [m for m in OPTIONAL_MODULES if importlib.util.find_spec(m) is None]
    sys.meta_path.insert(0, _StubFinder(roots))


# ---------------------------------------------------------------------------
# 2. Substituto da janela principal (o objeto `ira`)
# ---------------------------------------------------------------------------
class _NoHistory:
    def add(self, parametres):
        pass


class Headless:
    """Atributos de `IraFrame` lidos pelo corpus e pelas análises."""
    def __init__(self, rpath):
        from chemins import ConstructConfigPath, ConstructDicoPath, PathOut, RscriptsPath
        self.AppliPath = APPLI_PATH
        self.UserConfigPath = os.path.join(APPLI_PATH, 'configuration')
        self.ConfigPath = ConstructConfigPath(APPLI_PATH, user=False)
        self.DictPath = ConstructDicoPath(APPLI_PATH)
        self.RscriptsPath = PathOut(dirout=os.path.join(APPLI_PATH, 'Rscripts'))
        self.RscriptsPath.basefiles(RscriptsPath)
        self.pref = RawConfigParser()
        self.pref.read(self.ConfigPath['preferences'], encoding='utf8')
        self.RPath = rpath
        self.r_errors = []  # check_Rresult escreve em Rerror; BugReport apaga-o logo a seguir
        self.history = _NoHistory()
        self.lexique = {}
        self.expressions = {}
        self.TEMPDIR = tempfile.mkdtemp(prefix='iracli')  # usado por Stat

    @property
    def Rerror(self):
        return ''  # o BugReport acrescenta isto ao seu texto; o erro já ficou em r_errors

    @Rerror.setter
    def Rerror(self, value):
        if value:
            self.r_errors.append(value)

    def GetChildren(self):  # usado por BugReport
        return []



# ---------------------------------------------------------------------------
# 3. Corpus
# ---------------------------------------------------------------------------


def build_corpus(ira, infile, lang, outdir, dictionary=None, analyser=None):
    from functions import DoConf, ReadDicoAsDico, ReadLexique
    from chemins import PathOut
    from corpus import BuildFromAlceste

    parametres = DoConf(ira.ConfigPath['corpus']).getoptions('corpus')
    parametres['originalpath'] = os.path.abspath(infile)
    parametres['pathout'] = PathOut(infile, 'corpus', dirout=outdir).mkdirout()
    parametres['corpus_name'] = os.path.basename(parametres['pathout'])
    parametres['lang'] = lang
    PathOut().createdir(parametres['pathout'])

    if analyser is not None:
        from lemmatiseur import build_parsed_corpus
        corpus, ambiguous = build_parsed_corpus(infile, parametres, analyser)
        corpus.conn_all()
        summarize_ambiguities(analyser.name, ambiguous)
        return corpus

    ReadLexique(ira, lang=lang, filein=dictionary)
    exp_path = ira.DictPath.get(lang + '_exp')
    ira.expressions = ReadDicoAsDico(exp_path) if lang != 'other' and exp_path and os.path.exists(exp_path) else {}
    corpus = BuildFromAlceste(infile, parametres, ira.lexique, ira.expressions, dlg=None).corpus
    corpus.conn_all()  # na interface, isto acontece quando OpenAnalyse reabre o corpus
    return corpus


def summarize_ambiguities(name, ambiguous, show=8):
    print('  %s: %i formas com mais de uma leitura (lista completa em ambiguidades.csv)' % (name, len(ambiguous)))
    top = sorted(ambiguous, key=lambda k: -sum(ambiguous[k].values()))[:show]
    for form in top:
        print('    %-12s %s' % (form, ' · '.join('%s/%s (%i)' % (l, g, n) for (l, g), n in ambiguous[form].most_common())))


def modalities(corpus, spec):
    """'tema' → todas as modalidades de *tema; '*tema_mar,*tema_escola' → essas modalidades."""
    from functions import treat_var_mod
    etoiles = corpus.make_etoiles()
    variables = treat_var_mod(etoiles)
    if spec is None:
        if len(variables) != 1:
            raise SystemExit('Indique a variável com --spec-var (disponíveis: %s)' %
                             ', '.join(sorted(v.lstrip('*') for v in variables)))
        spec = next(iter(variables))
    if ',' in spec or '_' in spec:
        mods = ['*' + m.strip().lstrip('*') for m in spec.split(',')]
        unknown = [m for m in mods if m not in etoiles]
        if unknown:
            raise SystemExit('Modalidades inexistentes: %s' % ', '.join(unknown))
        return sorted(mods)
    key = '*' + spec.lstrip('*')
    if key not in variables:
        raise SystemExit('Variável inexistente: %s (disponíveis: %s)' % (
            spec, ', '.join(sorted(v.lstrip('*') for v in variables))))
    return sorted(variables[key])


# ---------------------------------------------------------------------------
# 4. Análises
# ---------------------------------------------------------------------------
# Cada função recebe (ira, corpus, args) e devolve o objeto da análise.
# As subclasses Cli* substituem apenas o passo que, na interface, depende de um diálogo.

def run_stat(ira, corpus, args):
    from textstat import Stat
    return Stat(ira, corpus, parametres={'type': 'stat', 'lem': lem_flag(args)}, dlg=False)


def run_chd(ira, corpus, args):
    from functions import DoConf
    from textreinert import Reinert
    parametres = DoConf(ira.ConfigPath['reinert']).getoptions('ALCESTE')
    parametres.update({
        'type': 'alceste',
        'lem': lem_flag(args),
        'nbcl_p1': args.chd_classes,
        'classif_mode': CHD_MODES[args.chd_mode],
        'mincl': args.chd_min_segments,
        'max_actives': args.chd_max_actives,
        'tailleuc1': args.chd_rst1,
        'tailleuc2': args.chd_rst2,
        'svdmethod': args.chd_svd,
        'mode.patate': False,
    })
    return Reinert(ira, corpus, parametres=parametres, dlg=False)


def run_spec(ira, corpus, args):
    from textaslexico import Lexico

    class CliLexico(Lexico):
        def doanalyse(self):
            self.listet = self.parametres.pop('_listet')  # na interface vem do diálogo OptLexi
            return super().doanalyse()

    listet = modalities(corpus, args.spec_var)
    parametres = {
        'type': 'spec',
        'lem': lem_flag(args),
        'mineff': args.spec_min_freq,
        'indice': args.spec_index,
        'typeformes': FORM_TYPES[args.spec_forms],
        'clnb': len(listet),
        '_listet': listet,
    }
    print('  modalidades: %s' % ', '.join(listet))
    return CliLexico(ira, corpus, parametres=parametres, dlg=False)


def run_simi(ira, corpus, args):
    from functions import indices_simi
    from textsimi import SimiTxt

    class CliSimiTxt(SimiTxt):
        def doanalyse(self):
            # com dlg=False a SimiTxt lê em parametres['selected'] os índices (por frequência) das formas a usar
            n = len(self.corpus.make_actives_limit(3))
            self.parametres['selected'] = list(range(min(args.simi_words, n)))
            return super().doanalyse()

    defaults = types.SimpleNamespace(parametres={})
    SimiTxt.makesimiparam(defaults)  # os mesmos valores por omissão que o diálogo da interface
    parametres = defaults.parametres
    parametres.update({
        'type': 'simitxt',
        'lem': lem_flag(args),
        'coeff': indices_simi.index(args.simi_index),
        'type_graph': SIMI_FORMATS[args.simi_format],
        'layout': SIMI_LAYOUTS[args.simi_layout],
        'arbremax': 0 if args.simi_no_tree else 1,
        'com': 1 if args.simi_communities else 0,                    # liga a deteção
        'communities': SIMI_COMMUNITIES.get(args.simi_communities, 0),  # algoritmo
        'halo': 1 if args.simi_communities else 0,
        'stars': [],
        'sfromchi': False,
        'svg': 1 if args.simi_svg else 0,
    })
    return CliSimiTxt(ira, corpus, parametres=parametres, dlg=False)


def run_nuvem(ira, corpus, args):
    from textwordcloud import WordCloud
    from PrintRScript import WordCloudRScript

    class CliWordCloud(WordCloud):
        def doanalyse(self):
            p = self.parametres
            mode = p['mode']
            self.actives = []
            if mode in (0, 2):
                self.actives += self.corpus.make_actives_limit(3, 1)
            if mode in (1, 2):
                self.actives += self.corpus.make_actives_limit(3, 2)
            # na interface: diálogos PrefWordCloud e SelectColumn (aqui, todas as formas selecionadas)
            with open(self.pathout['selected.csv'], 'w', encoding='utf8') as f:
                f.write('\n'.join(repr(i) for i in range(len(self.actives))))
            p['graphout'] = os.path.join(self.pathout.dirout, 'nuage_1' + ('.svg' if p['svg'] else '.png'))
            self.make_wordcloud()
            script = WordCloudRScript(self)
            script.make_script()
            if not self.doR(script.scriptout, message='R...'):
                return 'NOK'

    parametres = {
        'type': 'wordcloud',
        'lem': lem_flag(args),
        'mode': FORM_TYPES_CLOUD[args.nuvem_forms],
        'width': args.nuvem_size, 'height': args.nuvem_size,
        'maxword': args.nuvem_max_words,
        'mincex': 0.5, 'maxcex': 7.0,
        'col_text': (0, 0, 0), 'col_bg': (255, 255, 255),
        'svg': 1 if args.nuvem_svg else 0,
    }
    return CliWordCloud(ira, corpus, parametres=parametres, dlg=False)


def lem_flag(args):
    return 0 if args.no_lem else 1


CHD_MODES = {'double-rst': 0, 'simple-st': 1, 'simple-text': 2}
FORM_TYPES = {'todas': 0, 'ativas': 1, 'suplementares': 2}           # Lexico: 0 = ativas + suplementares
FORM_TYPES_CLOUD = {'ativas': 0, 'suplementares': 1, 'todas': 2}     # WordCloud: ordem diferente
SIMI_FORMATS = {'png': 1, 'gexf': 3}
SIMI_COMMUNITIES = {'edge-betweenness': 0, 'fastgreedy': 1, 'label-propagation': 2,
                    'leading-eigenvector': 3, 'multilevel': 4, 'optimal': 5, 'spinglass': 6,
                    'walktrap': 7}  # índices de Rscripts/simi.R
SIMI_LAYOUTS = {'random': 0, 'circle': 1, 'frutch': 2, 'kawa': 3, 'graphopt': 4}

ANALYSES = {
    # nome: (função, pacotes R, descrição)
    'stat':  (run_stat,  [],                                   'estatísticas e lei de Zipf'),
    'chd':   (run_chd,   ['Matrix', 'cluster', 'ape', 'ca'],   'classificação hierárquica descendente (Reinert)'),
    'spec':  (run_spec,  ['ca'],                               'especificidades e AFC por variável'),
    'simi':  (run_simi,  ['igraph', 'proxy', 'Matrix'],        'análise de similitude'),
    'nuvem': (run_nuvem, ['wordcloud'],                        'nuvem de palavras'),
}


def r_packages_for(args, analyses):
    pkgs = []
    for name in analyses:
        pkgs += ANALYSES[name][1]
    if 'chd' in analyses and args.chd_svd == 'irlba':
        pkgs.append('irlba')
    if 'spec' in analyses and args.spec_index == 'hypergeo':
        pkgs.append('textometry')
    if 'simi' in analyses and args.simi_layout == 'frutch':
        pkgs += ['sna', 'intergraph', 'network']  # simi.R: gplot.layout.fruchtermanreingold
    if 'simi' in analyses and args.simi_format == 'gexf':
        pkgs.append('rgexf')
    return sorted(set(pkgs))


def missing_r_packages(rpath, pkgs):
    import subprocess
    if not pkgs:
        return []
    rscript = os.path.join(os.path.dirname(rpath), 'Rscript')
    code = 'p <- c(%s); cat(p[!p %%in%% rownames(installed.packages())])' % ', '.join('"%s"' % p for p in pkgs)
    out = subprocess.run([rscript, '--vanilla', '-e', code], capture_output=True, text=True)
    return out.stdout.split()


# ---------------------------------------------------------------------------
# 5. Resumos
# ---------------------------------------------------------------------------
def summarize_corpus(corpus):
    print('  textos: %s · segmentos: %s · formas: %s · ocorrências: %s' % (
        corpus.getucinb(), corpus.getucenb(), len(corpus.formes), corpus.gettotocc()))


def summarize_chd(corpus, analyse):
    p = analyse.parametres
    print('  formas ativas usadas: %s (frequência ≥ %s)' % (p.get('nbactives'), p.get('eff_min_forme')))
    lc = getattr(corpus, 'lc', None) or []
    if not lc:
        return
    classified = sum(len(c) for c in lc)
    total = corpus.getucenb()
    print('  %i classes · %i/%i segmentos classificados (%.1f %%)' % (
        len(lc), classified, total, 100.0 * classified / total))
    for i, cl in enumerate(lc, 1):
        print('    classe %i: %5i segmentos (%.1f %%)' % (i, len(cl), 100.0 * len(cl) / classified))


# Ficheiro (padrão glob) que cada análise tem de deixar na sua pasta para ser considerada bem-sucedida.
EXPECTED_OUTPUT = {
    'stat': 'zipf.png',
    'chd': 'profiles.csv',
    'spec': 'tablespecf.csv',
    'simi': ['graph_simi_*.*', 'web_*/gexf.gexf'],
    'nuvem': 'nuage_*.*',
}


def analysis_problems(name, analyse, ira):
    """Lista de problemas: erros do R registados e/ou ficheiro de resultado em falta."""
    import glob
    problems = list(ira.r_errors)
    pathout = analyse.parametres.get('pathout', '')
    patterns = EXPECTED_OUTPUT[name]
    patterns = [patterns] if isinstance(patterns, str) else patterns
    if not any(glob.glob(os.path.join(pathout, pat)) for pat in patterns):
        problems.append('resultado em falta em %s: %s' % (pathout or '?', ' ou '.join(patterns)))
    return problems


# ---------------------------------------------------------------------------
# 6. Linha de comandos
# ---------------------------------------------------------------------------
import corpuslangs  # noqa: E402
from lemmaconf import DEFAULT_FREELING_DIR, freeling_lang, stanza_code, udpipe_default  # noqa: E402


def lang_key(value):
    """--lang: chave do IRaMuTeQ (french, galician…), código ISO (ca, ru, ast…) ou other."""
    if value == corpuslangs.OTHER or corpuslangs.get(value):
        return value
    for entry in corpuslangs.LANGS:
        if entry['iso'] == value:
            return entry['key']
    raise argparse.ArgumentTypeError('língua desconhecida: %s (ver corpuslangs_data.py)' % value)


def make_analyser(args, ap):
    """Analisador contextual pedido em --parser (None = dicionário da aplicação)."""
    from lemmatiseur import FreeLing, Stanza, Udpipe
    try:
        if args.parser == 'udpipe':
            model = args.udpipe_model or udpipe_default(args.lang)
            if not model:
                ap.error('indique o modelo com --udpipe-model (não há modelo por omissão para %s)' % args.lang)
            return Udpipe(model, rpath=args.rpath, download=True)   # descarrega o modelo se faltar
        if args.parser == 'freeling':
            lang = args.freeling_lang or freeling_lang(args.lang, args.freeling_dir)
            if not lang:
                ap.error('indique a língua do FreeLing com --freeling-lang')
            return FreeLing(lang, freeling_dir=args.freeling_dir, ner=not args.freeling_no_ner)
        if args.parser == 'stanza':
            lang = args.stanza_lang or stanza_code(args.lang)
            if not lang:
                ap.error('indique a língua do Stanza com --stanza-lang')
            return Stanza(lang, package=args.stanza_package)
    except FileNotFoundError as e:
        ap.error(str(e))
    return None


def build_parser():
    from_simi = ['cooccurrence', 'pourcentage de cooccurrence', 'Russel', 'Jaccard', 'Kulczynski1', 'Kulczynski2',
                 'Mountford', 'Fager', 'simple matching', 'Hamman', 'Faith', 'Tanimoto', 'Dice', 'Phi', 'Stiles',
                 'Michael', 'Mozley', 'Yule', 'Yule2', 'Ochiai', 'Simpson', 'Braun-Blanquet', 'Chi-squared',
                 'Phi-squared', 'Tschuprow', 'Cramer', 'Pearson', 'binomial']  # = functions.indices_simi
    ap = argparse.ArgumentParser(
        description='IRaMuTeQ sem interface: constrói o corpus uma vez e corre as análises pedidas.',
        epilog='Análises: ' + '; '.join('%s = %s' % (k, v[2]) for k, v in ANALYSES.items()))
    ap.add_argument('corpus', help='ficheiro de texto no formato IRaMuTeQ (**** *var_mod)')
    ap.add_argument('-a', '--analyses', default='chd',
                    help='lista separada por vírgulas: %s (omissão: chd)' % ','.join(ANALYSES))
    ap.add_argument('--lang', default='portuguese', type=lang_key, metavar='LÍNGUA',
                    help='língua do corpus: french, galician… ou código ISO (ca, ru, ast…), ou other '
                         '(omissão: portuguese). As línguas sem dicionário precisam de --parser')
    ap.add_argument('--dictionary', help='dicionário próprio (forma<TAB>lema<TAB>categoria)')
    ap.add_argument('--out', help='pasta onde criar os resultados (omissão: junto ao corpus)')
    ap.add_argument('--no-lem', action='store_true', help='não lematizar')
    ap.add_argument('--parser', default='dicionario', choices=['dicionario', 'udpipe', 'freeling', 'stanza'],
                    help='lematização: dicionario (omissão, a da aplicação), ou contextual com udpipe '
                    '(pacote R), FreeLing ou Stanza')
    ap.add_argument('--udpipe-model', help='modelo udpipe: nome (ex.: spanish-ancora, galician-ctg) procurado em '
                    '~/.iramuteq-udpipe e descarregado se faltar, ou caminho para um ficheiro .udpipe; '
                    'omissão: o modelo de --lang (ex.: french-gsd)')
    ap.add_argument('--freeling-lang', help='língua do FreeLing (gl, es, pt…); omissão: deduzida de --lang')
    ap.add_argument('--freeling-dir', default=DEFAULT_FREELING_DIR,
                    help='pasta de instalação do FreeLing (omissão: ~/.iramuteq-tools/freeling-4.2.1)')
    ap.add_argument('--stanza-lang', help='língua do Stanza (gl, es, pt…); omissão: deduzida de --lang')
    ap.add_argument('--stanza-package', help='modelo do Stanza (ex.: ctg, treegal); omissão: o padrão da língua')
    ap.add_argument('--freeling-no-ner', action='store_true',
                    help='não juntar nomes próprios compostos (ex.: Xosé_Luís_Barreiro)')
    ap.add_argument('--rpath', default=shutil.which('R'), help='executável R (omissão: R no PATH)')
    ap.add_argument('-v', '--verbose', action='store_true', help='mostrar o registo interno do IRaMuTeQ')

    g = ap.add_argument_group('chd (Reinert)')
    g.add_argument('--chd-classes', type=int, default=10, help='classes terminais da fase 1 (omissão: 10)')
    g.add_argument('--chd-mode', default='simple-st', choices=CHD_MODES, help='omissão: simple-st')
    g.add_argument('--chd-min-segments', type=int, default=0, help='mínimo de segmentos por classe (0 = automático)')
    g.add_argument('--chd-max-actives', type=int, default=20000, help='máximo de formas ativas')
    g.add_argument('--chd-rst1', type=int, default=12, help='tamanho dos RST1 (double-rst)')
    g.add_argument('--chd-rst2', type=int, default=14, help='tamanho dos RST2 (double-rst)')
    g.add_argument('--chd-svd', default='svdR', choices=['svdR', 'irlba'], help='irlba exige o pacote R')

    g = ap.add_argument_group('spec (especificidades e AFC)')
    g.add_argument('--spec-var', help='variável (ex.: tema) ou modalidades (ex.: tema_mar,tema_escola)')
    g.add_argument('--spec-index', default='chi2', choices=['chi2', 'hypergeo'],
                   help='chi2 (omissão) ou hypergeo (lei hipergeométrica; exige o pacote R textometry)')
    g.add_argument('--spec-min-freq', type=int, default=10, help='frequência mínima das formas (omissão: 10)')
    g.add_argument('--spec-forms', default='todas', choices=FORM_TYPES, help='omissão: todas')

    g = ap.add_argument_group('simi (similitude)')
    g.add_argument('--simi-words', type=int, default=100, help='número de formas mais frequentes (omissão: 100)')
    g.add_argument('--simi-index', default='cooccurrence', choices=from_simi, metavar='ÍNDICE',
                   help='índice de similitude (omissão: cooccurrence; também Jaccard, Ochiai, binomial, …)')
    g.add_argument('--simi-format', default='png', choices=SIMI_FORMATS, help='png (omissão) ou gexf (Gephi)')
    g.add_argument('--simi-layout', default='frutch', choices=SIMI_LAYOUTS, help='omissão: frutch (Fruchterman-Reingold)')
    g.add_argument('--simi-no-tree', action='store_true', help='não reduzir à árvore máxima')
    g.add_argument('--simi-communities', nargs='?', const='edge-betweenness', choices=SIMI_COMMUNITIES,
                   metavar='ALGORITMO', help='detetar e colorir comunidades, com halo (omissão do algoritmo: '
                   'edge-betweenness; ver a lista em --simi-communities x)')
    g.add_argument('--simi-svg', action='store_true', help='gráfico em SVG')

    g = ap.add_argument_group('nuvem (nuvem de palavras)')
    g.add_argument('--nuvem-forms', default='ativas', choices=FORM_TYPES_CLOUD, help='omissão: ativas')
    g.add_argument('--nuvem-max-words', type=int, default=600, help='omissão: 600')
    g.add_argument('--nuvem-size', type=int, default=800, help='largura e altura em píxeis (omissão: 800)')
    g.add_argument('--nuvem-svg', action='store_true', help='gráfico em SVG')
    return ap


def main(argv=None):
    ap = build_parser()
    args = ap.parse_args(argv)
    analyses = [a.strip() for a in args.analyses.split(',') if a.strip()]
    unknown = [a for a in analyses if a not in ANALYSES]
    if unknown:
        ap.error('análise desconhecida: %s (disponíveis: %s)' % (', '.join(unknown), ', '.join(ANALYSES)))

    logging.basicConfig(level=logging.INFO if args.verbose else logging.WARNING, format='%(name)s: %(message)s')
    if not args.rpath:
        ap.error('R não encontrado; indique-o com --rpath')
    if not os.path.isfile(args.corpus):
        ap.error('corpus não encontrado: %s' % args.corpus)
    if args.parser != 'dicionario' and args.dictionary:
        ap.error('--dictionary não se aplica com --parser %s' % args.parser)
    if args.parser == 'dicionario' and not args.dictionary and args.lang != corpuslangs.OTHER:
        from chemins import ConstructDicoPath
        if not corpuslangs.has_dictionary(args.lang, ConstructDicoPath(APPLI_PATH)):
            ap.error('o IRaMuTeQ não tem dicionário para %s: use --parser udpipe (ou freeling/stanza) '
                     'ou --dictionary' % corpuslangs.label(args.lang))
    pkgs = r_packages_for(args, analyses) + (['udpipe'] if args.parser == 'udpipe' else [])
    missing = missing_r_packages(args.rpath, pkgs)
    if missing:
        print('Faltam pacotes R para %s: %s\nInstale-os com:\n  Rscript -e \'install.packages(c(%s))\'' % (
            ', '.join(analyses), ', '.join(missing), ', '.join('"%s"' % p for p in missing)), file=sys.stderr)
        return 3
    outdir = os.path.abspath(args.out or os.path.dirname(os.path.abspath(args.corpus)))
    os.makedirs(outdir, exist_ok=True)

    install_headless_wx()
    sys.argv[0] = os.path.join(APPLI_PATH, 'iramuteq.py')  # langue.py deduz o AppliPath de argv[0]
    if APPLI_PATH not in sys.path:
        sys.path.insert(0, APPLI_PATH)

    ira = Headless(args.rpath)
    analyser = make_analyser(args, ap)
    print('== Corpus (%s)' % (args.lang if analyser is None else analyser.describe()['parser_model']))
    corpus = build_corpus(ira, args.corpus, args.lang, outdir, args.dictionary, analyser=analyser)
    summarize_corpus(corpus)
    print('  pasta:', corpus.parametres['pathout'])

    failed = []
    for name in analyses:
        print('\n== %s: %s' % (name, ANALYSES[name][2]))
        ira.r_errors.clear()
        analyse = ANALYSES[name][0](ira, corpus, args)
        problems = analysis_problems(name, analyse, ira)
        if problems:
            failed.append(name)
            print('  FALHOU', file=sys.stderr)
            for problem in problems:
                print('  ' + problem.strip().replace('\n', '\n  '), file=sys.stderr)
            continue
        if name == 'chd':
            summarize_chd(corpus, analyse)
        print('  resultados:', analyse.parametres['pathout'])

    if failed:
        print('\nAnálises com erro: %s' % ', '.join(failed), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
