## Stack Bridge test task

FastAPI backend with custom authentication and role based authorization for a
small helpdesk domain.

### Business domain

The application models support tickets:

- `user` creates and manages only own tickets.
- `support` sees and updates all tickets.
- `manager` sees and updates all tickets and can inspect users.
- `admin` manages users, roles, business elements, and access rules.

### Authorization model

Authorization rules are stored in the database:

- `roles` stores role codes such as `admin`, `manager`, `support`, `user`.
- `business_elements` stores protected application areas: `tickets`, `users`,
  `access_rules`.
- `access_role_rules` stores permissions for each role and business element.

Permission columns:

- `read_permission`
- `read_all_permission`
- `create_permission`
- `update_permission`
- `update_all_permission`
- `delete_permission`
- `delete_all_permission`

Rules ending with `_all_permission` allow working with all objects. Regular
permissions allow working only with owned objects where applicable.

### Seed data

The RBAC tables, demo users, and demo tickets are inserted by Alembic migration
`d4e91a7b6c32_rbac_and_mock_tickets.py`.

Demo password for all seed users:

```text
password123
```

Seed users:

```text
admin@example.com    role=admin
manager@example.com  role=manager
support@example.com  role=support
user@example.com     role=user
```

### API groups

User endpoints:

```text
POST   /user/register
POST   /user/login
POST   /user/logout
GET    /user/me
PATCH  /user/me
DELETE /user/me
```

Ticket endpoints:

```text
GET    /tickets
GET    /tickets/{ticket_id}
POST   /tickets
PATCH  /tickets/{ticket_id}
DELETE /tickets/{ticket_id}
```

Admin endpoints:

```text
GET    /admin/roles
POST   /admin/roles
PATCH  /admin/roles/{role_code}
DELETE /admin/roles/{role_code}

GET    /admin/business-elements
POST   /admin/business-elements
PATCH  /admin/business-elements/{business_element_code}
DELETE /admin/business-elements/{business_element_code}

GET    /admin/access-rules
POST   /admin/access-rules
PATCH  /admin/access-rules/{rule_id}
DELETE /admin/access-rules/{rule_id}

GET    /admin/users
PATCH  /admin/users/{user_id}/role
```

Protected endpoints expect:

```text
Authorization: Bearer <access_token>
```
