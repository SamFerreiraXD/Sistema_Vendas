from typing import Optional, List
from sqlalchemy import and_
from sqlalchemy.orm import Session, joinedload
from app.models.client import Client, Address


class ClientRepository:
    """
    Repositório para operações de CRUD em Clientes.
    
    Responsabilidades:
    - Gerenciar acesso ao banco de dados para a tabela 'clients'
    - Fornecer métodos CRUD básicos
    - Fornecer métodos de busca e filtro
    """

    @staticmethod
    def get_all(
        db: Session,
        skip: int = 0,
        limit: int = 10,
        only_active: bool = True
    ) -> List[Client]:
        """
        Retorna listagem paginada de clientes.
        
        Args:
            db: Sessão do banco
            skip: Deslocamento de paginação
            limit: Limite de resultados
            only_active: Se True, retorna apenas clientes ativos
        
        Returns:
            Lista de clientes
        """
        query = db.query(Client)
        
        if only_active:
            query = query.filter(Client.ativo == True)
        
        return query.offset(skip).limit(limit).all()

    @staticmethod
    def get_by_id(db: Session, client_id: int) -> Optional[Client]:
        """
        Retorna cliente por ID (com relacionamentos carregados).
        
        Args:
            db: Sessão do banco
            client_id: ID do cliente
        
        Returns:
            Cliente ou None se não encontrado
        """
        return db.query(Client).options(
            joinedload(Client.addresses)
        ).filter(Client.id == client_id).first()

    @staticmethod
    def get_by_cpf_cnpj(db: Session, cpf_cnpj: str) -> Optional[Client]:
        """
        Retorna cliente por CPF/CNPJ.
        
        Args:
            db: Sessão do banco
            cpf_cnpj: CPF ou CNPJ (sem formatação)
        
        Returns:
            Cliente ou None se não encontrado
        """
        clean = cpf_cnpj.replace(".", "").replace("-", "").replace("/", "")
        return db.query(Client).filter(Client.cpf_cnpj == clean).first()

    @staticmethod
    def get_by_email(db: Session, email: str) -> Optional[Client]:
        """
        Retorna cliente por email.
        
        Args:
            db: Sessão do banco
            email: Email do cliente
        
        Returns:
            Cliente ou None se não encontrado
        """
        return db.query(Client).filter(Client.email == email).first()

    @staticmethod
    def search_by_name(
        db: Session,
        nome: str,
        skip: int = 0,
        limit: int = 10
    ) -> List[Client]:
        """
        Busca clientes por nome (LIKE).
        
        Args:
            db: Sessão do banco
            nome: Fragmento do nome
            skip: Deslocamento de paginação
            limit: Limite de resultados
        
        Returns:
            Lista de clientes encontrados
        """
        return db.query(Client).filter(
            and_(
                Client.nome.ilike(f"%{nome}%"),
                Client.ativo == True
            )
        ).offset(skip).limit(limit).all()

    @staticmethod
    def search_by_telefone(
        db: Session,
        telefone: str,
        skip: int = 0,
        limit: int = 10
    ) -> List[Client]:
        """
        Busca clientes por telefone.
        
        Args:
            db: Sessão do banco
            telefone: Telefone (parcial ou completo)
            skip: Deslocamento de paginação
            limit: Limite de resultados
        
        Returns:
            Lista de clientes encontrados
        """
        clean_phone = telefone.replace("(", "").replace(")", "").replace("-", "").replace(" ", "")
        return db.query(Client).filter(
            and_(
                Client.telefone.contains(clean_phone),
                Client.ativo == True
            )
        ).offset(skip).limit(limit).all()

    @staticmethod
    def get_by_tipo_pessoa(
        db: Session,
        tipo_pessoa: str,
        skip: int = 0,
        limit: int = 10
    ) -> List[Client]:
        """
        Retorna clientes por tipo de pessoa (PF ou PJ).
        
        Args:
            db: Sessão do banco
            tipo_pessoa: 'PF' ou 'PJ'
            skip: Deslocamento de paginação
            limit: Limite de resultados
        
        Returns:
            Lista de clientes
        """
        return db.query(Client).filter(
            and_(
                Client.tipo_pessoa == tipo_pessoa.upper(),
                Client.ativo == True
            )
        ).offset(skip).limit(limit).all()

    @staticmethod
    def create(db: Session, client: Client) -> Client:
        """
        Cria novo cliente.
        
        Args:
            db: Sessão do banco
            client: Instância de Client a ser persistida
        
        Returns:
            Cliente criado com ID
        """
        db.add(client)
        db.commit()
        db.refresh(client)
        return client

    @staticmethod
    def update(db: Session, client: Client) -> Client:
        """
        Atualiza cliente existente.
        
        Args:
            db: Sessão do banco
            client: Instância de Client com dados atualizados
        
        Returns:
            Cliente atualizado
        """
        db.merge(client)
        db.commit()
        db.refresh(client)
        return client

    @staticmethod
    def deactivate(db: Session, client_id: int) -> Optional[Client]:
        """
        Desativa cliente (soft delete).
        
        Args:
            db: Sessão do banco
            client_id: ID do cliente
        
        Returns:
            Cliente desativado ou None se não encontrado
        """
        client = db.query(Client).filter(Client.id == client_id).first()
        if client:
            client.ativo = False
            db.commit()
            db.refresh(client)
        return client

    @staticmethod
    def activate(db: Session, client_id: int) -> Optional[Client]:
        """
        Ativa cliente desativado.
        
        Args:
            db: Sessão do banco
            client_id: ID do cliente
        
        Returns:
            Cliente ativado ou None se não encontrado
        """
        client = db.query(Client).filter(Client.id == client_id).first()
        if client:
            client.ativo = True
            db.commit()
            db.refresh(client)
        return client

    @staticmethod
    def get_count_by_tipo(db: Session, tipo_pessoa: str) -> int:
        """
        Conta clientes por tipo de pessoa.
        
        Args:
            db: Sessão do banco
            tipo_pessoa: 'PF' ou 'PJ'
        
        Returns:
            Quantidade de clientes
        """
        return db.query(Client).filter(
            and_(
                Client.tipo_pessoa == tipo_pessoa.upper(),
                Client.ativo == True
            )
        ).count()
