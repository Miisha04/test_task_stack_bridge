"""rbac and mock tickets

Revision ID: d4e91a7b6c32
Revises: f2ce873f717a
Create Date: 2026-07-23 18:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from passlib.context import CryptContext


revision: str = "d4e91a7b6c32"
down_revision: Union[str, Sequence[str], None] = "f2ce873f717a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


pwd_context = CryptContext(schemes=["argon2", "bcrypt"], deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password)


def upgrade() -> None:
    """Upgrade schema."""

    op.create_table(
        "roles",
        sa.Column("code", sa.String(length=64), primary_key=True),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("description", sa.String(length=512), nullable=True),
    )

    op.create_table(
        "business_elements",
        sa.Column("code", sa.String(length=64), primary_key=True),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("description", sa.String(length=512), nullable=True),
    )

    roles_table = sa.table(
        "roles",
        sa.column("code", sa.String),
        sa.column("name", sa.String),
        sa.column("description", sa.String),
    )
    op.bulk_insert(
        roles_table,
        [
            {"code": "admin", "name": "Administrator", "description": "Manages users and access rules"},
            {"code": "manager", "name": "Manager", "description": "Controls all support tickets"},
            {"code": "support", "name": "Support", "description": "Processes customer tickets"},
            {"code": "user", "name": "User", "description": "Creates and manages own tickets"},
        ],
    )

    business_elements_table = sa.table(
        "business_elements",
        sa.column("code", sa.String),
        sa.column("name", sa.String),
        sa.column("description", sa.String),
    )
    op.bulk_insert(
        business_elements_table,
        [
            {"code": "tickets", "name": "Tickets", "description": "Support requests"},
            {"code": "users", "name": "Users", "description": "Application users"},
            {"code": "access_rules", "name": "Access rules", "description": "Role permission rules"},
        ],
    )

    op.execute(
        f"""
        INSERT INTO users (id, first_name, last_name, middle_name, email, hashed_password, is_active, role)
        VALUES
            (1, 'Admin', 'Demo', NULL, 'admin@example.com', '{hash_password("123")}', true, 'admin'),
            (2, 'Support', 'Demo', NULL, 'support@example.com', '{hash_password("1234")}', true, 'support'),
            (3, 'User', 'One', NULL, 'user@example.com', '{hash_password("1235")}', true, 'user'),
            (4, 'Manager', 'Demo', NULL, 'manager@example.com', '{hash_password("1236")}', true, 'manager')
        ON CONFLICT DO NOTHING
        """
    )
    op.execute(
        """
        SELECT setval(
            pg_get_serial_sequence('users', 'id'),
            GREATEST((SELECT MAX(id) FROM users), 1),
            true
        )
        """
    )

    op.execute(
        """
        UPDATE users
        SET role = 'user'
        WHERE role NOT IN ('admin', 'manager', 'support', 'user')
        """
    )
    op.create_foreign_key(
        "fk_users_role_roles_code",
        "users",
        "roles",
        ["role"],
        ["code"],
    )

    op.create_table(
        "access_role_rules",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("role_code", sa.String(length=64), nullable=False),
        sa.Column("business_element_code", sa.String(length=64), nullable=False),
        sa.Column("read_permission", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("read_all_permission", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("create_permission", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("update_permission", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("update_all_permission", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("delete_permission", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("delete_all_permission", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.ForeignKeyConstraint(["role_code"], ["roles.code"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["business_element_code"], ["business_elements.code"], ondelete="CASCADE"),
        sa.UniqueConstraint("role_code", "business_element_code", name="uq_access_role_rules_role_element"),
    )
    op.create_index("ix_access_role_rules_role_code", "access_role_rules", ["role_code"])
    op.create_index(
        "ix_access_role_rules_business_element_code",
        "access_role_rules",
        ["business_element_code"],
    )

    access_role_rules_table = sa.table(
        "access_role_rules",
        sa.column("role_code", sa.String),
        sa.column("business_element_code", sa.String),
        sa.column("read_permission", sa.Boolean),
        sa.column("read_all_permission", sa.Boolean),
        sa.column("create_permission", sa.Boolean),
        sa.column("update_permission", sa.Boolean),
        sa.column("update_all_permission", sa.Boolean),
        sa.column("delete_permission", sa.Boolean),
        sa.column("delete_all_permission", sa.Boolean),
    )
    op.bulk_insert(
        access_role_rules_table,
        [
            {
                "role_code": "user",
                "business_element_code": "tickets",
                "read_permission": True,
                "read_all_permission": False,
                "create_permission": True,
                "update_permission": True,
                "update_all_permission": False,
                "delete_permission": True,
                "delete_all_permission": False,
            },
            {
                "role_code": "user",
                "business_element_code": "users",
                "read_permission": True,
                "read_all_permission": False,
                "create_permission": False,
                "update_permission": True,
                "update_all_permission": False,
                "delete_permission": True,
                "delete_all_permission": False,
            },
            {
                "role_code": "user",
                "business_element_code": "access_rules",
                "read_permission": False,
                "read_all_permission": False,
                "create_permission": False,
                "update_permission": False,
                "update_all_permission": False,
                "delete_permission": False,
                "delete_all_permission": False,
            },
            {
                "role_code": "support",
                "business_element_code": "tickets",
                "read_permission": True,
                "read_all_permission": True,
                "create_permission": False,
                "update_permission": True,
                "update_all_permission": True,
                "delete_permission": False,
                "delete_all_permission": False,
            },
            {
                "role_code": "support",
                "business_element_code": "users",
                "read_permission": False,
                "read_all_permission": False,
                "create_permission": False,
                "update_permission": False,
                "update_all_permission": False,
                "delete_permission": False,
                "delete_all_permission": False,
            },
            {
                "role_code": "support",
                "business_element_code": "access_rules",
                "read_permission": False,
                "read_all_permission": False,
                "create_permission": False,
                "update_permission": False,
                "update_all_permission": False,
                "delete_permission": False,
                "delete_all_permission": False,
            },
            {
                "role_code": "manager",
                "business_element_code": "tickets",
                "read_permission": True,
                "read_all_permission": True,
                "create_permission": False,
                "update_permission": True,
                "update_all_permission": True,
                "delete_permission": False,
                "delete_all_permission": False,
            },
            {
                "role_code": "manager",
                "business_element_code": "users",
                "read_permission": True,
                "read_all_permission": True,
                "create_permission": False,
                "update_permission": False,
                "update_all_permission": False,
                "delete_permission": False,
                "delete_all_permission": False,
            },
            {
                "role_code": "manager",
                "business_element_code": "access_rules",
                "read_permission": False,
                "read_all_permission": False,
                "create_permission": False,
                "update_permission": False,
                "update_all_permission": False,
                "delete_permission": False,
                "delete_all_permission": False,
            },
            {
                "role_code": "admin",
                "business_element_code": "tickets",
                "read_permission": True,
                "read_all_permission": True,
                "create_permission": True,
                "update_permission": True,
                "update_all_permission": True,
                "delete_permission": True,
                "delete_all_permission": True,
            },
            {
                "role_code": "admin",
                "business_element_code": "users",
                "read_permission": True,
                "read_all_permission": True,
                "create_permission": True,
                "update_permission": True,
                "update_all_permission": True,
                "delete_permission": True,
                "delete_all_permission": True,
            },
            {
                "role_code": "admin",
                "business_element_code": "access_rules",
                "read_permission": True,
                "read_all_permission": True,
                "create_permission": True,
                "update_permission": True,
                "update_all_permission": True,
                "delete_permission": True,
                "delete_all_permission": True,
            },
        ],
    )

    op.create_table(
        "tickets",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.String(length=2048), nullable=False),
        sa.Column("status", sa.String(length=32), server_default="open", nullable=False),
        sa.Column("priority", sa.String(length=32), server_default="medium", nullable=False),
        sa.Column("owner_id", sa.Integer(), nullable=False),
        sa.Column("assignee_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["assignee_id"], ["users.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_tickets_owner_id", "tickets", ["owner_id"])
    op.create_index("ix_tickets_assignee_id", "tickets", ["assignee_id"])

    tickets_table = sa.table(
        "tickets",
        sa.column("id", sa.Integer),
        sa.column("title", sa.String),
        sa.column("description", sa.String),
        sa.column("status", sa.String),
        sa.column("priority", sa.String),
        sa.column("owner_id", sa.Integer),
        sa.column("assignee_id", sa.Integer),
    )
    op.bulk_insert(
        tickets_table,
        [
            {
                "id": 1,
                "title": "Cannot log in",
                "description": "User cannot log in after password change",
                "status": "open",
                "priority": "high",
                "owner_id": 3,
                "assignee_id": 2,
            },
            {
                "id": 2,
                "title": "Need to change email",
                "description": "Customer asks support to update account email",
                "status": "in_progress",
                "priority": "medium",
                "owner_id": 3,
                "assignee_id": 2,
            },
        ],
    )
    op.execute(
        """
        SELECT setval(
            pg_get_serial_sequence('tickets', 'id'),
            GREATEST((SELECT MAX(id) FROM tickets), 1),
            true
        )
        """
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_index("ix_tickets_assignee_id", table_name="tickets")
    op.drop_index("ix_tickets_owner_id", table_name="tickets")
    op.drop_table("tickets")

    op.drop_index("ix_access_role_rules_business_element_code", table_name="access_role_rules")
    op.drop_index("ix_access_role_rules_role_code", table_name="access_role_rules")
    op.drop_table("access_role_rules")

    op.drop_constraint("fk_users_role_roles_code", "users", type_="foreignkey")
    op.execute(
        """
        DELETE FROM users
        WHERE email IN (
            'admin@example.com',
            'support@example.com',
            'user@example.com',
            'manager@example.com'
        )
        """
    )

    op.drop_table("business_elements")
    op.drop_table("roles")
