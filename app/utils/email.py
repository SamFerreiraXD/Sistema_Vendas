"""
Utilitários de email.

Atualmente implementa envio simulado com log.
Futuramente pode ser integrado com SMTP ou serviço de email em nuvem.
"""

import logging

logger = logging.getLogger(__name__)


def send_password_reset_email(to_email: str, user_name: str, reset_token: str) -> bool:
    """
    Envia email de reset de senha.
    Por enquanto, simula o envio apenas registrando em log.

    Args:
        to_email: Email do destinatário
        user_name: Nome do usuário
        reset_token: Token único para reset

    Returns:
        True se o "envio" foi bem-sucedido
    """
    reset_url = f"http://localhost:3000/reset-password?token={reset_token}"

    email_body = f"""
    Olá {user_name},

    Você solicitou um reset de senha. Clique no link abaixo para redefinir sua senha:

    {reset_url}

    Este link é válido por 30 minutos.

    Se você não solicitou este reset, ignore este email.

    Atenciosamente,
    Sistema de Vendas
    """

    logger.info(
        f"[SIMULATED EMAIL] Para: {to_email} | Assunto: Reset de Senha\n"
        f"Corpo:\n{email_body}"
    )

    return True


def send_welcome_email(to_email: str, user_name: str) -> bool:
    """
    Envia email de boas-vindas para novo usuário.
    Por enquanto, simula o envio apenas registrando em log.

    Args:
        to_email: Email do novo usuário
        user_name: Nome do usuário

    Returns:
        True se o "envio" foi bem-sucedido
    """
    email_body = f"""
    Bem-vindo {user_name},

    Sua conta foi criada com sucesso no Sistema de Vendas.

    Acesse a aplicação em: http://localhost:3000

    Atenciosamente,
    Sistema de Vendas
    """

    logger.info(
        f"[SIMULATED EMAIL] Para: {to_email} | Assunto: Bem-vindo\n"
        f"Corpo:\n{email_body}"
    )

    return True
