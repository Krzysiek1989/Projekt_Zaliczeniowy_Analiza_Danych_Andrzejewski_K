import shop_list as sl

if __name__ == "__main__":
    list_of_shop_file = (f"./source/shop_list"
                         "/list_of_shops.csv")
    list_of_shops_df = sl.load_df_from_csv(list_of_shop_file)
    list_of_shops_df = sl.clean_shop_df(list_of_shops_df)
    list_of_shops_df = sl.format_and_fill_shop_list_df(list_of_shops_df)
    lista_spolek = list_of_shops_df['Nazwa_Spolki'].unique()
    workbook = sl.xlsxwriter.Workbook(f'./output/LH'
                                   '/Histora-sieci-sklepów-Lewiatan.xlsx', {"nan_inf_to_errors": True})
    for spolka in lista_spolek:
        print(f"Szykuję dane dla Spółki {spolka}")
        sl.generate_history_graph(spolka, list_of_shops_df, workbook)
        sl.save_shop_list_for_sr(spolka, list_of_shops_df[list_of_shops_df['Nazwa_Spolki'] == spolka].drop(columns=['ws_year', 'ws_month', 'wy_year', 'wy_month']))
    workbook.close()
    sl.generate_active_shop_graph(list_of_shops_df)
