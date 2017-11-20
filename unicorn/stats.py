from unicorn.core.utils import cached_property
from unicorn.values import GameOutcomes


class InvalidMetricName(Exception):
    pass


class FranchiseHead2HeadStats:
    metrics = {
        'won': lambda gs: 1 if GameOutcomes.was_won(gs.outcome) else 0,
        'drawn': lambda gs: 1 if GameOutcomes.was_drawn(gs.outcome) else 0,
        'lost': lambda gs: 1 if GameOutcomes.was_lost(gs.outcome) else 0,
        'score_for': lambda gs: gs.score,
        'score_against': lambda gs: gs.opponent.score,
        'score_difference': lambda gs: gs.score - gs.opponent.score,
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
    def games_reversed(self):
        return reversed(self.games)

    @property
    def total_played(self):
        return len(self.games)

    @property
    def total_win_percentage(self):
        return 100.0 * self.total_won_sum / self.total_played

    def __getattr__(self, item):
        # prefixes = ('total', 'regular', 'finals')
        # suffixes = ('sum', 'avg',)

        if '_' not in item:
            raise InvalidMetricName(item)

        prefix, rest = item.split('_', 1)

        if '_' not in rest:
            raise InvalidMetricName(item)

        metric_name, suffix = rest.rsplit('_', 1)

        if prefix != 'total':
            # Others not supported yet
            raise InvalidMetricName(item)

        games = self.games
        metric_sum = sum(self.metrics[metric_name](gs) for gs in games)

        num_games = len(games)

        if suffix == 'sum':
            return metric_sum
        elif suffix == 'avg':
            return 1.0 * metric_sum / num_games
        else:
            raise InvalidMetricName(item)

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
