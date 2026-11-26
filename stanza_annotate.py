#!/usr/bin/env python3
"""Anota textos com o Stanza. Corre no ambiente Python onde o Stanza está instalado.

Entrada (stdin): JSON {"lang": "gl", "model_dir": "...", "package": "default", "texts": ["...", ...]}
Saída (stdout):  JSON [[[forma, lema, upos, traços], ...], ...]  — uma lista de palavras por texto.

As contrações (gl "do" = de + o) saem já divididas nas palavras sintáticas (processador mwt).
"""
import json
import sys


def main():
    req = json.load(sys.stdin)
    import stanza
    from stanza.models.common.doc import Document  # noqa: F401  (garante que o Stanza está completo)

    kwargs = dict(lang=req['lang'], processors='tokenize,mwt,pos,lemma', verbose=False,
                  download_method=None, use_gpu=False)
    if req.get('model_dir'):
        kwargs['dir'] = req['model_dir']
    if req.get('package'):
        kwargs['package'] = req['package']
    nlp = stanza.Pipeline(**kwargs)
    docs = nlp.bulk_process([t if t.strip() else '.' for t in req['texts']])
    out = []
    for doc in docs:
        words = []
        for sent in doc.sentences:
            for w in sent.words:
                words.append([w.text, w.lemma or w.text, w.upos or 'X', w.feats or ''])
        out.append(words)
    json.dump(out, sys.stdout, ensure_ascii=False)


if __name__ == '__main__':
    sys.exit(main())
