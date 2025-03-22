import yfinance as yf
import pandas as pd

def calculate_avg_candle_change(ticker: str, period: str = "1y", interval: str = "30m", top_n: int = 20):
    # Stažení 30minutových dat za uplynulý rok
    data = yf.Ticker(ticker).history(period=period, interval=interval)
    
    # Přidání sloupce s datem pro seskupení podle dní
    data['Date'] = data.index.date
    
    # Přidání sloupce s pořadím svíčky během dne
    data['Candle_Number'] = data.groupby('Date').cumcount() + 1
    
    # Výpočet procentuální změny (absolutní hodnota) mezi Open a Close každé svíčky
    data['Abs_Change'] = abs((data['Close'] - data['Open']) / data['Open']) * 100
    
    # Seskupení podle pořadí svíčky a výpočet průměru
    avg_change_by_candle = data.groupby('Candle_Number')['Abs_Change'].mean()
    
    # Získání 20 největších změn pro každou svíčku
    top_changes_by_candle = data.groupby('Candle_Number').apply(
        lambda x: x.nlargest(top_n, 'Abs_Change')[['Date', 'Abs_Change']]
    )
    
    return avg_change_by_candle, top_changes_by_candle

# Příklad použití
ticker = "AAPL"  # SPDR S&P 500 ETF
period = "60d"  # 60 dní (max pro intradenní data v yfinance)
interval = "1h"
top_n = 20      # Počet největších změn

# Zavolání funkce
avg_changes, top_changes = calculate_avg_candle_change(ticker, period, interval, top_n)

# Výpis průměrných změn
print("Průměrná absolutní změna ceny (%) podle pořadí 30minutové svíčky během dne:")
for candle_num, avg_change in avg_changes.items():
    print(f"Svíčka {candle_num}: {avg_change:.2f}%")

# Výpis maximální a minimální průměrné změny
max_change = avg_changes.max()
max_candle = avg_changes.idxmax()
min_change = avg_changes.min()
min_candle = avg_changes.idxmin()
print(f"\nNejvětší průměrná změna: {max_change:.2f}% (Svíčka {max_candle})")
print(f"Nejmenší průměrná změna: {min_change:.2f}% (Svíčka {min_candle})")

# Výpis 20 největších změn pro každou svíčku
print("\n20 největších změn pro každou svíčku:")
for candle_num in top_changes.index.get_level_values('Candle_Number').unique():
    print(f"\nSvíčka {candle_num}:")
    candle_data = top_changes.loc[candle_num].reset_index(drop=True)
    for i, row in candle_data.iterrows():
        print(f"  {row['Date']}: {row['Abs_Change']:.2f}%")
