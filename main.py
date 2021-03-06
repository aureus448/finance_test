"""No-doc"""
import pandas as pd
import yfinance as yf
import datetime
import time
import requests
import io

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # Adapted from somewhere, I'm sorry I forgot original code. Was a jupyter book

    # Input Start and End Date [chose present]
    start = datetime.datetime(2000, 1, 1)

    url = "https://pkgstore.datahub.io/core/nasdaq-listings/nasdaq-listed_csv/data/7665719fb51081ba0bd834fde71ce822" \
          "/nasdaq-listed_csv.csv"
    s = requests.get(url).content
    companies = pd.read_csv(io.StringIO(s.decode('utf-8')))
    Symbols = companies['Symbol'].tolist()

    t0 = time.perf_counter()

    # create empty dataframe
    stock_final = pd.DataFrame()
    removed = 0
    total = len(Symbols)
    file_name = 'test.xlsx'
    # iterate over each symbol
    for i in range(0, len(Symbols), 10):
        # print(i)
        # print(Symbols[i:i+10])
        tickers = Symbols[i:i + 10]
        # print the symbol which is being downloaded
        print(f'{{#{i // 10 + 1:0>3}}} [{time.perf_counter() - t0:=6.2f}s] Beginning Download of {", ".join(tickers)}')

        try:
            # download the stock price
            stock = yf.download(" ".join(tickers), period='max', interval='1mo', progress=False, group_by='ticker')
            if len(stock) > 0:
                # print(f'\tRun {i // 10 + 1} contains data for {len(stock)} points') - uncomment to see original points
                # Remove nulls (dividents/splits are not filtered properly - don't care for now*)
                stock = stock[~stock.isna().all(axis=1) & (stock.index >= datetime.datetime(2000, 1, 1))]
                # Remove tickers with no data in the entire range (bankrupt, removed, who knows)
                stock = stock.loc[:, ~stock.isna().all(axis=0)]

                # print(f'Run {i//10+1} trimmed to {len(stock)} points') - not needed - should always be 261
                stock_num = set(stock.columns.get_level_values(0))
                if len(stock_num) != 10:
                    print(f'\t\t{len(stock_num)} Tickers left after removal of null-data Tickers')
                    removed += 10 - len(stock_num)  # add the diff from expected

                # Set stock list to stock if first set, otherwise merge
                if len(stock_final) == 0:
                    stock_final = stock
                else:
                    # Keep all 261 if poossible - this works (left) because AAPL is in first set
                    # (which has been around since before 2000, so contains all expected data points)
                    stock_final = stock_final.merge(stock, how='outer', left_index=True, right_index=True)

        except Exception as e:
            print(f'Encountered exception: {e}')
    total = time.perf_counter() - t0

    stock_final.to_excel(file_name)
    print(f'Done! Provided {total-removed} tickers in output file: {file_name}')
