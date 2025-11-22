# Key Algorithms and Calculations

## Portfolio Calculations

### 1. Total Investment
**Formula**: `quantity * purchase_price`

**Code Location**: `data/models.py` - Stock.total_investment property

```python
@property
def total_investment(self) -> float:
    return self.quantity * self.purchase_price
```

**Example**:
- Quantity: 100 shares
- Purchase Price: ₹2,200
- Total Investment: 100 × ₹2,200 = ₹220,000

### 2. Current Value
**Formula**: `quantity * current_price`

**Code Location**: `data/models.py` - Stock.current_value property

```python
@property
def current_value(self) -> float:
    if self.current_price is None:
        return 0
    return self.quantity * self.current_price
```

**Example**:
- Quantity: 100 shares
- Current Price: ₹2,500
- Current Value: 100 × ₹2,500 = ₹250,000

### 3. Profit/Loss Amount
**Formula**: `current_value - total_investment`

**Code Location**: `data/models.py` - Stock.profit_loss_amount property

```python
@property
def profit_loss_amount(self) -> float:
    return self.current_value - self.total_investment
```

**Example**:
- Current Value: ₹250,000
- Total Investment: ₹220,000
- Profit/Loss: ₹250,000 - ₹220,000 = ₹30,000 (Profit)

### 4. Profit/Loss Percentage
**Formula**: `(profit_loss_amount / total_investment) × 100`

**Code Location**: `data/models.py` - Stock.profit_loss_percentage property

```python
@property
def profit_loss_percentage(self) -> float:
    if self.total_investment == 0:
        return 0
    return (self.profit_loss_amount / self.total_investment) * 100
```

**Example**:
- Profit/Loss Amount: ₹30,000
- Total Investment: ₹220,000
- Profit/Loss %: (30,000 / 220,000) × 100 = 13.64%

### 5. Days Held
**Formula**: `current_date - purchase_date`

**Code Location**: `data/models.py` - Stock.days_held property

```python
@property
def days_held(self) -> int:
    try:
        purchase_dt = datetime.strptime(self.purchase_date, "%Y-%m-%d")
        return (datetime.now() - purchase_dt).days
    except:
        return 0
```

**Example**:
- Purchase Date: 2023-06-15
- Current Date: 2024-09-17
- Days Held: 460 days

### 6. Annualized Return
**Formula**: `(profit_loss_percentage / days_held) × 365`

**Code Location**: `data/models.py` - Stock.annualized_return property

```python
@property
def annualized_return(self) -> float:
    days = self.days_held
    if days == 0:
        return 0
    return (self.profit_loss_percentage / days) * 365
```

**Example**:
- Profit/Loss %: 13.64%
- Days Held: 460 days
- Annualized Return: (13.64 / 460) × 365 = 10.83%

## Portfolio Summary Calculations

### 1. Portfolio Total Investment
**Formula**: `Σ(quantity × purchase_price)` for all stocks

**Code Location**: `services/calculator.py` - PortfolioCalculator.calculate_portfolio_summary

```python
total_investment = sum(stock.total_investment for stock in stocks)
```

### 2. Portfolio Current Value
**Formula**: `Σ(quantity × current_price)` for all stocks with valid prices

```python
current_value = sum(
    stock.current_value 
    for stock in stocks 
    if stock.current_price is not None
)
```

### 3. Portfolio Profit/Loss
**Formula**: `total_current_value - total_investment`

```python
total_profit_loss = current_value - total_investment
```

### 4. Portfolio Profit/Loss Percentage
**Formula**: `(total_profit_loss / total_investment) × 100`

```python
if total_investment > 0:
    total_profit_loss_percentage = (total_profit_loss / total_investment) * 100
else:
    total_profit_loss_percentage = 0
```

### 5. Best/Worst Performers
**Algorithm**: Find stocks with max/min profit_loss_percentage

```python
valid_stocks = [stock for stock in stocks if stock.current_price is not None]

if valid_stocks:
    best_performer = max(valid_stocks, key=lambda s: s.profit_loss_percentage)
    worst_performer = min(valid_stocks, key=lambda s: s.profit_loss_percentage)
```

## Cash Management Calculations

### 1. Cash Balance
**Formula**: `Σ(deposits) - Σ(withdrawals)`

**Code Location**: Database query in `data/database.py`

```python
deposits = sum(
    t['amount'] 
    for t in transactions 
    if t['transaction_type'] == 'deposit'
)

withdrawals = sum(
    t['amount'] 
    for t in transactions 
    if t['transaction_type'] == 'withdrawal'
)

cash_balance = deposits - withdrawals
```

