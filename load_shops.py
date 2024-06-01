import glob
import pandas as pd
import numpy as np
from _datetime import datetime

from pandas import DataFrame

path = r"./source/shop_sale/"
list_of_files = glob.glob(path + '*.{}'.format('csv'))


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
    return df


def calculate_shop_sales(df: pd.DataFrame) -> pd.DataFrame:
    """Funkcja dodaje kolumny do tabeli sprzedażowej"""
    df['shop_zn_all'] = df['shop_zn'] * df['Ilosc']
    df['shop_sn_all'] = df['shop_sn'] * df['Ilosc']
    df['shop_sb_all'] = df['shop_sb'] * df['Ilosc']
    df['marza'] = ((df['shop_sb_all'] - df['shop_zn_all']) / df['shop_sb_all']) * 100
    df = df.round(2)
    return df


def add_sr_name(main_df: pd.DataFrame, second_df: pd.DataFrame) -> pd.DataFrame:
    """Funkcja łączy tabelę sprzedażową z tabelą listy sklepów,
    do tabeli sprzedażowej dodawana jest kolumna z nazwą spółki"""
    temp_df = pd.merge(main_df, second_df[["Shop_ID", "Nazwa_Spolki"]], on='Shop_ID', how="left")
    return temp_df


def reorder_sr_column(df_to_reorder: pd.DataFrame) -> pd.DataFrame:
    """Funkcja przenosi kolumnę nazwy spółki na początek DF"""
    temp_col = df_to_reorder.pop('Nazwa_Spolki')
    df_to_reorder.insert(0, 'Nazwa_Spolki', temp_col)
    return df_to_reorder


def save_turnover_to_sr(sum_df: pd.DataFrame) -> None:
    """Funkcja zapisuje obroty dla Spółek Regionalnych"""
    list_of_sr = sum_df['Nazwa_Spolki'].unique()
    for sr in list_of_sr:
        temp_df = sum_df[sum_df['Nazwa_Spolki'] == sr]
        writer_sr = pd.ExcelWriter(f"./output/SR/{sr}/Obroty_{sr}.xlsx", engine='xlsxwriter',
                                   date_format='%Y-%m-%d',
                                   datetime_format='YYYY-MM-DD')
        temp_df.to_excel(writer_sr, sheet_name="Obroty", index=False)
        writer_sr.close()


def save_report_for_fb(df_sr_ok: pd.DataFrame, df_sr_error: pd.DataFrame) -> None:
    """Funkcja zapisuje wyniki sprzedażowe dla FB z podziałem na dane poprawne i niepoprawne.
    Każdy df zapisywany jest w odrębnej zakładce pliku xlsx"""
    sr_name_and_id = tuple(pd.unique(df_sr_ok[['Nazwa_Spolki', 'Shop_ID']].values.ravel()))
    with pd.ExcelWriter(f'./output/SR/{sr_name_and_id[0]}/FB/{sr_name_and_id[1]}.xlsx', engine='xlsxwriter',
                        date_format='%Y-%m-%d',
                        datetime_format='YYYY-MM-DD') as writer_fb:
        df_sr_ok.to_excel(writer_fb, sheet_name='Dane sprzedażowe poprawne', index=False,
                          header=['Nazwa Spółki', 'ID sklepu', 'Kod EAN', 'Sprzedana ilość', 'Stawka VAT',
                                  'Cena sprzedaży zakup netto', 'Cena sprzedaży brutto', 'Cena sprzedaży netto', 'Data',
                                  'Sprzedaż całkowita w cenie zakupu', 'Sprzedaż całkowita netto',
                                  'Sprzedaż całkowita brutto', 'Marża'])
        if len(df_sr_error) > 0:
            df_sr_error.to_excel(writer_fb, sheet_name='Błędy w danych sprzedażowych', index=False,
                                 header=['Nazwa Spółki', 'ID sklepu', 'Kod EAN', 'Sprzedana ilość', 'Stawka VAT',
                                         'Cena sprzedaży zakup netto', 'Cena sprzedaży brutto', 'Cena sprzedaży netto',
                                         'Data', 'Sprzedaż całkowita w cenie zakupu', 'Sprzedaż całkowita netto',
                                         'Sprzedaż całkowita brutto', 'Marża'])


