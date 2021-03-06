"""empty message

Revision ID: 5659a8d02ca1
Revises: f8f073a1a118
Create Date: 2021-05-21 14:30:56.679404

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '5659a8d02ca1'
down_revision = 'f8f073a1a118'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('Show',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('start_time', sa.DateTime(), nullable=False),
    sa.Column('artist_id', sa.Integer(), nullable=False),
    sa.Column('venue_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['artist_id'], ['Artist.id'], ),
    sa.ForeignKeyConstraint(['venue_id'], ['Venue.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('Shows')
    op.drop_column('Artist', 'past_shows')
    op.drop_column('Artist', 'upcoming_shows')
    op.drop_column('Venue', 'past_shows')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Venue', sa.Column('past_shows', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('Artist', sa.Column('upcoming_shows', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('Artist', sa.Column('past_shows', sa.INTEGER(), autoincrement=False, nullable=True))
    op.create_table('Shows',
    sa.Column('id', sa.INTEGER(), server_default=sa.text('nextval(\'"Shows_id_seq"\'::regclass)'), autoincrement=True, nullable=False),
    sa.Column('start_time', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('artist_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('venue_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['artist_id'], ['Artist.id'], name='Shows_artist_id_fkey'),
    sa.ForeignKeyConstraint(['venue_id'], ['Venue.id'], name='Shows_venue_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='Shows_pkey')
    )
    op.drop_table('Show')
    # ### end Alembic commands ###
