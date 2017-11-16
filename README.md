
    create database unicorn default charset "utf8mb4" collate "utf8mb4_unicode_ci";


    python -m unicorn.create_tables


    truncate games;
    delete from teams;
    delete from seasons;




    python -m unicorn.recreate_tables
    python -m unicorn.parse_season_pages

