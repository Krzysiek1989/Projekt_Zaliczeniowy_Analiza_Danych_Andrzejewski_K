import glob
import pandas as pd

path = r"./source/shop_sale/"
list_of_files = glob.glob(path+'*.{}'.format('csv'))


def load_sales_to_df(file_name: path) -> pd.DataFrame:
    """Funkcja wczytuje dane z pliku CSV do zmiennej DataFrame"""
    df = pd.read_csv(file_name, sep=',', dtype={
        'Shop_ID': 'int',
        'Kod': 'object',
        'Ilosc': 'float',
        'StawkaVAT': 'float',
        'shop_zn': 'float',
        'shop_sb': 'float',
        'shop_sn': 'float',
    }, parse_dates=['data'], index_col=0, date_format='%Y-%m-%d')
    df['shop_zn_all'] = df['shop_zn'] * df['Ilosc']
    df['shop_sb_all'] = df['shop_sb'] * df['Ilosc']
    df['shop_sn_all'] = df['shop_sn'] * df['Ilosc']
    df['marza'] = ((df['shop_sb_all'] - df['shop_zn_all']) / df['shop_sb_all']) * 100
    df = df.round(2)
    return df


if __name__ == "__main__":
    summed_turnover = pd.DataFrame()
    for file in list_of_files:
        print(f'Przetwarzam plik: {file}')
        sales_df = load_sales_to_df(file)
        sales_df['data'] = pd.to_datetime(sales_df['data'])
        df_error = sales_df[sales_df['shop_sb_all'] >= int(10000)]
        sales_df_wo_errors = sales_df.drop(df_error.index, axis=0)
        grouped_values_turnover_per_month = sales_df_wo_errors.groupby(['Shop_ID', 'data'])[
            ['shop_zn_all', 'shop_sb_all', 'shop_sn_all']].sum().reset_index()
        grouped_values_turnover_per_month = grouped_values_turnover_per_month.round(2)
        temp = pd.concat([summed_turnover, grouped_values_turnover_per_month])
        summed_turnover = temp
    writer = pd.ExcelWriter('./output/LH/Obroty.xlsx', engine='xlsxwriter', date_format='%Y-%m-%d')
    summed_turnover.to_excel(writer, sheet_name="Obroty", index=False)
    writer.close()
