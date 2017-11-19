
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



select * from teams where season_id = 105 order by regular_rank;

select * from seasons order by first_week_date asc;

select * from games where home_team_score is null or away_team_score is null;

select f.id, f.name, s.id, s.name, s.first_week_date, s.last_week_date, t.name
from franchises as f
left join teams as t on f.id = t.franchise_id
left join seasons as s on t.season_id = s.id
order by f.id asc, s.first_week_date asc;

select f.id, f.name, count(*) from franchises as f
left join teams as t on f.id = t.franchise_id
group by f.id;
