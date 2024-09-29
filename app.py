import pandas as pd
from datetime import timedelta
from flask import Flask, jsonify
app = Flask(__name__)


def read_stocks(filename) -> pd.DataFrame:
    """Reads CSV file and return a DataFrame sorted reverse chronological order."""
    try:
        stocks = pd.read_csv(filename + '.csv', sep=';', parse_dates=['Date'])
        stocks.sort_values(by=['Date'], inplace=True, ascending=False)
    except:
        raise Exception("Could not find CSV-file.")
    return stocks


def get_stocks(df) -> pd.DataFrame:
    """Takes the information of today and yesterday stocks and calculate (if any) ratio between two stocks"""
    today = df['Date'].dt.date.max()
    yesterday = today - timedelta(days=1)
    df['Date'] = df['Date'].dt.date
    stocks_today = df[df['Date'] == today].drop_duplicates(subset='Kod', keep='first')
    stocks_yesterday = df[df['Date'] == yesterday].drop_duplicates(subset='Kod', keep='first')
    stocks_delta = pd.merge(stocks_today, stocks_yesterday, on='Kod', suffixes=('_t', '_y'), how='left')
    stocks_delta['ratio'] = round((stocks_delta['Kurs_t'] / stocks_delta['Kurs_y'] - 1) * 100, 2)
    return stocks_delta


def get_winners(df_delta) -> dict:
    """ Takes the stocks, sorts and sends it back as a dictionary"""
    result = df_delta[['Kod', 'Kurs_t', 'ratio']].sort_values(by=['ratio'], ascending=False, ignore_index=True)[0:3]
    result = result.rename(columns={
        'Kod': 'name',
        'Kurs_t': 'latest',
        'ratio': 'percent'
    })
    result['rank'] = [1, 2, 3]
    result = result[['rank', 'name', 'percent', 'latest']]
    return result.to_dict(orient='records')


@app.route("/winners")
def main():
    stocks = read_stocks('input')
    stocks_delta = get_stocks(stocks)
    winners = get_winners(stocks_delta)
    return jsonify({"winners": winners})


if __name__ == "__main__":
    main()
