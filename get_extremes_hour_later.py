import yfinance as yf
import pandas as pd
from datetime import timedelta

def get_top_moves_from_hour_after_open(ticker: str, period: str, top_n: int = 10):
    # Stažení hodinových dat za zadané období
    data = yf.Ticker(ticker).history(period=period, interval="1h")
    
    # Seznam pro ukládání růstů a poklesů
    all_gains = []
    all_losses = []
    
    # Skupina dat podle jednotlivých dní
    data['Date'] = data.index.date
    daily_groups = data.groupby('Date')
    
    for date, day_data in daily_groups:
        # Vytvoříme naivní timestamp pro 9:30 a pak přidáme časové pásmo
        market_open_naive = pd.Timestamp(date).replace(hour=9, minute=30)
        market_open = pd.Timestamp(market_open_naive, tz='America/New_York')
        one_hour_later = market_open + timedelta(hours=1)  # 10:30 EST
        
        # Najdeme cenu v 10:30 (nebo nejbližší čas po 10:30)
        try:
            start_price_row = day_data[day_data.index >= one_hour_later].iloc[0]
            start_price = start_price_row['Close']
        except IndexError:
            continue  # Pokud data pro 10:30 nebo později chybí, přeskočíme den
        
        # Najdeme high a low ze zbytku dne (po 10:30)
        remaining_day = day_data[day_data.index >= one_hour_later]
        if remaining_day.empty:
            continue
        
        day_high = remaining_day['High'].max()
        day_low = remaining_day['Low'].min()
        
        # Výpočet procentuálního růstu a poklesu
        gain = (day_high - start_price) / start_price * 100
        loss = (start_price - day_low) / start_price * 100
        
        # Uložení výsledků s datem
        all_gains.append((date, gain))
        all_losses.append((date, loss))
    
    # Převedení na DataFrame
    gains_df = pd.DataFrame(all_gains, columns=['Date', 'Gain']).set_index('Date')
    losses_df = pd.DataFrame(all_losses, columns=['Date', 'Loss']).set_index('Date')
    
    # Seřazení a výběr top N
    top_gains = gains_df.nlargest(top_n, 'Gain')
    top_losses = losses_df.nlargest(top_n, 'Loss')
    
    return top_gains, top_losses

# Příklad použití
ticker = "AAPL"  # SPDR S&P 500 ETF
period = "60d"   # 1 rok
top_n = 10      # Top 10 největších pohybů

# Zavolání funkce
gains, losses = get_top_moves_from_hour_after_open(ticker, period, top_n)

# Výpis výsledků
print("Top 10 největších růstů (Gain %) od 10:30:")
print(gains)
print("\nTop 10 největších poklesů (Loss %) od 10:30:")
print(losses)