def level_of_data_completion(level_df: pd.DataFrame) -> pd.DataFrame:
    """Funkcja zapisuje w pliku excel poziom uzupełnienia danych sprzedażowych sklepów za dany miesiąc kalendarzowy."""
    level_df = level_df.drop(columns=['shop_zn_all', 'shop_sb_all', 'shop_sn_all'])
    grouped_data = level_df.groupby(['Shop_ID', 'data', 'Nazwa_Spolki']).count().reset_index()
    pv_table: DataFrame = grouped_data.pivot_table(index='Shop_ID', columns=['data'], aggfunc='count', fill_value=0)
    pv_table.columns = [''.join(str(s).strip().replace('Nazwa_Spolki', '')
                                .replace('00:00:00', '') for s in col if s) for col in pv_table.columns]
    pv_table = pv_table.reset_index()
    final_table = pv_table.merge(grouped_data[['Shop_ID', 'Nazwa_Spolki']])
    order_cols = list(final_table.columns)
    order_cols = [order_cols[-1]] + order_cols[:-1]
    final_table = final_table[order_cols]
    final_table = final_table.drop_duplicates(subset='Shop_ID', keep='last')
    return final_table


def save_completion_report(df_completion: pd.DataFrame) -> None:
    df_completion = df_completion.style.map(lambda x: 'background-color : blue' if x == 1 else ('background-color : red'
                                                                                                if x == 0 else
                                                                                                'background-color : '
                                                                                                'white'))
    df_completion.to_excel('./output/LH/Poziom_uzupelnienia_danych.xlsx', sheet_name='Poziom_danych',
                           index=False)


def load_promotions(file_string: str) -> pd.DataFrame:
    temp_df = pd.read_csv(file_string, sep=',')
    return temp_df


def prepare_promotions_report(promotions_df: pd.DataFrame, sales_dataf: pd.DataFrame) -> None:
    regional_name_and_id = tuple(pd.unique(sales_dataf[['Nazwa_Spolki', 'Shop_ID']].values.ravel()))
    promotions_df = promotions_df[promotions_df['Spolka'] == regional_name_and_id[0]]
    sales_dataf['Kod'] = sales_dataf['Kod'].astype(np.int64)
    promo_cover = pd.merge(promotions_df, sales_dataf[['Nazwa_Spolki', 'Shop_ID', 'Kod', 'shop_sb', 'data']],
                           left_on='EAN produktu', right_on='Kod', how='left')
    promo_cover = promo_cover.fillna('BRAK')
    promo_cover = promo_cover.drop(columns=['Nazwa_Spolki', 'Kod'])
    promo_cover.to_excel(f'./output/SR/{regional_name_and_id[0]}/promocje_{regional_name_and_id[1]}.xlsx',
                         index=False, header=['Typ promocji', 'Nazwa promocji', 'Data od', 'Data do', 'Spółka',
                                              'EAN produktu', 'Cena brutto - półka', 'Status towaru', 'ID Sklepu',
                                              'Cena sprzedaży brutto na sklepie', 'Data sprzedaży na sklepie'])


if __name__ == "__main__":
    print(f"Program uruchomiono: {datetime.now()}")
    summed_turnover = pd.DataFrame()
    list_of_shops = pd.read_csv(f"./source/shop_list/list_of_shops.csv", sep=',')
    for file in list_of_files:
        print(f'Przetwarzam plik: {file}')
        sales_df = load_sales_to_df(file)
        sales_df = calculate_shop_sales(sales_df)
        sales_df['data'] = pd.to_datetime(sales_df['data'], format='yyyy-mm-dd')
        sales_df = add_sr_name(sales_df, list_of_shops)
        sales_df = reorder_sr_column(sales_df)
        df_error = sales_df[sales_df['shop_sb_all'] >= int(10000)]
        sales_df_wo_errors = sales_df.drop(df_error.index, axis=0)
        save_report_for_fb(sales_df_wo_errors, df_error)
        promo_df = load_promotions('./source/shop_promotion/lewiatan_promotions.csv')
        prepare_promotions_report(promo_df, sales_df_wo_errors)
        grouped_values_turnover_per_month = sales_df_wo_errors.groupby(['Nazwa_Spolki', 'Shop_ID', 'data'])[
            ['shop_zn_all', 'shop_sb_all', 'shop_sn_all']].sum().reset_index()
        grouped_values_turnover_per_month = grouped_values_turnover_per_month.round(2)
        temp = pd.concat([summed_turnover, grouped_values_turnover_per_month])
        summed_turnover = temp
    writer = pd.ExcelWriter('./output/LH/Obroty.xlsx', engine='xlsxwriter', date_format='%Y-%m-%d',
                            datetime_format='YYYY-MM-DD')
    summed_turnover.to_excel(writer, sheet_name="Obroty", index=False, header=['Nazwa Spółki', 'ID sklepu', 'Data',
                                                                               'Sprzedaż w cenie zakupu',
                                                                               'Sprzedaż brutto całkowita',
                                                                               'Sprzedaż netto całkowita'])
    writer.close()
    save_turnover_to_sr(summed_turnover)
    lvl_of_completion = (level_of_data_completion(summed_turnover))
    save_completion_report(lvl_of_completion)
    print(f"Program zakończono: {datetime.now()}")
