#!/usr/bin/env python3
"""Met à jour la note et le nombre d'avis Google affichés dans index.html.
Lit l'API Places (nouvelle) avec la clé GOOGLE_PLACES_API_KEY. Ne modifie rien en cas de doute."""
import json, os, re, sys, urllib.request

PLACE_ID = 'ChIJsbRhELkYiGcRYlPw8QaCfw4'
PATH = os.path.join(os.path.dirname(__file__), '..', 'index.html')

def fetch():
    mock = os.environ.get('MOCK_PLACE_JSON')
    if mock:
        return json.loads(mock)
    key = os.environ.get('GOOGLE_PLACES_API_KEY')
    if not key:
        sys.exit('GOOGLE_PLACES_API_KEY manquante : aucune modification.')
    req = urllib.request.Request(
        f'https://places.googleapis.com/v1/places/{PLACE_ID}',
        headers={'X-Goog-Api-Key': key, 'X-Goog-FieldMask': 'rating,userRatingCount'})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)

d = fetch()
rating, count = d.get('rating'), d.get('userRatingCount')
if not isinstance(rating, (int, float)) or not isinstance(count, int) or not (1 <= rating <= 5) or count < 1:
    sys.exit(f'Réponse inattendue ({d}) : aucune modification.')

s = open(PATH, encoding='utf-8').read()
cur = re.search(r'(\d+) avis Google', s)
if not cur:
    sys.exit("Motif « N avis Google » introuvable : aucune modification.")
old = int(cur.group(1))
if count < old - 2:  # un nombre qui chute fortement est suspect
    sys.exit(f'Nombre en baisse suspecte ({old} -> {count}) : aucune modification.')

r_fr = f'{rating:.1f}'.replace('.', ',')
r_en = f'{rating:.1f}'
n = s
n = re.sub(r'\d+ avis Google', f'{count} avis Google', n)
n = re.sub(r'\d+ Google reviews', f'{count} Google reviews', n)
n = re.sub(r'(sur Google · )\d+( avis)', rf'\g<1>{count}\2', n)
n = re.sub(r'(on Google · )\d+( reviews)', rf'\g<1>{count}\2', n)
n = re.sub(r'<strong>\d,\d</strong>', f'<strong>{r_fr}</strong>', n)
n = re.sub(r'\d,\d sur Google', f'{r_fr} sur Google', n)
n = re.sub(r'\d\.\d on Google', f'{r_en} on Google', n)
if n == s:
    print(f'Déjà à jour : {r_fr} / {count} avis.')
else:
    open(PATH, 'w', encoding='utf-8').write(n)
    print(f'Mis à jour : {r_fr} / {count} avis (avant : {old}).')
