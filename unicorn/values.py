class SeasonStages:
    regular = 'regular'
    final1st = 'final1st'
    final3rd = 'final3rd'
    final5th = 'final5th'
    final7th = 'final7th'
    semifinal1 = 'semifinal1'
    semifinal2 = 'semifinal2'
    semifinal5th1 = 'semifinal5th1'
    semifinal5th2 = 'semifinal5th2'

    all_playoffs = (
        final1st,
        final3rd,
        final5th,
        final7th,
        semifinal1,
        semifinal2,
        semifinal5th1,
        semifinal5th2,
    )

    gm_season_stages = {
        'Semi Final 1': semifinal1,
        'Semi Final 2': semifinal2,
        'Semi Final 3': semifinal5th1,
        'Semi Final 4': semifinal5th2,
        'Final': final1st,
        '3rd/4th playoff': final3rd,
    }

    @classmethod
    def decode_gm_season_stage(cls, stage):
        return cls.gm_season_stages.get(stage, None)
