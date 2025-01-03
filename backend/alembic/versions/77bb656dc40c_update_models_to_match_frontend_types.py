"""Update models to match frontend types

Revision ID: 77bb656dc40c
Revises: 97af6496da18
Create Date: 2024-12-25 03:45:13.479731

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '77bb656dc40c'
down_revision: Union[str, None] = '97af6496da18'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    
    # Drop dependent tables first
    op.drop_index('ix_user_answers_id', table_name='user_answers')
    op.drop_table('user_answers')
    op.drop_index('ix_questions_id', table_name='questions')
    op.drop_table('questions')
    
    # Create new tables
    op.create_table('profiles',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('study_preferences', sa.JSON(), nullable=True),
    sa.Column('statistics', sa.JSON(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('user_id')
    )
    op.create_index(op.f('ix_profiles_id'), 'profiles', ['id'], unique=False)
    
    op.create_table('research_recommendations',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('recording_id', sa.Integer(), nullable=True),
    sa.Column('title', sa.String(), nullable=True),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('url', sa.String(), nullable=True),
    sa.Column('difficulty', sa.Enum('beginner', 'intermediate', 'advanced', name='difficultylevel'), nullable=True),
    sa.Column('key_takeaways', sa.JSON(), nullable=True),
    sa.Column('relevance', sa.Integer(), nullable=True),
    sa.Column('publication_date', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['recording_id'], ['recordings.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_research_recommendations_id'), 'research_recommendations', ['id'], unique=False)
    
    op.create_table('quiz_questions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('quiz_id', sa.Integer(), nullable=True),
    sa.Column('question', sa.String(), nullable=True),
    sa.Column('options', sa.JSON(), nullable=True),
    sa.Column('correct_answer', sa.Integer(), nullable=True),
    sa.Column('explanation', sa.String(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['quiz_id'], ['quizzes.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_quiz_questions_id'), 'quiz_questions', ['id'], unique=False)
    
    op.create_table('saved_papers',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('recommendation_id', sa.Integer(), nullable=True),
    sa.Column('read_status', sa.Enum('unread', 'reading', 'completed', name='readstatus'), nullable=True),
    sa.Column('reading_progress', sa.Integer(), nullable=True),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['recommendation_id'], ['research_recommendations.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_saved_papers_id'), 'saved_papers', ['id'], unique=False)
    
    # Update existing tables
    op.alter_column('quizzes', 'created_at',
               existing_type=postgresql.TIMESTAMP(),
               type_=sa.DateTime(timezone=True),
               existing_nullable=True,
               server_default=sa.text('now()'))
    op.alter_column('quizzes', 'updated_at',
               existing_type=postgresql.TIMESTAMP(),
               type_=sa.DateTime(timezone=True),
               existing_nullable=True,
               server_default=sa.text('now()'))
    op.drop_column('quizzes', 'title')
    
    op.add_column('recordings', sa.Column('duration', sa.String(), nullable=True))
    op.add_column('recordings', sa.Column('summary', sa.Text(), nullable=True))
    op.add_column('recordings', sa.Column('transcription', sa.Text(), nullable=True))
    op.add_column('recordings', sa.Column('file_path', sa.String(), nullable=True))
    op.create_index(op.f('ix_recordings_title'), 'recordings', ['title'], unique=False)
    op.drop_column('recordings', 'raw_audio_path')
    op.drop_column('recordings', 'transcript')
    op.drop_column('recordings', 'processed_audio_path')
    
    op.add_column('users', sa.Column('hashed_password', sa.String(), nullable=True))
    op.add_column('users', sa.Column('avatar_url', sa.String(), nullable=True))
    op.add_column('users', sa.Column('is_active', sa.Boolean(), nullable=True))
    op.add_column('users', sa.Column('is_superuser', sa.Boolean(), nullable=True))
    op.alter_column('users', 'email',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.drop_column('users', 'password_hash')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('password_hash', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.alter_column('users', 'email',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.drop_column('users', 'is_superuser')
    op.drop_column('users', 'is_active')
    op.drop_column('users', 'avatar_url')
    op.drop_column('users', 'hashed_password')
    
    op.add_column('recordings', sa.Column('processed_audio_path', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column('recordings', sa.Column('transcript', sa.TEXT(), autoincrement=False, nullable=True))
    op.add_column('recordings', sa.Column('raw_audio_path', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.drop_index(op.f('ix_recordings_title'), table_name='recordings')
    op.drop_column('recordings', 'file_path')
    op.drop_column('recordings', 'transcription')
    op.drop_column('recordings', 'summary')
    op.drop_column('recordings', 'duration')
    
    op.add_column('quizzes', sa.Column('title', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.alter_column('quizzes', 'updated_at',
               existing_type=sa.DateTime(timezone=True),
               type_=postgresql.TIMESTAMP(),
               existing_nullable=True)
    op.alter_column('quizzes', 'created_at',
               existing_type=sa.DateTime(timezone=True),
               type_=postgresql.TIMESTAMP(),
               existing_nullable=True)
    
    op.drop_index(op.f('ix_saved_papers_id'), table_name='saved_papers')
    op.drop_table('saved_papers')
    op.drop_index(op.f('ix_quiz_questions_id'), table_name='quiz_questions')
    op.drop_table('quiz_questions')
    op.drop_index(op.f('ix_research_recommendations_id'), table_name='research_recommendations')
    op.drop_table('research_recommendations')
    op.drop_index(op.f('ix_profiles_id'), table_name='profiles')
    op.drop_table('profiles')
    
    # Recreate old tables
    op.create_table('questions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('quiz_id', sa.Integer(), nullable=True),
    sa.Column('question_text', sa.String(), nullable=True),
    sa.Column('options', sa.JSON(), nullable=True),
    sa.Column('correct_answer', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['quiz_id'], ['quizzes.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_questions_id', 'questions', ['id'], unique=False)
    
    op.create_table('user_answers',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('question_id', sa.Integer(), nullable=True),
    sa.Column('selected_answer', sa.Integer(), nullable=True),
    sa.Column('is_correct', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['question_id'], ['questions.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_user_answers_id', 'user_answers', ['id'], unique=False)
    # ### end Alembic commands ###
