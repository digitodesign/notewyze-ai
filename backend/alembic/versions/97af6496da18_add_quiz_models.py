"""add_quiz_models"

Revision ID: 97af6496da18
Revises: b2988d11fa10
Create Date: 2024-12-24 00:12:44.060161

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '97af6496da18'
down_revision: Union[str, None] = 'b2988d11fa10'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create a temporary column for the array type
    op.add_column('questions', sa.Column('options_array', postgresql.ARRAY(sa.String()), nullable=True))
    
    # Update the temporary column with the converted data
    op.execute("""
        UPDATE questions 
        SET options_array = ARRAY(
            SELECT json_array_elements_text(options::json)
        )
        WHERE options IS NOT NULL
    """)
    
    # Drop the old column and rename the new one
    op.drop_column('questions', 'options')
    op.alter_column('questions', 'options_array', new_column_name='options')
    
    # Create user_answers table
    op.create_table('user_answers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('question_id', sa.Integer(), nullable=True),
        sa.Column('selected_answer', sa.String(), nullable=True),
        sa.Column('is_correct', sa.Boolean(), nullable=True),
        sa.Column('answered_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['question_id'], ['questions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_answers_id'), 'user_answers', ['id'], unique=False)
    
    # Add explanation column
    op.add_column('questions', sa.Column('explanation', sa.String(), nullable=True))
    
    # Update timestamps and foreign keys
    op.alter_column('questions', 'created_at',
        existing_type=postgresql.TIMESTAMP(timezone=True),
        type_=sa.DateTime(),
        existing_nullable=True,
        existing_server_default=sa.text('now()')
    )
    op.drop_constraint('questions_quiz_id_fkey', 'questions', type_='foreignkey')
    op.create_foreign_key(None, 'questions', 'quizzes', ['quiz_id'], ['id'], ondelete='CASCADE')
    op.drop_column('questions', 'updated_at')
    
    # Update quiz table
    op.alter_column('quizzes', 'created_at',
        existing_type=postgresql.TIMESTAMP(timezone=True),
        type_=sa.DateTime(),
        existing_nullable=True,
        existing_server_default=sa.text('now()')
    )
    op.alter_column('quizzes', 'updated_at',
        existing_type=postgresql.TIMESTAMP(timezone=True),
        type_=sa.DateTime(),
        existing_nullable=True,
        existing_server_default=sa.text('now()')
    )
    op.drop_constraint('quizzes_recording_id_fkey', 'quizzes', type_='foreignkey')
    op.drop_constraint('quizzes_user_id_fkey', 'quizzes', type_='foreignkey')
    op.create_foreign_key(None, 'quizzes', 'recordings', ['recording_id'], ['id'], ondelete='CASCADE')
    op.drop_column('quizzes', 'user_id')


def downgrade() -> None:
    # Revert all changes in reverse order
    op.add_column('quizzes', sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'quizzes', type_='foreignkey')
    op.create_foreign_key('quizzes_user_id_fkey', 'quizzes', 'users', ['user_id'], ['id'])
    op.create_foreign_key('quizzes_recording_id_fkey', 'quizzes', 'recordings', ['recording_id'], ['id'])
    op.alter_column('quizzes', 'updated_at',
        existing_type=sa.DateTime(),
        type_=postgresql.TIMESTAMP(timezone=True),
        existing_nullable=True,
        existing_server_default=sa.text('now()')
    )
    op.alter_column('quizzes', 'created_at',
        existing_type=sa.DateTime(),
        type_=postgresql.TIMESTAMP(timezone=True),
        existing_nullable=True,
        existing_server_default=sa.text('now()')
    )
    
    # Create a temporary column for JSON type
    op.add_column('questions', sa.Column('options_json', postgresql.JSON(astext_type=sa.Text()), nullable=True))
    
    # Convert array data back to JSON
    op.execute("""
        UPDATE questions 
        SET options_json = to_json(options::text::json)
        WHERE options IS NOT NULL
    """)
    
    # Drop array column and rename JSON column
    op.drop_column('questions', 'options')
    op.alter_column('questions', 'options_json', new_column_name='options')
    
    op.add_column('questions', sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'questions', type_='foreignkey')
    op.create_foreign_key('questions_quiz_id_fkey', 'questions', 'quizzes', ['quiz_id'], ['id'])
    op.alter_column('questions', 'created_at',
        existing_type=sa.DateTime(),
        type_=postgresql.TIMESTAMP(timezone=True),
        existing_nullable=True,
        existing_server_default=sa.text('now()')
    )
    op.drop_column('questions', 'explanation')
    op.drop_index(op.f('ix_user_answers_id'), table_name='user_answers')
    op.drop_table('user_answers')
