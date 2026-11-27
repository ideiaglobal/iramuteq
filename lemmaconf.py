# -*- coding: utf-8 -*-
"""Analisadores para a lematização contextual: onde estão, que línguas têm, qual escolher.

Sem dependências da interface nem do corpus: usado pelo diálogo de criação do corpus
(dialog.CorpusPref), pelo Builder (corpus.py) e pelo CLI (iracli.py). A anotação em si
está em lemmatiseur.py.

    udpipe   — pacote R udpipe; modelos UD de 3–24 MB descarregados na primeira utilização.
               Leve e universal: cobre todas as línguas do IRaMuTeQ (101 modelos, 66 línguas).
    FreeLing — programa C++ instalado à parte; o melhor para o galego; 13 línguas.
    Stanza   — Python + PyTorch num ambiente próprio; 100 línguas; o mais pesado.

As línguas (chave, ISO, modelos de cada analisador) estão em corpuslangs.py.
"""
import os
import subprocess

HOME = os.path.expanduser('~')
TOOLS_DIR = os.path.join(HOME, '.iramuteq-tools')
DEFAULT_FREELING_DIR = os.path.join(TOOLS_DIR, 'freeling-4.2.1')
UDPIPE_MODEL_DIR = os.path.join(HOME, '.iramuteq-udpipe')
STANZA_PYTHON = os.path.join(TOOLS_DIR, 'stanza-venv', 'bin', 'python')
STANZA_MODELS = os.path.join(TOOLS_DIR, 'stanza_resources')

ANALYSERS = ['udpipe', 'freeling', 'stanza']
LABELS = {'udpipe': 'udpipe', 'freeling': 'FreeLing', 'stanza': 'Stanza'}

import corpuslangs

# língua do IRaMuTeQ → código ISO (compatibilidade; o registo completo está em corpuslangs.py)
IRA_TO_ISO = dict((k, corpuslangs.iso(k)) for k in corpuslangs.OLD_KEYS)
IRA_TO_FREELING = IRA_TO_ISO   # compatibilidade com o nome antigo

# modelo udpipe (UD 2.5) por omissão para as línguas antigas do IRaMuTeQ; nas outras, o primeiro do registo
UDPIPE_DEFAULT = {'french': 'french-gsd', 'english': 'english-ewt', 'german': 'german-gsd',
                  'italian': 'italian-isdt', 'swedish': 'swedish-talbanken', 'portuguese': 'portuguese-bosque',
                  'spanish': 'spanish-ancora', 'greek': 'greek-gdt', 'galician': 'galician-ctg',
                  'dutch': 'dutch-alpino', 'norwegian': 'norwegian-bokmaal'}

# ordem de preferência por língua (a primeira disponível é a escolhida por omissão);
# para o galego, o FreeLing foi o melhor na avaliação (iramuteq-analise/avaliacao_gl/RESULTADOS.md)
PREFERENCE = {'galician': ['freeling', 'stanza', 'udpipe']}
DEFAULT_PREFERENCE = ['udpipe', 'freeling', 'stanza']


# ---------------------------------------------------------------------------
# FreeLing
# ---------------------------------------------------------------------------
def freeling_dir(pref=None):
    """Pasta do FreeLing: opção `freeling_path` das preferências (secção iramuteq) ou a pasta por omissão."""
    path = ''
    if pref is not None:
        try:
            path = pref.get('iramuteq', 'freeling_path').strip()
        except Exception:
            path = ''
    return os.path.expanduser(path) if path else DEFAULT_FREELING_DIR


def freeling_installed(path):
    return os.path.isfile(os.path.join(path, 'bin', 'analyze'))


