# Polish Shipment Tracking

English version: [README_EN.md](README_EN.md)

![Shipment Tracking card](images/screenshot.png)


[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](LICENSE)

Integracja dla Home Assistant do śledzenia przesyłek u popularnych przewoźników w Polsce. Tworzy encje sensor dla aktywnych przesyłek oraz zawiera kartę Lovelace z listą przesyłek.

## Funkcje

- Obsługa wielu przewoźników w jednej integracji (Config Flow)
- Encje sensor dla aktywnych przesyłek
- Normalizacja statusów na wspólny zestaw stanów
- Automatyczne wykrywanie nowych przesyłek oraz sprzątanie starych encji
- Wbudowana karta Lovelace:
  - serwowana przez integrację
  - automatyczna rejestracja zasobu w dashboardach w trybie storage

> [!TIP]
> Możesz dodać wiele kont / numerów dla tego samego przewoźnika (np. dla dwóch osób).

## Wspierani przewoźnicy

- InPost
- DHL
- DPD
- Pocztex
- GLS
- Allegro (zamówienia, eksperymentalne)

> [!WARNING]
> Integracja korzysta z nieoficjalnych API aplikacji/serwisów przewoźników. Te API mogą ulec zmianie bez uprzedzenia.

> [!CAUTION]
> Nie ponoszę odpowiedzialności za ewentualne blokady lub ograniczenia konta przez przewoźnika.


## Wymagania

- Home Assistant: 2024.6 lub nowszy
- (Opcjonalnie) HACS: 1.30 lub nowszy

## Instalacja

### Instalacja przez HACS (zalecane)

1. Otwórz HACS -> Integrations.
2. Dodaj repo jako Custom repository:
   - Repository: https://github.com/stirante/polish_shipment_tracking
   - Category: Integration
3. Zainstaluj integrację.
4. Zrestartuj Home Assistant.

### Instalacja ręczna

1. Skopiuj katalog `custom_components/polish_shipment_tracking` do:
   `<config>/custom_components/polish_shipment_tracking`
2. Zrestartuj Home Assistant.

## Konfiguracja

1. Ustawienia -> Urządzenia i usługi -> Dodaj integrację
2. Wyszukaj "Polish Shipment Tracking"
3. Wybierz przewoźnika i uzupełnij wymagane dane logowania
4. Zapisz

Po pierwszym odświeżeniu powinny pojawić się encje `sensor` dla przesyłek.

### Allegro (eksperymentalne)

Allegro nie ma publicznego API dla kupujących, więc integracja korzysta z sesji
z przeglądarki (ciasteczko `QXLSESSID`):

