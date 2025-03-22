import yfinance as yf

class Analyser:
    ticker = "AAPL"
    period = "3y"
    interval = "1d"

    thresholds = [-5, -4, -3, -2.5, -2, -1.5, -1, -0.5, 0, 0.5, 1, 1.5, 2, 2.5, 3, 4, 5]
    thresholds_for_print = [-2, 2]

    def __init__(self):
        self.set_df()
        self.analyse_losses_thresholds()
        self.analyse_profits_thresholds()
        self.find_threshold_dates()

    def set_df(self):
        df = yf.download(self.ticker, interval=self.interval, period=self.period)
        df["Change"] = ((df["Close"] - df["Open"]) / df["Open"]) * 100
        self.df = df

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
            print(f"Práh {threshold}% byl překročen v těchto dnech: {', '.join(str(date.date()) for date in dates)}")

# Spuštění
analyser = Analyser()
analyser.print_results()