def freeling_lang(ira_lang, path):
    """Código FreeLing para a língua do IRaMuTeQ, se essa língua estiver instalada; senão None.

    A instalação copia a configuração de todas as línguas (config/XX.cfg), mesmo quando só se
    compilaram os dados de algumas; por isso exige-se também a pasta de dados share/freeling/XX.
    """
    entry = corpuslangs.get(ira_lang)
    code = entry['freeling'] if entry else None
    share = os.path.join(path, 'share', 'freeling')
    if code and os.path.isfile(os.path.join(share, 'config', '%s.cfg' % code)) \
            and os.path.isdir(os.path.join(share, code)):
        return code
    return None


# ---------------------------------------------------------------------------
# udpipe
# ---------------------------------------------------------------------------
_r_udpipe_cache = {}


def r_has_udpipe(rpath):
    """O pacote R udpipe está instalado? (resultado guardado: a verificação chama o R)"""
    rscript = os.path.join(os.path.dirname(rpath), 'Rscript') if rpath else 'Rscript'
    if rscript not in _r_udpipe_cache:
        try:
            out = subprocess.run([rscript, '--vanilla', '-e', 'cat(requireNamespace("udpipe", quietly=TRUE))'],
                                 capture_output=True, text=True, timeout=60)
            _r_udpipe_cache[rscript] = out.stdout.strip().endswith('TRUE')
        except Exception:
            _r_udpipe_cache[rscript] = False
    return _r_udpipe_cache[rscript]


def udpipe_models(ira_lang):
    entry = corpuslangs.get(ira_lang)
    return list(entry['udpipe']) if entry else []


def udpipe_default(ira_lang):
    models = udpipe_models(ira_lang)
    default = UDPIPE_DEFAULT.get(ira_lang)
    return default if default in models else (models[0] if models else None)


def udpipe_model_file(model, model_dir=UDPIPE_MODEL_DIR):
    if os.path.isdir(model_dir):
        found = sorted(f for f in os.listdir(model_dir) if f.startswith(model + '-') and f.endswith('.udpipe'))
        if found:
            return os.path.join(model_dir, found[-1])
    return None


# ---------------------------------------------------------------------------
# Stanza
# ---------------------------------------------------------------------------
def stanza_installed(python=STANZA_PYTHON):
    return os.path.isfile(python)


def stanza_code(ira_lang):
    entry = corpuslangs.get(ira_lang)
    return entry['stanza'] if entry and entry['stanza'] else None


def stanza_lang(ira_lang, models=STANZA_MODELS):
    """Código Stanza da língua, se o lematizador e o etiquetador estiverem descarregados; senão None."""
    code = stanza_code(ira_lang)
    if code and os.path.isdir(os.path.join(models, code, 'lemma')) and os.path.isdir(os.path.join(models, code, 'pos')):
        return code
    return None


def _package_name(filename):
    name = filename[:-3] if filename.endswith('.pt') else filename
    for suffix in ('_nocharlm', '_charlm'):
        if name.endswith(suffix):
            return name[:-len(suffix)]
    return name


def stanza_packages(ira_lang, models=STANZA_MODELS):
    """(pacotes instalados, pacote por omissão do Stanza) para a língua."""
    code = stanza_lang(ira_lang, models)
    if code is None:
        return [], None
    found = sorted(set(_package_name(f) for f in os.listdir(os.path.join(models, code, 'lemma')) if f.endswith('.pt')))
    default = None
    try:
        import json
        with open(os.path.join(models, 'resources.json'), encoding='utf8') as f:
            default = _package_name(json.load(f)[code]['default_processors']['lemma'])
    except Exception:
        pass
    return found, (default if default in found else (found[0] if found else None))


# ---------------------------------------------------------------------------
# Estado de cada analisador para uma língua
# ---------------------------------------------------------------------------
def models(analyser, ira_lang):
    """(modelos ou pacotes entre os quais escolher, o de omissão) para a língua; ([], None) se não houver escolha."""
    if analyser == 'udpipe':
        return udpipe_models(ira_lang), udpipe_default(ira_lang)
    if analyser == 'stanza':
        return stanza_packages(ira_lang)
    return [], None


