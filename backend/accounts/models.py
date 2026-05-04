"""
Accounts app — Models.
Custom User model for laboratory professionals.
Email-based authentication, with role distinction (analyst / supervisor).
"""

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    """User manager that uses email as the unique identifier."""

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("O email é obrigatório.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", User.Role.SUPERVISOR)
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    Laboratory user.
    - ANALYST: can browse substances and run compatibility checks.
    - SUPERVISOR: full access (can also manage substances/hazards/records).
    """

    class Role(models.TextChoices):
        ANALYST = "analyst", "Analista"
        SUPERVISOR = "supervisor", "Supervisor"

    username = None  # Remove username field
    email = models.EmailField("Email", unique=True)
    role = models.CharField(
        "Função",
        max_length=20,
        choices=Role.choices,
        default=Role.ANALYST,
    )

    # Lab affiliation (optional, descriptive)
    institution = models.CharField(
        "Instituição / Laboratório",
        max_length=150,
        blank=True,
        help_text="Nome do laboratório, faculdade ou hospital onde atua.",
    )
    registration_number = models.CharField(
        "Registro profissional (CRBM, CRF, etc.)",
        max_length=30,
        blank=True,
    )

    accepted_terms_at = models.DateTimeField("Aceitou termos em", blank=True, null=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name"]

    objects = UserManager()

    class Meta:
        verbose_name = "Usuário"
        verbose_name_plural = "Usuários"
        ordering = ["-date_joined"]

    def __str__(self):
        return self.get_full_name() or self.email

    @property
    def is_supervisor(self) -> bool:
        return self.role == self.Role.SUPERVISOR or self.is_superuser
