# 💸 Personal Finance Dashboard
A modern, spreadsheet-style personal finance dashboard built with Streamlit to help users understand where their money is going, how much flexibility they actually have each month, and what their true emergency minimum looks like.

Designed to feel calm, readable, and practical, NOT overwhelming.

## ✨ Features
### Monthly Cash Flow
- Track income, fixed expenses, variable expenses, and saving/investing
- Automatic calculations for:
  - Net income
  - Total expenses
  - Leftover cash
  - Safe-to-spend

### Summary
- Summary card highlighting the most important numbers
- Clear visual hierarchy so you can immediately see:
  - What’s coming in
  - What’s going out
  - What you actually have to work with

### Emergency Minimum
- Estimates the minimum monthly amount needed if income stops
- Automatically includes:
  - Fixed bills (housing, insurance, phone, etc.)
  - Essentials (groceries, utilities, transportation)
  - Required debt payments
- Calculates 3, 6, and 12 month emergency fund targets

### Net Worth Tracking
- Track assets and liabilities side by side
- Automatic net worth calculation
- Optional detailed debt breakdown (balances, APRs, minimum payments)

### Export & Snapshots
- Download a full snapshot of your data as JSON
- Export monthly cash flow tables and net worth tables as CSV
- Useful for backups, analysis, or importing elsewhere

## Design Philosophy
- Modern dark UI that’s easy on the eyes
- Subtle contrast and grouping instead of loud colors
- Clear language over technical finance jargon
- Focused on clarity, not complexity

This tool is meant to support decision-making, not add stress.

## How Calculations Work
**Net Income**
- Uses entered income
- Optionally estimates taxes if income is entered as gross

**Expenses**
- Fixed & variable expenses are summed monthly

**Left Over**
- Net income − expenses − saving/investing

**Emergency Minimum**
- Fixed expenses
- + Essential variable expenses (auto-detected by category name)  
- + Minimum debt payments  

> The emergency minimum is intentionally conservative. It represents survival-level spending, not comfort.