### 2. Total Expenses
**Formula**: `Σ(expense_amount)` for all expenses

```python
total_expenses = sum(expense['amount'] for expense in expenses)
```

### 3. Remaining Cash
**Formula**: `cash_balance - total_expenses`

```python
remaining_cash = cash_balance - total_expenses
```

### 4. Cash vs Investment Reconciliation
**Two ways to track investment**:

1. **Calculated Investment**: `quantity × purchase_price`
2. **Actual Cash Invested**: `cash_invested` field (may include fees, commissions)

**Difference**: Shows impact of fees/commissions

```python
calculated = stock.quantity * stock.purchase_price
actual = stock.cash_invested
difference = actual - calculated  # Fees/commissions
```

## Tax Calculations

### 1. Holding Period Classification
**Rule**: 
- Short-Term Capital Gains (STCG): Held < 1 year (< 365 days)
- Long-Term Capital Gains (LTCG): Held ≥ 1 year (≥ 365 days)

**Code**:
```python
days_held = (datetime.now() - purchase_date).days

if days_held >= 365:
    tax_type = 'LTCG'
else:
    tax_type = 'STCG'
```

### 2. Indian Tax Rates (Built-in)
**STCG Rate**: 15.6% (15% base + surcharge/cess)
**LTCG Rate**: 10.4% (10% base + surcharge/cess) above ₹1 lakh exemption

**Code**:
```python
STCG_RATE = 0.156  # 15.6%
LTCG_RATE = 0.104  # 10.4%
LTCG_EXEMPTION = 100000  # ₹1 lakh
```

### 3. Tax Liability Calculation

**STCG Tax**:
```python
def calculate_stcg_tax(gain: float) -> float:
    if gain <= 0:
        return 0
    return gain * STCG_RATE
```

**LTCG Tax** (with exemption):
```python
def calculate_ltcg_tax(gain: float) -> float:
    if gain <= 0:
        return 0
    
    taxable_gain = max(0, gain - LTCG_EXEMPTION)
    return taxable_gain * LTCG_RATE
```

**Example**:
- LTCG Gain: ₹2,50,000
- Exemption: ₹1,00,000
- Taxable Gain: ₹1,50,000
- Tax: ₹1,50,000 × 10.4% = ₹15,600

### 4. Potential Tax if Sold Today
**Algorithm**:
```python
def calculate_tax_if_sold_today(stock: Stock, current_price: float) -> float:
    # Calculate gain
    current_value = stock.quantity * current_price
    gain = current_value - stock.total_investment
    
    # Determine tax type
    days_held = (datetime.now() - stock.purchase_date).days
    
    if days_held < 365:
        # STCG
        return gain * STCG_RATE if gain > 0 else 0
    else:
        # LTCG with exemption
        taxable_gain = max(0, gain - LTCG_EXEMPTION)
        return taxable_gain * LTCG_RATE
```

## Dividend Calculations

### 1. Total Dividend
**Formula**: `dividend_per_share × shares_held`

```python
total_dividend = dividend_per_share * shares_held
```

### 2. Net Dividend (After Tax)
**Formula**: `total_dividend - tax_deducted`

```python
net_dividend = total_dividend - tax_deducted
```

**Example**:
- Dividend per share: ₹10
- Shares held: 100
- Total dividend: ₹1,000
- TDS (10%): ₹100
- Net dividend: ₹900

### 3. Dividend Yield
**Formula**: `(annual_dividend_per_share / current_price) × 100`

```python
def calculate_dividend_yield(
    annual_dividend_per_share: float, 
    current_price: float
) -> float:
    if current_price == 0:
        return 0
    return (annual_dividend_per_share / current_price) * 100
```

**Example**:
- Annual dividend per share: ₹20
- Current price: ₹2,500
- Dividend yield: (20 / 2,500) × 100 = 0.8%

## Corporate Action Adjustments

### 1. Stock Split Adjustment
**Formula**:
- New quantity: `old_quantity × (ratio_to / ratio_from)`
- New price: `old_price × (ratio_from / ratio_to)`

**Example - 1:2 Split**:
```python
# Before: 100 shares @ ₹2,400
ratio_from = 1
ratio_to = 2

new_quantity = 100 * (2 / 1) = 200 shares
new_price = 2400 * (1 / 2) = ₹1,200

# After: 200 shares @ ₹1,200
# Investment unchanged: 100 × 2,400 = 200 × 1,200 = ₹240,000
```

### 2. Bonus Issue Adjustment
**Formula**: Same as stock split
- Bonus 1:1 means ratio_from=1, ratio_to=2

