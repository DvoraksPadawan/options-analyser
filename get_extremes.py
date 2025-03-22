import yfinance as yf

def get_top_moves(ticker: str, period: str, top_n: int = 5):
    # Stažení historických dat
    data = yf.Ticker(ticker).history(period=period)

    # Výpočet růstu a poklesu
    data['Gain'] = (data['High'] - data['Open']) / data['Open'] * 100  # Procentuální růst
    data['Loss'] = (data['Open'] - data['Low']) / data['Open'] * 100   # Procentuální pokles

    # Seřazení podle největšího růstu a poklesu
    top_gains = data[['Gain']].nlargest(top_n, 'Gain')
    top_losses = data[['Loss']].nlargest(top_n, 'Loss')

    return top_gains, top_losses

# Příklad použití
ticker = "AAPL"  # Např. Apple
period = "7y"  # Poslední měsíc
top_n = 10  # Top 5 největších pohybů

gains, losses = get_top_moves(ticker, period, top_n)
print("Top Gains:\n", gains)
print("Top Losses:\n", losses)