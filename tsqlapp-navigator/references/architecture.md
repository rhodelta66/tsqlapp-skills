# TSQL.APP Architecture Reference

Complete reference for TSQL.APP platform architecture and navigation patterns.

## Table of Contents

1. [Two-Database Architecture](#two-database-architecture)
2. [URL Deep Links](#url-deep-links)
3. [Meta Tables Reference](#meta-tables-reference)
4. [Action System](#action-system)
5. [Children System](#children-system)
6. [Discovery Patterns](#discovery-patterns)
7. [Observability](#observability)

---

## Two-Database Architecture

### Overview

Every TSQL.APP application consists of exactly 2 databases:

```
Application = Business Database + Meta Database

Pattern:
├─ {app}         (business tables, data, SPs)
└─ {app}_proj    (UI definition, complete app config)
```

### Business Database (`{app}`)

**Purpose**: Store actual business data

**Contains**:
- Business tables (customers, orders, inventory)
- Stored procedures (business logic)
- Views (data aggregation, q_*, rv_*, v_*)
- Foreign keys (data relationships)

### Meta Database (`{app}_proj`)

**Purpose**: Define the ENTIRE application

**Contains**: 95+ meta tables defining:
- UI screens (cards)
- Fields per screen
- Buttons and their SQL code
- Parent-child relationships
- Validation rules
- User permissions

**Key insight**: The `_proj` database IS the application. Change a row = change the app.

### Database Discovery

```sql
-- Get meta database name (must end with _proj)
SELECT DB_NAME() as meta_db

-- Get business database name
SELECT dbo.main_db() as business_db
```

### Synonyms

Meta database has synonyms to almost ALL tables and views in business database, enabling direct queries without cross-database syntax.

---

## URL Deep Links

### Complete URL Pattern

```
https://{domain}/{card}[/{parent_id}/{child_card}]?[ord={field_id}[d]][,{field_id}[d]][&red={filter_name}][&id={record_id}]
```

### URL Components

| Component | Location | Format | Description |
|-----------|----------|--------|-------------|
| `card` | path | string | Card name |
| `parent_id` | path | integer | Parent record ID (in child context) |
| `child_card` | path | string | Child card name |
| `ord` | query | `{field_id}[d]` | Sort by field ID, `d` suffix = descending |
| `ord` | query | `{id},{id}` | Multi-field sort (comma-separated) |
| `red` | query | URL-encoded string | Active filter name |
| `id` | query | integer | Selected record ID |

### URL Examples

```
# Simple card view
https://domain/incoming_invoice

# Sorted descending by dateInvoice (field 18377)
https://domain/incoming_invoice?ord=18377d

# With filter "Draft / Empty" applied
https://domain/incoming_invoice?ord=18377d&red=Draft+%2F+Empty

# With record 142338 selected
https://domain/incoming_invoice?ord=18377d&red=Draft+%2F+Empty&id=142338

# Child card context (invoice rows for parent invoice 142338)
https://domain/incoming_invoice/142338/invrow_1?ord=32408,30233
```

### URL Parsing Queries

```sql
-- 1. Parse card name from path
DECLARE @card_name NVARCHAR(128) = 'incoming_invoice'

-- 2. Get card details
SELECT id, name, tablename, basetable, reducer 
FROM api_card WHERE name = @card_name

-- 3. Parse sort field from ord parameter (e.g., 18377)
SELECT id, name, card_id FROM api_card_fields WHERE id = 18377

-- 4. Parse filter from red parameter (URL decode first)
SELECT id, name, sql FROM api_card_actions 
WHERE card_id = @card_id AND name = 'Draft / Empty' AND action = 'reducer'

-- 5. Get selected record
SELECT * FROM {tablename} WHERE id = @record_id
```

---

## Meta Tables Reference

### api_card

UI screen definitions.

| Column | Type | Description |
|--------|------|-------------|
| `id` | int | Primary key |
| `name` | nvarchar(128) | Card identifier (used in URL) |
| `tablename` | nvarchar(128) | View/query for READ |
| `basetable` | nvarchar(128) | Table for WRITE (CRUD) |
| `reducer` | nvarchar(max) | Default WHERE clause |
| `in_main_menu` | bit | Show in navigation |
| `role` | nvarchar(128) | Required role |

**CQRS Pattern**:
- `tablename` = READ (often view: q_*, rv_*, v_*)
- `basetable` = WRITE (actual table)

### api_card_fields

Column configuration per card.

| Column | Type | Description |
|--------|------|-------------|
| `id` | int | Primary key (used in URL ord parameter) |
| `name` | nvarchar(128) | Column name |
| `card_id` | int | Parent card |
| `list_order` | smallint | Position in list view |
| `detail_order` | smallint | Position in form view |
| `sql` | nvarchar(max) | Computed column expression |
| `picklist_sql` | nvarchar(max) | Dropdown options query |

### api_card_actions

Buttons, filters, and sub-menus.

| Column | Type | Description |
|--------|------|-------------|
| `id` | int | Primary key |
| `name` | nvarchar(128) | Action identifier |
| `display_name` | nvarchar(128) | Button label |
| `action` | nvarchar(128) | Type: 'stored_procedure' or 'reducer' |
| `sql` | nvarchar(max) | SQL to execute (button) or WHERE clause (filter) |
| `keycode` | nvarchar(128) | Keyboard shortcut |
| `card_id` | int | Parent card |
| `group_id` | int | Parent sub-menu (NULL = top level) |
| `type` | nvarchar(128) | Visibility: 'list', 'form', 'list_form', 'hidden' |
| `disabled` | bit | Active or not |
| `action_order` | int | Display order |
| `role` | nvarchar(128) | Required role |

### api_card_children

Parent-child card relationships.

| Column | Type | Description |
|--------|------|-------------|
| `id` | int | Primary key |
| `parent` | int | Parent card ID |
| `child` | int | Child card ID |
| `ref` | nvarchar(128) | FK column linking records |
| `keycode` | nvarchar(128) | Navigation shortcut (e.g., 'Enter') |
| `unbound` | bit | 0=filter by ref, 1=use custom reducer |
| `reducer` | nvarchar(max) | Custom WHERE clause |
| `is_hidden` | bit | Hide from UI |
| `group_id` | int | Place in sub-menu |
| `button_name` | nvarchar(128) | Custom button label |

---

## Action System

### Action Types

| `action` value | Type | Behavior |
|----------------|------|----------|
| `stored_procedure` | Button | Executes SQL in `sql` column |
| `reducer` | Filter | Applies WHERE clause from `sql` column |

### Action Visibility

| `type` value | Visible in |
|--------------|------------|
| `list` | List view only |
| `form` | Form view only |
| `list_form` | Both views |
| `hidden` | Not visible (triggered programmatically) |

### Sub-menu Hierarchy

Actions can be organized into sub-menus using `group_id`:

```
Card
├── Top-level actions (group_id IS NULL)
│   ├── Button (action='stored_procedure')
│   ├── Filter (action='reducer')
│   └── Sub-menu (id referenced by other actions' group_id)
└── Sub-menu contents (group_id = sub-menu action id)
```

### Keyboard Shortcuts

Shortcuts defined in `keycode` column. For nested actions:

```
{submenu_keycode} → {action_keycode}

Examples:
  K → N    (sub-menu K, then action N)
  I → S    (sub-menu I, then action S)
  Enter    (direct, no sub-menu)
```

### Query: All Actions with Full Shortcut Path

```sql
SELECT 
    a.id,
    CASE 
        WHEN g.keycode IS NOT NULL 
        THEN CONCAT(g.keycode, ' → ', ISNULL(a.keycode, '-'))
        ELSE ISNULL(a.keycode, '-')
    END as shortcut_sequence,
    a.name,
    a.display_name,
    CASE a.action 
        WHEN 'reducer' THEN 'filter' 
        ELSE 'button' 
    END as action_type,
    a.type as visibility,
    g.name as submenu,
    a.disabled
FROM api_card_actions a
LEFT JOIN api_card_actions g ON a.group_id = g.id
WHERE a.card_id = @card_id
ORDER BY 
    COALESCE(a.group_id, 0), 
    a.action_order, 
    a.name
```

### Query: Count by Type

```sql
SELECT 
    action,
    disabled,
    COUNT(*) as count
FROM api_card_actions 
WHERE card_id = @card_id
GROUP BY action, disabled
```

---

## Children System

### Navigation Behavior

When user presses child's `keycode` (e.g., Enter):

1. URL changes to: `/{parent_card}/{parent_id}/{child_card}`
2. Child card loads filtered by: `WHERE {ref} = {parent_id}`

### Bound vs Unbound Children

| `unbound` | Behavior |
|-----------|----------|
| `0` (false) | Auto-filter by `ref` column |
| `1` (true) | Use custom `reducer` clause |

### Query: Children with Shortcuts

```sql
SELECT 
    acc.keycode,
    c.name as child_card,
    c.tablename,
    acc.ref as link_column,
    CASE acc.unbound 
        WHEN 1 THEN 'custom reducer' 
        ELSE CONCAT('WHERE ', acc.ref, ' = @parent_id')
    END as filter_type,
    acc.is_hidden
FROM api_card_children acc
JOIN api_card c ON acc.child = c.id
WHERE acc.parent = @card_id
ORDER BY acc.keycode
```

### Query: What Does Enter Do?

```sql
SELECT 
    c.name as child_card,
    acc.ref as link_column,
    c.tablename
FROM api_card_children acc
JOIN api_card c ON acc.child = c.id
WHERE acc.parent = @card_id 
  AND acc.keycode = 'Enter'
  AND ISNULL(acc.is_hidden, 0) = 0
```

### Predict Next URL

```sql
-- Given current: /incoming_invoice?id=142338
-- Predict after pressing Enter:

SELECT CONCAT(
    '/', @parent_card, 
    '/', CAST(@parent_id as varchar), 
    '/', c.name
) as predicted_url
FROM api_card_children acc
JOIN api_card c ON acc.child = c.id
WHERE acc.parent = @card_id AND acc.keycode = 'Enter'
```

---

## Discovery Patterns

### Application Overview

```sql
-- Card count
SELECT COUNT(*) as total_cards FROM api_card

-- Action count  
SELECT COUNT(*) as total_actions FROM api_card_actions

-- Relationship count
SELECT COUNT(*) as total_children FROM api_card_children

-- Main menu items
SELECT name, tablename FROM api_card 
WHERE in_main_menu = 1 ORDER BY name
```

### Find Card for Table

```sql
SELECT name, tablename, basetable
FROM api_card
WHERE basetable = 'customers'
   OR tablename LIKE '%customers%'
```

### Deep Dive on Card

```sql
DECLARE @card_id INT = (SELECT id FROM api_card WHERE name = @card_name)

-- Card definition
SELECT * FROM api_card WHERE id = @card_id

-- Fields
SELECT id, name, list_order, detail_order 
FROM api_card_fields WHERE card_id = @card_id
ORDER BY list_order

-- Actions (buttons + filters)
SELECT id, name, action, keycode, group_id, disabled 
FROM api_card_actions WHERE card_id = @card_id
ORDER BY group_id, action_order

-- Children
SELECT child, ref, keycode, is_hidden 
FROM api_card_children WHERE parent = @card_id
```

### Search by Name

```sql
-- Find cards matching pattern
SELECT name, tablename FROM api_card 
WHERE name LIKE '%invoice%'

-- Find actions matching pattern
SELECT c.name as card, a.name as action, a.action as type
FROM api_card_actions a
JOIN api_card c ON a.card_id = c.id
WHERE a.name LIKE '%status%'
```

---

## Observability

### api_action_stats

Every user action logged.

```sql
SELECT 
    u.username,
    c.name as card,
    a.name as action,
    s.ts
FROM api_action_stats s
JOIN api_card c ON s.card_id = c.id
JOIN api_card_actions a ON s.action_id = a.id
JOIN api_user u ON s.context_user_id = u.id
WHERE s.ts > DATEADD(day, -1, GETDATE())
ORDER BY s.ts DESC
```

### api_history

Every data change logged.

```sql
SELECT 
    username,
    tablename,
    columnname,
    recordid,
    oldvalue,
    value,
    action,  -- INSERT/UPDATE/DELETE
    ts
FROM api_history
WHERE ts > DATEADD(day, -1, GETDATE())
ORDER BY ts DESC
```

### Trace User Journey

```sql
-- What did user do?
SELECT 
    c.name as card,
    a.name as action,
    s.ts
FROM api_action_stats s
JOIN api_card c ON s.card_id = c.id
LEFT JOIN api_card_actions a ON s.action_id = a.id
WHERE s.context_user_id = @user_id
ORDER BY s.ts DESC

-- What did user change?
SELECT tablename, columnname, oldvalue, value, ts
FROM api_history
WHERE username = @username
ORDER BY ts DESC
```

---

## Key Principles

1. **Metadata IS the app** - Not documentation, actual runtime config
2. **URL IS state** - Complete deep link to exact application state
3. **Do NOT guess** - Query metadata for exact values
4. **Two databases always** - Business data + meta data
5. **CQRS pattern** - tablename=READ, basetable=WRITE
6. **Hierarchy via group_id** - Actions and children can nest in sub-menus