**Example - 1:1 Bonus**:
```python
# Before: 100 shares @ ₹2,400
# Bonus 1:1 (for every 1 share, get 1 free share)

new_quantity = 100 * (2 / 1) = 200 shares
new_price = 2400 * (1 / 2) = ₹1,200

# After: 200 shares @ ₹1,200
```

### 3. Rights Issue
**Not automatically adjusted** - requires user action
- User must decide whether to exercise rights
- Additional purchase at discounted price

## Risk Metrics (Advanced Features)

### 1. Portfolio Concentration
**Formula**: `(stock_value / portfolio_value) × 100`

```python
def calculate_concentration(stock_value: float, portfolio_value: float) -> float:
    if portfolio_value == 0:
        return 0
    return (stock_value / portfolio_value) * 100
```

### 2. Sector Allocation
**Algorithm**: Group stocks by sector, sum values

```python
sector_allocation = {}
for stock in stocks:
    sector = stock.sector or 'Unknown'
    sector_allocation[sector] = sector_allocation.get(sector, 0) + stock.current_value

# Convert to percentages
total = sum(sector_allocation.values())
sector_percentages = {
    sector: (value / total) * 100 
    for sector, value in sector_allocation.items()
}
```

### 3. Risk Score (Template-based)
**Simplified Algorithm**:
```python
def calculate_risk_score(portfolio: Dict) -> float:
    risk_score = 0
    
    # Concentration risk (max 40 points)
    max_concentration = max(stock['concentration'] for stock in portfolio['stocks'])
    risk_score += min(max_concentration, 40)
    
    # Diversification (max 30 points, inverse)
    num_stocks = len(portfolio['stocks'])
    risk_score += max(30 - num_stocks * 2, 0)
    
    # Volatility estimate (max 30 points)
    avg_volatility = sum(stock.get('volatility', 15) for stock in portfolio['stocks']) / num_stocks
    risk_score += min(avg_volatility, 30)
    
    return risk_score  # 0-100 scale
```

## Price Fetching Optimization

### 1. Batch vs Individual Fetching
**Decision Algorithm**:
```python
def should_use_batch(num_symbols: int) -> bool:
    # Use batch if more than 5 symbols
    return num_symbols > 5

def get_prices(symbols: List[str]) -> Dict[str, float]:
    if should_use_batch(len(symbols)):
        return batch_fetch(symbols)
    else:
        return {symbol: individual_fetch(symbol) for symbol in symbols}
```

### 2. Cache Staleness Check
**Algorithm**:
```python
def is_cache_stale(last_updated: str, threshold_minutes: int = 15) -> bool:
    last_update = datetime.fromisoformat(last_updated)
    age = datetime.now() - last_update
    return age.total_seconds() > (threshold_minutes * 60)
```

### 3. Rate Limiting
**Token Bucket Algorithm**:
```python
def _rate_limit(self):
    current_time = time.time()
    time_since_last = current_time - self.last_request_time
    
    if time_since_last < self.min_request_interval:
        sleep_time = self.min_request_interval - time_since_last
        time.sleep(sleep_time)
    
    self.last_request_time = time.time()
```

## Rebalancing Algorithms (Advanced)

### 1. Equal Weight Strategy
**Target**: Each stock should be equal percentage of portfolio

```python
def equal_weight_rebalancing(stocks: List[Stock]) -> Dict:
    num_stocks = len(stocks)
    target_percentage = 100 / num_stocks
    
    total_value = sum(stock.current_value for stock in stocks)
    
    recommendations = []
    for stock in stocks:
        current_percentage = (stock.current_value / total_value) * 100
        target_value = total_value * (target_percentage / 100)
        
        difference = target_value - stock.current_value
        
        if abs(difference) > (total_value * 0.01):  # 1% threshold
            recommendations.append({
                'symbol': stock.symbol,
                'action': 'buy' if difference > 0 else 'sell',
                'amount': abs(difference),
                'reason': f'Rebalance to {target_percentage:.1f}%'
            })
    
    return recommendations
```

### 2. Risk Parity Strategy
**Target**: Equal risk contribution from each stock

```python
def risk_parity_allocation(stocks: List[Stock], volatilities: Dict[str, float]) -> Dict:
    # Inverse volatility weighting
    inverse_vols = {s.symbol: 1 / volatilities.get(s.symbol, 1) for s in stocks}
    total_inverse = sum(inverse_vols.values())
    
    target_weights = {
        symbol: (inv_vol / total_inverse) * 100 
        for symbol, inv_vol in inverse_vols.items()
    }
    
    return target_weights
```
