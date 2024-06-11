import io
from pathlib import Path

import pandas as pd
import seaborn as sns
import matplotlib as plt
import matplotlib.pyplot as plty
import os
import xlsxwriter


def load_df_from_csv(path: os.path) -> pd.DataFrame:
    """Funkcja zaczytuje dane do tabeli z pliku CSV"""
    temp = pd.read_csv(path, sep=',')
    return temp


def clean_shop_df(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Oczyszczam tabelę sklepów z wierszy które zawierają puste wartości we wskazanych kolumnach"""
    temp = dataframe.dropna(subset=['data_wstapienia', 'Nazwa_Spolki', 'Format_Sklepu'])
    return temp


def format_and_fill_shop_list_df(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Funkcja formatuje poszczególne kolumny jako kategorie oraz dodaje nowe kolumny na podstawie istniejących
    kolumn"""
    dataframe['Nazwa_Spolki'] = dataframe['Nazwa_Spolki'].astype('category')
    dataframe['Format_Sklepu'] = dataframe['Format_Sklepu'].astype('category')
    dataframe['data_wstapienia'] = pd.to_datetime(dataframe['data_wstapienia'])
    dataframe['data_wystapienia'] = pd.to_datetime(dataframe['data_wystapienia'])
    dataframe['ws_year'] = pd.DatetimeIndex(dataframe['data_wstapienia']).year
    dataframe['ws_month'] = pd.DatetimeIndex(dataframe['data_wstapienia']).month
    dataframe['wy_year'] = pd.DatetimeIndex(dataframe['data_wystapienia']).year
    dataframe['wy_month'] = pd.DatetimeIndex(dataframe['data_wystapienia']).month
    dataframe['ws_year'] = dataframe['ws_year'].astype("Int64")
    dataframe['ws_month'] = dataframe['ws_month'].astype("Int64")
    dataframe['wy_year'] = dataframe['wy_year'].astype("Int64")
    dataframe['wy_month'] = dataframe['wy_month'].astype("Int64")
    return dataframe


def generate_active_shop_graph(df: pd.DataFrame) -> None:
    """Skrypt generuje listę aktywnych sklepów, graf ze wskazaniem ilości aktywnych sklepów per spółka oraz udział
    formatu sklepu w strukturze per spółka"""
    print("Tworzę plik z listą aktywnych sklepów. ")
    wrkbook = xlsxwriter.Workbook(f'./output/LH'
                                  '/Aktywne-sklepy-sieci-Lewiatan.xlsx', {"nan_inf_to_errors": True})
    fig, ax = plt.pyplot.subplots(figsize=(10, 10))
    ax.set(xlabel='Ilość aktywnych sklepów', ylabel='Nazwa Spółki')
    ax.set_title(f"Ilość aktywnych sklepów w spółkach sieci Lewiatan")
    sns.countplot(y='Nazwa_Spolki', data=df[pd.isnull(df['data_wystapienia']) & pd.notnull(df['data_wstapienia'])],
                  order=df.Nazwa_Spolki.value_counts().index.sort_values(ascending=True))
    for container in ax.containers:
        ax.bar_label(container)
    worksheet = wrkbook.add_worksheet('Lista-aktywnych-sklepów')
    imgdata = io.BytesIO()
    fig.savefig(imgdata, format='png')
    worksheet.insert_image(0, 14, '', {'image_data': imgdata})
    temp_df = df[pd.isnull(df['data_wystapienia']) & pd.notnull(df['data_wstapienia'])]
    temp_df = temp_df.drop(columns=['ws_year', 'ws_month', 'wy_year', 'wy_month'])
    temp_df['data_wystapienia'] = temp_df['data_wystapienia'].astype(object).where(
        temp_df['data_wystapienia'].notnull(), None)
    (max_row, max_col) = temp_df.shape
    kolumny = ['ID Sklepu', 'Nazwa Sklepu', 'Nazwa Spółki', 'Format sklepu',
               'Powierzchnia Sali', 'Powierzchnia Ogółem', 'Ilość Kas', 'Data wstąpienia', 'Data wystąpienia',
               'Liczba Pracowników', 'Liczba Uczniow', 'Program Magazynowy', 'Standard promocji']
    column_settings = [{"header": column} for column in kolumny]
    worksheet.add_table(0, 0, max_row, max_col-1,
                        {"columns": column_settings, "data": temp_df.values.tolist()})
    formatdict = {'num_format': 'yyyy-mm-dd'}
    fmt = wrkbook.add_format(formatdict)
    worksheet.set_column('H:I', None, fmt)
    plt.pyplot.close(fig)
    lista_sr = df['Nazwa_Spolki'].unique()
    for sr in lista_sr:
        worksheet = wrkbook.add_worksheet(f"Formaty_{sr}")
        temp = temp_df[temp_df['Nazwa_Spolki'] == sr]
        total = temp['Format_Sklepu'].value_counts().values.sum()

        def fmt(x):
            return '{:.1f}%\n{:.0f}'.format(x, total * x / 100)

        plt.pyplot.figure(figsize=(10, 10))
        print(f"Tworzę graf kołowy dla Spółki {sr}")
        plt.pyplot.pie(temp['Format_Sklepu'].value_counts(), autopct=fmt,
                       textprops={'fontsize': 13}, labels=temp['Format_Sklepu'].value_counts().index, startangle=90)
        plt.pyplot.title(f'Lewiatan {sr} struktura aktywnych sklepów według formatu.')
        plt.pyplot.legend(temp['Format_Sklepu'].unique(), loc='upper left', title='Formaty sklepów')
        imgdata = io.BytesIO()
        plt.pyplot.savefig(imgdata, format='png')
        worksheet.insert_image(0, 0, '', {'image_data': imgdata})
        save_copy_for_sr(sr, imgdata, 'Aktwne_sklepy_w_podziale_na_formaty')
        plt.pyplot.close()
    wrkbook.close()


def save_copy_for_sr(nazwa_spolki: str, image_data: io.BytesIO, nazwa_pliku: str) -> None:
    file_name = Path(f'./output/SR/{nazwa_spolki}/{nazwa_pliku}.png')
    with open(file_name, 'wb') as f:
        f.write(image_data.getbuffer())


def generate_history_graph(sr: str, df: pd.DataFrame, wrkbook: xlsxwriter.Workbook) -> None:
    """Skrypt generuje na podstawie nazwy spółki, tabeli oraz łącza do pliku graf oraz dane na podstawie których go
    zbudowano. Wszystko zapisywane jest w arkuszu z nazwą spółki"""
    group_wstapienie = df.groupby(['Nazwa_Spolki', 'ws_year'], observed=True)['Nazwa_Spolki'].count().reset_index(
        name='nmb_of_occurences')
    group_wystapienie = df.groupby(['Nazwa_Spolki', 'wy_year'], observed=True)['Nazwa_Spolki'].count().reset_index(
        name='nmb_of_occurences')
    fig, ax = plt.pyplot.subplots(figsize=(10, 10))
    sns.barplot(x=group_wstapienie['ws_year'], y="nmb_of_occurences",
                data=group_wstapienie[group_wstapienie['Nazwa_Spolki'] == sr], ax=ax, color="green",
                errorbar=None)
    sns.barplot(x=group_wystapienie['wy_year'], y="nmb_of_occurences",
                data=group_wystapienie[group_wystapienie['Nazwa_Spolki'] == sr], ax=ax, color="red",
                errorbar=None, width=.25)
    ax.legend(title='', loc='upper left', labels=['Wstąpienie sklepu', 'Wystąpienie sklepu'])
    ax.set(xlabel='Rok', ylabel='Liczba sklepów')
    ax.set_title(f"Ilość wstąpień i wystąpień sklepów sieci Lewiatan {sr} na przestrzeni lat")
    for container in ax.containers:
        ax.bar_label(container)
    plty.xticks(rotation=90)
    worksheet = wrkbook.add_worksheet(sr)
    temp_df = df[df['Nazwa_Spolki'] == sr]
    temp_df['Format_Sklepu'].value_counts().sort_values()
    temp_df = temp_df.drop(columns=['ws_year', 'ws_month', 'wy_year', 'wy_month'])
    temp_df['data_wystapienia'] = temp_df['data_wystapienia'].astype(object).where(
        temp_df['data_wystapienia'].notnull(), None)
    (max_row, max_col) = temp_df.shape
    kolumny = ['ID Sklepu', 'Nazwa Sklepu', 'Nazwa Spółki', 'Format sklepu',
               'Powierzchnia Sali', 'Powierzchnia Ogółem', 'Ilość Kas', 'Data wstąpienia', 'Data wystąpienia',
               'Liczba Pracowników', 'Liczba Uczniow', 'Program Magazynowy', 'Standard promocji']
    column_settings = [{"header": column} for column in kolumny]
    worksheet.add_table(0, 0, max_row, max_col - 1,
                        {"columns": column_settings, "data": temp_df.values.tolist()})
    formatdict = {'num_format': 'yyyy-mm-dd'}
    fmt = wrkbook.add_format(formatdict)
    worksheet.set_column('H:I', None, fmt)
    imgdata = io.BytesIO()
    fig.savefig(imgdata, format='png')
    worksheet.insert_image(0, 14, '', {'image_data': imgdata})
    save_copy_for_sr(sr, imgdata, f'Historia sklepow sieci Lewiatan {sr}')


def save_shop_list_for_sr(nazwa_spolki: str, data_frame: pd.DataFrame) -> None:
    file_name = Path(f'./output/SR/{nazwa_spolki}/Lista_sklepow_sieci_Lewiatan_{nazwa_spolki}.xlsx')
    data_frame['data_wstapienia'] = pd.to_datetime(data_frame['data_wstapienia'], format='yyyy-mm-dd', errors='ignore')
    data_frame.to_excel(file_name, index=False, header=['ID Sklepu', 'Nazwa Sklepu', 'Nazwa Spółki', 'Format Sklepu', 'Powierzchnia Sali', 'Powierzchnia Ogółem', 'Ilość kas', 'Data wstąpienia', 'Data wystąpienia', 'Liczba pracowników', 'Liczba uczniów', 'Program Magazynowy', 'Standard promocji'])
