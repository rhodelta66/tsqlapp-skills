# TSQL.APP Skills

A collection of AI skills for working with [TSQL.APP](https://tsql.app) applications.

## What is TSQL.APP?

TSQL.APP is a radical metadata-driven application framework where **everything** is defined in database tables, not code. Every application consists of two databases:

- **Business Database** (`{app}`) - Your actual data
- **Meta Database** (`{app}_proj`) - The complete application definition

## Available Skills

| Skill | Purpose |
|-------|---------|
| [tsqlapp-navigator](./tsqlapp-navigator/) | Parse URLs, discover features, understand application state |
| [tsqlapp-developer](./tsqlapp-developer/) | Write action scripts, modal forms, T-SQL code |

## Installation

### Claude Desktop / Claude.ai

1. Download the `.skill` file from [Releases](../../releases)
2. Upload to Claude via the skills interface

### Manual Installation

Copy the skill folder to your skills directory:

```bash
git clone https://github.com/rhodelta66/tsqlapp-skills.git
cp -r tsqlapp-skills/tsqlapp-navigator /path/to/your/skills/
```

## Skills Overview

### tsqlapp-navigator

**Use when:** Users share TSQL.APP URLs, ask about cards/screens, want to understand available actions/buttons/filters, or need to locate features.

**Capabilities:**
- Parse URLs into application state
- Discover available actions (buttons, filters, sub-menus)
- Explain parent-child relationships
- Show keyboard shortcuts
- Predict navigation outcomes

**Example triggers:**
- "What does this URL mean: https://app.example.com/orders?ord=123d&red=Open"
- "What buttons are available on the orders card?"
- "What happens when I press Enter?"

### tsqlapp-developer

**Use when:** Creating TSQL.APP action scripts, modal forms, or any T-SQL code that runs within the TSQL.APP environment.

**Capabilities:**
- Generate production-ready T-SQL scripts
- Enforce 11 mandated coding practices
- Verify procedures against CSV catalog
- Create modal forms with proper state management

**Example triggers:**
- "Create a modal form for adding a new customer"
- "Write an action script to update invoice status"

## TSQL.APP URL Pattern

```
https://{domain}/{card}[/{parent_id}/{child_card}]?[ord={field_id}[d]][&red={filter_name}][&id={record_id}]
```

| Parameter | Example | Meaning |
|-----------|---------|---------|
| `card` | `orders` | Card/screen name |
| `parent_id` | `12345` | Parent record ID (child context) |
| `child_card` | `order_lines` | Child card name |
| `ord` | `456d` | Sort by field ID, `d`=descending |
| `red` | `Open+Orders` | Active filter (URL encoded) |
| `id` | `789` | Selected record ID |

## Contributing

Contributions are welcome! Please read the skill structure guidelines before submitting.

### Skill Structure

```
skill-name/
├── SKILL.md           # Required: Main skill file with frontmatter
├── references/        # Optional: Detailed documentation
└── scripts/           # Optional: Helper scripts
```

## License

MIT License - See [LICENSE](./LICENSE) for details.

## Links

- [TSQL.APP Documentation](https://tsql.app)
- [Anthropic Skills Documentation](https://docs.anthropic.com)
