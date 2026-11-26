# -*- coding: utf-8 -*-
"""Analisadores para a lematização contextual: onde estão, que línguas têm, qual escolher.

Sem dependências da interface nem do corpus: usado pelo diálogo de criação do corpus
(dialog.CorpusPref), pelo Builder (corpus.py) e pelo CLI (iracli.py). A anotação em si
está em lemmatiseur.py.

    udpipe   — pacote R udpipe; modelos UD de 3–20 MB descarregados na primeira utilização.
               Leve e universal: cobre todas as línguas do IRaMuTeQ (101 modelos, ~65 línguas).
    FreeLing — programa C++ instalado à parte; o melhor para o galego; gl/es/pt/en/fr/it/…
    Stanza   — Python + PyTorch num ambiente próprio; ~70 línguas; o mais pesado.
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

# língua do IRaMuTeQ (dialog.langues) → código ISO usado pelo FreeLing e pelo Stanza
IRA_TO_ISO = {'galician': 'gl', 'spanish': 'es', 'portuguese': 'pt', 'english': 'en', 'french': 'fr',
              'italian': 'it', 'german': 'de', 'norwegian': 'nb', 'swedish': 'sv', 'greek': 'el', 'dutch': 'nl'}
IRA_TO_FREELING = IRA_TO_ISO   # compatibilidade com o nome antigo

# modelo udpipe (UD 2.5) por omissão para cada língua do IRaMuTeQ
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
    code = IRA_TO_ISO.get(ira_lang)
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


def stanza_lang(ira_lang, models=STANZA_MODELS):
    code = IRA_TO_ISO.get(ira_lang)
    if code and os.path.isdir(os.path.join(models, code, 'lemma')) and os.path.isdir(os.path.join(models, code, 'pos')):
        return code
    return None


# ---------------------------------------------------------------------------
# Estado de cada analisador para uma língua
# ---------------------------------------------------------------------------
def status(analyser, ira_lang, pref=None, rpath=None):
    """(disponível, mensagem, argumento, parâmetros do corpus).

    A mensagem está em inglês, para o diálogo a traduzir com _(); o argumento (caminho, modelo…)
    acrescenta-se depois. Os parâmetros são os que o Builder precisa para criar o analisador.
    """
    if analyser == 'freeling':
        path = freeling_dir(pref)
        if not freeling_installed(path):
            return False, 'not installed', path, {}
        code = freeling_lang(ira_lang, path)
        if code is None:
            return False, 'language not available', '', {}
        return True, '', '%s - %s' % (code, path), {'freeling_lang': code, 'freeling_path': path}
    if analyser == 'udpipe':
        model = UDPIPE_DEFAULT.get(ira_lang)
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
            return False, 'language not available', '', {}
        return True, '', code, {'stanza_lang': code}
    return False, 'unknown', analyser, {}


def default_analyser(ira_lang, pref=None, rpath=None):
    """Primeiro analisador disponível na ordem de preferência da língua (ou None)."""
    for name in PREFERENCE.get(ira_lang, DEFAULT_PREFERENCE):
        if status(name, ira_lang, pref, rpath)[0]:
            return name
    return None


def make_analyser(parametres, rpath=None):
    """Instancia o analisador descrito nos parâmetros do corpus (parser, freeling_lang, udpipe_model…)."""
    from lemmatiseur import FreeLing, Stanza, Udpipe
    parser = parametres.get('parser')
    if parser == 'freeling':
        return FreeLing(parametres['freeling_lang'], freeling_dir=parametres.get('freeling_path', DEFAULT_FREELING_DIR))
    if parser == 'udpipe':
        return Udpipe(parametres['udpipe_model'], rpath=rpath, download=True)
    if parser == 'stanza':
        return Stanza(parametres['stanza_lang'], package=parametres.get('stanza_package') or None)
    raise ValueError('analisador desconhecido: %s' % parser)
