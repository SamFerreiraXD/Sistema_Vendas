from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, field_validator


class AddressBase(BaseModel):
    """Schema base de Endereço"""
    apelido: str
    cep: str
    logradouro: str
    numero: str
    complemento: Optional[str] = None
    bairro: str
    cidade: str
    estado: str
    pais: str = "Brasil"
    principal: bool = False

    @field_validator("estado")
    @classmethod
    def validate_estado(cls, v: str) -> str:
        """Valida UF (2 caracteres)"""
        if len(v) != 2:
            raise ValueError("Estado deve ter 2 caracteres (UF)")
        return v.upper()

    @field_validator("cep")
    @classmethod
    def validate_cep(cls, v: str) -> str:
        """Valida formato do CEP estruturalmente"""
        # Aceita formatos: 12345678 ou 12345-678
        clean_cep = v.replace("-", "")
        if not clean_cep.isdigit() or len(clean_cep) != 8:
            raise ValueError("CEP deve conter 8 dígitos")
        return v


class AddressCreate(AddressBase):
    """Schema para criar endereço"""
    pass


class AddressUpdate(BaseModel):
    """Schema para atualizar endereço"""
    apelido: Optional[str] = None
    cep: Optional[str] = None
    logradouro: Optional[str] = None
    numero: Optional[str] = None
    complemento: Optional[str] = None
    bairro: Optional[str] = None
    cidade: Optional[str] = None
    estado: Optional[str] = None
    pais: Optional[str] = None
    principal: Optional[bool] = None

    @field_validator("estado")
    @classmethod
    def validate_estado(cls, v: Optional[str]) -> Optional[str]:
        """Valida UF se fornecido"""
        if v and len(v) != 2:
            raise ValueError("Estado deve ter 2 caracteres (UF)")
        return v.upper() if v else None

    @field_validator("cep")
    @classmethod
    def validate_cep(cls, v: Optional[str]) -> Optional[str]:
        """Valida formato do CEP estruturalmente se fornecido"""
        if v:
            clean_cep = v.replace("-", "")
            if not clean_cep.isdigit() or len(clean_cep) != 8:
                raise ValueError("CEP deve conter 8 dígitos")
        return v


class AddressOut(AddressBase):
    """Schema de saída de Endereço"""
    id: int
    client_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ClientBase(BaseModel):
    """Schema base de Cliente"""
    nome: str
    tipo_pessoa: str
    cpf_cnpj: str
    email: EmailStr
    telefone: str
    data_nascimento: Optional[datetime] = None
    observacoes: Optional[str] = None

    @field_validator("tipo_pessoa")
    @classmethod
    def validate_tipo_pessoa(cls, v: str) -> str:
        """Valida tipo de pessoa"""
        if v.upper() not in ("PF", "PJ"):
            raise ValueError("tipo_pessoa deve ser 'PF' ou 'PJ'")
        return v.upper()

    @field_validator("cpf_cnpj")
    @classmethod
    def validate_cpf_cnpj(cls, v: str) -> str:
        """Valida formato de CPF/CNPJ estruturalmente"""
        clean = v.replace(".", "").replace("-", "").replace("/", "")
        
        if not clean.isdigit():
            raise ValueError("CPF/CNPJ deve conter apenas dígitos")
        
        if len(clean) == 11:  # CPF
            if len(clean) != 11:
                raise ValueError("CPF deve conter 11 dígitos")
        elif len(clean) == 14:  # CNPJ
            if len(clean) != 14:
                raise ValueError("CNPJ deve conter 14 dígitos")
        else:
            raise ValueError("CPF/CNPJ deve conter 11 ou 14 dígitos")
        
        return clean

    @field_validator("telefone")
    @classmethod
    def validate_telefone(cls, v: str) -> str:
        """Valida telefone estruturalmente"""
        clean = v.replace("(", "").replace(")", "").replace("-", "").replace(" ", "")
        if not clean.isdigit() or len(clean) < 10:
            raise ValueError("Telefone deve conter pelo menos 10 dígitos")
        return v


class ClientCreate(ClientBase):
    """Schema para criar cliente"""
    pass


class ClientUpdate(BaseModel):
    """Schema para atualizar cliente"""
    nome: Optional[str] = None
    email: Optional[EmailStr] = None
    telefone: Optional[str] = None
    data_nascimento: Optional[datetime] = None
    observacoes: Optional[str] = None

    @field_validator("telefone")
    @classmethod
    def validate_telefone(cls, v: Optional[str]) -> Optional[str]:
        """Valida telefone estruturalmente se fornecido"""
        if v:
            clean = v.replace("(", "").replace(")", "").replace("-", "").replace(" ", "")
            if not clean.isdigit() or len(clean) < 10:
                raise ValueError("Telefone deve conter pelo menos 10 dígitos")
        return v


class ClientOut(ClientBase):
    """Schema de saída de Cliente"""
    id: int
    ativo: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ClientDetailOut(ClientOut):
    """Schema detalhado de Cliente com endereços"""
    addresses: List[AddressOut] = []

    class Config:
        from_attributes = True
