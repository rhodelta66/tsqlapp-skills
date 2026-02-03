# 🚀 TSQL.APP Skills

[![GitHub release](https://img.shields.io/github/v/release/rhodelta66/tsqlapp-skills)](https://github.com/rhodelta66/tsqlapp-skills/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![TSQL.APP](https://img.shields.io/badge/Platform-TSQL.APP-blue)](https://tsql.app)

> **AI-powered skills for navigating and developing TSQL.APP applications**

---

## 🎬 Demo

[![Watch the demo](https://img.youtube.com/vi/9Vf_PvScjWI/maxresdefault.jpg)](https://www.youtube.com/watch?v=9Vf_PvScjWI)

*Click to watch how the TSQL.APP skills work in action*

---

## 🎯 What is TSQL.APP?

[TSQL.APP](https://tsql.app) is a revolutionary **metadata-driven application framework** where everything is defined in database tables, not code.

```
┌─────────────────────────────────────────────────────────┐
│                    TSQL.APP Architecture                │
├─────────────────────────────────────────────────────────┤
│                                                         │
│   📊 Business Database        📋 Meta Database          │
│   ─────────────────────       ─────────────────────     │
│   • Your actual data          • Cards (screens)         │
│   • Tables & Views            • Fields (columns)        │
│   • Stored Procedures         • Actions (buttons)       │
│   • Business Logic            • Children (relations)    │
│                                                         │
│              Database = Code + UI + Logic               │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 📦 Available Skills

### 🧭 tsqlapp-navigator

**Understand and navigate TSQL.APP applications**

| Capability | Description |
|------------|-------------|
| 🔗 URL Parsing | Decode any TSQL.APP URL into card, filters, sorting, selection |
| 🔘 Action Discovery | List all buttons, filters, and sub-menus with keyboard shortcuts |
| 👶 Relationship Mapping | Explore parent-child card hierarchies |
| ⌨️ Shortcut Sequences | Show full keyboard paths (e.g., `K` → `N`) |
| 🔮 Navigation Prediction | Predict next URL after user actions |

**Example prompts:**
```
"What does this URL mean: https://app.example.com/orders?ord=123d&red=Open"
"What buttons are available on the orders card?"
"What happens when I press Enter on this screen?"
```

---

### 💻 tsqlapp-developer

**Generate production-ready TSQL.APP code**

| Capability | Description |
|------------|-------------|
| 📝 Action Scripts | Create button logic with proper patterns |
| 🖼️ Modal Forms | Build forms with state management |
| ✅ Code Validation | Enforce 11 mandated practices |
| 🔍 Procedure Verification | Check against 1500+ documented procedures |
| 🎯 First-Time-Right | Production-ready code, no placeholders |

**Example prompts:**
```
"Create a modal form for adding a new customer"
"Write an action script to update invoice status"
"Build a data entry form with validation"
```

---

## 📥 Installation

### Quick Install

1. Download the `.skill` file from [**Releases**](https://github.com/rhodelta66/tsqlapp-skills/releases/latest)
2. Upload to Claude via the skills interface

### Direct Download Links

| Skill | Download | Size |
|-------|----------|------|
| tsqlapp-navigator | [⬇️ Download](https://github.com/rhodelta66/tsqlapp-skills/releases/latest/download/tsqlapp-navigator.skill) | ~10 KB |
| tsqlapp-developer | [⬇️ Download](https://github.com/rhodelta66/tsqlapp-skills/releases/latest/download/tsqlapp-developer.skill) | ~50 KB |

---

## 🔗 URL Deep Links

TSQL.APP URLs capture complete application state:

```
https://domain/card[/parent_id/child]?ord=field[d]&red=filter&id=record
         │      │       │       │         │    │      │         │
         │      │       │       │         │    │      │         └── Selected record
         │      │       │       │         │    │      └── Active filter
         │      │       │       │         │    └── d = descending
         │      │       │       │         └── Sort by field ID
         │      │       │       └── Child card (detail view)
         │      │       └── Parent record ID
         │      └── Card name (screen)
         └── Your domain
```

### Examples

| URL | Meaning |
|-----|---------|
| `/orders` | Orders list |
| `/orders?ord=5d` | Orders sorted by field 5, descending |
| `/orders?red=Open` | Orders with "Open" filter active |
| `/orders/123/lines` | Order lines for order #123 |
| `/orders?id=456` | Orders with record 456 selected |

---

## 🏗️ Architecture Overview

```
┌────────────────────────────────────────────────────────────────┐
│                        Meta Tables                             │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  api_card              api_card_actions       api_card_children│
│  ┌──────────────┐      ┌──────────────┐      ┌──────────────┐ │
│  │ id           │      │ id           │      │ parent       │ │
│  │ name    ◄────┼──────┼─ card_id     │      │ child        │ │
│  │ tablename    │      │ name         │      │ ref          │ │
│  │ basetable    │      │ action       │      │ keycode      │ │
│  │ reducer      │      │ keycode      │      │ reducer      │ │
│  └──────────────┘      │ group_id ◄───┼──┐   └──────────────┘ │
│                        │ sql          │  │                    │
│  api_card_fields       └──────────────┘  │                    │
│  ┌──────────────┐             │          │                    │
│  │ id           │             └──────────┘                    │
│  │ card_id      │           (sub-menus)                       │
│  │ name         │                                             │
│  │ list_order   │                                             │
│  └──────────────┘                                             │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

---

## 🤝 Contributing

Contributions are welcome! 

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🔗 Links

- [TSQL.APP Platform](https://tsql.app)
- [Releases](https://github.com/rhodelta66/tsqlapp-skills/releases)
- [Report Issues](https://github.com/rhodelta66/tsqlapp-skills/issues)

---

<p align="center">
  <i>Built with ❤️ for the TSQL.APP community</i>
</p>
