"""Modulo 3: Clientes e Enderecos

Revision ID: 003_clientes_enderecos
Revises: None
Create Date: 2026-06-15 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '003_clientes_enderecos'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Criar tabela de Clientes
    op.create_table(
        'clients',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nome', sa.String(length=150), nullable=False),
        sa.Column('tipo_pessoa', sa.String(length=2), nullable=False),
        sa.Column('cpf_cnpj', sa.String(length=20), nullable=False),
        sa.Column('email', sa.String(length=150), nullable=False),
        sa.Column('telefone', sa.String(length=20), nullable=False),
        sa.Column('data_nascimento', sa.DateTime(), nullable=True),
        sa.Column('observacoes', sa.String(length=500), nullable=True),
        sa.Column('ativo', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('cpf_cnpj', name='uq_client_cpf_cnpj'),
        sa.UniqueConstraint('email', name='uq_client_email'),
    )
    
    # Criar índices para a tabela de Clientes
    op.create_index('idx_client_nome', 'clients', ['nome'])
    op.create_index('idx_client_cpf_cnpj', 'clients', ['cpf_cnpj'])
    op.create_index('idx_client_email', 'clients', ['email'])
    op.create_index('idx_client_ativo', 'clients', ['ativo'])
    op.create_index('idx_client_cpf_cnpj_ativo', 'clients', ['cpf_cnpj', 'ativo'])
    op.create_index('idx_client_email_ativo', 'clients', ['email', 'ativo'])

    # Criar tabela de Endereços
    op.create_table(
        'addresses',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('client_id', sa.Integer(), nullable=False),
        sa.Column('apelido', sa.String(length=50), nullable=False),
        sa.Column('cep', sa.String(length=10), nullable=False),
        sa.Column('logradouro', sa.String(length=150), nullable=False),
        sa.Column('numero', sa.String(length=20), nullable=False),
        sa.Column('complemento', sa.String(length=100), nullable=True),
        sa.Column('bairro', sa.String(length=100), nullable=False),
        sa.Column('cidade', sa.String(length=100), nullable=False),
        sa.Column('estado', sa.String(length=2), nullable=False),
        sa.Column('pais', sa.String(length=50), nullable=False),
        sa.Column('principal', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['client_id'], ['clients.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )
    
    # Criar índices para a tabela de Endereços
    op.create_index('idx_address_client_id', 'addresses', ['client_id'])
    op.create_index('idx_address_client_principal', 'addresses', ['client_id', 'principal'])


def downgrade() -> None:
    # Remover índices
    op.drop_index('idx_address_client_principal', table_name='addresses')
    op.drop_index('idx_address_client_id', table_name='addresses')
    
    # Remover tabela de Endereços
    op.drop_table('addresses')
    
    # Remover índices
    op.drop_index('idx_client_email_ativo', table_name='clients')
    op.drop_index('idx_client_cpf_cnpj_ativo', table_name='clients')
    op.drop_index('idx_client_ativo', table_name='clients')
    op.drop_index('idx_client_email', table_name='clients')
    op.drop_index('idx_client_cpf_cnpj', table_name='clients')
    op.drop_index('idx_client_nome', table_name='clients')
    
    # Remover tabela de Clientes
    op.drop_table('clients')
