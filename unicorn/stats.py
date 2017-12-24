from cached_property import cached_property

from unicorn.values import GameOutcomes, SeasonStages


class InvalidMetricName(Exception):
    pass


class FranchiseHead2HeadStats:
    metrics = {
        'played': lambda gs: 1,
        'won': lambda gs: 1 if GameOutcomes.was_won(gs.outcome) else 0,
        'drawn': lambda gs: 1 if GameOutcomes.was_drawn(gs.outcome) else 0,
        'lost': lambda gs: 1 if GameOutcomes.was_lost(gs.outcome) else 0,
        'score_for': lambda gs: gs.score,
        'score_against': lambda gs: gs.opponent.score,
        'score_difference': lambda gs: gs.score - gs.opponent.score if gs.score is not None and gs.opponent.score is not None else None,
    }

    def __init__(self, us, them):
        self.us = us
        self.them = them

    @property
    def franchise(self):
        return self.them

    @cached_property
    def games(self):
        all = []
        for t in self.us.teams:
            for gs in t.games:
                if gs.opponent.team.franchise_id == self.them.id:
                    all.append(gs)
        return all

    @property
    def total_games(self):
        return self.games

    @property
    def regular_games(self):
        return [gs for gs in self.games if SeasonStages.is_regular(gs.game.season_stage)]

    @property
    def finals_games(self):
        return [gs for gs in self.games if SeasonStages.is_finals(gs.game.season_stage)]

    @property
    def total_win_percentage(self):
        return 100.0 * self.total_won_sum / self.total_played_sum

    @property
    def regular_win_percentage(self):
        return 100.0 * self.regular_won_sum / self.regular_played_sum

    @property
    def finals_win_percentage(self):
        return 100.0 * self.finals_won_sum / self.finals_played_sum

    def __getattr__(self, item):
        # prefixes = ('total', 'regular', 'finals')
        # suffixes = ('sum', 'avg',)

        if '_' not in item:
            raise InvalidMetricName(item)

        prefix, rest = item.split('_', 1)

        if '_' not in rest:
            raise InvalidMetricName(item)

        metric_name, suffix = rest.rsplit('_', 1)

        games = getattr(self, '{}_games'.format(prefix))

        all_items = [self.metrics[metric_name](gs) for gs in games]
        valid_items = [m for m in all_items if m is not None]
        metric_sum = sum(valid_items)
        num_games = len(valid_items)

        if suffix == 'sum':
            return metric_sum
        elif suffix == 'avg':
            return 1.0 * metric_sum / num_games
        else:
            raise InvalidMetricName(item)

    @property
    def games_reversed(self):
        return reversed(self.games)

    @property
    def streak(self):
        streak_outcome = None
        streak_length = 0

        for gs in reversed(self.games):
            outcome = GameOutcomes.normalize(gs.outcome)
            if outcome == GameOutcomes.missing:
                continue
            if streak_outcome is None:
                streak_outcome = outcome
                streak_length += 1
            elif streak_outcome == outcome:
                streak_length += 1
            else:
                break

        if streak_length == 0:
            return ''
        elif streak_outcome == GameOutcomes.won:
            return 'Won {}'.format(streak_length)
        elif streak_outcome == GameOutcomes.lost:
            return 'Lost {}'.format(streak_length)
        else:
            return 'Drawn {}'.format(streak_length)
