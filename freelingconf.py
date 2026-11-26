# -*- coding: utf-8 -*-
"""Localização do FreeLing e línguas disponíveis (sem dependências da interface nem do corpus).

Usado pelo diálogo de criação do corpus (dialog.CorpusPref), pelo Builder (corpus.py) e pelo CLI.
"""
import os

DEFAULT_FREELING_DIR = os.path.join(os.path.expanduser('~'), '.iramuteq-tools', 'freeling-4.2.1')

# línguas do IRaMuTeQ (dialog.langues) → código de configuração do FreeLing (share/freeling/config/XX.cfg)
IRA_TO_FREELING = {'galician': 'gl', 'spanish': 'es', 'portuguese': 'pt', 'english': 'en', 'french': 'fr',
                   'italian': 'it', 'german': 'de', 'norwegian': 'nb'}


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
    code = IRA_TO_FREELING.get(ira_lang)
    share = os.path.join(path, 'share', 'freeling')
    if code and os.path.isfile(os.path.join(share, 'config', '%s.cfg' % code)) \
            and os.path.isdir(os.path.join(share, code)):
        return code
    return None
