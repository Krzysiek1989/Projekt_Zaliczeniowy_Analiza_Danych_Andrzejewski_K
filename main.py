import shop_list as sl
import load_shops as loads
import pandas as pd


def main() -> None:
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
        sl.save_shop_list_for_sr(spolka, list_of_shops_df[list_of_shops_df['Nazwa_Spolki'] == spolka].drop(
            columns=['ws_year', 'ws_month', 'wy_year', 'wy_month']))
    workbook.close()
    sl.generate_active_shop_graph(list_of_shops_df)
    summed_turnover = pd.DataFrame()
    for file in loads.list_of_files:
        print(f'Przetwarzam plik: {file}')
        sales_df = loads.load_sales_to_df(file)
        sales_df = loads.calculate_shop_sales(sales_df)
        sales_df['data'] = pd.to_datetime(sales_df['data'], format='yyyy-mm-dd')
        sales_df = loads.add_sr_name(sales_df, loads.list_of_shops)
        sales_df = loads.reorder_sr_column(sales_df)
        df_error = sales_df[sales_df['shop_sb_all'] >= int(10000)]
        sales_df_wo_errors = sales_df.drop(df_error.index, axis=0)
        loads.save_report_for_fb(sales_df_wo_errors, df_error)
        promo_df = loads.load_promotions('./source/shop_promotion/lewiatan_promotions.csv')
        loads.prepare_promotions_report(promo_df, sales_df_wo_errors)
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
    loads.save_turnover_to_sr(summed_turnover)
    lvl_of_completion = (loads.level_of_data_completion(summed_turnover))
    loads.save_completion_report(lvl_of_completion)
    loads.generate_top_min_10_shops(summed_turnover)


if __name__ == "__main__":
    main()