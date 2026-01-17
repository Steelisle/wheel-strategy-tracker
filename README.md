# Wheel Strategy Options Tracker

A Mac desktop application for tracking options trading positions using the Wheel Strategy (selling cash-secured puts and covered calls).

## Features

- **Dashboard Overview**: Total portfolio value, options P&L summary, year-end projections
- **Position Tracking**: Track positions by ticker with covered call and put premiums
- **Trade Entry**: Manual entry for CSPs, covered calls, assignments, and rolls
- **Charts**: Portfolio value and options income visualization
- **Market Data**: Polygon.io integration for stock prices and options data
- **Market Rankings**: Compare your performance vs major indices
- **Demo Mode**: View sample data to explore the app before entering your own trades

## Installation

```bash
# Navigate to project directory
cd wheel-tracker

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

Or use the launch script:
```bash
./run.sh
```

## Demo vs Active Mode

The app supports two modes, toggled via the button in the top-right corner:

| Mode | Button Color | Description |
|------|--------------|-------------|
| **Active Mode** | Green (📈) | Your real trading data. Starts empty. |
| **Demo Mode** | Yellow (📊) | Sample data to explore the app. |

Each mode uses a separate database, so your real data is never mixed with demo data.

---

## How to Use

### Understanding the Dashboard

The dashboard has several sections:

1. **Premiums Card** (top left)
   - Week X: Premium collected this week (weeks count from your first trade)
   - Month: Premium collected this calendar month
   - YTD: Year-to-date premium
   - Year-End Projection: Estimated annual premium based on current pace

2. **Portfolio Card** (top right)
   - Your investment philosophy and milestones
   - Click ✏️ to edit

3. **Positions Table** (left)
   - All tickers you've traded
   - Covered Call premium, PUT premium, and total per ticker

4. **Portfolio Chart** (center)
   - Visual representation of portfolio value over time

5. **Options Income Chart** (right)
   - Bar chart showing options income by period

6. **Market Rankings** (bottom left)
   - Compare your options performance vs major indices (S&P 500, Nasdaq, etc.)

7. **Top Performers** (bottom right)
   - Your best-performing tickers by premium collected

---

## Adding Trades

### Selling a Cash-Secured Put (CSP)

1. Click **"+ CSP"** button in the top-right
2. Fill in the details:
   - **Ticker**: Stock symbol (e.g., AAPL)
   - **Strike Price**: The strike price of the put
   - **Expiration**: When the option expires
   - **Premium**: Premium received per share (e.g., $1.50)
   - **Contracts**: Number of contracts (1 contract = 100 shares)
   - **Delta**: Optional - the delta when you sold it
3. Click **"Add CSP Trade"**

### Selling a Covered Call

1. Click **"+ Covered Call"** button
2. Fill in the same details as above
3. Click **"Add Covered Call"**

### Recording an Assignment

When a PUT or CALL option gets assigned:

1. Click **"More..."** button
2. Go to the **"Assignment"** tab
3. Fill in:
   - **Ticker**: The stock symbol
   - **Shares**: Number of shares (usually 100 per contract)
   - **Cost Basis**: The strike price (price per share)
   - **Type**: 
     - "PUT Assignment (bought shares)" - You were assigned on a CSP
     - "CALL Assignment (sold shares)" - Your covered call was exercised
4. Click **"Record Assignment"**

### Closing a Trade Early

If you buy back an option before expiration:

1. Click **"More..."** button
2. Go to the **"Close/Roll"** tab
3. Enter the Trade ID and select the status
4. Click **"Close Trade"**

---

## The Wheel Strategy Workflow

The Wheel Strategy is a systematic approach to generating income:

```
┌─────────────────────────────────────────────────────────────────┐
│                        THE WHEEL CYCLE                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. SELL CASH-SECURED PUT                                       │
│     └─> Collect premium                                         │
│         │                                                       │
│         ├─> Option expires worthless → Keep premium, repeat     │
│         │                                                       │
│         └─> Option assigned → You buy shares at strike price    │
│                               │                                 │
│  2. SELL COVERED CALL         │                                 │
│     └─> Collect premium <─────┘                                 │
│         │                                                       │
│         ├─> Option expires worthless → Keep premium, repeat     │
│         │                                                       │
│         └─> Option assigned → Sell shares at strike price       │
│                               │                                 │
│                               └─> Back to step 1                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Example Wheel Cycle in the App

1. **Sell CSP**: AAPL $150 strike, collect $1.50 premium
   - Add via "+ CSP" button
   
2. **PUT Assigned**: AAPL drops below $150, you buy 100 shares
   - Record via "More..." → "Assignment" tab
   - Your cost basis: $150/share (minus the $1.50 premium = $148.50 effective)

3. **Sell Covered Call**: AAPL $155 strike, collect $2.00 premium
   - Add via "+ Covered Call" button

4. **CALL Assigned**: AAPL rises above $155, shares called away
   - Record via "More..." → "Assignment" tab (select "CALL Assignment")

5. **Repeat**: Start over with a new CSP

Throughout this cycle, all premiums are tracked and shown in your dashboard.

---

## Configuring Your Portfolio

Click the ✏️ button on the Portfolio card to set up:

- **Started Investing**: When you began (e.g., "January 2026")
- **Investment Philosophy**: Your approach to investing
- **Milestones**: Portfolio value milestones you've reached
  - Amount (e.g., $10,000)
  - Date reached (e.g., "Mar 2026")
  - Time to reach (e.g., "3 months")

---

## Polygon.io API Integration

The app supports Polygon.io for real-time market data:

| Tier | Features | Cost |
|------|----------|------|
| **Free** | End-of-day prices, ticker search | $0/month |
| **Starter** | Delayed quotes, options chain, Greeks, IV | ~$29/month |
| **Advanced** | Real-time quotes, options chain, Greeks, IV | ~$79/month |
| **Business** | All features + historical options | ~$199/month |

### Setup

1. Get an API key from [polygon.io](https://polygon.io)
2. Click **"⚙️ Settings"** in the app
3. Enter your API key
4. Select your subscription tier
5. Click **"Test Connection"** to verify
6. Click **"Save"**

---

## Data Storage

All data is stored locally in SQLite databases:

- `data/wheel_tracker.db` - Your real trading data (Active Mode)
- `data/demo_data.db` - Sample data (Demo Mode)

### Exporting Data

Go to **File → Export to CSV** to export all trades to a CSV file.

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Cmd+R` | Refresh data |
| `Cmd+1` | Go to Dashboard |
| `Cmd+,` | Open Settings |

---

## Tech Stack

- Python 3.14+
- PySide6 (Qt for Python)
- SQLite for local data storage
- Polygon.io API for market data
