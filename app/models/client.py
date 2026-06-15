from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, Integer, String, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.core.database import Base


class Client(Base):
    """
    Modelo de Cliente (Pessoa Física ou Jurídica)
    
    Campos:
    - id: Identificador único
    - nome: Nome do cliente (PF ou empresa)
    - tipo_pessoa: 'PF' (Pessoa Física) ou 'PJ' (Pessoa Jurídica)
    - cpf_cnpj: CPF (PF) ou CNPJ (PJ) - único
    - email: E-mail único
    - telefone: Telefone principal
    - data_nascimento: Data de nascimento (opcional, apenas PF)
    - observacoes: Anotações sobre o cliente
    - ativo: Soft delete (True = ativo, False = inativo)
    - created_at: Data de criação
    - updated_at: Data de última atualização
    - addresses: Relacionamento com endereços
    """
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(150), nullable=False, index=True)
    tipo_pessoa = Column(String(2), nullable=False)  # PF ou PJ
    cpf_cnpj = Column(String(20), unique=True, nullable=False, index=True)
    email = Column(String(150), unique=True, nullable=False, index=True)
    telefone = Column(String(20), nullable=False)
    data_nascimento = Column(DateTime, nullable=True)
    observacoes = Column(String(500), nullable=True)
    ativo = Column(Boolean, default=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relacionamentos
    addresses = relationship("Address", back_populates="client", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_client_cpf_cnpj_ativo", "cpf_cnpj", "ativo"),
        Index("idx_client_email_ativo", "email", "ativo"),
    )


class Address(Base):
    """
    Modelo de Endereço do Cliente
    
    Campos:
    - id: Identificador único
    - client_id: FK para Cliente
    - apelido: Identificação do endereço (Casa, Trabalho, Entrega, Cobrança)
    - cep: CEP (formato: 00000-000)
    - logradouro: Rua, avenida, etc
    - numero: Número do imóvel
    - complemento: Apto, bloco, etc
    - bairro: Bairro
    - cidade: Cidade
    - estado: UF (2 caracteres)
    - pais: País (padrão: Brasil)
    - principal: Endereço principal para entregas
    - created_at: Data de criação
    - updated_at: Data de última atualização
    - client: Relacionamento com cliente
    """
    __tablename__ = "addresses"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False, index=True)
    apelido = Column(String(50), nullable=False)  # Casa, Trabalho, Entrega, etc
    cep = Column(String(10), nullable=False)
    logradouro = Column(String(150), nullable=False)
    numero = Column(String(20), nullable=False)
    complemento = Column(String(100), nullable=True)
    bairro = Column(String(100), nullable=False)
    cidade = Column(String(100), nullable=False)
    estado = Column(String(2), nullable=False)  # UF
    pais = Column(String(50), default="Brasil", nullable=False)
    principal = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relacionamentos
    client = relationship("Client", back_populates="addresses")

    __table_args__ = (
        Index("idx_address_client_principal", "client_id", "principal"),
    )
