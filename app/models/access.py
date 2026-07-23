from sqlalchemy import Boolean, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class RoleModel(Base):
    __tablename__ = "roles"

    code: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str | None] = mapped_column(String(512), nullable=True)

    users = relationship("User", back_populates="role_model")
    access_rules = relationship(
        "AccessRoleRule",
        back_populates="role",
        cascade="all, delete-orphan",
    )


class BusinessElementModel(Base):
    __tablename__ = "business_elements"

    code: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str | None] = mapped_column(String(512), nullable=True)

    access_rules = relationship(
        "AccessRoleRule",
        back_populates="business_element",
        cascade="all, delete-orphan",
    )


class AccessRoleRule(Base):
    __tablename__ = "access_role_rules"
    __table_args__ = (
        UniqueConstraint(
            "role_code",
            "business_element_code",
            name="uq_access_role_rules_role_element",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    role_code: Mapped[str] = mapped_column(
        ForeignKey("roles.code", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    business_element_code: Mapped[str] = mapped_column(
        ForeignKey("business_elements.code", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    read_permission: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false", nullable=False)
    read_all_permission: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false", nullable=False)
    create_permission: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false", nullable=False)
    update_permission: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false", nullable=False)
    update_all_permission: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false", nullable=False)
    delete_permission: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false", nullable=False)
    delete_all_permission: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false", nullable=False)

    role = relationship("RoleModel", back_populates="access_rules")
    business_element = relationship("BusinessElementModel", back_populates="access_rules")
