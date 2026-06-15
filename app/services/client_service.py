from datetime import datetime
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from app.models.client import Client, Address
from app.repositories.client_repository import ClientRepository
from app.repositories.address_repository import AddressRepository
from app.schemas.client import (
    ClientCreate,
    ClientUpdate,
    AddressCreate,
    AddressUpdate,
)


class ClientService:
    """
    Serviço de negócio para Cliente.
    
    Responsabilidades:
    - Validação de regras de negócio
    - Coordenação entre repositórios
    - Tratamento de erros
    """

    @staticmethod
    def create_client(db: Session, client_data: ClientCreate) -> Client:
        """
        Cria novo cliente com validações.
        
        Validações:
        - CPF/CNPJ único
        - Email único
        
        Args:
            db: Sessão do banco
            client_data: Dados do cliente
        
        Returns:
            Cliente criado
        
        Raises:
            HTTPException: Se CPF/CNPJ ou email já existem
        """
        # Verificar CPF/CNPJ único
        existing_cpf = ClientRepository.get_by_cpf_cnpj(db, client_data.cpf_cnpj)
        if existing_cpf:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="CPF/CNPJ já cadastrado"
            )
        
        # Verificar email único
        existing_email = ClientRepository.get_by_email(db, client_data.email)
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email já cadastrado"
            )
        
        # Limpar CPF/CNPJ (remover formatação)
        clean_cpf_cnpj = client_data.cpf_cnpj.replace(".", "").replace("-", "").replace("/", "")
        
        # Criar cliente
        new_client = Client(
            nome=client_data.nome,
            tipo_pessoa=client_data.tipo_pessoa.upper(),
            cpf_cnpj=clean_cpf_cnpj,
            email=client_data.email,
            telefone=client_data.telefone,
            data_nascimento=client_data.data_nascimento,
            observacoes=client_data.observacoes,
            ativo=True,
        )
        
        try:
            return ClientRepository.create(db, new_client)
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Erro ao criar cliente. Verifique os dados."
            )

    @staticmethod
    def update_client(
        db: Session,
        client_id: int,
        client_data: ClientUpdate
    ) -> Client:
        """
        Atualiza cliente existente.
        
        Args:
            db: Sessão do banco
            client_id: ID do cliente
            client_data: Dados a atualizar
        
        Returns:
            Cliente atualizado
        
        Raises:
            HTTPException: Se cliente não encontrado ou email já existe
        """
        client = ClientRepository.get_by_id(db, client_id)
        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cliente não encontrado"
            )
        
        # Validar email único se foi alterado
        if client_data.email and client_data.email != client.email:
            existing_email = ClientRepository.get_by_email(db, client_data.email)
            if existing_email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email já cadastrado"
                )
            client.email = client_data.email
        
        # Atualizar outros campos
        if client_data.nome:
            client.nome = client_data.nome
        if client_data.telefone:
            client.telefone = client_data.telefone
        if client_data.data_nascimento is not None:
            client.data_nascimento = client_data.data_nascimento
        if client_data.observacoes is not None:
            client.observacoes = client_data.observacoes
        
        client.updated_at = datetime.utcnow()
        
        try:
            return ClientRepository.update(db, client)
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Erro ao atualizar cliente"
            )

    @staticmethod
    def get_client(db: Session, client_id: int) -> Client:
        """
        Obtém cliente por ID.
        
        Args:
            db: Sessão do banco
            client_id: ID do cliente
        
        Returns:
            Cliente encontrado
        
        Raises:
            HTTPException: Se cliente não encontrado
        """
        client = ClientRepository.get_by_id(db, client_id)
        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cliente não encontrado"
            )
        return client

    @staticmethod
    def list_clients(
        db: Session,
        skip: int = 0,
        limit: int = 10,
        tipo_pessoa: Optional[str] = None
    ) -> List[Client]:
        """
        Lista clientes com paginação.
        
        Args:
            db: Sessão do banco
            skip: Deslocamento de paginação
            limit: Limite de resultados
            tipo_pessoa: Filtro por tipo (PF/PJ)
        
        Returns:
            Lista de clientes
        """
        if tipo_pessoa:
            return ClientRepository.get_by_tipo_pessoa(db, tipo_pessoa, skip, limit)
        return ClientRepository.get_all(db, skip, limit, only_active=True)

    @staticmethod
    def search_clients(
        db: Session,
        query: str,
        search_type: str = "nome",
        skip: int = 0,
        limit: int = 10
    ) -> List[Client]:
        """
        Busca clientes por diferentes critérios.
        
        Args:
            db: Sessão do banco
            query: Termo de busca
            search_type: 'nome', 'email', 'cpf_cnpj', 'telefone'
            skip: Deslocamento de paginação
            limit: Limite de resultados
        
        Returns:
            Lista de clientes encontrados
        
        Raises:
            HTTPException: Se search_type inválido
        """
        if search_type == "nome":
            return ClientRepository.search_by_name(db, query, skip, limit)
        elif search_type == "cpf_cnpj":
            client = ClientRepository.get_by_cpf_cnpj(db, query)
            return [client] if client else []
        elif search_type == "email":
            client = ClientRepository.get_by_email(db, query)
            return [client] if client else []
        elif search_type == "telefone":
            return ClientRepository.search_by_telefone(db, query, skip, limit)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="search_type inválido"
            )

    @staticmethod
    def deactivate_client(db: Session, client_id: int) -> Client:
        """
        Desativa cliente (soft delete).
        
        Args:
            db: Sessão do banco
            client_id: ID do cliente
        
        Returns:
            Cliente desativado
        
        Raises:
            HTTPException: Se cliente não encontrado
        """
        client = ClientRepository.deactivate(db, client_id)
        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cliente não encontrado"
            )
        return client

    @staticmethod
    def activate_client(db: Session, client_id: int) -> Client:
        """
        Ativa cliente desativado.
        
        Args:
            db: Sessão do banco
            client_id: ID do cliente
        
        Returns:
            Cliente ativado
        
        Raises:
            HTTPException: Se cliente não encontrado
        """
        client = ClientRepository.activate(db, client_id)
        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cliente não encontrado"
            )
        return client


