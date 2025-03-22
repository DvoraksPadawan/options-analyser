import yfinance as yf
import pandas as pd

class Analyser:
    ticker = "AAPL"
    period = "1y"
    interval = "1h"  # Použití hodinového intervalu

    thresholds = [-5, -4, -3, -2.5, -2, -1.5, -1, -0.5, 0, 0.5, 1, 1.5, 2, 2.5, 3, 4, 5]
    thresholds_for_print = [-1.5, 1.5]

    def __init__(self):
        self.set_df()
        self.analyse_losses_thresholds()
        self.analyse_profits_thresholds()
        self.find_threshold_dates()

    def set_df(self):
        df = yf.download(self.ticker, interval=self.interval, period=self.period)

        # Zobrazení prvních několika řádků, abychom zjistili správné názvy sloupců
        print(df.head())

        # Pokud má DataFrame víceúrovňové sloupce, použijeme správné názvy
        if isinstance(df.columns, pd.MultiIndex):
            df = df.xs(self.ticker, level=1, axis=1)  # Získáme správné sloupce pro ticker 'SPY'

        # Převod indexu na datetime a přidání sloupce s datem bez času
        df.index = pd.to_datetime(df.index)
        df["Date"] = df.index.date

        # Odstranění první obchodní hodiny každého dne
        first_hours = df.groupby("Date").head(1).index  # Najdi první hodinu každého dne
        df = df.drop(first_hours)  # Odstraň první hodinu

        # Znovu seskupit podle dnů, aby se dopočítaly nové denní Open a Close
        daily_data = df.groupby("Date").agg({"Open": "first", "Close": "last"})

        # Spočítání procentuální změny
        daily_data["Change"] = ((daily_data["Close"] - daily_data["Open"]) / daily_data["Open"]) * 100
        self.df = daily_data

    def analyse_losses_thresholds(self):
        self.loss_stats = {}
        for threshold in self.thresholds:
            adjusted_losses = self.df["Change"].copy()
            adjusted_losses[adjusted_losses > threshold] = 0
            adjusted_losses[adjusted_losses <= threshold] = adjusted_losses - threshold
            
            count = (self.df["Change"] <= threshold).sum()
            average_loss = adjusted_losses.mean()
            
            self.loss_stats[threshold] = {"count": count, "avg_loss": average_loss}

    def analyse_profits_thresholds(self):
        self.profit_stats = {}
        for threshold in self.thresholds:
            adjusted_profits = self.df["Change"].copy()
            adjusted_profits[adjusted_profits < threshold] = 0
            adjusted_profits[adjusted_profits >= threshold] = adjusted_profits - threshold
            
            count = (self.df["Change"] >= threshold).sum()
            average_profit = adjusted_profits.mean()
            
            self.profit_stats[threshold] = {"count": count, "avg_profit": average_profit}

    def find_threshold_dates(self):
        self.threshold_dates = {}
        for threshold in self.thresholds_for_print:
            dates = self.df[self.df["Change"] <= threshold].index.tolist() if threshold < 0 else self.df[self.df["Change"] >= threshold].index.tolist()
            self.threshold_dates[threshold] = dates

    def print_results(self):
        print(self.period)
        for threshold, stats in self.loss_stats.items():
            print(f"Pokles alespoň o {threshold}%: {stats['count']}x, průměrný pokles: {stats['avg_loss']:.5f}%")
        for threshold, stats in self.profit_stats.items():
            print(f"Nárůst alespoň o {threshold}%: {stats['count']}x, průměrný nárůst: {stats['avg_profit']:.5f}%")
        
        print("\nData překročení prahů:")
        for threshold, dates in self.threshold_dates.items():
            print(f"Práh {threshold}% byl překročen v těchto dnech: {', '.join(str(date) for date in dates)}")

# Spuštění
analyser = Analyser()
analyser.print_results()