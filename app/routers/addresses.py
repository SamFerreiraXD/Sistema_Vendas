from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.utils.permissions import require_permission
from app.models.user import User
from app.schemas.client import (
    AddressCreate,
    AddressUpdate,
    AddressOut,
)
from app.services.client_service import AddressService

router = APIRouter(prefix="/addresses", tags=["addresses"])


@router.get("/client/{client_id}", response_model=List[AddressOut])
def list_client_addresses(
    client_id: int,
    skip: int = 0,
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Lista endereços de um cliente.
    
    Permissão: addresses:read
    
    Path params:
    - client_id: ID do cliente
    
    Query params:
    - skip: Deslocamento de paginação (padrão: 0)
    - limit: Limite de resultados (padrão: 10)
    """
    require_permission(current_user, "addresses:read")
    
    if limit > 50:
        limit = 50
    
    return AddressService.list_addresses(db, client_id, skip, limit)


@router.post("", response_model=AddressOut, status_code=status.HTTP_201_CREATED)
def create_address(
    client_id: int,
    address_data: AddressCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Cria novo endereço para cliente.
    
    Permissão: addresses:write
    
    Query params:
    - client_id: ID do cliente
    
    Body:
    - apelido: Identificação (Casa, Trabalho, Entrega, etc)
    - cep: CEP (formato: 00000-000 ou 00000000)
    - logradouro: Rua, avenida, etc
    - numero: Número do imóvel
    - complemento: Apto, bloco, etc (opcional)
    - bairro: Bairro
    - cidade: Cidade
    - estado: UF (2 caracteres)
    - pais: País (padrão: Brasil)
    - principal: Definir como endereço principal (padrão: False)
    
    Nota: Se for o primeiro endereço, será automaticamente definido como principal
    """
    require_permission(current_user, "addresses:write")
    
    return AddressService.create_address(db, client_id, address_data)


@router.get("/{address_id}", response_model=AddressOut)
def get_address(
    address_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Obtém endereço por ID.
    
    Permissão: addresses:read
    
    Path params:
    - address_id: ID do endereço
    """
    require_permission(current_user, "addresses:read")
    
    return AddressService.get_address(db, address_id)


@router.put("/{address_id}", response_model=AddressOut)
def update_address(
    address_id: int,
    address_data: AddressUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Atualiza endereço.
    
    Permissão: addresses:write
    
    Path params:
    - address_id: ID do endereço
    
    Body (todos opcionais):
    - apelido: Novo apelido
    - cep: Novo CEP
    - logradouro: Novo logradouro
    - numero: Novo número
    - complemento: Novo complemento
    - bairro: Novo bairro
    - cidade: Nova cidade
    - estado: Nova UF
    - pais: Novo país
    - principal: Definir como principal
    """
    require_permission(current_user, "addresses:write")
    
    return AddressService.update_address(db, address_id, address_data)


@router.delete("/{address_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_address(
    address_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Deleta endereço.
    
    Permissão: addresses:delete
    
    Path params:
    - address_id: ID do endereço
    
    Nota: Não é possível deletar endereço principal
    """
    require_permission(current_user, "addresses:delete")
    
    AddressService.delete_address(db, address_id)


@router.post("/{address_id}/set-principal", response_model=AddressOut)
def set_principal_address(
    address_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Define endereço como principal.
    
    Permissão: addresses:write
    
    Path params:
    - address_id: ID do endereço
    
    Nota: O endereço principal anterior será automaticamente desativado
    """
    require_permission(current_user, "addresses:write")
    
    return AddressService.set_principal_address(db, address_id)
