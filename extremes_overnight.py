import yfinance as yf

def get_top_moves(ticker: str, period: str, top_n: int = 5):
    # Stažení historických dat
    data = yf.Ticker(ticker).history(period=period)

    # Přidání sloupce s předchozím zavíracím kurzem
    data['Prev_Close'] = data['Close'].shift(1)

    # Výpočet růstu a poklesu relativně k předchozímu Close
    data['Gain'] = (data['High'] - data['Prev_Close']) / data['Prev_Close'] * 100
    data['Loss'] = (data['Prev_Close'] - data['Low']) / data['Prev_Close'] * 100

    # Seřazení podle největšího růstu a poklesu
    top_gains = data[['Gain']].nlargest(top_n, 'Gain')
    top_losses = data[['Loss']].nlargest(top_n, 'Loss')

    return top_gains, top_losses

# Příklad použití
ticker = "AAPL"  # Např. Apple
period = "2y"  # Posledních 7 let
top_n = 10  # Top 10 největších pohybů

gains, losses = get_top_moves(ticker, period, top_n)
print("Top Gains:\n", gains)
print("Top Losses:\n", losses)
