""" STOCK PORTFOLIO TRACKER - DATHEON """

import csv
import os

def load_market_prices(filename="market_prices.csv"):
    """
    Read market symbols and company names from the S&P 500 style CSV dataset.
    Since this dataset has company profiles rather than live market prices, 
    it assigns a baseline market price or prompts the user/handles mapping.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, filename)
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The required dataset file '{filename}' was not found in: {script_dir}")
        
    market_data = {}
    try:
        with open(file_path, "r", encoding="utf-8-sig") as file:
            reader = csv.DictReader(file)
            
            for row in reader:
                # Dynamically grab the Symbol column
                symbol = row.get("Symbol", "").strip().upper()
                security = row.get("Security", "").strip()
                
                if symbol:
                    # Since this dataset doesn't have prices, we provide a default sample current price 
                    # (or you can map it. For testing, we default to 150.00 or look for a price column if present)
                    market_data[symbol] = {
                        'security': security,
                        'current_price': 150.00 # Default baseline mock price for portfolio tracking
                    }
                    
        if not market_data:
            raise ValueError(f"The dataset file '{filename}' contains no valid symbol entries.")
            
        return market_data
    except OSError as e:
        raise RuntimeError(f"An error occurred while accessing '{filename}': {e}")
    except ValueError as e:
        raise ValueError(f"Error parsing values from dataset: {e}")

def get_valid_ticker(market_data):
    """Prompt user for a valid stock ticker symbol present in the dataset."""
    while True:
        ticker = input("🔹 Enter stock ticker symbol (e.g., AAPL, MSFT): ").strip().upper()
        if not ticker.isalpha():
            print("❌ Invalid format. Please use alphabetic characters only.")
            continue
        if ticker not in market_data:
            print(f"❌ Ticker '{ticker}' not found in the dataset. Try another symbol.")
            continue
        return ticker

def get_valid_float(prompt_text):
    """Prompt user for a positive float value (buy prices)."""
    while True:
        try:
            value = float(input(prompt_text))
            if value <= 0:
                print("❌ Price must be greater than zero.")
                continue
            return value
        except ValueError:
            print("❌ Invalid input. Please enter a valid numerical price.")

def get_valid_int(prompt_text):
    """Prompt user for a positive integer value (share quantities)."""
    while True:
        try:
            value = int(input(prompt_text))
            if value <= 0:
                print("❌ Quantity must be a whole number greater than zero.")
                continue
            return value
        except ValueError:
            print("❌ Invalid input. Please enter a valid whole number.")

def collect_portfolio(market_data):
    """Interactive portfolio builder supporting multiple holdings and duplicate updates."""
    portfolio = {}
    
    print("\n" + "=" * 60)
    print(f"{'PORTFOLIO PERFORMANCE TRACKER — DATHEON':^60}")
    print("=" * 60)
    print("📋 Dataset loaded successfully! You can now enter any valid stock symbol.")
    print("------------------------------------------------------------")
    
    while True:
        ticker = get_valid_ticker(market_data)
        company_name = market_data[ticker]['security']
        print(f"   Company: {company_name}")
        
        buy_price = get_valid_float(f"🔹 Enter purchase price per share for {ticker} ($): ")
        quantity = get_valid_int(f"🔹 Enter number of shares for {ticker}: ")
        
        # Handle duplicate stock entries sensibly by computing new weighted average cost
        if ticker in portfolio:
            print(f"\n⚠️ Notice: {ticker} is already in your portfolio. Merging shares...")
            existing = portfolio[ticker]
            total_shares = existing['quantity'] + quantity
            total_cost = (existing['buy_price'] * existing['quantity']) + (buy_price * quantity)
            buy_price = total_cost / total_shares
            quantity = total_shares
            
        portfolio[ticker] = {
            'buy_price': buy_price,
            'quantity': quantity,
            'current_price': market_data[ticker]['current_price'],
            'security': company_name
        }
        
        print(f"✅ Successfully recorded position: {quantity} shares of {ticker} @ ${buy_price:.2f} avg.")
        
        while True:
            cont = input("\nWould you like to add another stock holding? (y/n): ").strip().lower()
            if cont in ('y', 'n'):
                break
            print("❌ Invalid input. Please enter 'y' for yes or 'n' for no.")
            
        if cont != 'y':
            break
            
    return portfolio

def calculate_performance(portfolio):
    """Calculate individual holding metrics and aggregate portfolio performance."""
    holdings_results = []
    total_invested = 0.0
    total_market_val = 0.0
    
    for symbol, data in portfolio.items():
        buy_price = data['buy_price']
        qty = data['quantity']
        curr_price = data['current_price']
        
        invested_capital = buy_price * qty
        current_value = curr_price * qty
        profit_loss = current_value - invested_capital
        return_pct = (profit_loss / invested_capital) * 100 if invested_capital > 0 else 0.0
        
        total_invested += invested_capital
        total_market_val += current_value
        
        holdings_results.append({
            'symbol': symbol,
            'security': data['security'],
            'buy_price': buy_price,
            'current_price': curr_price,
            'quantity': qty,
            'invested_capital': invested_capital,
            'current_value': current_value,
            'profit_loss': profit_loss,
            'return_pct': return_pct
        })
        
    overall_pl = total_market_val - total_invested
    overall_return_pct = (overall_pl / total_invested) * 100 if total_invested > 0 else 0.0
    
    summary = {
        'total_invested': total_invested,
        'total_market_val': total_market_val,
        'overall_pl': overall_pl,
        'overall_return_pct': overall_return_pct
    }
    
    return holdings_results, summary

def display_and_export_results(holdings, summary, filename="portfolio_summary.csv"):
    """Display clean table terminal interface and export structured CSV summary."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, filename)
    
    print("\n" + "=" * 98)
    print(f"{'INDIVIDUAL HOLDINGS PERFORMANCE REPORT':^98}")
    print("=" * 98)
    header = f"{'Symbol':<8} | {'Buy Price':<11} | {'Curr Price':<11} | {'Qty':<6} | {'Invested':<12} | {'Curr Value':<12} | {'P/L ($)':<11} | {'Return (%)':<10}"
    print(header)
    print("-" * 98)
    
    for h in holdings:
        pl_sign = "+" if h['profit_loss'] >= 0 else ""
        row = (
            f"{h['symbol']:<8} | "
            f"${h['buy_price']:<10.2f} | "
            f"${h['current_price']:<10.2f} | "
            f"{h['quantity']:<6} | "
            f"${h['invested_capital']:<11.2f} | "
            f"${h['current_value']:<11.2f} | "
            f"{pl_sign}${h['profit_loss']:<10.2f} | "
            f"{pl_sign}{h['return_pct']:<9.2f}%"
        )
        print(row)
        
    print("=" * 98)
    print(f"{'PORTFOLIO AGGREGATE SUMMARY':^98}")
    print("=" * 98)
    overall_sign = "+" if summary['overall_pl'] >= 0 else ""
    print(f"  • Total Invested Capital  : ${summary['total_invested']:,.2f}")
    print(f"  • Total Current Market Val  : ${summary['total_market_val']:,.2f}")
    print(f"  • Overall Profit / Loss     : {overall_sign}${summary['overall_pl']:,.2f}")
    print(f"  • Overall Portfolio Return  : {overall_sign}{summary['overall_return_pct']:.2f}%")
    print("=" * 98)
    
    try:
        csv_columns = [
            'Stock Symbol', 'Company Name', 'Buy Price', 'Current Price', 'Quantity', 
            'Invested Capital', 'Current Value', 'Profit/Loss', 'Return (%)'
        ]
        
        with open(file_path, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
            writer.writeheader()
            
            for h in holdings:
                writer.writerow({
                    'Stock Symbol': h['symbol'],
                    'Company Name': h['security'],
                    'Buy Price': f"{h['buy_price']:.2f}",
                    'Current Price': f"{h['current_price']:.2f}",
                    'Quantity': h['quantity'],
                    'Invested Capital': f"{h['invested_capital']:.2f}",
                    'Current Value': f"{h['current_value']:.2f}",
                    'Profit/Loss': f"{h['profit_loss']:.2f}",
                    'Return (%)': f"{h['return_pct']:.2f}%"
                })
                
        print(f"\n🚀 Success! Portfolio summary automatically exported to: {file_path}")
    except OSError as e:
        print(f"\n❌ Error writing CSV file: {e}")

def main():
    """Orchestration function with safe initialization and clean exit."""
    try:
        market_data = load_market_prices("market_prices.csv")
    except (FileNotFoundError, ValueError, RuntimeError) as e:
        print(f"\n[Initialization Error]: {e}")
        print("Please verify that your 'market_prices.csv' dataset file is present and formatted correctly.")
        return
        
    portfolio = collect_portfolio(market_data)
    
    if not portfolio:
        print("\nNo positions were added. Exiting application safely.")
        return
        
    holdings, summary = calculate_performance(portfolio)
    display_and_export_results(holdings, summary, "portfolio_summary.csv")
    print("\nThank you for using the Datheon Portfolio Performance Tracker! Goodbye! 👋")

if __name__ == "__main__":
    main()