# Party colors and other constants.
party_colors = {
    'SPD': '#e3000f',
    'CDU/CSU': '#000000',
    'Grüne': '#46962b',
    'FDP': '#ffed00',
    'AfD': '#009ee0',
    'Linke': '#be3075',
    'Sonstige': '#808080',
    'BSW': '#691d42',
    'Kein offizieller Parteiaccount': '#8B4513'  # Brown color
}

candidate_parties = [
    'SPD',
    'CDU/CSU',
    'Grüne',
    'FDP',
    'AfD',
    'Linke',
    'Sonstige'
]
parties_order = [
    'SPD',
    'CDU/CSU',
    'Grüne',
    'FDP',
    'AfD',
    'Linke',
    'BSW',
    'Sonstige',
    'Kein offizieller Parteiaccount'
]


def extract_video_id(url):
    try:
        return int(url.strip('/').split('/')[-1])
    except Exception:
        return None
