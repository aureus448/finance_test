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

    t0 = time.time()

    # create empty dataframe
    stock_final = pd.DataFrame()

    # iterate over each symbol
    for i in range(0, len(Symbols), 10):
        # print(i)
        # print(Symbols[i:i+10])
        tickers = Symbols[i:i + 10]
        # print the symbol which is being downloaded
        print(f'Beginning Download of {", ".join(tickers)}')

        try:
            # download the stock price
            stock = []
            stock = yf.download(" ".join(tickers), period='max', interval='1mo', progress=False, group_by='ticker')
            if len(stock) > 0:
                print(f'Run {i // 10 + 1} contains data for {len(stock)} points')
                # Remove nulls (dividents/splits are not filtered properly - don't care for now*)
                stock = stock[~stock.isna().all(axis=1) & (stock.index >= datetime.datetime(2000, 1, 1))]
                # Remove tickers with no data in the entire range (bankrupt, removed, who knows)
                stock = stock.loc[:,~stock.isna().all(axis=0)]

                # print(f'Run {i//10+1} trimmed to {len(stock)} points') - not needed - should always be 261
                stock_num = set(stock.columns.get_level_values(0))
                if len(stock_num) != 10:
                    print(f'\t{len(stock_num)} Tickers left after removal of null-data Tickers')

                # Set stock list to stock if first set, otherwise merge
                if len(stock_final) == 0:
                    stock_final = stock
                else:
                    # Keep all 261 if poossible - this works (left) because AAPL is in first set
                    # (which has been around since before 2000, so contains all expected data points)
                    stock_final = stock_final.merge(stock, how='outer', left_index=True, right_index=True)

        except Exception:
            None
        if i == 100:
            break
    t1 = time.time()

    total = t1 - t0

#     # %%
#
#     stock_final.Name.unique()
#.
#     # %%
#
#     len(stock_final)
#
#     # %%
#
#     stock_final.to_excel('stock_final_11Oct2020.xlsx', index=False)
#
#     # %%
#
#     stock_final.Name.nunique()
#
#     # %%
#
#     stock_final.head(10)
#
#     # %%
#
# # See PyCharm help at https://www.jetbrains.com/help/pycharm/
