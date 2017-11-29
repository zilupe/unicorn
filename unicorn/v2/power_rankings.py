from unicorn.app import run_in_app_context
from unicorn.core.apps import current_app
from unicorn.values import SeasonStages


class RatingValue:
    def __init__(self, value, game=None, change=0):
        self.value = value
        self.game = game
        self.change = change

    def __lt__(self, other):
        return self.value < other.value

    @property
    def int_value(self):
        return int(self.value)

    @property
    def change_int_value(self):
        return int(self.change)


class FranchiseRating:
    def __init__(self, *, franchise, current, best_rating, worst_rating, best_game, worst_game):
        self.franchise = franchise
        self.current = current
        self.best_rating = best_rating
        self.worst_rating = worst_rating
        self.best_game = best_game
        self.worst_game = worst_game

    @property
    def sort_key(self):
        return (
            1 if self.franchise.status == 'active' else 0,
            self.current,
        )


class PowerRankings:
    initial_rating = 1000.0

    game_value = {
        SeasonStages.final1st: 0.08,
        SeasonStages.semifinal1: 0.07,
        SeasonStages.semifinal2: 0.07,
        SeasonStages.final3rd: 0.06,
        SeasonStages.regular: 0.05,
    }

    game_value_others = 0.04  # no one seems to care about other games

    def __init__(self, franchises=None, games=None):
        if franchises is None:
            franchises = self._get_all_franchises()

        if games is None:
            games = self._get_all_games()

        self.franchises = list(franchises)
        self.games = list(games)
        self.current = {f.id: RatingValue(value=self.initial_rating) for f in self.franchises}

        self.best_rating = {f.id: RatingValue(value=self.initial_rating) for f in self.franchises}
        self.worst_rating = {f.id: RatingValue(self.initial_rating) for f in self.franchises}

        self.best_game = {f.id: None for f in self.franchises}
        self.worst_game = {f.id: None for f in self.franchises}

    @staticmethod
    def _get_all_franchises():
        return list(current_app.franchises.values())

    @staticmethod
    def _get_all_games():
        for season in current_app.seasons.values():
            yield from season.games

    def update_current(self, franchise_id, change, game=None):
        self.current[franchise_id] = RatingValue(
            value=self.current[franchise_id].value + change,
            game=game,
            change=change,
        )

    def advance(self):
        for g in self.games:
            game_value_ratio = self.game_value.get(g.season_stage, self.game_value_others)

            underdog_side, favourite_side = sorted(g.sides, key=lambda gs: self.current[gs.team.franchise_id])
            underdog_franchise_id = underdog_side.team.franchise_id
            favourite_franchise_id = favourite_side.team.franchise_id

            if g.winner_side is favourite_side and favourite_side.is_won:
                game_value = game_value_ratio * self.current[underdog_franchise_id].value
                self.update_current(favourite_franchise_id, +game_value, g)
                self.update_current(underdog_franchise_id, -game_value, g)
            elif g.winner_side is underdog_side and underdog_side.is_won:
                game_value = game_value_ratio * self.current[favourite_franchise_id].value
                self.update_current(favourite_franchise_id, -game_value, g)
                self.update_current(underdog_franchise_id, +game_value, g)
            else:
                assert g.winner_side.is_drawn
                game_value = game_value_ratio * (
                    self.current[favourite_franchise_id].value - self.current[underdog_franchise_id].value
                )
                self.update_current(favourite_franchise_id, -game_value, g)
                self.update_current(underdog_franchise_id, +game_value, g)

            assert game_value >= 0

            # Register best/worst ever ratings
            for franchise_id in (favourite_franchise_id, underdog_franchise_id):
                if self.current[franchise_id] > self.best_rating[franchise_id]:
                    self.best_rating[franchise_id] = self.current[franchise_id]
                elif self.current[franchise_id] < self.worst_rating[franchise_id]:
                    self.worst_rating[franchise_id] = self.current[franchise_id]

                if self.best_game[franchise_id] is None or self.current[franchise_id].change > self.best_game[franchise_id].change:
                    # TODO Should not register ones where the team still loses
                    self.best_game[franchise_id] = self.current[franchise_id]
                elif self.worst_game[franchise_id] is None or self.current[franchise_id].change < self.worst_game[franchise_id].change:
                    self.worst_game[franchise_id] = self.current[franchise_id]

            yield g, self.current

    def calculate(self):
        for _ in self.advance():
            pass

    def __iter__(self):
        franchises = {f.id: f for f in self.franchises}
        all = []
        for franchise_id, ranking in self.current.items():
            all.append(FranchiseRating(
                franchise=franchises[franchise_id],
                current=ranking,
                best_rating=self.best_rating[franchise_id],
                worst_rating=self.worst_rating[franchise_id],
                best_game=self.best_game[franchise_id],
                worst_game=self.worst_game[franchise_id],
            ))

        for i, pr in enumerate(sorted(all, key=lambda pr: pr.sort_key, reverse=True)):
            yield i + 1, pr


def main():
    rankings = PowerRankings()
    for i, (game, current) in enumerate(rankings.advance()):
        print(i, current)


if __name__ == '__main__':
    run_in_app_context(main)()
