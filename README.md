# Тестовое задание Stack Bridge

Backend-приложение на FastAPI с собственной системой аутентификации и
авторизации. В качестве бизнес-домена используется mini helpdesk: пользователи
создают заявки в поддержку, сотрудники поддержки их обрабатывают, менеджеры
контролируют заявки, администратор управляет доступами.

## Стек

- FastAPI
- SQLAlchemy async
- PostgreSQL
- Alembic
- JWT access/refresh tokens
- passlib/argon2 для хеширования паролей


## Запуск

Поднять PostgreSQL и API:

```bash
docker compose up --build
```

Применить миграции:

```bash
docker exec stack_bridge_api uv run alembic upgrade head
```


Swagger UI:

```text
http://localhost:8000/docs
```


## Бизнес-логика

Основной бизнес-объект приложения - `ticket`, заявка в поддержку.

Заявка содержит:

```text
id
title
description
status
priority
owner_id
assignee_id
created_at
updated_at
```

Логика ролей:

```text
user     - создает заявки и работает только со своими заявками
support  - видит и обновляет все заявки
manager  - видит и обновляет все заявки, а также может смотреть пользователей
admin    - управляет пользователями, ролями, бизнес-объектами и правилами доступа
```

## Аутентификация

После login пользователь получает:

```text
access_token
refresh_token
```

`access_token` используется в защищенных запросах:

```text
Authorization: Bearer <access_token>
```

`refresh_token` хранится в БД не в открытом виде, а как hash. При logout refresh
token отзывается через поле `revoked_at`.

При soft delete аккаунта:

```text
users.is_active = false
```

После этого пользователь не может снова залогиниться, а его активные refresh
tokens отзываются.

## Авторизация

Авторизация построена на RBAC-модели с учетом владения объектом.

Таблицы для управления доступом:

```text
roles
business_elements
access_role_rules
```

`roles` хранит роли:

```text
admin
manager
support
user
```

`business_elements` хранит защищенные области приложения:

```text
tickets
users
access_rules
```

`access_role_rules` хранит права конкретной роли на конкретный бизнес-объект:

```text
role_code
business_element_code
read_permission
read_all_permission
create_permission
update_permission
update_all_permission
delete_permission
delete_all_permission
```

Права без `_all_permission` дают доступ только к своим объектам, если у объекта
есть владелец. Например, `user` может читать заявку только если:

```text
ticket.owner_id == current_user.id
```

Права с `_all_permission` дают доступ ко всем объектам этого типа.

Если пользователь не авторизован, API возвращает `401`. Если пользователь
авторизован, но прав недостаточно, API возвращает `403 Forbidden`.

## Seed-данные

Начальные роли, бизнес-объекты, правила доступа, demo-пользователи и demo-заявки
добавляются миграцией:

```text
alembic/versions/d4e91a7b6c32_rbac_and_mock_tickets.py
```

Пароли для демо пользователей можно посмотреть в миграции (d4e91a7b6c32_rbac_and_mock_tickets)
Demo-пользователи:

```text
admin@example.com    role=admin
manager@example.com  role=manager
support@example.com  role=support
user@example.com     role=user
```


## Основные endpoints

Пользовательские endpoints:

```text
POST   /user/register
POST   /user/login
POST   /user/logout
GET    /user/me
PATCH  /user/me
DELETE /user/me
```

Заявки:

```text
GET    /tickets
GET    /tickets/{ticket_id}
POST   /tickets
PATCH  /tickets/{ticket_id}
DELETE /tickets/{ticket_id}
```

Администрирование ролевой модели:

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
