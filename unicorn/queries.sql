
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


-- Number of points scored

select t.id, t.name, hh.num_points + aa.num_points as total_points from
teams as t
join (
  select g.home_team_id, sum(g.home_team_points) as num_points from games as g
  group by g.home_team_id
) as hh on t.id = hh.home_team_id
join (
  select g.away_team_id, sum(g.away_team_points) as num_points from games as g
  group by g.away_team_id
) as aa on t.id = aa.away_team_id
group by t.id;
