# Tytuł

Prezentacja możliwości wykorzystania najnowszych technologii (Python, Pandas, Seaborn) 
w automatyzacji raportowania stanu sieci Franczyzowej na przykładzie analizy danych sprzedażowych sieci sklepów Lewiatan Holding S. A. za miesiąc styczeń 2024.

# Opis

Program pobiera dane wejściowe znajdujące się w folderze ./source które podzielone zostały na osobne podkatalogi:
- /shop_list - w katalogu znajduje się plik csv zawierający listę sklepów sieci franczyzowej
- /shop_sale - w katalogu znajdują się pliki zawierające dane sprzedażowe sklepów (obecnie za miesiąc styczeń 2024, docelowo można wprowadzić dane za dowolny okres)
- /shop_promotion - w katalogu znajduje się plik z definicjami promocji za dany miesiąc (j. w.)

Program przetwarza dane odpowiednio przygotowując raport zawierający:
- Analizę ekspansji sieci sklepów na przestrzeni lat w rozbiciu na poszczególne Spółki, listę aktywnych sklepów w danym miesiącu, strukturę aktywnych sklepów sieci w podziale według formatu sklepu
- Analizę sprzedaży sklepów sieci per produkt, wyszukanie anomalii sprzedaży sklepu (sprzedaż powyżej 10 tys.), analiza poprawności przekazywania danych w skali miesiąca, raport zawierający top/min 10 sklepów według sprzedaży
- Analiza działań promocyjnych i efektywności cenowej promocji na podstawie podstawie weryfikacji poziomu utrzymania ceny towarów promocyjnych w sklepach z wykorzystaniem zdefiniowanych promocji (identyfikator promocji, identyfikator produktu, czas)

Przygotowane raporty zapisywane są w formie plików graficznych oraz plików excel w katalogu ./output odpowiednio
- /LH - katalog zawierający wyniki przeznaczone dla centrali organizacji
- /SR/Nazwa_Spółki - katalog zawiera wyniki przeznaczone dla oddziału regionalnego
- /SR/Nazwa_Spółki/FB - w katalogu znajdują się raporty franczyzobiorców odpowiedniego oddziału

# Instalacja

Lista potrzebnych bibliotek znajduje się w pliku 'requirements.txt'

# Instrukcja użytkowania

Plikiem zawierającym logikę programu jest 'main.py', kolejne pliki zawierają:
- shop_list.py - funkcje odpowiedzialne za przetwarzanie danych listy sklepów
- load_shops.py - funkcje odpowiedzialne za przetwarzanie danych sprzedażowych sklepów oraz danych promocji