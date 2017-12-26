"""Base models

Revision ID: 0002
Revises: 0001
Create Date: 2017-12-26 14:46:30.902653

"""
from alembic import op
import sqlalchemy as sa


revision = '0002'
down_revision = '0001'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'franchises',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('colors', sa.String(length=255), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'seasons',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('number', sa.String(length=2), nullable=True),
        sa.Column('name', sa.String(length=50), nullable=True),
        sa.Column('first_week_date', sa.Date(), nullable=True),
        sa.Column('last_week_date', sa.Date(), nullable=True),
        sa.Column('gm_league_id', sa.Integer(), nullable=True),
        sa.Column('gm_division_id', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'games',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('season_id', sa.Integer(), nullable=True),
        sa.Column('season_stage', sa.String(length=20), server_default='regular', nullable=True),
        sa.Column('starts_at', sa.DateTime(), nullable=True),
        sa.Column('score_status', sa.Integer(), nullable=True),
        sa.Column('score_status_comments', sa.String(length=255), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['season_id'], ['seasons.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'teams',
        sa.Column('id', sa.String(length=15), nullable=False),
        sa.Column('season_id', sa.Integer(), nullable=True),
        sa.Column('franchise_id', sa.Integer(), nullable=True),
        sa.Column('name', sa.String(length=50), nullable=True),
        sa.Column('regular_rank', sa.Integer(), nullable=True),
        sa.Column('regular_played', sa.Integer(), nullable=True),
        sa.Column('regular_won', sa.Integer(), nullable=True),
        sa.Column('regular_lost', sa.Integer(), nullable=True),
        sa.Column('regular_drawn', sa.Integer(), nullable=True),
        sa.Column('regular_forfeits_for', sa.Integer(), nullable=True),
        sa.Column('regular_forfeits_against', sa.Integer(), nullable=True),
        sa.Column('regular_score_for', sa.Integer(), nullable=True),
        sa.Column('regular_score_against', sa.Integer(), nullable=True),
        sa.Column('regular_score_difference', sa.Integer(), nullable=True),
        sa.Column('regular_bonus_points', sa.Integer(), nullable=True),
        sa.Column('regular_points', sa.Integer(), nullable=True),
        sa.Column('finals_rank', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['franchise_id'], ['franchises.id'], ),
        sa.ForeignKeyConstraint(['season_id'], ['seasons.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'game_sides',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('team_id', sa.String(length=15), nullable=False),
        sa.Column('score', sa.Integer(), nullable=True),
        sa.Column('points', sa.Integer(), nullable=True),
        sa.Column('outcome', sa.String(length=5), nullable=True),
        sa.Column('game_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['game_id'], ['games.id'], ),
        sa.ForeignKeyConstraint(['team_id'], ['teams.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('game_sides')
    op.drop_table('teams')
    op.drop_table('games')
    op.drop_table('seasons')
    op.drop_table('franchises')
