#!/usr/bin/env python3
"""
build_kpis.py — Propage les KPIs Cegos sur tout le site fuzzy-formation.fr
Usage : python3 build_kpis.py
À lancer après chaque modification de kpis.json
"""

import json, re, os, glob
from datetime import date

BASE = os.path.dirname(os.path.abspath(__file__)) + '/'

# ── Charger les KPIs ──────────────────────────────────────────────────────────
with open(BASE + 'kpis.json') as f:
    K = json.load(f)

C = K['cegos']
SESSIONS    = C['sessions']
STAGIAIRES  = C['stagiaires']
REPONDANTS  = C['repondants']
EXPERTISE   = C['score_expertise']          # 98.5
UTILITE     = C['score_utilite_moyen']      # 87.2
ECHANGES    = C['score_echanges']           # 92.2
PERIODE     = C['periode']
MAJ         = K['_mise_a_jour']

def fmt(v):
    """98.5 → '98,5' / 87.2 → '87,2'"""
    return str(v).replace('.', ',')

# ── Substitutions à appliquer sur toutes les pages ──────────────────────────
# Chaque entrée : (pattern_regex, remplacement)
# On utilise des patterns assez précis pour ne pas casser le HTML autour

SUBS = [
    # Stagiaires
    (r'\b46\b(?=.*stagiaires|.*apprenants)', str(STAGIAIRES)),
    (r'\b51\b(?=.*stagiaires|.*apprenants)', str(STAGIAIRES)),  # déjà bon, idempotent
    # Expertise
    (r'98[,\.]2(?=/100.*[Ee]xpertise|.*[Ee]xpertise.*[Cc]egos)', fmt(EXPERTISE)),
    (r'98[,\.]5(?=/100.*[Ee]xpertise|.*[Ee]xpertise.*[Cc]egos)', fmt(EXPERTISE)),  # idempotent
    # Satisfaction / utilité globale
    (r'84[,\.]6(?=.*satisfaction|.*utilit)', fmt(UTILITE)),
    (r'87[,\.]2(?=.*satisfaction|.*utilit)', fmt(UTILITE)),  # idempotent
    # Sessions
    (r'\b5\b(?= sessions| session)', str(SESSIONS)),
    (r'\b6\b(?= sessions| session)', str(SESSIONS)),  # idempotent
]

def fix_kpis_in_html(content):
    """Applique les substitutions de chiffres dans le HTML."""
    # Stratégie : chercher les occurrences connues avec contexte
    replacements = [
        # ── Expertise ──
        ('98,2/100', f'{fmt(EXPERTISE)}/100'),
        ('98.2/100', f'{fmt(EXPERTISE)}/100'),
        ('>98,2<', f'>{fmt(EXPERTISE)}<'),
        ('>98.2<', f'>{fmt(EXPERTISE)}<'),
        # ── Satisfaction globale ──
        ('84,6', fmt(UTILITE)),
        ('84.6', fmt(UTILITE)),
        # ── Stagiaires ──
        ('>46<', f'>{STAGIAIRES}<'),
        ('46 stagiaires', f'{STAGIAIRES} stagiaires'),
        ('46 apprenants', f'{STAGIAIRES} apprenants'),
        # ── Sessions ──
        ('5 sessions', f'{SESSIONS} sessions'),
        ('5 session', f'{SESSIONS} session'),
        ('Moyenne sur 5 sessions', f'Moyenne sur {SESSIONS} sessions'),
        ('sur 5 sessions', f'sur {SESSIONS} sessions'),
        # ── Période ──
        ('Mars → Juin 2026', PERIODE.replace('–', ' → ')),
        ('Mars-Juin 2026', PERIODE.replace('–', '-')),
    ]
    for old, new in replacements:
        content = content.replace(old, new)
    return content

def fix_meta_description(content, fname):
    """Met à jour les meta description avec les bons chiffres."""
    # Pattern meta description
    def repl_meta(m):
        desc = m.group(1)
        desc = desc.replace('98,2', fmt(EXPERTISE)).replace('98.2', fmt(EXPERTISE))
        desc = desc.replace('84,6', fmt(UTILITE)).replace('84.6', fmt(UTILITE))
        desc = desc.replace('46 stagiaires', f'{STAGIAIRES} stagiaires')
        desc = desc.replace('46 apprenants', f'{STAGIAIRES} apprenants')
        return f'<meta name="description" content="{desc}">'
    content = re.sub(r'<meta name="description" content="([^"]*)">', repl_meta, content)
    return content

# ── Appliquer sur tous les fichiers HTML ─────────────────────────────────────
html_files = sorted(glob.glob(BASE + '*.html'))
count_changed = 0

for filepath in html_files:
    fname = os.path.basename(filepath)
    with open(filepath, 'r') as f:
        original = f.read()

    updated = fix_kpis_in_html(original)
    updated = fix_meta_description(updated, fname)

    if updated != original:
        with open(filepath, 'w') as f:
            f.write(updated)
        count_changed += 1
        print(f"  ✓ {fname}")

print(f"\n{count_changed} fichier(s) mis à jour")
print(f"\nKPIs propagés :")
print(f"  Sessions    : {SESSIONS}")
print(f"  Stagiaires  : {STAGIAIRES}")
print(f"  Répondants  : {REPONDANTS}")
print(f"  Expertise   : {fmt(EXPERTISE)}/100")
print(f"  Utilité moy.: {fmt(UTILITE)}/100")
print(f"  Échanges    : {fmt(ECHANGES)}/100")
print(f"  Période     : {PERIODE}")
print(f"  MAJ         : {MAJ}")
