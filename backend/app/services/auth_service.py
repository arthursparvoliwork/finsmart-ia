"""
auth_service.py — Regras de negócio de autenticação.

Esta camada fica ENTRE as rotas HTTP e os modelos (banco).
- Rotas não sabem nada de banco, só chamam os services.
- Models não sabem nada de regra de negócio, só guardam dados.
"""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import SecurityService
from app.models import User


class AuthService:
    """
    Regras de negócio: cadastro e login de usuários.
    """

    def __init__(self, db: Session, security: SecurityService):
        # Injeção de dependência: recebe o banco e o serviço de segurança.
        # Isso facilita MUITO testar (podemos passar mocks/fakes).
        self._db = db
        self._security = security

    def register(self, name: str, email: str, password: str) -> User:
        """
        Cadastra um novo usuário.
        - Verifica se email já existe (não pode repetir)
        - Valida senha mínima
        - Hasheia a senha (JAMAIS salva em texto puro)
        """
        email = email.lower().strip()  # normaliza: "Foo@BAR.com" == "foo@bar.com"

        # Verifica se já existe usuário com este email
        existing = self._db.scalar(select(User).where(User.email == email))
        if existing:
            raise ValueError("Email já cadastrado")

        # Validação mínima de senha (em produção: 8+, números, símbolos)
        if len(password) < 6:
            raise ValueError("Senha deve ter ao menos 6 caracteres")

        # Cria o usuário com a senha JÁ HASHEADA
        user = User(
            name=name.strip(),
            email=email,
            password_hash=self._security.hash_password(password),
        )
        self._db.add(user)
        self._db.commit()
        # refresh recarrega o objeto pra pegar o id gerado pelo banco
        self._db.refresh(user)
        return user

    def login(self, email: str, password: str) -> tuple[User, str]:
        """
        Autentica um usuário.
        Retorna (user, token_jwt) se der certo.
        Levanta ValueError se email/senha inválidos.

        Segurança: a mensagem de erro é a MESMA pra "email errado" e "senha errada".
        Assim o atacante não descobre quais emails existem (user enumeration).
        """
        email = email.lower().strip()
        user = self._db.scalar(select(User).where(User.email == email))

        # Mesmo se não achou o usuário, verificamos a senha (timing attack defense)
        valid = (
            user is not None
            and self._security.verify_password(password, user.password_hash)
        )
        if not valid:
            raise ValueError("Credenciais inválidas")  # msg genérica de propósito

        # Gera o token JWT
        token = self._security.create_access_token(user.id)
        return user, token
