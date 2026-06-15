from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.dependencies.auth import get_current_user, require_permission
from app.models.user import User
from app.schemas.client import (
    ClientCreate,
    ClientUpdate,
    ClientOut,
    ClientDetailOut,
)
from app.services.client_service import ClientService

router = APIRouter(prefix="/clients", tags=["clients"])


@router.get("", response_model=List[ClientOut])
def list_clients(
    skip: int = 0,
    limit: int = 10,
    tipo_pessoa: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Lista clientes com paginação.
    
    Permissão: clients:read
    
    Query params:
    - skip: Deslocamento de paginação (padrão: 0)
    - limit: Limite de resultados (padrão: 10)
    - tipo_pessoa: Filtro por 'PF' ou 'PJ' (opcional)
    """
    require_permission(current_user, "clients:read")
    
    if limit > 100:
        limit = 100
    
    return ClientService.list_clients(db, skip, limit, tipo_pessoa)


@router.post("", response_model=ClientOut, status_code=status.HTTP_201_CREATED)
def create_client(
    client_data: ClientCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Cria novo cliente.
    
    Permissão: clients:write
    
    Body:
    - nome: Nome do cliente
    - tipo_pessoa: 'PF' ou 'PJ'
    - cpf_cnpj: CPF (11 dígitos) ou CNPJ (14 dígitos)
    - email: Email único
    - telefone: Telefone
    - data_nascimento: Data de nascimento (opcional)
    - observacoes: Anotações (opcional)
    """
    require_permission(current_user, "clients:write")
    
    return ClientService.create_client(db, client_data)


@router.get("/{client_id}", response_model=ClientDetailOut)
def get_client(
    client_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Obtém cliente por ID (com endereços).
    
    Permissão: clients:read
    """
    require_permission(current_user, "clients:read")
    
    return ClientService.get_client(db, client_id)


@router.put("/{client_id}", response_model=ClientOut)
def update_client(
    client_id: int,
    client_data: ClientUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Atualiza cliente.
    
    Permissão: clients:write
    
    Body (todos opcionais):
    - nome: Novo nome
    - email: Novo email
    - telefone: Novo telefone
    - data_nascimento: Nova data de nascimento
    - observacoes: Novas anotações
    """
    require_permission(current_user, "clients:write")
    
    return ClientService.update_client(db, client_id, client_data)


@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
def deactivate_client(
    client_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Desativa cliente (soft delete).
    
    Permissão: clients:delete
    """
    require_permission(current_user, "clients:delete")
    
    ClientService.deactivate_client(db, client_id)


@router.post("/{client_id}/activate", response_model=ClientOut)
def activate_client(
    client_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Ativa cliente desativado.
    
    Permissão: clients:write
    """
    require_permission(current_user, "clients:write")
    
    return ClientService.activate_client(db, client_id)


@router.get("/search/by-nome", response_model=List[ClientOut])
def search_by_nome(
    q: str,
    skip: int = 0,
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Busca clientes por nome.
    
    Permissão: clients:read
    
    Query params:
    - q: Termo de busca
    - skip: Deslocamento (padrão: 0)
    - limit: Limite (padrão: 10)
    """
    require_permission(current_user, "clients:read")
    
    if not q or len(q) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Termo de busca deve ter pelo menos 2 caracteres"
        )
    
    return ClientService.search_clients(db, q, "nome", skip, limit)


@router.get("/search/by-cpf-cnpj", response_model=List[ClientOut])
def search_by_cpf_cnpj(
    q: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Busca cliente por CPF ou CNPJ.
    
    Permissão: clients:read
    
    Query params:
    - q: CPF ou CNPJ
    """
    require_permission(current_user, "clients:read")
    
    if not q:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CPF/CNPJ é obrigatório"
        )
    
    return ClientService.search_clients(db, q, "cpf_cnpj")


@router.get("/search/by-email", response_model=List[ClientOut])
def search_by_email(
    q: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Busca cliente por email.
    
    Permissão: clients:read
    
    Query params:
    - q: Email
    """
    require_permission(current_user, "clients:read")
    
    if not q:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email é obrigatório"
        )
    
    return ClientService.search_clients(db, q, "email")


@router.get("/search/by-telefone", response_model=List[ClientOut])
def search_by_telefone(
    q: str,
    skip: int = 0,
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Busca clientes por telefone.
    
    Permissão: clients:read
    
    Query params:
    - q: Telefone (parcial ou completo)
    - skip: Deslocamento (padrão: 0)
    - limit: Limite (padrão: 10)
    """
    require_permission(current_user, "clients:read")
    
    if not q or len(q) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Telefone deve ter pelo menos 2 dígitos"
        )
    
    return ClientService.search_clients(db, q, "telefone", skip, limit)
