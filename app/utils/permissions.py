"""
Utilitários de permissões.

Lógica para ler e verificar permissões salvas como JSON na coluna 'permissions' da tabela 'roles'.
"""

import json
import logging
from typing import List

logger = logging.getLogger(__name__)


def parse_permissions(permissions_json: str) -> List[str]:
    """
    Parseia a coluna 'permissions' (JSON string) e retorna uma lista de permissões.

    Args:
        permissions_json: String JSON contendo lista de permissões

    Returns:
        Lista de strings de permissões, ou lista vazia se inválido
    """
    if not permissions_json:
        return []

    try:
        permissions = json.loads(permissions_json)
        if isinstance(permissions, list):
            return permissions
        else:
            logger.warning(f"Permissions JSON não é uma lista: {permissions_json}")
            return []
    except (json.JSONDecodeError, TypeError) as e:
        logger.error(f"Erro ao fazer parse de permissions JSON: {e}")
        return []


def has_permission(user_permissions: List[str], required_permission: str) -> bool:
    """
    Verifica se o usuário tem uma permissão específica.

    Args:
        user_permissions: Lista de permissões do usuário
        required_permission: Permissão a verificar

    Returns:
        True se o usuário tem a permissão, False caso contrário
    """
    return required_permission in user_permissions


def has_any_permission(user_permissions: List[str], required_permissions: List[str]) -> bool:
    """
    Verifica se o usuário tem qualquer uma das permissões na lista.

    Args:
        user_permissions: Lista de permissões do usuário
        required_permissions: Lista de permissões a verificar

    Returns:
        True se o usuário tem pelo menos uma das permissões
    """
    return any(perm in user_permissions for perm in required_permissions)


def has_all_permissions(user_permissions: List[str], required_permissions: List[str]) -> bool:
    """
    Verifica se o usuário tem todas as permissões na lista.

    Args:
        user_permissions: Lista de permissões do usuário
        required_permissions: Lista de permissões a verificar

    Returns:
        True se o usuário tem todas as permissões
    """
    return all(perm in user_permissions for perm in required_permissions)
