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

    all_stages = all_playoffs + (regular,)

    gm_season_stages = {
        'Semi Final 1': semifinal1,
        'Semi Final 2': semifinal2,
        'Semi Final 3': semifinal5th1,
        'Semi Final 4': semifinal5th2,

        'Final': final1st,
        'Finals': final1st,
        'Grand Final': final1st,

        '3rd/4th playoff': final3rd,
        '3rd Place Playoff': final3rd,
        '3rd Place Final': final3rd,
        'Third Place Final': final3rd,

        'Fifth Place Playoff': final5th,
        '5th Place Playoff': final5th,
        '5th/6th playoff': final5th,
        '5th Place Final': final5th,

        '7th Place Final': final7th,
        '7th/8th playoff': final7th,
        '7th Place Play Offs': final7th,
    }

    @classmethod
    def decode_gm_season_stage(cls, stage):
        return cls.gm_season_stages.get(stage, None)

    @classmethod
    def is_regular(cls, stage):
        return stage == cls.regular

    @classmethod
    def is_finals(cls, stage):
        return stage != cls.regular


class GameOutcomes:
    won = 'W'
    lost = 'L'
    drawn = 'D'
    forfeit_for = 'FF'
    forfeit_against = 'FA'
    missing = 'M'

    regular_season_points = {
        won: 3,
        lost: 1,
        drawn: 2,
        forfeit_for: 3,
        forfeit_against: 1,
        missing: None,
    }

    to_simple = {
        won: won,
        lost: lost,
        drawn: drawn,
        forfeit_for: won,
        forfeit_against: lost,
        missing: missing,
    }

    decided = (
        won, lost, drawn, forfeit_for, forfeit_against
    )

    @classmethod
    def from_scores(cls, home, away):
        if (home, away) == (20, 0):
            return GameOutcomes.forfeit_for, GameOutcomes.forfeit_against
        elif (home, away) == (0, 20):
            return GameOutcomes.forfeit_against, GameOutcomes.forfeit_for
        elif home == away:
            return GameOutcomes.drawn, GameOutcomes.drawn
        elif home > away:
            return GameOutcomes.won, GameOutcomes.lost
        elif home < away:
            return GameOutcomes.lost, GameOutcomes.won
        else:
            raise RuntimeError('Could not work out game outcome from {} - {}'.format(home, away))

    @classmethod
    def get_points_for(cls, outcome, season_stage):
        assert season_stage in SeasonStages.all_stages
        if season_stage != SeasonStages.regular:
            return 0
        else:
            return cls.regular_season_points[outcome]

    @classmethod
    def was_won(cls, outcome):
        return outcome in (cls.won, cls.forfeit_for)

    @classmethod
    def was_drawn(cls, outcome):
        return outcome in (cls.drawn,)

    @classmethod
    def was_lost(cls, outcome):
        return outcome in (cls.lost, cls.forfeit_against)

    @classmethod
    def normalize(cls, outcome):
        if cls.was_won(outcome):
            return GameOutcomes.won
        elif cls.was_lost(outcome):
            return GameOutcomes.lost
        else:
            return outcome


class ScoreStatuses:
    undecided = 0
    winner_and_score_ok = 1
    winner_ok_score_probable = 2
    winner_ok_score_fake = 3
    winner_probable_score_fake = 4
    unknown = 5
