# Party colors and other constants.
party_colors = {
    'SPD': '#e4454f',  # '#e3000f',
    'CDU/CSU': '#454545',  # '#000000',
    'Grüne': '#76ae63',  # '#46962b',
    'FDP': '#f8eb45',  # '#ffed00',
    'AfD': '#45b4e2',  # '#009ee0',
    'Linke': '#ca6697',  # '#be3075',
    'Sonstige': '#9f9f9f',  # '#808080',
    'BSW': '#8e5973',  # '#691d42',
    'Kein Parteiaccount': '#d4c5aa'
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
    'Kein Parteiaccount'
]


def extract_video_id(url):
    try:
        return int(url.strip('/').split('/')[-1])
    except Exception:
        return None
