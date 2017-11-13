
-- Number of home and away games

select t.id, t.name, hh.num_games, aa.num_games from
teams as t
join (
  select g.home_team_id, count(*) as num_games from games as g
  group by g.home_team_id
) as hh on t.id = hh.home_team_id
join (
  select g.away_team_id, count(*) as num_games from games as g
  group by g.away_team_id
) as aa on t.id = aa.away_team_id
group by t.id;