class AddressService:
    """
    Serviço de negócio para Endereço.
    
    Responsabilidades:
    - Validação de regras de negócio
    - Gerenciamento de endereço principal
    - Coordenação entre repositórios
    """

    @staticmethod
    def create_address(
        db: Session,
        client_id: int,
        address_data: AddressCreate
    ) -> Address:
        """
        Cria novo endereço para cliente.
        
        Validações:
        - Cliente deve existir
        - Se principal=True, desativa endereço principal anterior
        
        Args:
            db: Sessão do banco
            client_id: ID do cliente
            address_data: Dados do endereço
        
        Returns:
            Endereço criado
        
        Raises:
            HTTPException: Se cliente não encontrado
        """
        # Verificar cliente
        client = ClientRepository.get_by_id(db, client_id)
        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cliente não encontrado"
            )
        
        # Se é primeiro endereço, define como principal
        count = AddressRepository.count_by_client(db, client_id)
        is_principal = address_data.principal or (count == 0)
        
        # Se é principal, desativa anterior
        if is_principal:
            AddressRepository.set_principal(db, client_id, -1)  # Desativa todos
        
        # Criar endereço
        new_address = Address(
            client_id=client_id,
            apelido=address_data.apelido,
            cep=address_data.cep,
            logradouro=address_data.logradouro,
            numero=address_data.numero,
            complemento=address_data.complemento,
            bairro=address_data.bairro,
            cidade=address_data.cidade,
            estado=address_data.estado.upper(),
            pais=address_data.pais,
            principal=is_principal,
        )
        
        try:
            return AddressRepository.create(db, new_address)
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Erro ao criar endereço"
            )

    @staticmethod
    def update_address(
        db: Session,
        address_id: int,
        address_data: AddressUpdate
    ) -> Address:
        """
        Atualiza endereço existente.
        
        Args:
            db: Sessão do banco
            address_id: ID do endereço
            address_data: Dados a atualizar
        
        Returns:
            Endereço atualizado
        
        Raises:
            HTTPException: Se endereço não encontrado
        """
        address = AddressRepository.get_by_id(db, address_id)
        if not address:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Endereço não encontrado"
            )
        
        # Se está definindo como principal
        if address_data.principal is True:
            AddressRepository.set_principal(db, address.client_id, address_id)
            # Recarregar para pegar estado atualizado
            address = AddressRepository.get_by_id(db, address_id)
        elif address_data.principal is False and address.principal:
            # Não pode remover principal sem designar outro
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Não pode remover endereço como principal sem designar outro"
            )
        
        # Atualizar campos
        if address_data.apelido:
            address.apelido = address_data.apelido
        if address_data.cep:
            address.cep = address_data.cep
        if address_data.logradouro:
            address.logradouro = address_data.logradouro
        if address_data.numero:
            address.numero = address_data.numero
        if address_data.complemento is not None:
            address.complemento = address_data.complemento
        if address_data.bairro:
            address.bairro = address_data.bairro
        if address_data.cidade:
            address.cidade = address_data.cidade
        if address_data.estado:
            address.estado = address_data.estado.upper()
        if address_data.pais:
            address.pais = address_data.pais
        
        address.updated_at = datetime.utcnow()
        
        try:
            return AddressRepository.update(db, address)
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Erro ao atualizar endereço"
            )

    @staticmethod
    def get_address(db: Session, address_id: int) -> Address:
        """
        Obtém endereço por ID.
        
        Args:
            db: Sessão do banco
            address_id: ID do endereço
        
        Returns:
            Endereço encontrado
        
        Raises:
            HTTPException: Se endereço não encontrado
        """
        address = AddressRepository.get_by_id(db, address_id)
        if not address:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Endereço não encontrado"
            )
        return address

    @staticmethod
    def list_addresses(
        db: Session,
        client_id: int,
        skip: int = 0,
        limit: int = 10
    ) -> List[Address]:
        """
        Lista endereços de um cliente.
        
        Args:
            db: Sessão do banco
            client_id: ID do cliente
            skip: Deslocamento de paginação
            limit: Limite de resultados
        
        Returns:
            Lista de endereços
        
        Raises:
            HTTPException: Se cliente não encontrado
        """
        client = ClientRepository.get_by_id(db, client_id)
        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cliente não encontrado"
            )
        
        return AddressRepository.get_all_by_client(db, client_id, skip, limit)

    @staticmethod
    def delete_address(db: Session, address_id: int) -> bool:
        """
        Deleta endereço.
        
        Args:
            db: Sessão do banco
            address_id: ID do endereço
        
        Returns:
            True se deletado
        
        Raises:
            HTTPException: Se endereço não encontrado ou é principal
        """
        address = AddressRepository.get_by_id(db, address_id)
        if not address:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Endereço não encontrado"
            )
        
        if address.principal:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Não é possível deletar endereço principal"
            )
        
        return AddressRepository.delete(db, address_id)

    @staticmethod
    def set_principal_address(db: Session, address_id: int) -> Address:
        """
        Define endereço como principal.
        
        Args:
            db: Sessão do banco
            address_id: ID do endereço
        
        Returns:
            Endereço agora principal
        
        Raises:
            HTTPException: Se endereço não encontrado
        """
        address = AddressRepository.get_by_id(db, address_id)
        if not address:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Endereço não encontrado"
            )
        
        success = AddressRepository.set_principal(db, address.client_id, address_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Erro ao definir endereço como principal"
            )
        
        return AddressRepository.get_by_id(db, address_id)
