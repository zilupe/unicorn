
    create database unicorn default charset "utf8mb4" collate "utf8mb4_unicode_ci";


    python -m unicorn.create_tables


    truncate games;
    delete from teams;
    delete from seasons;
