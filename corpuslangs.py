# -*- coding: utf-8 -*-
"""Registo das línguas do corpus: dicionários do IRaMuTeQ + línguas dos analisadores.

A tabela fixa (nome, ISO, modelos udpipe, código Stanza/FreeLing) está em corpuslangs_data.py,
gerada por iramuteq-analise/linguas/gerar_registo.py. O que está instalado (dicionários,
FreeLing, Stanza, pacote R udpipe) vê-se em tempo de execução, em lemmaconf.status.

Chaves: as 11 línguas antigas mantêm o nome inglês ('french', 'galician'…), para os .cira e as
preferências antigas continuarem a funcionar; as novas usam o código ISO ('ca', 'ru', 'ast').
A chave 'other' é a língua sem lematização.
"""
from corpuslangs_data import LANGS

OTHER = 'other'
BY_KEY = dict((l['key'], l) for l in LANGS)
# as 11 línguas do seletor antigo, pela ordem antiga (iracli e compatibilidade)
OLD_KEYS = ['french', 'english', 'german', 'italian', 'swedish', 'portuguese', 'spanish', 'greek',
            'galician', 'dutch', 'norwegian']


def get(key):
    """Entrada da língua (dicionário) ou None; 'other' e chaves desconhecidas dão None."""
    return BY_KEY.get(key)


def iso(key):
    entry = BY_KEY.get(key)
    return entry['iso'] if entry else None


def label(key, other_label='other'):
    """Texto do seletor: "Galego (gl)"; para 'other', o texto dado (já traduzido)."""
    entry = BY_KEY.get(key)
    if entry is None:
        return other_label if key == OTHER else key
    return '%s (%s)' % (entry['name'], entry['iso'])


def has_dictionary(key, dictpath):
    import os
    path = dictpath.get(key) if dictpath else None
    return bool(path) and os.path.isfile(path)


def has_expressions(key, dictpath):
    import os
    path = dictpath.get(key + '_exp') if dictpath else None
    return bool(path) and os.path.isfile(path)


def sort_key(entry):
    return entry['name'].casefold()


def choices(dictpath, usable, show_all=False):
    """Chaves para o seletor: primeiro as que têm dicionário, depois as outras, e no fim 'other'.

    usable(key) diz se algum analisador serve a língua nesta máquina; com show_all=True entram
    também as línguas que só teriam analisador se ele fosse instalado.
    """
    with_dict = sorted((l for l in LANGS if has_dictionary(l['key'], dictpath)), key=sort_key)
    rest = [l for l in LANGS if not has_dictionary(l['key'], dictpath)]
    if not show_all:
        rest = [l for l in rest if usable(l['key'])]
    rest.sort(key=sort_key)
    return [l['key'] for l in with_dict] + [l['key'] for l in rest] + [OTHER]