1. Zaloguj się na [allegro.pl](https://allegro.pl) w przeglądarce na komputerze.
2. Naciśnij F12. Firefox: zakładka Storage -> Cookies -> `https://allegro.pl`.
   Chrome / Edge: zakładka Application -> Cookies -> `https://allegro.pl`.
3. Skopiuj wartość ciasteczka `QXLSESSID` i wklej ją przy dodawaniu konta Allegro.

Gdy sesja wygaśnie, Home Assistant pokaże powiadomienie o ponownym
uwierzytelnieniu. Wystarczy wtedy wkleić nowe ciasteczko.

Każde zamówienie Allegro jest osobnym sensorem z produktami, sprzedawcą, osią
czasu i punktem odbioru. Jeśli paczkę z zamówienia śledzi już konto kuriera
(np. InPost), sensor Allegro nie powstaje. Zamiast tego paczka kuriera dostaje
atrybuty `allegro_items`, `allegro_seller`, `allegro_order_id` i inne, a karta
pokazuje zamówione produkty.

### Filtry odbiorcy

W opcjach każdego konta (Konfiguruj) można ustawić:

- Pokazuj tylko paczki dla: widoczne są tylko paczki pasujące do któregoś wzorca,
- Ukryj paczki dla: paczki pasujące do któregoś wzorca są ukrywane.

Jeden wzorzec w linii (lub po przecinku). Wzorzec pasuje do numeru telefonu
odbiorcy (porównywane jest ostatnie 9 cyfr, więc format nie ma znaczenia),
imienia i nazwiska albo adresu, także adresu punktu odbioru. Wielkość liter i
polskie znaki nie mają znaczenia. Paczka jest ukrywana tylko wtedy, gdy
przewoźnik podaje dane, które pozwalają to rozstrzygnąć. Na przykład wzorzec
telefonu nie ukryje paczki, dla której przewoźnik nie podaje numeru odbiorcy.

## Encje

Integracja tworzy encję `sensor` dla każdej aktywnej (niedostarczonej) przesyłki.

- unique_id: `<courier>_<shipment_id>`
- stan sensora: status znormalizowany (np. in_transport)
- atrybuty: zależnie od przewoźnika, przykładowo:
  - numer przesyłki
  - status surowy
  - historia zdarzeń
  - daty zdarzeń
  - informacje o punkcie odbioru

Dodatkowo integracja udostępnia licznik przesyłek gotowych do odbioru dla
każdego konta kuriera oraz licznik zbiorczy dla wszystkich skonfigurowanych
kont i kurierów. Liczniki uwzględniają znormalizowany status
`waiting_for_pickup` i maleją, gdy przesyłka znika z listy aktywnych.
Licznik zbiorczy obejmuje wszystkie konta; do rozdzielenia kont służą
liczniki na urządzeniach poszczególnych kont.




## Zdarzenia (custom events)

Integracja publikuje zdarzenia na magistrali `hass.bus`:

- `polish_shipment_tracking_new_shipment` - nowa przesyłka
- `polish_shipment_tracking_shipment_status_changed` - przesyłka zmieniła stan
- `polish_shipment_tracking_shipment_removed` - śledzona przesyłka zniknęła z
  listy kuriera albo została zarchiwizowana bez znanego statusu końcowego

Przykładowy payload:

```json
{
  "courier": "inpost",
  "shipment_id": "1234567890",
  "entity_id": "sensor.inpost_paczka_1234567890",
  "status_raw": "in_transit",
  "status_key": "in_transport"
}
```

Dla `polish_shipment_tracking_shipment_status_changed` dodatkowo występują pola:

- `old_status_raw`
- `old_status_key`
- `new_status_raw`
- `new_status_key`

Zmiany na status końcowy (`delivered`, `returned`, `cancelled`) są zgłaszane
przed usunięciem czujnika przesyłki. Jeśli kurier całkowicie pomija przesyłkę,
integracja czeka na dwa kolejne udane odpytywania przed emisją zdarzenia
`polish_shipment_tracking_shipment_removed`, zamiast wnioskować o stanie
końcowym z jednej niepełnej odpowiedzi. Czujnik przesyłki pozostaje dostępny
po pierwszym braku. Zdarzenie zawiera poprzedni status i pole `reason`
o wartości `missing_from_feed` lub `archived` (dla znacznika archiwizacji Pocztex).

## Statusy (normalizacja)

Różne nazwy statusów przewoźników są mapowane do wspólnego zestawu. Przykładowo:
- created
- in_transport
- waiting_for_pickup
- delivered
- exception
- cancelled
- returned
- unknown

> [!NOTE]
> Mapowanie statusów nie jest jeszcze kompletne; PR-y z nowymi mapowaniami są mile widziane.

Dokładne mapowania są w kodzie integracji (sensor.py).

## Karta Lovelace


Integracja zawiera kartę Lovelace (JavaScript module) i automatycznie dodaje ją jako zasób w dashboardach.

W sekcji Filtry edytora karty można ograniczyć kartę, np. żeby mieć osobną
kartę dla każdego domownika:

- Pokazuj tylko te konta: wybrane konta (wpisy integracji),
- Pokazuj tylko paczki dla numerów telefonu / e-maili: paczka pasuje, gdy
  numer lub e-mail należy do konta albo do odbiorcy paczki. Format numeru nie
  ma znaczenia.

Oba filtry działają razem. Nie każdy przewoźnik podaje dane odbiorcy (np. DPD
ich nie podaje), więc takie paczki pasują tylko po danych konta.

```yaml
type: custom:shipment-tracking-card
contacts:
  - "+48 600 100 200"
  - jan@example.com
```

## Debugowanie

Możesz włączyć debug logi dla integracji:

```yaml
logger:
  default: info
  logs:
    custom_components.polish_shipment_tracking: debug
```

## Znane problemy

* Zmiany po stronie przewoźników (API, autoryzacja, limity) mogą powodować błędy logowania lub pobierania przesyłek.

## Zgłoszenia błędów i wsparcie

* Issues: [https://github.com/stirante/polish_shipment_tracking/issues](https://github.com/stirante/polish_shipment_tracking/issues)
* Pull requests: mile widziane

W zgłoszeniu błędu dołącz:

* wersję Home Assistant
* logi (z włączonym debug dla integracji)
* wybranego przewoźnika
* opis kroków odtworzenia

## Licencja

GNU General Public License v3.0. Zobacz plik LICENSE.
