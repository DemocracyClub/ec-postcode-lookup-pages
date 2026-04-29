RELATED_CONTENT = {
    "nia": {
        "en": (
            "Northern Ireland Assembly",
            "/voting-and-elections/how-elections-work/types-elections/northern-ireland-assembly",
        ),
        "cy": (
            "Cynulliad Gogledd Iwerddon",
            "/cy/pleidleisio-ac-etholiadau/sut-mae-etholiadaun-gweithio/am-beth-alla-i-bleidleisio/cynulliad-gogledd-iwerddon",
        ),
    },
    "senedd": {
        "en": (
            "Voting in Senedd elections",
            "/voting-and-elections/how-elections-work/types-elections/voting-senedd-elections",
        ),
        "cy": (
            "Pleidleisio yn Etholiadau'r Senedd",
            "/cy/pleidleisio-ac-etholiadau/sut-mae-etholiadaun-gweithio/am-beth-alla-i-bleidleisio/pleidleisio-yn-etholiadaur-senedd",
        ),
    },
    "sp": {
        "en": (
            "Scottish Parliament",
            "/voting-and-elections/how-elections-work/types-elections/scottish-parliament",
        ),
        "cy": (
            "Senedd yr Alban",
            "/cy/pleidleisio-ac-etholiadau/sut-mae-etholiadaun-gweithio/am-beth-alla-i-bleidleisio/senedd-yr-alban",
        ),
    },
    "pcc": {
        "en": (
            "Police and Crime Commissioners",
            "/voting-and-elections/how-elections-work/types-elections/police-and-crime-commissioners",
        ),
        "cy": (
            "Comisiynwyr yr Heddlu a Throseddu",
            "/cy/pleidleisio-ac-etholiadau/sut-mae-etholiadaun-gweithio/am-beth-alla-i-bleidleisio/comisiynwyr-yr-heddlu-a-throseddu",
        ),
    },
    "mayor": {
        "en": (
            "Mayoral elections",
            "/voting-and-elections/how-elections-work/types-elections/mayoral-elections",
        ),
        "cy": (
            "Etholiadau maerol",
            "/cy/pleidleisio-ac-etholiadau/sut-mae-etholiadaun-gweithio/am-beth-alla-i-bleidleisio/etholiadau-maerol",
        ),
    },
    "gla": {
        "en": (
            "Mayor of London and London Assembly",
            "/voting-and-elections/how-elections-work/types-elections/mayor-london-and-london-assembly",
        ),
        "cy": (
            "Maer Llundain a Chynulliad Llundain",
            "/cy/pleidleisio-ac-etholiadau/sut-mae-etholiadaun-gweithio/am-beth-alla-i-bleidleisio/maer-llundain-a-chynulliad-llundain",
        ),
    },
    "parl.by": {
        "en": (
            "UK parliamentary by-elections",
            "/voting-and-elections/how-elections-work/types-elections/uk-parliamentary-elections",
        ),
        "cy": (
            "Is-etholiadau Senedd y DU",
            "/cy/pleidleisio-ac-etholiadau/sut-mae-etholiadaun-gweithio/am-beth-alla-i-bleidleisio/etholiadau-senedd-y-du",
        ),
    },
    "parl": {
        "en": (
            "UK Parliament",
            "/voting-and-elections/how-elections-work/types-elections/uk-parliament",
        ),
        "cy": (
            "Senedd y DU",
            "/cy/pleidleisio-ac-etholiadau/sut-mae-etholiadaun-gweithio/am-beth-alla-i-bleidleisio/senedd-y-du",
        ),
    },
    "local.by": {
        "en": (
            "Local council by-elections",
            "/voting-and-elections/how-elections-work/types-elections/local-council-elections",
        ),
        "cy": (
            "Is-etholiadau cynghorau lleol",
            "/cy/pleidleisio-ac-etholiadau/sut-mae-etholiadaun-gweithio/am-beth-alla-i-bleidleisio/etholiadau-cynghorau-lleol",
        ),
    },
    "local": {
        "en": (
            "Local councils",
            "/voting-and-elections/how-elections-work/types-elections/local-councils",
        ),
        "cy": (
            "Cynghorau lleol",
            "/cy/pleidleisio-ac-etholiadau/sut-mae-etholiadaun-gweithio/am-beth-alla-i-bleidleisio/cynghorau-lleol",
        ),
    },
}


def get_content_key(ballot_id):
    id_parts = ballot_id.split(".")
    election_type = id_parts[0]
    org = id_parts[1]
    by_election = id_parts[-2] == "by"

    if election_type == "mayor" and org != "london":
        return "mayor"
    if (election_type == "mayor" and org == "london") or (
        election_type == "gla"
    ):
        return "gla"
    if by_election and election_type in ("parl", "local"):
        return f"{election_type}.by"
    return election_type


def get_related_content(dates, language):
    related_content = []
    seen_keys = set()

    """
    Add related for election types, limiting to a max of 2
    and avoiding duplicates.

    Ballots are already sorted by date and charisma
    so if there are upcoming elections of 3 or more types, we will
    drop the ones that are furthest in the future/least charismatic
    """
    for date in dates:
        for ballot in date.ballots:
            key = get_content_key(ballot.ballot_paper_id)
            if key in RELATED_CONTENT and key not in seen_keys:
                related_content.append(RELATED_CONTENT[key][language])
                seen_keys.add(key)

            if len(related_content) == 2:
                break

        if len(related_content) == 2:
            break

    # always show these links
    if language == "cy":
        related_content.append(
            (
                "Mathau o etholiadau",
                "/cy/pleidleisio-ac-etholiadau/sut-mae-etholiadaun-gweithio/mathau-o-etholiadau",
            )
        )
        related_content.append(
            (
                "Pleidleisio ac etholiadau",
                "/cy/pleidleisio-ac-etholiadau",
            )
        )
    else:
        # en
        related_content.append(
            (
                "Types of elections",
                "/voting-and-elections/how-elections-work/types-elections",
            )
        )
        related_content.append(
            (
                "Voting and elections",
                "/voting-and-elections",
            )
        )

    return related_content
