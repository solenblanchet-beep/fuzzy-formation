#!/usr/bin/env python3
"""
build_kpis.py — Propage les KPIs Cegos sur tout le site fuzzy-formation.fr
Usage : python3 build_kpis.py
À lancer après chaque modification de kpis.json
"""
import json, re, os, glob

BASE = os.path.dirname(os.path.abspath(__file__)) + '/'

with open(BASE + 'kpis.json') as f:
    K = json.load(f)

C = K['cegos']
SESSIONS   = C['sessions']
STAGIAIRES = C['stagiaires']
REPONDANTS = C['repondants']
EXPERTISE  = C['score_expertise']
UTILITE    = C['score_utilite_moyen']
ECHANGES   = C['score_echanges']
VARIETE    = C['score_variete']
OBJECTIFS  = C['score_objectifs']
PERIODE    = C['periode']
MAJ        = K['_mise_a_jour']

def fmt(v):
    return str(v).replace('.', ',')

# Toutes les valeurs connues (passées et présentes) à remplacer
EXPERTISE_VALS = ['98,2', '98.2', '98,5', '98.5', '98,0', '98.0']
UTILITE_VALS   = ['84,6', '84.6', '87,2', '87.2', '87,6', '87.6']
STAGIAIRES_VALS = ['46', '51', '61']
SESSIONS_VALS   = ['5', '6', '7']

def fix_html(content):
    # Expertise /100
    for v in EXPERTISE_VALS:
        content = content.replace(f'{v}/100', f'{fmt(EXPERTISE)}/100')
        content = content.replace(f'>{v}<', f'>{fmt(EXPERTISE)}<')
    # Satisfaction / utilité
    for v in UTILITE_VALS:
        content = content.replace(v, fmt(UTILITE))
    # Stagiaires (contexte)
    for v in STAGIAIRES_VALS:
        content = content.replace(f'{v} stagiaires', f'{STAGIAIRES} stagiaires')
        content = content.replace(f'{v} apprenants', f'{STAGIAIRES} apprenants')
        content = content.replace(f'>{v}<\n          <div class="hstat-label">stagiaires',
                                  f'>{STAGIAIRES}<\n          <div class="hstat-label">stagiaires')
        content = content.replace(f'>{v}<\n          <div class="score-small-label">Stagiaires',
                                  f'>{STAGIAIRES}<\n          <div class="score-small-label">Stagiaires')
        content = content.replace(f'>{v}<\n      <div style="font-size:0.72rem;color:rgba(255,255,255,0.4);">Apprenants',
                                  f'>{STAGIAIRES}<\n      <div style="font-size:0.72rem;color:rgba(255,255,255,0.4);">Apprenants')
    # Sessions
    for v in SESSIONS_VALS:
        content = content.replace(f'{v} sessions', f'{SESSIONS} sessions')
        content = content.replace(f'{v} session', f'{SESSIONS} session')
        content = content.replace(f'Moyenne sur {v} sessions', f'Moyenne sur {SESSIONS} sessions')
        content = content.replace(f'>{v}<\n          <div class="hstat-label">sessions',
                                  f'>{SESSIONS}<\n          <div class="hstat-label">sessions')
        content = content.replace(f'>{v}<\n          <div class="score-small-label">Sessions',
                                  f'>{SESSIONS}<\n          <div class="score-small-label">Sessions')
        content = content.replace(f'>{v}<\n      <div style="font-size:0.72rem;color:rgba(255,255,255,0.4);">Sessions',
                                  f'>{SESSIONS}<\n      <div style="font-size:0.72rem;color:rgba(255,255,255,0.4);">Sessions')
    # Période
    content = content.replace('Mars–Juin 2026', PERIODE)
    content = content.replace('Mars → Juin 2026', PERIODE.replace('–', ' → '))
    content = content.replace('Mars-Juin 2026', PERIODE.replace('–', '-'))
    # Répondants dans footer stats
    content = content.replace('51 stagiaires · Mars', f'{STAGIAIRES} stagiaires · Mars')
    content = content.replace('46 stagiaires · Mars', f'{STAGIAIRES} stagiaires · Mars')
    return content

def fix_meta(content):
    def repl(m):
        d = m.group(1)
        for v in EXPERTISE_VALS:
            d = d.replace(v, fmt(EXPERTISE))
        for v in UTILITE_VALS:
            d = d.replace(v, fmt(UTILITE))
        for v in STAGIAIRES_VALS:
            d = d.replace(f'{v} stagiaires', f'{STAGIAIRES} stagiaires')
            d = d.replace(f'{v} apprenants', f'{STAGIAIRES} apprenants')
        return f'<meta name="description" content="{d}">'
    return re.sub(r'<meta name="description" content="([^"]*)">', repl, content)

count = 0
for fp in sorted(glob.glob(BASE + '*.html')):
    with open(fp) as f:
        orig = f.read()
    updated = fix_meta(fix_html(orig))
    if updated != orig:
        with open(fp, 'w') as f:
            f.write(updated)
        count += 1
        print(f"  ✓ {os.path.basename(fp)}")

print(f"\n{count} fichier(s) mis à jour")
print(f"\nKPIs actifs :")
print(f"  Sessions   : {SESSIONS} ({PERIODE})")
print(f"  Stagiaires : {STAGIAIRES} · Répondants : {REPONDANTS}")
print(f"  Expertise  : {fmt(EXPERTISE)}/100")
print(f"  Utilité    : {fmt(UTILITE)}/100")
print(f"  Échanges   : {fmt(ECHANGES)}/100")
print(f"  Mise à jour: {MAJ}")
