from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models.client import Address, Client


class AddressRepository:
    """
    Repositório para operações de CRUD em Endereços.
    
    Responsabilidades:
    - Gerenciar acesso ao banco de dados para a tabela 'addresses'
    - Fornecer métodos CRUD básicos
    - Gerenciar endereço principal por cliente
    """

    @staticmethod
    def get_all_by_client(
        db: Session,
        client_id: int,
        skip: int = 0,
        limit: int = 10
    ) -> List[Address]:
        """
        Retorna listagem paginada de endereços de um cliente.
        
        Args:
            db: Sessão do banco
            client_id: ID do cliente
            skip: Deslocamento de paginação
            limit: Limite de resultados
        
        Returns:
            Lista de endereços
        """
        return db.query(Address).filter(
            Address.client_id == client_id
        ).offset(skip).limit(limit).all()

    @staticmethod
    def get_by_id(db: Session, address_id: int) -> Optional[Address]:
        """
        Retorna endereço por ID.
        
        Args:
            db: Sessão do banco
            address_id: ID do endereço
        
        Returns:
            Endereço ou None se não encontrado
        """
        return db.query(Address).filter(Address.id == address_id).first()

    @staticmethod
    def get_principal(db: Session, client_id: int) -> Optional[Address]:
        """
        Retorna endereço principal de um cliente.
        
        Args:
            db: Sessão do banco
            client_id: ID do cliente
        
        Returns:
            Endereço principal ou None se não houver
        """
        return db.query(Address).filter(
            and_(
                Address.client_id == client_id,
                Address.principal == True
            )
        ).first()

    @staticmethod
    def get_by_apelido(db: Session, client_id: int, apelido: str) -> Optional[Address]:
        """
        Retorna endereço por apelido dentro de um cliente.
        
        Args:
            db: Sessão do banco
            client_id: ID do cliente
            apelido: Apelido do endereço
        
        Returns:
            Endereço ou None se não encontrado
        """
        return db.query(Address).filter(
            and_(
                Address.client_id == client_id,
                Address.apelido == apelido
            )
        ).first()

    @staticmethod
    def create(db: Session, address: Address) -> Address:
        """
        Cria novo endereço.
        
        Args:
            db: Sessão do banco
            address: Instância de Address a ser persistida
        
        Returns:
            Endereço criado com ID
        """
        db.add(address)
        db.commit()
        db.refresh(address)
        return address

    @staticmethod
    def update(db: Session, address: Address) -> Address:
        """
        Atualiza endereço existente.
        
        Args:
            db: Sessão do banco
            address: Instância de Address com dados atualizados
        
        Returns:
            Endereço atualizado
        """
        db.merge(address)
        db.commit()
        db.refresh(address)
        return address

    @staticmethod
    def delete(db: Session, address_id: int) -> bool:
        """
        Deleta endereço (delete físico).
        
        Args:
            db: Sessão do banco
            address_id: ID do endereço
        
        Returns:
            True se deletado, False se não encontrado
        """
        address = db.query(Address).filter(Address.id == address_id).first()
        if address:
            db.delete(address)
            db.commit()
            return True
        return False

    @staticmethod
    def set_principal(db: Session, client_id: int, address_id: int) -> bool:
        """
        Define um endereço como principal.
        Automaticamente desativa o endereço principal anterior.
        
        Args:
            db: Sessão do banco
            client_id: ID do cliente
            address_id: ID do endereço a ser definido como principal
        
        Returns:
            True se sucesso, False se falhar
        """
        # Verificar se endereço pertence ao cliente
        address = db.query(Address).filter(
            and_(
                Address.id == address_id,
                Address.client_id == client_id
            )
        ).first()
        
        if not address:
            return False
        
        # Desativar endereço principal anterior
        old_principal = db.query(Address).filter(
            and_(
                Address.client_id == client_id,
                Address.principal == True,
                Address.id != address_id
            )
        ).first()
        
        if old_principal:
            old_principal.principal = False
            db.merge(old_principal)
        
        # Ativar novo principal
        address.principal = True
        db.merge(address)
        db.commit()
        
        return True

    @staticmethod
    def count_by_client(db: Session, client_id: int) -> int:
        """
        Conta endereços de um cliente.
        
        Args:
            db: Sessão do banco
            client_id: ID do cliente
        
        Returns:
            Quantidade de endereços
        """
        return db.query(Address).filter(
            Address.client_id == client_id
        ).count()