def status(analyser, ira_lang, pref=None, rpath=None, model=None):
    """(disponível, mensagem, argumento, parâmetros do corpus).

    A mensagem está em inglês, para o diálogo a traduzir com _(); o argumento (caminho, modelo…)
    acrescenta-se depois. Os parâmetros são os que o Builder precisa para criar o analisador.
    model escolhe o modelo udpipe ou o pacote Stanza (omissão: models(...)[1]).
    """
    if analyser == 'freeling':
        path = freeling_dir(pref)
        if not freeling_installed(path):
            return False, 'not installed', path, {}
        code = freeling_lang(ira_lang, path)
        if code is None:
            # o FreeLing 4.2.1 tem a língua, mas os dados dela não foram instalados (compilação com -DLANGUAGES)
            if 'freeling' in supported(ira_lang):
                return False, 'language not installed', path, {}
            return False, 'language not available', '', {}
        return True, '', '%s - %s' % (code, path), {'freeling_lang': code, 'freeling_path': path}
    if analyser == 'udpipe':
        available, default = models('udpipe', ira_lang)
        model = model if model in available else default
        if model is None:
            return False, 'language not available', '', {}
        if not r_has_udpipe(rpath):
            return False, 'R package udpipe not installed', '', {}
        if udpipe_model_file(model) is None:
            return True, 'model downloaded on first use', model, {'udpipe_model': model}
        return True, '', model, {'udpipe_model': model}
    if analyser == 'stanza':
        if not stanza_installed():
            return False, 'not installed', os.path.dirname(os.path.dirname(STANZA_PYTHON)), {}
        code = stanza_lang(ira_lang)
        if code is None:
            # a língua existe no Stanza, mas os modelos não foram descarregados
            return False, ('model not downloaded' if stanza_code(ira_lang) else 'language not available'), \
                (stanza_code(ira_lang) or ''), {}
        available, default = models('stanza', ira_lang)
        package = model if model in available else default
        return True, '', '%s/%s' % (code, package) if package else code, \
            {'stanza_lang': code, 'stanza_package': package or ''}
    return False, 'unknown', analyser, {}


def usable(ira_lang, pref=None, rpath=None):
    """Algum analisador serve esta língua nesta máquina?"""
    return any(status(a, ira_lang, pref, rpath)[0] for a in ANALYSERS)


def supported(ira_lang):
    """Analisadores que suportam a língua, instalados ou não (para a linha de estado do seletor)."""
    entry = corpuslangs.get(ira_lang)
    if entry is None:
        return []
    return [a for a in ANALYSERS if {'udpipe': entry['udpipe'], 'stanza': entry['stanza'], 'freeling': entry['freeling']}[a]]


def default_analyser(ira_lang, pref=None, rpath=None):
    """Primeiro analisador disponível na ordem de preferência da língua (ou None)."""
    for name in PREFERENCE.get(ira_lang, DEFAULT_PREFERENCE):
        if status(name, ira_lang, pref, rpath)[0]:
            return name
    return None


def make_analyser(parametres, rpath=None, progress=None):
    """Instancia o analisador descrito nos parâmetros do corpus (parser, freeling_lang, udpipe_model…).

    progress(event, detail) é chamado enquanto o analisador corre: event 'download' (detail = modelo
    udpipe a descarregar) ou 'annotate' (detail = nome do analisador)."""
    from lemmatiseur import FreeLing, Stanza, Udpipe
    parser = parametres.get('parser')
    if parser == 'freeling':
        analyser = FreeLing(parametres['freeling_lang'], freeling_dir=parametres.get('freeling_path', DEFAULT_FREELING_DIR))
    elif parser == 'udpipe':
        return Udpipe(parametres['udpipe_model'], rpath=rpath, download=True, progress=progress)
    elif parser == 'stanza':
        analyser = Stanza(parametres['stanza_lang'], package=parametres.get('stanza_package') or None)
    else:
        raise ValueError('analisador desconhecido: %s' % parser)
    analyser.progress = progress
    return analyser
