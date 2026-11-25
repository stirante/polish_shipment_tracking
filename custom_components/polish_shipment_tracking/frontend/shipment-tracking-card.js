const CARD_TRANSLATIONS = {
  en: {
    "card.title": "Shipments",
    "labels.pickup_code": "CODE",
    "labels.pickup_point": "Pickup point",
    "labels.courier_default": "Courier",
    "empty_state": "No active shipments",
    "meta.name": "Shipment Tracking Card",
    "meta.description": "Displays shipment tracking sensors with status badges.",
    "editor.title": "Title",
    "editor.show_list_sender": "Show sender in list",
    "editor.show_list_pickup_code": "Show pickup code in list",
    "editor.show_list_location": "Show pickup point in list",
    "editor.show_dialog_tracking_number": "Show tracking number in details",
    "editor.show_dialog_courier": "Show courier in details",
    "editor.show_dialog_sender": "Show sender in details",
    "editor.show_dialog_account_contact": "Show shipment account in details",
    "editor.show_dialog_recipient": "Show recipient in details",
    "editor.show_dialog_pickup_code": "Show pickup code in details",
    "editor.show_dialog_pickup_point": "Show pickup point in details",
    "editor.show_dialog_navigation": "Show navigation link in details",
    "editor.show_dialog_delivery_address": "Show delivery address in details",
    "editor.show_dialog_package_type": "Show shipment type in details",
    "editor.show_dialog_courier_contact": "Show courier name and phone in details",
    "editor.show_dialog_delivery_method": "Show delivery method in details",
    "editor.show_dialog_parcel_shop_type": "Show point type in details",
    "editor.show_dialog_live_tracking": "Show live courier tracking in details",
    "editor.show_dialog_cod": "Show COD amount in details",
    "editor.show_dialog_delivery_date": "Show planned delivery date in details",
    "editor.show_dialog_parcel_size": "Show parcel size in details",
    "editor.show_dialog_qr_code": "Show QR code in details",
    "editor.show_dialog_timeline": "Show timeline in details",
    "editor.show_dialog_manage_button": "Show manage button in details",
    "editor.show_dialog_entity_button": "Show entity button in details",
    "dialog.allegro_total": "Total",
    "editor.show_list_allegro_items": "Show Allegro products in list",
    "editor.show_dialog_allegro_items": "Show Allegro products in details",
    "editor.show_dialog_allegro_images": "Show Allegro product images",
    "editor.show_dialog_allegro_prices": "Show Allegro product prices",
    "editor.show_dialog_allegro_seller": "Show Allegro seller",
    "editor.show_dialog_allegro_total": "Show Allegro order total",
    "editor.show_dialog_allegro_order_date": "Show Allegro order date",
    "editor.show_dialog_allegro_shipment": "Show Allegro shipment number and tracking link",
    "editor.filters": "Filters",
    "editor.entries": "Show only these accounts",
    "editor.contacts": "Show only parcels for phone numbers / e-mails (account or recipient)",
    "dialog.sender": "Sender",
    "dialog.account_contact": "Shipment For",
    "dialog.recipient": "Recipient",
    "dialog.allegro_order": "Allegro order",
    "dialog.allegro_ordered": "Ordered",
    "dialog.allegro_shipment": "Shipment",
    "dialog.allegro_track": "Track parcel",
    "dialog.pickup_code": "Pickup Code",
    "dialog.pickup_point": "Pickup Point",
    "dialog.navigate": "Navigate",
    "dialog.parcel_size": "Size",
    "dialog.max_dimensions": "Max dimensions",
    "dialog.cod": "COD Amount",
    "dialog.planned_delivery_date": "Planned Delivery",
    "dialog.courier_name": "Courier Name",
    "dialog.timeline": "Timeline",
    "dialog.no_timeline": "No timeline history available",
    "dialog.scan_qr": "Scan at the parcel locker",
    "dialog.show_entity": "Show entity",
    "dialog.refresh_shipment": "Refresh shipment",
    "dialog.hide_shipment": "Hide shipment",
    "dialog.hide_shipment_confirm": "Hide this shipment? You can show it again in the account options (Configure).",
    "dialog.manage_shipment": "Manage shipment",
    "dialog.live_tracking": "Track courier live",
    "dialog.weight": "Weight",
    "dialog.package_count": "Packages",
    "dialog.courier_phone": "Courier phone",
    "dialog.delivery_method": "Delivery method",
    "dialog.parcel_shop_type": "Point type",
    "dialog.close": "Close",
    "card.refresh_all": "Refresh all shipments",
    "dialog.package_type": "Shipment type",
    "dialog.delivery_address": "Delivery address",
    "dhl.COURIER": "Courier delivery",
    "dhl.LOCKER": "DHL BOX parcel locker",
    "dhl.POP": "DHL POP point",
    "dhl.OBSERVED": "Observed shipment",
    "dhl.step.SENT": "Posted",
    "dhl.step.ROUTE": "In transit",
    "dhl.step.DELIVERY": "Out for delivery",
    "dhl.step.DELIVERED": "Collected",
    "dpd.DELIVERED": "Delivered",
    "dpd.HANDED_OVER_FOR_DELIVERY": "Out for delivery",
    "dpd.HANDED_OVER_FOR_DELIVERY_PUDO": "Out for delivery to pickup point",
    "dpd.READY_TO_PICK_UP_PUDO": "Ready for pickup",
    "dpd.HANDED_OVER_FOR_DELIVERY_SP": "Out for delivery to parcel locker",
    "dpd.READY_TO_PICK_UP_SP": "Ready for pickup",
    "dpd.RECEIVED_IN_DEPOT": "Received in depot",
    "dpd.IN_TRANSPORT": "In transit",
    "dpd.RECEIVED_FROM_SENDER": "Received from sender",
    "dpd.READY_TO_SEND": "Ready to send",
    "gls.PUDO": "Pickup point",
    "gls.APM": "Parcel locker",
    "gls.TO_DOOR": "To door",
    "gls.UNKNOWN": "Unknown delivery method",
    "labels.multicompartment": "Multi-compartment",
    "labels.size_short": "Size",
    "labels.expand": "Expand",
    "labels.collapse": "Collapse",
    "labels.shipments_count_one": "1 shipment",
    "labels.shipments_count_many": "{count} shipments",
    "dialog.multicompartment_title": "Multi-compartment",
    "dialog.multicompartment_shipments": "Shipments in compartment",
    "dialog.back_to_multicompartment": "Back to multi-compartment",
    "dialog.shipment_details": "Details & history",
    "dialog.tracking_number": "Tracking number",
    "editor.group_multicompartment": "Group InPost multi-compartment shipments"
  },
  pl: {
    "card.title": "Przesyłki",
    "labels.pickup_code": "KOD",
    "labels.pickup_point": "Punkt odbioru",
    "labels.courier_default": "Kurier",
    "empty_state": "Brak aktywnych przesyłek",
    "meta.name": "Karta śledzenia przesyłek",
    "meta.description": "Wyświetla sensory śledzenia przesyłek z etykietami statusu.",
    "editor.title": "Tytuł",
    "editor.show_list_sender": "Pokaż nadawcę na liście",
    "editor.show_list_pickup_code": "Pokaż kod odbioru na liście",
    "editor.show_list_location": "Pokaż lokalizację na liście",
    "editor.show_dialog_tracking_number": "Pokaż numer przesyłki w szczegółach",
    "editor.show_dialog_courier": "Pokaż kuriera w szczegółach",
    "editor.show_dialog_sender": "Pokaż nadawcę w szczegółach",
    "editor.show_dialog_account_contact": "Pokaż dane konta przesyłki w szczegółach",
    "editor.show_dialog_recipient": "Pokaż odbiorcę w szczegółach",
    "editor.show_dialog_pickup_code": "Pokaż kod odbioru w szczegółach",
    "editor.show_dialog_pickup_point": "Pokaż punkt odbioru w szczegółach",
    "editor.show_dialog_navigation": "Pokaż link nawigacji w szczegółach",
    "editor.show_dialog_delivery_address": "Pokaż adres doręczenia w szczegółach",
    "editor.show_dialog_package_type": "Pokaż typ przesyłki w szczegółach",
    "editor.show_dialog_courier_contact": "Pokaż imię i telefon kuriera w szczegółach",
    "editor.show_dialog_delivery_method": "Pokaż metodę doręczenia w szczegółach",
    "editor.show_dialog_parcel_shop_type": "Pokaż typ punktu w szczegółach",
    "editor.show_dialog_live_tracking": "Pokaż śledzenie kuriera na żywo w szczegółach",
    "editor.show_dialog_cod": "Pokaż kwotę pobrania w szczegółach",
    "editor.show_dialog_delivery_date": "Pokaż planowaną datę doręczenia w szczegółach",
    "editor.show_dialog_parcel_size": "Pokaż gabaryt paczki w szczegółach",
    "editor.show_dialog_qr_code": "Pokaż kod QR w szczegółach",
    "editor.show_dialog_timeline": "Pokaż historię przesyłki w szczegółach",
    "editor.show_dialog_manage_button": "Pokaż przycisk zarządzania w szczegółach",
    "editor.show_dialog_entity_button": "Pokaż przycisk encji w szczegółach",
    "dialog.allegro_total": "Razem",
    "editor.show_list_allegro_items": "Pokaż produkty Allegro na liście",
    "editor.show_dialog_allegro_items": "Pokaż produkty Allegro w szczegółach",
    "editor.show_dialog_allegro_images": "Pokaż zdjęcia produktów Allegro",
    "editor.show_dialog_allegro_prices": "Pokaż ceny produktów Allegro",
    "editor.show_dialog_allegro_seller": "Pokaż sprzedawcę Allegro",
    "editor.show_dialog_allegro_total": "Pokaż sumę zamówienia Allegro",
    "editor.show_dialog_allegro_order_date": "Pokaż datę zamówienia Allegro",
    "editor.show_dialog_allegro_shipment": "Pokaż numer i link śledzenia przesyłki Allegro",
    "editor.filters": "Filtry",
    "editor.entries": "Pokazuj tylko te konta",
    "editor.contacts": "Pokazuj tylko paczki dla numerów telefonu / e-maili (konta lub odbiorcy)",
    "dialog.sender": "Nadawca",
    "dialog.account_contact": "Przesyłka na",
    "dialog.recipient": "Odbiorca",
    "dialog.allegro_order": "Zamówienie Allegro",
    "dialog.allegro_ordered": "Zamówiono",
    "dialog.allegro_shipment": "Przesyłka",
    "dialog.allegro_track": "Śledź przesyłkę",
    "dialog.pickup_code": "Kod odbioru",
    "dialog.pickup_point": "Punkt odbioru",
    "dialog.navigate": "Nawiguj",
    "dialog.parcel_size": "Gabaryt",
    "dialog.max_dimensions": "Maksymalne wymiary",
    "dialog.cod": "Kwota pobrania",
    "dialog.planned_delivery_date": "Planowane doręczenie",
    "dialog.courier_name": "Kurier",
    "dialog.timeline": "Historia przesyłki",
    "dialog.no_timeline": "Brak historii przesyłki",
    "dialog.scan_qr": "Zeskanuj w paczkomacie",
    "dialog.show_entity": "Pokaż encję",
    "dialog.refresh_shipment": "Odśwież przesyłkę",
    "dialog.hide_shipment": "Ukryj przesyłkę",
    "dialog.hide_shipment_confirm": "Ukryć tę przesyłkę? Możesz ją przywrócić w opcjach konta (Konfiguruj).",
    "dialog.manage_shipment": "Zarządzaj przesyłką",
    "dialog.live_tracking": "Śledź kuriera na żywo",
    "dialog.weight": "Waga",
    "dialog.package_count": "Liczba paczek",
    "dialog.courier_phone": "Telefon kuriera",
    "dialog.delivery_method": "Metoda doręczenia",
    "dialog.parcel_shop_type": "Typ punktu",
    "dialog.close": "Zamknij",
    "card.refresh_all": "Odśwież wszystkie przesyłki",
    "dialog.package_type": "Typ przesyłki",
    "dialog.delivery_address": "Adres doręczenia",
    "dhl.COURIER": "Doręczenie kurierem",
    "dhl.LOCKER": "Automat DHL BOX",
    "dhl.POP": "Punkt DHL POP",
    "dhl.OBSERVED": "Przesyłka obserwowana",
    "dhl.step.SENT": "Nadana",
    "dhl.step.ROUTE": "W drodze",
    "dhl.step.DELIVERY": "W doręczeniu",
    "dhl.step.DELIVERED": "Odebrana",
    "dpd.DELIVERED": "Dostarczona",
    "dpd.HANDED_OVER_FOR_DELIVERY": "Wydana do doręczenia",
    "dpd.HANDED_OVER_FOR_DELIVERY_PUDO": "Wydana do doręczenia do punktu odbioru",
    "dpd.READY_TO_PICK_UP_PUDO": "Gotowa do odbioru",
    "dpd.HANDED_OVER_FOR_DELIVERY_SP": "Wydana do doręczenia do automatu",
    "dpd.READY_TO_PICK_UP_SP": "Gotowa do odbioru",
    "dpd.RECEIVED_IN_DEPOT": "Przyjęta w oddziale",
    "dpd.IN_TRANSPORT": "W drodze",
    "dpd.RECEIVED_FROM_SENDER": "Odebrana od nadawcy",
    "dpd.READY_TO_SEND": "Gotowa do wysłania",
    "gls.PUDO": "Punkt odbioru",
    "gls.APM": "Paczkomat",
    "gls.TO_DOOR": "Dostawa do drzwi",
    "gls.UNKNOWN": "Nieznana metoda doręczenia",
    "labels.multicompartment": "Multiskrytka",
    "labels.size_short": "Gabaryt",
    "labels.expand": "Rozwiń",
    "labels.collapse": "Zwiń",
    "labels.shipments_count_one": "1 przesyłka",
    "labels.shipments_count_few": "{count} przesyłki",
    "labels.shipments_count_many": "{count} przesyłek",
    "dialog.multicompartment_title": "Multiskrytka",
    "dialog.multicompartment_shipments": "Przesyłki w multiskrytce",
    "dialog.back_to_multicompartment": "Wróć do multiskrytki",
    "dialog.shipment_details": "Szczegóły i historia",
    "dialog.tracking_number": "Numer",
    "editor.group_multicompartment": "Grupuj paczki InPost w Multiskrytkę"
  }
};

const DEFAULT_LANGUAGE = "en";

const normalizeLanguage = (language) => {
  if (!language) return DEFAULT_LANGUAGE;
  return language.toLowerCase().split("-")[0];
};

const localize = (hass, key) => {
  const fallbackLanguage = typeof navigator !== "undefined" ? navigator.language : DEFAULT_LANGUAGE;
  const language = normalizeLanguage(hass?.language || hass?.locale?.language || fallbackLanguage);
  const translations = CARD_TRANSLATIONS[language] || CARD_TRANSLATIONS[DEFAULT_LANGUAGE];
  return translations[key] || CARD_TRANSLATIONS[DEFAULT_LANGUAGE][key] || key;
};

class ShipmentTrackingCard extends HTMLElement {
  set hass(hass) {
    this._hass = hass;
    if (!this.content) {
      this.innerHTML = `
        <style>
          ha-card {
            background: var(--ha-card-background, var(--card-background-color, white));
            border-radius: var(--ha-card-border-radius, 12px);
            box-shadow: var(--ha-card-box-shadow, 0px 2px 1px -1px rgba(0,0,0,0.2), 0px 1px 1px 0px rgba(0,0,0,0.14), 0px 1px 3px 0px rgba(0,0,0,0.12));
            padding: 16px;
            color: var(--primary-text-color);
          }
          .header {
            font-family: var(--paper-font-headline_-_font-family);
            font-size: 1.5rem;
            font-weight: 500;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            justify-content: space-between;
          }
          .header-actions {
            display: flex;
            align-items: center;
            gap: 8px;
          }
          .header-refresh-btn {
            border: none;
            background: transparent;
            color: var(--secondary-text-color);
            border-radius: 50%;
            width: 40px;
            height: 40px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: background-color 0.2s ease, color 0.2s ease, transform 0.1s ease;
          }
          .header-refresh-btn:hover {
            background-color: var(--secondary-background-color);
            color: var(--primary-color);
          }
          .header-refresh-btn:active {
            transform: scale(0.9);
          }
          @keyframes spin {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
          }
          .header-refresh-btn.loading ha-icon,
          .header-icon-btn.loading ha-icon,
          .manage-btn.loading ha-icon {
            animation: spin 0.8s linear infinite;
            transform-origin: center;
          }
          .shipment-list {
            display: flex;
            flex-direction: column;
            gap: 16px;
          }
          .shipment-item {
            display: flex;
            align-items: flex-start;
            padding: 12px;
            background: var(--secondary-background-color);
            border-radius: 12px;
            transition: all 0.2s ease-in-out;
            border: 1px solid transparent;
            position: relative;
            cursor: pointer;
          }
          .shipment-item:hover {
            border-color: var(--primary-color);
          }
          .icon-wrapper {
            position: relative;
            margin-right: 16px;
            flex-shrink: 0;
            margin-top: 2px;
            width: 48px;
            height: 48px;
          }
          .icon-container {
            width: 48px;
            height: 48px;
            border-radius: 50%;
            background: white;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
            color: var(--primary-color);
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            overflow: hidden;
            position: relative;
          }
          .icon-container img {
            width: 70%;
            height: 70%;
            object-fit: contain;
          }
          .content-right {
            flex-grow: 1;
            display: flex;
            flex-direction: column;
            min-width: 0;
          }
          .row-top {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            gap: 8px;
            margin-bottom: 4px;
          }
          .info-main {
            min-width: 0;
            flex: 1;
            overflow: hidden;
          }
          .name {
            font-weight: 600;
            font-size: 1.1rem;
            margin-bottom: 2px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            line-height: 1.2;
          }
          .courier {
            font-size: 0.85rem;
            color: var(--secondary-text-color);
            display: block;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
          }
          .truncate-left {
            direction: rtl;
            text-align: left;
          }
          .row-bottom {
            display: block;
            width: 100%;
          }
          .extra-info {
            display: flex;
            flex-direction: column;
            gap: 6px;
            margin-top: 6px;
          }
          .extra-info-text {
            font-size: 0.75rem;
            color: var(--secondary-text-color);
            opacity: 0.9;
            line-height: 1.3;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
          }
          .status-badge {
            padding: 6px 10px;
            border-radius: 20px;
            font-size: 0.70rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            white-space: nowrap;
            text-align: center;
            flex-shrink: 0;
            margin-left: 4px;
          }
          .pickup-code {
            display: inline-block;
            background-color: var(--primary-color);
            color: var(--text-primary-color, white);
            padding: 4px 8px;
            border-radius: 6px;
            font-weight: bold;
            font-size: 0.85rem;
            letter-spacing: 1px;
            width: fit-content;
          }
          .inpost-progress-container {
            display: flex;
            align-items: center;
            gap: 8px;
            margin-top: 4px;
            width: 100%;
          }
          .inpost-progress-bar {
            flex: 1;
            height: 6px;
            border-radius: 3px;
            background-color: #e0e0e0;
            display: flex;
            overflow: hidden;
          }
          .inpost-progress-elapsed {
            background-color: #9e9e9e;
            height: 100%;
          }
          .inpost-progress-remaining {
            background-color: #ffcc00;
            height: 100%;
          }
          .inpost-progress-label {
            font-size: 0.75rem;
            font-weight: 600;
            color: var(--secondary-text-color);
            white-space: nowrap;
          }
          .modal-progress-row {
            margin-top: -2px;
            margin-bottom: 6px;
          }
          .status-delivered { background-color: rgba(76, 175, 80, 0.2); color: #4CAF50; }
          .status-ready { background-color: rgba(255, 193, 7, 0.2); color: #FFC107; border: 1px solid rgba(255, 193, 7, 0.3); }
          .status-transit { background-color: rgba(33, 150, 243, 0.2); color: #2196F3; }
          .status-pending { background-color: rgba(158, 158, 158, 0.2); color: #9E9E9E; }
          .status-exception { background-color: rgba(244, 67, 54, 0.2); color: #F44336; }
          .empty-state {
            text-align: center;
            padding: 20px;
            color: var(--secondary-text-color);
          }

          .multicompartment-wrapper {
            display: flex;
            flex-direction: column;
            background: var(--secondary-background-color);
            border-radius: 12px;
            border: 1px solid transparent;
            transition: all 0.2s ease-in-out;
            position: relative;
          }
          .multicompartment-wrapper:hover {
            border-color: var(--primary-color);
          }
          .multicompartment-header {
            margin-bottom: 0;
            background: transparent;
            border-color: transparent;
          }
          .multicompartment-header:hover {
            border-color: transparent;
          }
          .multicompartment-badge {
            position: absolute;
            bottom: -3px;
            right: -3px;
            background-color: var(--primary-color);
            color: var(--text-primary-color, white);
            font-size: 0.7rem;
            font-weight: bold;
            border-radius: 50%;
            min-width: 19px;
            height: 19px;
            padding: 0 4px;
            box-sizing: border-box;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 1px 3px rgba(0,0,0,0.3);
            border: 2px solid var(--secondary-background-color, var(--card-background-color, white));
            z-index: 2;
            pointer-events: none;
          }
          .multicompartment-header-actions {
            display: flex;
            align-items: center;
            gap: 4px;
            flex-shrink: 0;
          }
          .multicompartment-expand-btn {
            background: transparent;
            border: none;
            cursor: pointer;
            color: var(--secondary-text-color);
            width: 32px;
            height: 32px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 50%;
            transition: background-color 0.2s, color 0.2s;
            padding: 0;
            margin-left: 2px;
          }
          .multicompartment-expand-btn:hover {
            background-color: rgba(128, 128, 128, 0.2);
            color: var(--primary-color);
          }
          .multicompartment-subitems {
            display: flex;
            flex-direction: column;
            border-top: 1px dashed var(--divider-color, rgba(128,128,128,0.25));
            background: rgba(128, 128, 128, 0.06);
            padding: 8px 12px 12px 12px;
            gap: 6px;
            border-radius: 0 0 12px 12px;
          }
          .multicompartment-subitem {
            display: flex;
            align-items: center;
            padding: 8px 10px;
            border-radius: 8px;
            background: var(--ha-card-background, var(--card-background-color, white));
            border: 1px solid var(--divider-color, rgba(128,128,128,0.15));
            cursor: pointer;
            transition: all 0.15s ease-in-out;
            gap: 10px;
          }
          .multicompartment-subitem:hover {
            border-color: var(--primary-color);
            transform: translateX(2px);
          }
          .subitem-icon {
            color: var(--primary-color);
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
            font-size: 20px;
          }
          .subitem-content {
            flex: 1;
            min-width: 0;
          }
          .subitem-row-top {
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 8px;
          }
          .subitem-name {
            font-weight: 600;
            font-size: 0.95rem;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            line-height: 1.2;
          }
          .subitem-meta {
            display: flex;
            gap: 6px;
            align-items: center;
            flex-shrink: 0;
          }
          .subitem-status {
            padding: 2px 7px;
            border-radius: 12px;
            font-size: 0.65rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.3px;
            white-space: nowrap;
          }
          .subitem-size {
            background-color: rgba(128, 128, 128, 0.15);
            color: var(--secondary-text-color);
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 0.72rem;
            font-weight: 600;
          }
          .subitem-row-bottom {
            display: flex;
            flex-direction: column;
            gap: 2px;
            margin-top: 2px;
          }
          .subitem-tracking {
            font-size: 0.8rem;
            color: var(--secondary-text-color);
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
          }
          .subitem-allegro {
            font-size: 0.75rem;
            color: var(--secondary-text-color);
            opacity: 0.9;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
          }
          .modal-back-row {
            margin-bottom: 14px;
          }
          .modal-back-btn {
            background: var(--secondary-background-color);
            border: 1px solid var(--divider-color, rgba(128,128,128,0.2));
            color: var(--primary-text-color);
            padding: 6px 12px;
            border-radius: 8px;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 6px;
            font-size: 0.9rem;
            font-weight: 500;
            transition: all 0.2s ease;
          }
          .modal-back-btn:hover {
            background: rgba(128, 128, 128, 0.15);
            border-color: var(--primary-color);
            color: var(--primary-color);
          }
          .modal-mc-list {
            display: flex;
            flex-direction: column;
            gap: 8px;
            margin-top: 10px;
          }
          .modal-mc-item {
            background: var(--secondary-background-color);
            border: 1px solid var(--divider-color, rgba(128,128,128,0.12));
            border-radius: 8px;
            padding: 10px 14px;
            display: flex;
            flex-direction: column;
            gap: 6px;
          }
          .modal-mc-item-header {
            display: flex;
            align-items: center;
            gap: 8px;
          }
          .modal-mc-item-num {
            font-weight: bold;
            color: var(--secondary-text-color);
            font-size: 0.9rem;
            min-width: 18px;
          }
          .modal-mc-item-main {
            flex: 1;
            min-width: 0;
          }
          .modal-mc-item-sender {
            font-weight: 600;
            font-size: 1rem;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
          }
          .modal-mc-item-tracking {
            font-size: 0.8rem;
            color: var(--secondary-text-color);
          }
          .modal-mc-item-badges {
            display: flex;
            gap: 6px;
            align-items: center;
            flex-shrink: 0;
            flex-wrap: wrap;
            justify-content: flex-end;
          }
          .modal-mc-size-badge {
            background: rgba(128, 128, 128, 0.15);
            color: var(--secondary-text-color);
            font-size: 0.75rem;
            padding: 2px 6px;
            border-radius: 4px;
            font-weight: 600;
          }
          .modal-mc-code-badge {
            background: var(--primary-color);
            color: var(--text-primary-color, white);
            font-size: 0.8rem;
            font-weight: bold;
            padding: 2px 8px;
            border-radius: 4px;
            letter-spacing: 0.5px;
          }
          .modal-mc-allegro {
            margin-top: 4px;
            padding-left: 26px;
          }
          .modal-mc-item-footer {
            display: flex;
            justify-content: flex-end;
            gap: 8px;
            margin-top: 4px;
          }
          .modal-mc-view-btn {
            background: transparent;
            border: 1px solid var(--divider-color, rgba(128,128,128,0.25));
            color: var(--primary-text-color);
            padding: 4px 10px;
            border-radius: 6px;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 4px;
            font-size: 0.8rem;
            transition: all 0.2s;
          }
          .modal-mc-view-btn ha-icon {
            --mdc-icon-size: 15px;
          }
          .modal-mc-view-btn:hover {
            background: rgba(128, 128, 128, 0.1);
            border-color: var(--primary-color);
            color: var(--primary-color);
          }

          .modal-overlay {
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0, 0, 0, 0.5); z-index: 9999;
            display: none; justify-content: center; align-items: center;
            backdrop-filter: blur(2px);
          }
          .modal-overlay.open { display: flex; }
          .modal-surface {
            background: var(--primary-background-color);
            color: var(--primary-text-color);
            width: 90%; max-width: 500px; max-height: 85vh;
            border-radius: var(--ha-card-border-radius, 12px);
            box-shadow: var(--ha-card-box-shadow, 0 8px 24px rgba(0,0,0,0.2));
            display: flex; flex-direction: column; overflow: hidden;
          }
          .modal-header {
            padding: 16px 20px; border-bottom: 1px solid var(--divider-color, rgba(0,0,0,0.1));
            display: flex; justify-content: space-between; align-items: center;
            font-size: 1.2rem; font-weight: 500; background: var(--secondary-background-color);
          }
          #modal-title {
            flex: 1;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            margin-right: 12px;
          }
          .modal-header-actions {
            display: flex;
            align-items: center;
            gap: 12px;
          }
          .modal-header-actions ha-icon { cursor: pointer; color: var(--secondary-text-color); }
          .header-icon-btn {
            background: none; border: none; padding: 0; cursor: pointer;
            color: var(--secondary-text-color); display: flex; align-items: center;
            justify-content: center; transition: color 0.2s ease; outline: none;
          }
          .header-icon-btn:hover { color: var(--primary-text-color); }
          
          .modal-content { 
            padding: 20px; overflow-y: auto; flex: 1; 
            user-select: text; -webkit-user-select: text; 
          }
          
          .modal-info-block {
            background: var(--secondary-background-color, rgba(0,0,0,0.02));
            padding: 14px; border-radius: 8px; margin-bottom: 20px;
            font-size: 0.95rem; border: 1px solid var(--divider-color, rgba(0,0,0,0.05));
          }
          .modal-info-block-row { margin-bottom: 8px; line-height: 1.4; display: flex; align-items: flex-start;}
          .modal-info-block-row:last-child { margin-bottom: 0; }
          .modal-info-block-row strong { color: var(--secondary-text-color); font-weight: 500; min-width: 155px; flex-shrink: 0; }
          .modal-info-block-row span.val { flex-grow: 1; }
          
          .qr-code-container {
            display: flex; flex-direction: column; align-items: center; justify-content: center;
            background: #ffffff; padding: 16px; border-radius: 12px; margin-top: 16px;
            border: 2px solid var(--primary-color); cursor: pointer;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1); transition: transform 0.2s, box-shadow 0.2s;
          }
          .qr-code-container:hover { transform: scale(1.08); box-shadow: 0 8px 22px rgba(0,0,0,0.18); }
          .qr-code-container:active { transform: scale(0.98); }
          .qr-code-container img {
            width: 150px; height: 150px; image-rendering: crisp-edges;
          }
          .qr-code-label {
            margin-top: 12px; font-size: 0.9rem; color: #333333; font-weight: 600; text-align: center;
          }

          .qr-fullscreen-overlay {
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: #ffffff; z-index: 10000;
            display: none; justify-content: center; align-items: center; flex-direction: column;
          }
          .qr-fullscreen-overlay.open { display: flex; }
          .qr-fullscreen-overlay img { 
            width: 80vw; max-width: 400px; height: auto; image-rendering: crisp-edges;
            box-shadow: 0 10px 30px rgba(0,0,0,0.15); border-radius: 12px; padding: 10px; border: 1px solid #eee;
          }
          .qr-fullscreen-close {
            margin-top: 40px; padding: 12px 24px; background: var(--primary-color);
            color: var(--text-primary-color, white); border-radius: 8px; font-weight: bold; cursor: pointer;
            font-size: 1.1rem; box-shadow: 0 4px 6px rgba(0,0,0,0.1);
          }

          .parcel-sizes { display: flex; gap: 12px; align-items: flex-end; margin-top: 8px; margin-bottom: 4px; }
          .parcel-size {
            display: flex; flex-direction: column; align-items: center; justify-content: flex-end;
            background: var(--primary-background-color, rgba(0,0,0,0.05)); border-radius: 8px; padding: 8px;
            min-width: 45px; color: var(--secondary-text-color); border: 1px solid var(--divider-color, rgba(0,0,0,0.1));
            opacity: 0.5; transition: all 0.2s ease; cursor: help;
            user-select: none; -webkit-user-select: none;
          }
          .parcel-size.active {
            opacity: 1; background: var(--primary-color); color: var(--text-primary-color, white);
            border-color: var(--primary-color); font-weight: bold; transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.15); cursor: default;
          }
          .parcel-size span { display: block; background: currentColor; border-radius: 2px; margin-bottom: 6px; opacity: 0.9; }
          .parcel-size .box-xs { width: 26px; height: 4px; }
          .parcel-size .box-s { width: 26px; height: 8px; }
          .parcel-size .box-m { width: 26px; height: 18px; }
          .parcel-size .box-l { width: 26px; height: 32px; }
          .parcel-size-info { font-size: 0.8rem; color: var(--secondary-text-color); margin-top: 6px; }

          .modal-nav-link {
            display: inline-flex; align-items: center; gap: 4px;
            color: var(--primary-color); text-decoration: none; font-weight: 500;
            margin-top: 4px; font-size: 0.9rem;
          }
          .modal-nav-link ha-icon { --mdc-icon-size: 16px; }
          
          .manage-shipment-container {
            margin-bottom: 24px;
            width: 100%;
          }
          .manage-accordion { width: 100%; }
          .manage-accordion > summary {
            list-style: none;
            position: relative;
          }
          .manage-accordion > summary::-webkit-details-marker { display: none; }
          .manage-accordion > summary .chevron {
            position: absolute; right: 12px; --mdc-icon-size: 20px;
            transition: transform 0.2s ease;
          }
          .manage-accordion[open] > summary .chevron { transform: rotate(180deg); }
          .manage-accordion[open] > summary { border-radius: 8px 8px 0 0; }
          .manage-options {
            display: flex; flex-direction: column;
            border: 1px solid var(--primary-color); border-top: none;
            border-radius: 0 0 8px 8px; overflow: hidden;
          }
          .manage-options a {
            display: flex; align-items: center; gap: 10px;
            padding: 12px 16px; text-decoration: none;
            color: var(--primary-text-color); font-size: 0.95rem;
            border-top: 1px solid var(--divider-color, rgba(0,0,0,0.1));
          }
          .manage-options a:first-child { border-top: none; }
          .manage-options a:hover { background: var(--secondary-background-color, rgba(0,0,0,0.05)); }
          .manage-options a ha-icon { --mdc-icon-size: 20px; color: var(--primary-color); flex-shrink: 0; }
          .manage-option-desc { display: block; font-size: 0.8rem; color: var(--secondary-text-color); }
          .manage-btn {
            display: flex; align-items: center; justify-content: center; width: 100%;
            box-sizing: border-box;
            gap: 8px; border: 1px solid var(--primary-color); background: transparent;
            color: var(--primary-color); border-radius: 8px; padding: 12px 16px;
            font-size: 1rem; font-weight: 500; cursor: pointer; transition: all 0.2s ease;
          }
          .manage-btn:hover { background: var(--primary-color); color: var(--text-primary-color, white); }
          .manage-btn ha-icon { --mdc-icon-size: 20px; }

          .modal-section-title { font-size: 1.1rem; font-weight: 500; margin-bottom: 12px; color: var(--primary-text-color); }
          .timeline { position: relative; padding-left: 20px; margin-top: 10px; }
          .timeline-item { position: relative; padding-bottom: 20px; }
          .timeline-item:last-child { padding-bottom: 0; }
          .timeline-item::before {
            content: ''; position: absolute; left: -20px; top: 6px;
            width: 10px; height: 10px; border-radius: 50%;
            background: var(--primary-color); border: 2px solid var(--ha-card-background, white);
            box-shadow: 0 0 0 1px var(--primary-color); z-index: 1;
          }
          .timeline-item::after {
            content: ''; position: absolute; left: -16px; top: 16px; bottom: -6px;
            width: 2px; background: var(--divider-color, rgba(0,0,0,0.1));
          }
          .timeline-item:last-child::after { display: none; }
          .timeline-date { font-size: 0.8rem; color: var(--secondary-text-color); margin-bottom: 4px; }
          .timeline-title { font-weight: 500; font-size: 0.95rem; margin-bottom: 2px; }
          .timeline-desc { font-size: 0.85rem; color: var(--secondary-text-color); line-height: 1.4; }
        </style>

        <ha-card>
          <div class="header">
            <span id="card-title"></span>
            <div class="header-actions">
              <button id="refresh-all-btn" class="header-refresh-btn" type="button" title="">
                <ha-icon icon="mdi:refresh"></ha-icon>
              </button>
              <ha-icon icon="mdi:truck-delivery-outline"></ha-icon>
            </div>
          </div>
          <div class="shipment-list" id="shipment-list"></div>
        </ha-card>

        <div class="modal-overlay" id="modal-overlay">
          <div class="modal-surface">
            <div class="modal-header">
              <span id="modal-title"></span>
              <div class="modal-header-actions">
                <span id="header-dynamic-actions" style="display:flex; gap:12px; align-items:center;"></span>
                <ha-icon icon="mdi:close" id="modal-close"></ha-icon>
              </div>
            </div>
            <div class="modal-content" id="modal-content"></div>
          </div>
        </div>

        <div class="qr-fullscreen-overlay" id="qr-fullscreen">
          <img id="qr-fullscreen-img" src="" alt="QR Code Fullscreen" />
          <div class="qr-fullscreen-close" id="qr-fullscreen-close"></div>
        </div>
      `;
      this.content = this.querySelector("#shipment-list");
      this.titleElement = this.querySelector("#card-title");
      this.refreshAllButton = this.querySelector("#refresh-all-btn");

      this.querySelector('#modal-close').addEventListener('click', () => {
        this._closeDialog();
      });
      this.querySelector('#modal-overlay').addEventListener('click', (e) => {
        if (e.target.id === 'modal-overlay') {
          this._closeDialog();
        }
      });
      
      this.querySelector('#qr-fullscreen-close').addEventListener('click', () => {
        this.querySelector('#qr-fullscreen').classList.remove('open');
      });
      this.querySelector('#qr-fullscreen').addEventListener('click', (e) => {
        if (e.target.id === 'qr-fullscreen') {
          this.querySelector('#qr-fullscreen').classList.remove('open');
        }
      });
      this.refreshAllButton.addEventListener('click', async (e) => {
        e.stopPropagation();
        await this._refreshAllShipments();
      });
    }
    this._updateTitle();
    this.updateContent();
    this._refreshOpenDialog();
  }

  setConfig(config) {
    this.config = { ...(config || {}) };
    this._updateTitle();
    this.updateContent();
  }

  _configList(key) {
    const value = this.config?.[key];
    const items = Array.isArray(value) ? value : (typeof value === 'string' ? value.split(',') : []);
    return items.map((item) => String(item).trim()).filter(Boolean);
  }

  _passesFilters(attrs) {
    // Card filters from #5: one card per account / person.
    const entries = this._configList('entries');
    if (entries.length && !entries.includes(attrs.config_entry_id)) return false;

    const contacts = this._configList('contacts');
    if (!contacts.length) return true;
    const digits = (text) => String(text || '').replace(/\D/g, '');
    const account = String(attrs.account_contact || '').toLowerCase();
    const phones = [...(attrs.recipient_phones || [])];
    const accountDigits = digits(account);
    if (!account.includes('@') && accountDigits.length >= 9) phones.push(accountDigits.slice(-9));
    const emails = (attrs.recipient_emails || []).map((email) => String(email).toLowerCase());
    if (account.includes('@')) emails.push(account);

    return contacts.some((contact) => {
      if (contact.includes('@')) return emails.includes(contact.toLowerCase());
      const wanted = digits(contact).slice(-9);
      return wanted.length >= 6 && phones.some((phone) => phone.endsWith(wanted));
    });
  }

  static getStubConfig() {
    return {};
  }

  static getConfigElement() {
    return document.createElement("shipment-tracking-card-editor");
  }

  getCardSize() {
    return 3;
  }

  _localize(key) {
    return localize(this._hass, key);
  }

  _updateTitle() {
    if (!this.titleElement) return;
    const title = this.config?.title || this._localize("card.title");
    this.titleElement.innerText = title;
    if (this.refreshAllButton) this.refreshAllButton.title = this._localize("card.refresh_all");
    
    const closeBtn = this.querySelector('#qr-fullscreen-close');
    if (closeBtn) closeBtn.innerText = this._localize("dialog.close");
  }

  _isEnabled(optionName) {
    return this.config?.[optionName] !== false;
  }

  _closeDialog() {
    this._openDialogEntityId = null;
    this._openDialogMcUuid = null;
    this._fromMcUuid = null;
    this._manageAccordionOpen = false;
    this._lastModalContentHtml = null;
    this._lastModalHeaderHtml = null;
    this.querySelector('#modal-overlay')?.classList.remove('open');
  }

  _refreshOpenDialog() {
    if (this._openDialogMcUuid) {
      const items = this._getMcItems(this._openDialogMcUuid);
      if (items.length === 0) {
        this._closeDialog();
        return;
      }
      if (items.length === 1) {
        this.openDialog(items[0].entity_id, { reopen: false, fromMcUuid: null });
        return;
      }
      this.openMulticompartmentDialog(this._openDialogMcUuid, { reopen: false });
      return;
    }
    if (!this._openDialogEntityId) return;

    const stateObj = this._hass?.states?.[this._openDialogEntityId];
    if (!stateObj) {
      this._closeDialog();
      return;
    }

    this.openDialog(this._openDialogEntityId, { reopen: false, fromMcUuid: this._fromMcUuid });
  }

  _getRefreshAllButtonIds() {
    if (!this._hass?.states) return [];
    const byScope = Object.keys(this._hass.states).filter((entityId) => {
      if (!entityId.startsWith("button.")) return false;
      const attrs = this._hass.states[entityId]?.attributes || {};
      return (
        attrs.integration_domain === "polish_shipment_tracking"
        && attrs.refresh_scope === "all"
      );
    });
    if (byScope.length) return byScope;

    return Object.keys(this._hass.states).filter((entityId) => (
      entityId.startsWith("button.")
      && entityId.includes("_refresh_all")
    ));
  }

  _getRefreshShipmentButtonId(attrs) {
    if (!this._hass?.states || !attrs?.tracking_number || !attrs?.courier) return null;
    const trackingNumber = String(attrs.tracking_number);
    const courier = String(attrs.courier).toLowerCase();

    return Object.keys(this._hass.states).find((entityId) => {
      if (!entityId.startsWith("button.")) return false;
      const buttonAttrs = this._hass.states[entityId]?.attributes || {};
      return (
        buttonAttrs.integration_domain === "polish_shipment_tracking"
        && buttonAttrs.refresh_scope === "single"
        && String(buttonAttrs.tracking_number) === trackingNumber
        && String(buttonAttrs.courier).toLowerCase() === courier
      );
    }) || null;
  }

  _getManageShipmentButtonId(attrs) {
    if (!this._hass?.states || !attrs?.tracking_number || !attrs?.courier) return null;
    const trackingNumber = String(attrs.tracking_number);
    const courier = String(attrs.courier).toLowerCase();

    return Object.keys(this._hass.states).find((entityId) => {
      if (!entityId.startsWith("button.")) return false;
      const buttonAttrs = this._hass.states[entityId]?.attributes || {};
      return (
        buttonAttrs.integration_domain === "polish_shipment_tracking"
        && buttonAttrs.action === "manage_url"
        && String(buttonAttrs.tracking_number) === trackingNumber
        && String(buttonAttrs.courier).toLowerCase() === courier
      );
    }) || null;
  }

  _getHideShipmentButtonId(attrs) {
    if (!this._hass?.states || !attrs?.tracking_number || !attrs?.courier) return null;
    const trackingNumber = String(attrs.tracking_number);
    const courier = String(attrs.courier).toLowerCase();

    return Object.keys(this._hass.states).find((entityId) => {
      if (!entityId.startsWith("button.")) return false;
      const buttonAttrs = this._hass.states[entityId]?.attributes || {};
      return (
        buttonAttrs.integration_domain === "polish_shipment_tracking"
        && buttonAttrs.action === "hide"
        && String(buttonAttrs.tracking_number) === trackingNumber
        && String(buttonAttrs.courier).toLowerCase() === courier
      );
    }) || null;
  }

  _hasDpdManageAction(attrs, raw) {
    const courier = String(attrs?.courier || "").toLowerCase();
    if (courier !== "dpd" || !raw || typeof raw !== "object") return false;
    if (raw.is_manageable === true) return true;
    if (!Array.isArray(raw.user_actions)) return false;
    return raw.user_actions.some((action) => action?.code === "MANAGE_PACKAGE");
  }

  async _pressButtonEntity(entityId) {
    if (!entityId || !this._hass) return;
    await this._hass.callService("button", "press", { entity_id: entityId });
  }

  _waitForManageUrl(trackingNumber, courier, timeoutMs = 15000) {
    if (!this._hass?.connection) {
      return Promise.reject(new Error("Home Assistant connection unavailable"));
    }

    return new Promise((resolve, reject) => {
      let settled = false;
      let unsubscribe = null;
      const finish = (handler, value) => {
        if (settled) return;
        settled = true;
        clearTimeout(timeoutId);
        if (typeof unsubscribe === "function") unsubscribe();
        handler(value);
      };

      const timeoutId = window.setTimeout(() => {
        finish(reject, new Error("Timed out waiting for DPD manage URL"));
      }, timeoutMs);

      this._hass.connection.subscribeEvents((event) => {
        const data = event?.data || {};
        if (String(data.courier || "").toLowerCase() !== String(courier || "").toLowerCase()) return;
        if (String(data.tracking_number || "") !== String(trackingNumber || "")) return;
        if (!data.manage_url) {
          finish(reject, new Error("DPD manage URL missing in event payload"));
          return;
        }
        finish(resolve, data.manage_url);
      }, "polish_shipment_tracking_manage_url").then((unsub) => {
        unsubscribe = unsub;
      }).catch((err) => {
        finish(reject, err);
      });
    });
  }

  _getManageUrlCache() {
    if (!this._manageUrlCache) {
      this._manageUrlCache = new Map();
    }
    return this._manageUrlCache;
  }

  _getManageUrlRequests() {
    if (!this._manageUrlRequests) {
      this._manageUrlRequests = new Map();
    }
    return this._manageUrlRequests;
  }

  _getManageCacheKey(attrs) {
    if (!attrs?.tracking_number || !attrs?.courier) return null;
    return `${String(attrs.courier).toLowerCase()}::${String(attrs.tracking_number)}`;
  }

  _getCachedManageUrl(attrs) {
    const key = this._getManageCacheKey(attrs);
    if (!key) return null;
    return this._getManageUrlCache().get(key) || null;
  }

  _isManageUrlPending(attrs) {
    const key = this._getManageCacheKey(attrs);
    if (!key) return false;
    return this._getManageUrlRequests().has(key);
  }

  _prefetchManageShipmentUrl(buttonEntityId, attrs, entityId) {
    const key = this._getManageCacheKey(attrs);
    if (!key || !buttonEntityId) return;
    if (this._getManageUrlCache().has(key) || this._getManageUrlRequests().has(key)) return;

    const request = (async () => {
      try {
        const waitPromise = this._waitForManageUrl(attrs.tracking_number, attrs.courier);
        await this._pressButtonEntity(buttonEntityId);
        const manageUrl = await waitPromise;
        if (manageUrl) {
          this._getManageUrlCache().set(key, manageUrl);
          if (this._openDialogEntityId === entityId) {
            this.openDialog(entityId, { reopen: false });
          }
        }
      } catch (err) {
        console.error("Failed to prefetch DPD manage URL", err);
      } finally {
        this._getManageUrlRequests().delete(key);
        if (this._openDialogEntityId === entityId) {
          this.openDialog(entityId, { reopen: false });
        }
      }
    })();

    this._getManageUrlRequests().set(key, request);
  }

  _openExternalUrl(url) {
    if (!url) return;
    const link = document.createElement("a");
    link.href = url;
    link.target = "_blank";
    link.rel = "noopener noreferrer";
    link.style.display = "none";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }

  async _openManageShipment(attrs) {
    const manageUrl = this._getCachedManageUrl(attrs);
    if (manageUrl) {
      this._openExternalUrl(manageUrl);
    }
  }

  async _refreshAllShipments() {
    const refreshIds = this._getRefreshAllButtonIds();
    if (!refreshIds.length) return;
    if (this.refreshAllButton) this.refreshAllButton.classList.add("loading");
    try {
      await Promise.all(refreshIds.map((entityId) => this._pressButtonEntity(entityId)));
    } finally {
      setTimeout(() => this.refreshAllButton?.classList.remove("loading"), 400);
    }
  }

  _renderInPostProgressBar(attrs) {
    if (!attrs) return '';
    const expiryStr = attrs.expiry_date;
    const storedStr = attrs.stored_date;
    if (!expiryStr) return '';

    const parseDateMs = (str) => {
      if (!str) return NaN;
      if (typeof str === 'number') return str > 1e11 ? str : str * 1000;
      const clean = String(str).trim().replace(' ', 'T');
      return new Date(clean).getTime();
    };

    const expiryTime = parseDateMs(expiryStr);
    if (isNaN(expiryTime)) return '';

    const storedTime = storedStr ? parseDateMs(storedStr) : (expiryTime - 48 * 3600 * 1000);
    if (isNaN(storedTime) || expiryTime <= storedTime) return '';

    const now = Date.now();
    const totalTime = expiryTime - storedTime;
    const elapsed = Math.min(totalTime, Math.max(0, now - storedTime));
    const percentElapsed = ((elapsed / totalTime) * 100).toFixed(1);
    const percentRemaining = (100 - percentElapsed).toFixed(1);

    const msRemaining = Math.max(0, expiryTime - now);
    const totalMinutes = Math.floor(msRemaining / (1000 * 60));
    const hours = Math.floor(totalMinutes / 60);
    const minutes = totalMinutes % 60;

    const timeText = msRemaining <= 0 ? "0h 0min" : `${hours}h ${minutes}min`;

    return `
      <div class="inpost-progress-container">
        <div class="inpost-progress-bar">
          <div class="inpost-progress-elapsed" style="width: ${percentElapsed}%;"></div>
          <div class="inpost-progress-remaining" style="width: ${percentRemaining}%;"></div>
        </div>
        <div class="inpost-progress-label">${timeText}</div>
      </div>
    `;
  }

  getStatusInfo(stateObj) {
    const attributes = stateObj?.attributes || {};
    const statusKey = (attributes.status_key || '').toString().toLowerCase();
    const raw = (attributes.status_raw || '').toString();
    const state = (stateObj?.state || '').toString();

    const classMap = {
      delivered: 'status-delivered',
      waiting_for_pickup: 'status-ready',
      handed_out_for_delivery: 'status-transit',
      in_transport: 'status-transit',
      created: 'status-pending',
      unknown: 'status-pending',
      returned: 'status-exception',
      cancelled: 'status-exception',
      exception: 'status-exception',
    };

    const badgeClass = classMap[statusKey] || 'status-pending';

    let label = state || raw || statusKey || '';
    if (this._hass?.localize && statusKey) {
      const key = `component.polish_shipment_tracking.entity.sensor.shipment_status.state.${statusKey}`;
      const localized = this._hass.localize(key);
      if (localized && localized !== key) {
        label = localized;
      }
    } else if (this._hass?.formatEntityState && stateObj) {
      label = this._hass.formatEntityState(stateObj);
    }

    return { class: badgeClass, text: label };
  }

  getCourierIcon(name) {
    const n = name.toLowerCase();
    if (n.includes('inpost')) return 'mdi:locker';
    if (n.includes('dhl') || n.includes('ups') || n.includes('fedex')) return 'mdi:truck-fast';
    if (n.includes('gls')) return 'mdi:truck-delivery-outline';
    if (n.includes('allegro')) return 'mdi:shopping-outline';
    if (n.includes('orlen')) return 'mdi:gas-station-outline';
    if (n.includes('pocztex') || n.includes('poczta')) return 'mdi:post-outline';
    return 'mdi:package-variant-closed';
  }

  _allegroItems(attrs) {
    const items = attrs.items || attrs.allegro_items;
    return Array.isArray(items) ? items.filter(Boolean) : [];
  }

  _escapeHtml(value) {
    return String(value ?? '').replace(/[&<>"']/g, (ch) => ({
      '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;',
    }[ch]));
  }

  _formatMoney(amount, currency) {
    const value = Number(amount);
    if (amount === null || amount === undefined || amount === '' || Number.isNaN(value)) return '';
    try {
      return value.toLocaleString(this._hass?.language || 'pl', { style: 'currency', currency: currency || 'PLN' });
    } catch (e) {
      return `${value.toFixed(2)} ${currency || ''}`.trim();
    }
  }

  _renderAllegroInfo(attrs) {
    // Allegro orders, and carrier parcels matched to an Allegro order.
    const isAllegro = String(attrs.courier || '').toLowerCase() === 'allegro';
    const offers = Array.isArray(attrs.offers) ? attrs.offers : (Array.isArray(attrs.allegro_offers) ? attrs.allegro_offers : []);
    const items = this._allegroItems(attrs);
    if (!offers.length && !items.length) return '';
    const on = (key) => this._isEnabled(key);
    const esc = (value) => this._escapeHtml(value);
    const row = (label, value) => `<div class="modal-info-block-row"><strong>${label}:</strong> <span class="val">${value}</span></div>`;

    let productsHtml;
    if (offers.length) {
      productsHtml = offers.map((offer) => {
        const title = esc(offer.title || '');
        const link = typeof offer.url === 'string' && offer.url.startsWith('https://')
          ? `<a href="${esc(offer.url)}" target="_blank" rel="noopener noreferrer" style="color: inherit;">${title}</a>`
          : title;
        const img = on("show_dialog_allegro_images") && typeof offer.image_url === 'string' && offer.image_url.startsWith('https://')
          ? `<img src="${esc(offer.image_url.replace('/original/', '/s128/'))}" alt="" loading="lazy" style="width: 48px; height: 48px; object-fit: contain; border-radius: 8px; background: #fff; flex-shrink: 0;">`
          : '';
        const price = on("show_dialog_allegro_prices") ? this._formatMoney(offer.unit_price, offer.currency) : '';
        const qty = Number(offer.quantity) > 1 ? `${offer.quantity} × ` : '';
        return `<div style="display: flex; gap: 10px; align-items: center; margin: 6px 0;">
            ${img}
            <div style="min-width: 0;">
              <div style="line-height: 1.3;">${link}</div>
              ${price ? `<div style="opacity: 0.7; font-size: 0.9em;">${qty}${esc(price)}</div>` : ''}
            </div>
          </div>`;
      }).join('');
    } else {
      productsHtml = items.map((item) => esc(item)).join('<br>');
    }

    // Allegro sensors already list the seller as the parcel sender.
    const seller = !isAllegro && on("show_dialog_allegro_seller") && attrs.allegro_seller ? ` · ${esc(attrs.allegro_seller)}` : '';
    let html = '';
    if (on("show_dialog_allegro_items")) {
      html += `<div class="modal-info-block-row" style="flex-direction: column; align-items: stretch;"><strong>${this._localize("dialog.allegro_order")}${seller}</strong>${productsHtml}</div>`;
    }

    const total = this._formatMoney(attrs.total_cost ?? attrs.allegro_total_cost, attrs.currency ?? attrs.allegro_currency);
    if (total && on("show_dialog_allegro_total")) html += row(this._localize("dialog.allegro_total"), esc(total));

    const orderDate = attrs.order_date || attrs.allegro_order_date;
    if (orderDate && on("show_dialog_allegro_order_date")) {
      const date = new Date(orderDate);
      const text = Number.isNaN(date.getTime())
        ? orderDate
        : date.toLocaleString(this._hass.language || 'pl', { dateStyle: 'short', timeStyle: 'short' });
      html += row(this._localize("dialog.allegro_ordered"), esc(text));
    }

    if (isAllegro) {
      const shipment = attrs.carrier && attrs.waybill ? `${attrs.carrier} ${attrs.waybill}` : attrs.waybill;
      if (shipment && on("show_dialog_allegro_shipment")) {
        const value = typeof attrs.tracking_url === 'string' && attrs.tracking_url.startsWith('https://')
          ? `<a href="${esc(attrs.tracking_url)}" target="_blank" rel="noopener noreferrer">${esc(shipment)}</a>`
          : esc(shipment);
        html += row(this._localize("dialog.allegro_shipment"), value);
      }
    }
    return html;
  }

  getCourierImage(name) {
    const n = name.toLowerCase();
    if (this.config.courier_logos && this.config.courier_logos[n]) {
      return this.config.courier_logos[n];
    }

    const LOGOS = {
      'allegro one': 'https://a.allegroimg.com/original/1290dc/e7e2356c4e71897171bbcdd359d4',
      'inpost': 'https://upload.wikimedia.org/wikipedia/commons/c/c5/InPost_logo.svg',
      'dhl': 'https://upload.wikimedia.org/wikipedia/commons/a/ac/DHL_Logo.svg',
      'dpd': 'https://upload.wikimedia.org/wikipedia/commons/a/ab/DPD_logo_%282015%29.svg',
      'pocztex': 'https://www.poczta-polska.pl/wp-content/uploads/2023/04/logo-Pocztex-podstawowy.svg',
      'gls': 'https://upload.wikimedia.org/wikipedia/commons/a/a6/GLS_Logo_2021.svg',
      'orlen': 'https://www.orlenpaczka.pl/wp-content/themes/orlenpaczka/img/logo.svg'
    };

    for (const [key, url] of Object.entries(LOGOS)) {
      if (n.includes(key)) return url;
    }
    return null;
  }

  openDialog(entityId, options = {}) {
    const { reopen = true, fromMcUuid = null } = options;
    const stateObj = this._hass.states[entityId];
    if (!stateObj) return;
    if (this._openDialogEntityId !== entityId) {
      this._manageAccordionOpen = false;
    }
    this._openDialogEntityId = entityId;
    this._openDialogMcUuid = null;
    if (fromMcUuid !== undefined) {
      this._fromMcUuid = fromMcUuid;
    }

    const attrs = stateObj.attributes;
    const rawStr = attrs.raw_response;
    const friendlyName = this._isEnabled("show_dialog_sender")
      ? (attrs.sender || attrs.sender_name || attrs.recipient_name || attrs.tracking_number)
      : attrs.tracking_number;
    
    const titleEl = this.querySelector('#modal-title');
    if (titleEl.innerText !== friendlyName) titleEl.innerText = friendlyName;

    // Header Actions Check
    const refreshShipmentButtonId = this._getRefreshShipmentButtonId(attrs);
    const hideShipmentButtonId = this._getHideShipmentButtonId(attrs);
    let headerActionsHtml = '';
    
    if (this._isEnabled("show_dialog_entity_button")) {
      headerActionsHtml += `<button class="header-icon-btn" data-entity-button="${entityId}" title="${this._localize("dialog.show_entity")}"><ha-icon icon="mdi:information-outline"></ha-icon></button>`;
    }
    if (refreshShipmentButtonId) {
      headerActionsHtml += `<button class="header-icon-btn" data-refresh-button="${refreshShipmentButtonId}" title="${this._localize("dialog.refresh_shipment")}"><ha-icon icon="mdi:refresh"></ha-icon></button>`;
    }
    if (hideShipmentButtonId) {
      headerActionsHtml += `<button class="header-icon-btn" data-hide-button="${hideShipmentButtonId}" title="${this._localize("dialog.hide_shipment")}"><ha-icon icon="mdi:eye-off-outline"></ha-icon></button>`;
    }
    // The dialog is re-run on every state update; rewriting identical markup
    // would drop the user's text selection mid-copy, so only touch the DOM when
    // the markup actually changed. Listeners are bound in the same branch,
    // otherwise skipping the rewrite would stack duplicates on the old nodes.
    const headerDynamicContainer = this.querySelector('#header-dynamic-actions');
    const headerChanged = this._lastModalHeaderHtml !== headerActionsHtml;
    if (headerDynamicContainer && headerChanged) {
      headerDynamicContainer.innerHTML = headerActionsHtml;
    }
    this._lastModalHeaderHtml = headerActionsHtml;

    // Bind Header Listeners
    const entityBtn = headerChanged ? this.querySelector('[data-entity-button]') : null;
    if (entityBtn) {
      entityBtn.addEventListener('click', () => {
        this._closeDialog();
        this.dispatchEvent(new CustomEvent("hass-more-info", {
          detail: { entityId },
          bubbles: true,
          composed: true
        }));
      });
    }

    const refreshBtn = headerChanged ? this.querySelector('[data-refresh-button]') : null;
    if (refreshBtn) {
      refreshBtn.addEventListener('click', async () => {
        const refreshEntityId = refreshBtn.getAttribute('data-refresh-button');
        if (!refreshEntityId) return;
        
        refreshBtn.classList.add('loading');
        
        try {
            await this._pressButtonEntity(refreshEntityId);
        } finally {
            setTimeout(() => {
                refreshBtn.classList.remove('loading');
            }, 400);
        }
      });
    }

    const hideBtn = headerChanged ? this.querySelector('[data-hide-button]') : null;
    if (hideBtn) {
      hideBtn.addEventListener('click', async () => {
        const hideEntityId = hideBtn.getAttribute('data-hide-button');
        if (!hideEntityId) return;
        if (!window.confirm(this._localize("dialog.hide_shipment_confirm"))) return;
        await this._pressButtonEntity(hideEntityId);
        if (this._fromMcUuid) {
          const remaining = this._getMcItems(this._fromMcUuid).filter((item) => item.entity_id !== entityId);
          if (remaining.length > 1) {
            this.openMulticompartmentDialog(this._fromMcUuid);
            return;
          }
        }
        this._closeDialog();
      });
    }

    // Modal Content
    let backHtml = '';
    if (this._fromMcUuid && this._getMcItems(this._fromMcUuid).length > 1) {
      backHtml = `
        <div class="modal-back-row">
          <button type="button" class="modal-back-btn" data-back-mc="${this._escapeHtml(this._fromMcUuid)}">
            <ha-icon icon="mdi:arrow-left"></ha-icon>
            <span>${this._localize("dialog.back_to_multicompartment")}</span>
          </button>
        </div>
      `;
    }
    let infoHtml = `${backHtml}<div class="modal-info-block">`;
    
    if (this._isEnabled("show_dialog_tracking_number") && attrs.tracking_number) {
        infoHtml += `<div class="modal-info-block-row"><strong>${this._localize("dialog.tracking_number")}:</strong> <span class="val" style="flex-grow: 1; user-select: all; -webkit-user-select: all;">${this._escapeHtml(attrs.tracking_number)}</span></div>`;
    }
    if (this._isEnabled("show_dialog_courier") && attrs.courier) {
      infoHtml += `<div class="modal-info-block-row"><strong>${this._localize("dialog.courier_name")}:</strong> <span class="val">${attrs.courier}</span></div>`;
    }
    if (this._isEnabled("show_dialog_sender") && (attrs.sender || attrs.sender_name)) {
      infoHtml += `<div class="modal-info-block-row"><strong>${this._localize("dialog.sender")}:</strong> <span class="val">${attrs.sender || attrs.sender_name}</span></div>`;
    }
    if (this._isEnabled("show_dialog_account_contact") && attrs.account_contact) {
      infoHtml += `<div class="modal-info-block-row"><strong>${this._localize("dialog.account_contact")}:</strong> <span class="val">${attrs.account_contact}</span></div>`;
    }
    if (this._isEnabled("show_dialog_recipient") && attrs.recipient_name) {
      infoHtml += `<div class="modal-info-block-row"><strong>${this._localize("dialog.recipient")}:</strong> <span class="val">${attrs.recipient_name}</span></div>`;
    }
    if (this._isEnabled("show_dialog_pickup_code") && (attrs.pickup_code || attrs.open_code)) {
      infoHtml += `<div class="modal-info-block-row"><strong>${this._localize("dialog.pickup_code")}:</strong> <span class="val">${attrs.pickup_code || attrs.open_code}</span></div>`;
    }
    infoHtml += this._renderAllegroInfo(attrs);
    
    let timelineHtml = '';
    let manageShipmentAvailable = false;
    let dhlOptions = [];
    
    if (rawStr) {
      try {
        const raw = JSON.parse(rawStr);
        const courier = (attrs.courier || (entityId.includes('inpost') ? 'inpost' : '')).toLowerCase();
        manageShipmentAvailable = this._hasDpdManageAction(attrs, raw);
        const locale = this._hass.language || 'pl';
        const formatDateTime = (value) => {
          if (!value) return '';
          const date = new Date(value);
          if (Number.isNaN(date.getTime())) return value;
          return date.toLocaleString(locale, { dateStyle: 'short', timeStyle: 'short' });
        };

        if (courier === 'dpd') {
          // Courier person details appear once the parcel is out for delivery.
          const dpdDelivery = raw.delivery || {};
          const dpdCourierName = dpdDelivery.courier_name;
          const dpdCourierPhone = dpdDelivery.courier_phone || raw.courier_phone;
          if (this._isEnabled("show_dialog_courier_contact") && dpdCourierName) {
            infoHtml += `<div class="modal-info-block-row"><strong>${this._localize("labels.courier_default")}:</strong> <span class="val">${dpdCourierName}</span></div>`;
          }
          if (this._isEnabled("show_dialog_courier_contact") && dpdCourierPhone) {
            infoHtml += `<div class="modal-info-block-row"><strong>${this._localize("dialog.courier_phone")}:</strong> <span class="val"><a href="tel:${dpdCourierPhone}" class="modal-nav-link">${dpdCourierPhone}</a></span></div>`;
          }
        }

        if (this._isEnabled("show_dialog_cod") && courier === 'pocztex' && (raw.amount !== null || raw.paymentAmount !== null)) {
          const amountStr = (raw.amount !== null ? raw.amount : raw.paymentAmount) + ' zł';
          infoHtml += `<div class="modal-info-block-row"><strong>${this._localize("dialog.cod")}:</strong> <span class="val">${amountStr}</span></div>`;
        }

        if (this._isEnabled("show_dialog_delivery_date") && courier === 'dpd') {
          const plannedDeliveryDate = raw.delivery?.planned_delivery_date || raw.planned_delivery_date;
          if (plannedDeliveryDate) {
            infoHtml += `<div class="modal-info-block-row"><strong>${this._localize("dialog.planned_delivery_date")}:</strong> <span class="val">${plannedDeliveryDate}</span></div>`;
          }
        }

        if (courier === 'dhl') {
          const packageType = attrs.package_type || raw.packageType;
          if (this._isEnabled("show_dialog_package_type") && packageType) {
            const typeKey = `dhl.${String(packageType).toUpperCase()}`;
            const typeLabel = this._localize(typeKey) !== typeKey ? this._localize(typeKey) : packageType;
            infoHtml += `<div class="modal-info-block-row"><strong>${this._localize("dialog.package_type")}:</strong> <span class="val">${typeLabel}</span></div>`;
          }

          // Every option carries a ready-made https link, so there is no need
          // for the button-entity round trip DPD needs.
          dhlOptions = (Array.isArray(raw.options) ? raw.options : [])
            .filter(option => option?.label && typeof option.link === 'string' && option.link.startsWith('https://'));

          if (this._isEnabled("show_dialog_delivery_address") && attrs.delivery_address) {
            infoHtml += `<div class="modal-info-block-row"><strong>${this._localize("dialog.delivery_address")}:</strong> <span class="val">${attrs.delivery_address}</span></div>`;
          }

          if (this._isEnabled("show_dialog_cod") && raw.cod?.codService && raw.cod?.paymentValue) {
            const codStr = `${raw.cod.paymentValue} ${raw.cod.currency || 'zł'}`;
            infoHtml += `<div class="modal-info-block-row"><strong>${this._localize("dialog.cod")}:</strong> <span class="val">${codStr}</span></div>`;
          }

          // DHL fills the delivery window only once the parcel is on its way;
          // until then every date field stays null.
          if (this._isEnabled("show_dialog_delivery_date")) {
            const timeline = raw.menuTimelineLabel || {};
            const plannedFrom = raw.planOfDeliveryFromUtc || raw.deliveryUpToUtc || timeline.dateUtc;
            const plannedTo = raw.planOfDeliveryToUtc || timeline.dateToUtc;
            if (plannedFrom) {
              const plannedStr = plannedTo
                ? `${formatDateTime(plannedFrom)} - ${formatDateTime(plannedTo)}`
                : formatDateTime(plannedFrom);
              infoHtml += `<div class="modal-info-block-row"><strong>${this._localize("dialog.planned_delivery_date")}:</strong> <span class="val">${plannedStr}</span></div>`;
            }
          }
        }

        if (courier === 'gls') {
          const trackingShipment = raw.trackingShipment || {};
          const glsWeight = attrs.weight ?? trackingShipment.weight;
          const packageCount = attrs.package_count ?? attrs.package_amount ?? trackingShipment.packageAmount;
          const courierPhone = attrs.courier_phone_number || trackingShipment.courierPhoneNumber;
          const deliveryMethod = attrs.delivery_method || trackingShipment.deliveryMethod;
          const parcelShopType = attrs.parcel_shop_type || trackingShipment.parcelShop?.parcelShopType;

          const knownUids = new Set();
          if (trackingShipment.sender?.shipmentSenderUid) knownUids.add(trackingShipment.sender.shipmentSenderUid);
          if (trackingShipment.receiver?.shipmentSenderUid) knownUids.add(trackingShipment.receiver.shipmentSenderUid);
          const courierParty = Array.isArray(raw.trackingParties)
            ? raw.trackingParties.find(p => p.shipmentSenderUid && !knownUids.has(p.shipmentSenderUid))
            : null;
          const courierPersonName = courierParty?.shipmentName
            ? courierParty.shipmentName.replace(/\s+\d+\s*$/, '').trim()
            : null;

          if (this._isEnabled("show_dialog_parcel_size") && packageCount) {
            infoHtml += `<div class="modal-info-block-row"><strong>${this._localize("dialog.package_count")}:</strong> <span class="val">${packageCount}</span></div>`;
          }
          if (this._isEnabled("show_dialog_parcel_size") && glsWeight) {
            infoHtml += `<div class="modal-info-block-row"><strong>${this._localize("dialog.weight")}:</strong> <span class="val">${glsWeight} kg</span></div>`;
          }
          if (this._isEnabled("show_dialog_courier_contact") && courierPersonName) {
            infoHtml += `<div class="modal-info-block-row"><strong>${this._localize("labels.courier_default")}:</strong> <span class="val">${courierPersonName}</span></div>`;
          }
          if (this._isEnabled("show_dialog_courier_contact") && courierPhone) {
            infoHtml += `<div class="modal-info-block-row"><strong>${this._localize("dialog.courier_phone")}:</strong> <span class="val"><a href="tel:${courierPhone}" class="modal-nav-link">${courierPhone}</a></span></div>`;
          }
          if (this._isEnabled("show_dialog_delivery_method") && deliveryMethod) {
            infoHtml += `<div class="modal-info-block-row"><strong>${this._localize("dialog.delivery_method")}:</strong> <span class="val">${this._localize(`gls.${deliveryMethod}`)}</span></div>`;
          }
          if (this._isEnabled("show_dialog_parcel_shop_type") && parcelShopType) {
            infoHtml += `<div class="modal-info-block-row"><strong>${this._localize("dialog.parcel_shop_type")}:</strong> <span class="val">${parcelShopType}</span></div>`;
          }

          // The receiver object carries no address; the postcode lives either directly on
          // trackingShipment or on the matching party in trackingParties.
          const receiverParty = Array.isArray(raw.trackingParties)
            ? raw.trackingParties.find((p) => p?.shipmentSenderUid === trackingShipment.receiver?.shipmentSenderUid)
            : null;
          const postalCode = trackingShipment.receiverPostalCode
            || trackingShipment.receiver?.postalCode
            || receiverParty?.postalCode;
          // BetterMile keys parcels on the number WITHOUT its trailing check digit:
          // 266107156012 -> 26610715601. The full number returns PARCEL-404.
          const shipmentNo = trackingShipment.shipmentNo || attrs.tracking_number;
          const trackingNo = shipmentNo && String(shipmentNo).length > 1
            ? String(shipmentNo).slice(0, -1)
            : shipmentNo;
          if (this._isEnabled("show_dialog_live_tracking") && attrs.status_key === "handed_out_for_delivery" && deliveryMethod === "TO_DOOR" && postalCode && trackingNo) {
            const rttUrl = `https://gls-rtt.com/#/preview/gls-pl/pl/${encodeURIComponent(trackingNo)}/${encodeURIComponent(postalCode)}`;
            infoHtml += `
              <div class="manage-shipment-container">
                <a href="${rttUrl}" target="_blank" rel="noopener noreferrer" class="manage-btn" data-manage-link="true">
                  <ha-icon icon="mdi:map-marker-path"></ha-icon>
                  <span>${this._localize("dialog.live_tracking")}</span>
                </a>
              </div>`;
          }
        }

        let locationName = attrs.location || attrs.current_location;
        const dpdPoint = courier === 'dpd' ? (raw.delivery?.point || raw.delivery_point) : null;
        if (locationName && courier === 'inpost' && raw.pickUpPoint?.locationDescription) {
          locationName += ' (' + raw.pickUpPoint.locationDescription + ')';
        }
        if (dpdPoint && typeof dpdPoint === 'object') {
          const a = dpdPoint.address || {};
          const addr = [a.address, a.postal_code, a.city].filter(Boolean).join(', ');
          locationName = [dpdPoint.name, addr].filter(Boolean).join('<br>') || locationName;
        }
        if (!locationName && courier === 'pocztex') {
          const pickupLocation = raw.pickupLocation;
          if (typeof pickupLocation === 'string') {
            locationName = pickupLocation;
          } else if (pickupLocation && typeof pickupLocation === 'object') {
            const parts = [
              pickupLocation.name,
              pickupLocation.address,
              pickupLocation.street,
              pickupLocation.city
            ].filter(Boolean);
            if (parts.length > 0) {
              locationName = parts.join(', ');
            }
          }
        }
        if (this._isEnabled("show_dialog_pickup_point") && locationName) {
          let locationContent = `<span class="val">${locationName}`;
          
          if (this._isEnabled("show_dialog_navigation") && courier === 'inpost' && raw.pickUpPoint?.location?.latitude && raw.pickUpPoint?.location?.longitude) {
            const lat = raw.pickUpPoint.location.latitude;
            const lon = raw.pickUpPoint.location.longitude;
            locationContent += `<br><a href="https://maps.google.com/?q=${lat},${lon}" target="_blank" class="modal-nav-link"><ha-icon icon="mdi:map-marker-path"></ha-icon> ${this._localize("dialog.navigate")}</a>`;
          }

          if (this._isEnabled("show_dialog_navigation") && dpdPoint && dpdPoint.latitude && dpdPoint.longitude) {
            locationContent += `<br><a href="https://maps.google.com/?q=${dpdPoint.latitude},${dpdPoint.longitude}" target="_blank" class="modal-nav-link"><ha-icon icon="mdi:map-marker-path"></ha-icon> ${this._localize("dialog.navigate")}</a>`;
          }

          const allegroPoint = courier === 'allegro' ? attrs.pickup_point_location : null;
          if (this._isEnabled("show_dialog_navigation") && allegroPoint?.lat && allegroPoint?.lon) {
            locationContent += `<br><a href="https://maps.google.com/?q=${Number(allegroPoint.lat)},${Number(allegroPoint.lon)}" target="_blank" class="modal-nav-link"><ha-icon icon="mdi:map-marker-path"></ha-icon> ${this._localize("dialog.navigate")}</a>`;
          }
          if (courier === 'allegro' && attrs.pickup_point_hours) {
            locationContent += `<br><span class="timeline-desc">${this._escapeHtml(attrs.pickup_point_hours)}</span>`;
          }

          if (this._isEnabled("show_dialog_navigation") && courier === 'dhl' && raw.lockerInfo?.latitude && raw.lockerInfo?.longitude) {
            locationContent += `<br><a href="https://maps.google.com/?q=${raw.lockerInfo.latitude},${raw.lockerInfo.longitude}" target="_blank" class="modal-nav-link"><ha-icon icon="mdi:map-marker-path"></ha-icon> ${this._localize("dialog.navigate")}</a>`;
          }

          if (courier === 'dhl') {
            const hours = raw.dhlPointInfo?.openHoursMonFri || raw.lockerInfo?.lockerOpenHours;
            if (hours) {
              locationContent += `<br><span class="timeline-desc">${hours}</span>`;
            }
          }

          locationContent += `</span>`;
          infoHtml += `<div class="modal-info-block-row"><strong>${this._localize("dialog.pickup_point")}:</strong> ${locationContent}</div>`;
          const progressBarModal = this._renderInPostProgressBar(attrs);
          if (progressBarModal) {
            infoHtml += `<div class="modal-info-block-row modal-progress-row">${progressBarModal}</div>`;
          }
        }

        let qrPayload = null;
        if (courier === 'inpost') {
          qrPayload = raw.qrCode;
        } else if (courier === 'dhl' && ['LOCKER', 'POP'].includes(String(raw.packageType || '').toUpperCase())) {
          qrPayload = raw.qrCode;
        } else if (courier === 'allegro') {
          const own = Array.isArray(attrs.waybills) ? attrs.waybills.find(w => w?.qr_code) : null;
          const waybills = raw.delivery?.waybillsData?.waybills || raw.status?.primary?.waybillsData?.waybills || [];
          qrPayload = own?.qr_code
            || (attrs.parcel_count ? null : waybills.map(w => w?.pickupCode?.qrCode).find(Boolean))
            || null;
        }
        if (this._isEnabled("show_dialog_qr_code") && qrPayload && attrs.status_key === 'waiting_for_pickup') {
           const qrUrlSmall = `https://quickchart.io/qr?text=${encodeURIComponent(qrPayload)}&size=150&margin=0&ecLevel=H`;
           const qrUrlLarge = `https://quickchart.io/qr?text=${encodeURIComponent(qrPayload)}&size=500&margin=0&ecLevel=H`;
           infoHtml += `
             <div class="qr-code-container" data-large-qr="${qrUrlLarge}">
               <img src="${qrUrlSmall}" alt="QR Code" />
               <div class="qr-code-label">${this._localize("dialog.scan_qr")}</div>
             </div>
           `;
        }

        if (this._isEnabled("show_dialog_parcel_size") && courier === 'inpost' && raw.parcelSize) {
          const rawSize = raw.parcelSize.toUpperCase();
          const sizeInfo = {
            'D': { label: 'XS', dim: '4 x 23 x 40 cm', weight: '3 kg', name: 'Mini' },
            'A': { label: 'S', dim: '8 x 38 x 64 cm', weight: '25 kg', name: 'Mała' },
            'E': { label: 'S', dim: '8 x 38 x 64 cm', weight: '25 kg', name: 'Mała' },
            'H': { label: 'S', dim: '8 x 38 x 64 cm', weight: '25 kg', name: 'Mała' },
            'B': { label: 'M', dim: '19 x 38 x 64 cm', weight: '25 kg', name: 'Średnia' },
            'F': { label: 'M', dim: '19 x 38 x 64 cm', weight: '25 kg', name: 'Średnia' },
            'I': { label: 'M', dim: '19 x 38 x 64 cm', weight: '25 kg', name: 'Średnia' },
            'C': { label: 'L', dim: '41 x 38 x 64 cm', weight: '25 kg', name: 'Duża' },
            'G': { label: 'L', dim: '41 x 38 x 64 cm', weight: '25 kg', name: 'Duża' },
            'J': { label: 'L', dim: '41 x 38 x 64 cm', weight: '25 kg', name: 'Duża' }
          };

          const sInfo = sizeInfo[rawSize];

          if (sInfo) {
            const activeLabel = sInfo.label;

            infoHtml += `
              <div style="margin-top: 16px; border-top: 1px solid var(--divider-color, rgba(0,0,0,0.05)); padding-top: 12px;">
                <strong style="display:block; margin-bottom: 4px; color: var(--secondary-text-color);">${this._localize("dialog.parcel_size")}:</strong>
                <div class="parcel-sizes">
                    <div class="parcel-size ${activeLabel === 'XS' ? 'active' : ''}" title="Gabaryt XS (Mini): Max 4 x 23 x 40 cm, do 3 kg"><span class="box-xs"></span>XS</div>
                    <div class="parcel-size ${activeLabel === 'S' ? 'active' : ''}" title="Gabaryt S (Mala): Max 8 x 38 x 64 cm, do 25 kg"><span class="box-s"></span>S</div>
                    <div class="parcel-size ${activeLabel === 'M' ? 'active' : ''}" title="Gabaryt M (Srednia): Max 19 x 38 x 64 cm, do 25 kg"><span class="box-m"></span>M</div>
                    <div class="parcel-size ${activeLabel === 'L' ? 'active' : ''}" title="Gabaryt L (Duza): Max 41 x 38 x 64 cm, do 25 kg"><span class="box-l"></span>L</div>
                </div>
                <div class="parcel-size-info">${this._localize("dialog.max_dimensions")}: <strong>${sInfo.dim}</strong> (do ${sInfo.weight})</div>
              </div>`;
          } else {
            infoHtml += `
              <div class="modal-info-block-row">
                <strong>${this._localize("dialog.parcel_size")}:</strong>
                <span class="val"><span dir="ltr">${rawSize}</span></span>
              </div>`;
          }
        }

        if (courier === 'inpost' && raw.events && raw.events.length > 0) {
          raw.events.forEach(e => {
            const dateStr = new Date(e.date).toLocaleString(locale, { dateStyle: 'short', timeStyle: 'short' });
            timelineHtml += `
              <div class="timeline-item">
                <div class="timeline-date">${dateStr}</div>
                <div class="timeline-title">${e.eventTitle}</div>
                <div class="timeline-desc">${e.eventDescription || ''}</div>
              </div>`;
          });
        } else if (courier === 'dpd' && raw.statuses && raw.statuses.length > 0) {
          raw.statuses.forEach(s => {
            const dateStr = new Date(s.date).toLocaleString(locale, { dateStyle: 'short', timeStyle: 'short' });
            const title = this._localize(`dpd.${s.status}`) !== `dpd.${s.status}` ? this._localize(`dpd.${s.status}`) : s.status;
            timelineHtml += `
              <div class="timeline-item">
                <div class="timeline-date">${dateStr}</div>
                <div class="timeline-title">${title}</div>
              </div>`;
          });
        } else if (courier === 'pocztex' && Array.isArray(raw.history) && raw.history.length > 0) {
          [...raw.history].reverse().forEach(event => {
            const dateStr = formatDateTime(event.date);
            const title = event.state || event.stateCode || '';
            timelineHtml += `
              <div class="timeline-item">
                <div class="timeline-date">${dateStr}</div>
                <div class="timeline-title">${title}</div>
              </div>`;
          });
        } else if (courier === 'dhl') {
          // DHL exposes no event log at all - only a fixed four-point timeline
          // plus a headline describing where the parcel currently stands.
          const STEP_ORDER = {
            None: 0, Resigned: 0, Sent: 1, Route: 2, Delivery: 3,
            ReturnToSender: 4, Delivered: 5, DeliveredToSender: 6, Error: 7,
          };
          const currentStep = raw.timelineStep || attrs.timeline_step || 'None';
          // Lost / disposed parcels never light any step up in the DHL app.
          const brokenStatus = raw.status === 'TT_ZGN' || raw.status === 'TT_LIK';
          const isReached = (step) => !brokenStatus
            && (currentStep === step || STEP_ORDER[step] < (STEP_ORDER[currentStep] ?? -1));

          const plannedWindow = raw.planOfDeliveryFromUtc && raw.planOfDeliveryToUtc
            ? `${formatDateTime(raw.planOfDeliveryFromUtc)} - ${formatDateTime(raw.planOfDeliveryToUtc)}`
            : '';
          const steps = [
            {
              key: 'Sent',
              title: this._localize('dhl.step.SENT'),
              date: formatDateTime(raw.dateOfPostingUtc || raw.shipmentDateUtc),
              desc: '',
            },
            { key: 'Route', title: this._localize('dhl.step.ROUTE'), date: '', desc: '' },
            {
              key: 'Delivery',
              title: raw.timelineStep3Label || this._localize('dhl.step.DELIVERY'),
              date: formatDateTime(raw.deliveryDateUtc),
              desc: plannedWindow,
            },
            {
              key: 'Delivered',
              title: raw.timelineStep4Label || this._localize('dhl.step.DELIVERED'),
              date: formatDateTime(raw.receiptDateUtc),
              desc: '',
            },
          ];

          const renderStep = (step) => `
              <div class="timeline-item">
                ${step.date ? `<div class="timeline-date">${step.date}</div>` : ''}
                <div class="timeline-title">${step.title}</div>
                ${step.desc ? `<div class="timeline-desc">${step.desc}</div>` : ''}
              </div>`;

          // Only what already happened, newest first - same as every other
          // courier. The headline describes the newest entry, so it rides along
          // as its description.
          const reachedSteps = steps.filter(step => isReached(step.key)).reverse();
          if (reachedSteps.length === 0) {
            if (raw.step || raw.description) {
              timelineHtml += renderStep({ date: '', title: raw.step || '', desc: raw.description || '' });
            }
          } else {
            reachedSteps.forEach((step, index) => {
              timelineHtml += renderStep(index === 0
                ? { ...step, desc: [raw.description, step.desc].filter(Boolean).join('<br>') }
                : step);
            });
          }
        } else if (courier === 'allegro' && Array.isArray(attrs.timeline) && attrs.timeline.length) {
          // Allegro's own step list (paid, awaiting dispatch, on the way...):
          // show the steps reached so far, newest first, like other couriers.
          const steps = attrs.timeline;
          let current = steps.map((step) => !!step.active).lastIndexOf(true);
          if (current < 0) current = steps.length - 1;
          steps.slice(0, current + 1).reverse().forEach((step, index) => {
            const desc = index === 0 && attrs.delivery_estimate && this._isEnabled("show_dialog_delivery_date")
              ? `<div class="timeline-desc">${this._escapeHtml(attrs.delivery_estimate)}</div>`
              : '';
            timelineHtml += `
              <div class="timeline-item"${step.error ? ' style="color: var(--error-color);"' : ''}>
                <div class="timeline-date">${this._escapeHtml(step.hint || '')}</div>
                <div class="timeline-title">${this._escapeHtml(step.label || '')}</div>
                ${desc}
              </div>`;
          });
        } else if (courier === 'orlen' && Array.isArray(attrs.history) && attrs.history.length) {
          attrs.history.forEach(event => {
            timelineHtml += `
              <div class="timeline-item">
                <div class="timeline-date">${this._escapeHtml(formatDateTime(event.time))}</div>
                <div class="timeline-title">${this._escapeHtml(event.label || event.status || '')}</div>
                ${event.comment ? `<div class="timeline-desc">${this._escapeHtml(event.comment)}</div>` : ''}
              </div>`;
          });
        } else if (courier === 'gls' && Array.isArray(raw.trackingShipmentPackages)) {
          const glsEvents = [];
          raw.trackingShipmentPackages.forEach(pkg => {
            const packageNo = pkg.packageNo || pkg.packageTrackingId || '';
            (pkg.packageStatuses || []).forEach(event => {
              glsEvents.push({ ...event, packageNo });
            });
          });
          glsEvents
            .sort((a, b) => new Date(b.packageStatusDate || 0) - new Date(a.packageStatusDate || 0))
            .forEach(event => {
              const dateStr = formatDateTime(event.packageStatusDate);
              const title = event.packageStatusName || event.packageStatusDescription || '';
              const place = event.packageStatusPlace ? `<div class="timeline-desc">${event.packageStatusPlace}</div>` : '';
              const description = event.packageStatusDescription ? `<div class="timeline-desc">${event.packageStatusDescription}</div>` : '';
              timelineHtml += `
                <div class="timeline-item">
                  <div class="timeline-date">${dateStr}</div>
                  <div class="timeline-title">${title}</div>
                  ${description}
                  ${place}
                </div>`;
            });
        }
      } catch (e) {
        console.error("Failed to parse raw_response", e);
      }
    } else {
      if (this._isEnabled("show_dialog_pickup_point") && (attrs.location || attrs.current_location)) {
        infoHtml += `<div class="modal-info-block-row"><strong>${this._localize("dialog.pickup_point")}:</strong> <span class="val">${attrs.location || attrs.current_location}</span></div>`;
        const progressBarModal = this._renderInPostProgressBar(attrs);
        if (progressBarModal) {
          infoHtml += `<div class="modal-info-block-row modal-progress-row">${progressBarModal}</div>`;
        }
      }
    }

    infoHtml += `</div>`;

    const manageShipmentButtonId = this._isEnabled("show_dialog_manage_button") && manageShipmentAvailable
      ? this._getManageShipmentButtonId(attrs)
      : null;
    const manageShipmentUrl = this._getCachedManageUrl(attrs);
    const manageShipmentPending = manageShipmentButtonId && !manageShipmentUrl && this._isManageUrlPending(attrs);
      
    let finalHtml = infoHtml;

    // DHL hands out a ready-made https link per action - too many to stack as
    // buttons, so they live behind the same "manage shipment" affordance DPD
    // gets, collapsed until asked for.
    if (this._isEnabled("show_dialog_manage_button") && dhlOptions.length > 0) {
      finalHtml += `
        <div class="manage-shipment-container">
          <details class="manage-accordion">
            <summary class="manage-btn">
              <ha-icon icon="mdi:open-in-new"></ha-icon>
              <span>${this._localize("dialog.manage_shipment")}</span>
              <ha-icon class="chevron" icon="mdi:chevron-down"></ha-icon>
            </summary>
            <div class="manage-options">
              ${dhlOptions.map(option => `
              <a href="${option.link}" target="_blank" rel="noopener noreferrer">
                <ha-icon icon="mdi:chevron-right"></ha-icon>
                <span>${option.label}${option.description ? `<span class="manage-option-desc">${option.description}</span>` : ''}</span>
              </a>`).join('')}
            </div>
          </details>
        </div>`;
    }
    
    if (manageShipmentButtonId) {
      this._prefetchManageShipmentUrl(manageShipmentButtonId, attrs, entityId);
      finalHtml += `
        <div class="manage-shipment-container">
          ${manageShipmentUrl ? `
          <a href="${manageShipmentUrl}" target="_blank" rel="noopener noreferrer" class="manage-btn" data-manage-link="true">
            <ha-icon icon="mdi:open-in-new"></ha-icon>
            <span>${this._localize("dialog.manage_shipment")}</span>
          </a>
          ` : `
          <button type="button" class="manage-btn ${manageShipmentPending ? 'loading' : ''}" disabled>
            <ha-icon icon="mdi:open-in-new"></ha-icon>
            <span>${this._localize("dialog.manage_shipment")}</span>
          </button>
          `}
        </div>
      `;
    }
    
    if (this._isEnabled("show_dialog_timeline")) {
      finalHtml += `<div class="modal-section-title">${this._localize("dialog.timeline")}</div>`;
      if (timelineHtml) {
        finalHtml += `<div class="timeline">${timelineHtml}</div>`;
      } else {
        finalHtml += `<div class="timeline-desc">${this._localize("dialog.no_timeline")}</div>`;
      }
    }

    const modalContent = this.querySelector('#modal-content');
    if (this._lastModalContentHtml !== finalHtml) {
      this._lastModalContentHtml = finalHtml;
      modalContent.innerHTML = finalHtml;

      const manageAccordion = modalContent.querySelector('.manage-accordion');
      if (manageAccordion) {
        manageAccordion.open = this._manageAccordionOpen === true;
        manageAccordion.addEventListener('toggle', () => {
          this._manageAccordionOpen = manageAccordion.open;
        });
      }

      const qrContainer = modalContent.querySelector('.qr-code-container');
      if (qrContainer) {
        qrContainer.addEventListener('click', () => {
          const largeUrl = qrContainer.getAttribute('data-large-qr');
          const fullscreenOverlay = this.querySelector('#qr-fullscreen');
          this.querySelector('#qr-fullscreen-img').src = largeUrl;
          fullscreenOverlay.classList.add('open');
        });
      }

      const backBtn = modalContent.querySelector('[data-back-mc]');
      if (backBtn) {
        backBtn.addEventListener('click', () => {
          const mc = backBtn.getAttribute('data-back-mc');
          if (mc) {
            this.openMulticompartmentDialog(mc);
          }
        });
      }
    }

    if (reopen) {
      this.querySelector('#modal-overlay').classList.add('open');
    }
  }

  _parseRawResponse(rawStr) {
    if (!rawStr) return {};
    if (typeof rawStr === 'object') return rawStr;
    try {
      return JSON.parse(rawStr) || {};
    } catch (e) {
      return {};
    }
  }

  _getParcelSize(attrs, raw) {
    return attrs?.parcel_size || raw?.parcelSize || '';
  }

  _formatShipmentsCount(count) {
    const lang = normalizeLanguage(this._hass?.language || this._hass?.locale?.language || (typeof navigator !== "undefined" ? navigator.language : DEFAULT_LANGUAGE));
    if (lang === "pl") {
      if (count === 1) return this._localize("labels.shipments_count_one");
      if (count % 10 >= 2 && count % 10 <= 4 && (count % 100 < 10 || count % 100 >= 20)) {
        return this._localize("labels.shipments_count_few").replace("{count}", String(count));
      }
      return this._localize("labels.shipments_count_many").replace("{count}", String(count));
    }
    if (count === 1) return this._localize("labels.shipments_count_one");
    return this._localize("labels.shipments_count_many").replace("{count}", String(count));
  }

  _getMcUuid(attrs, entityId) {
    if (!attrs) return null;
    const courier = String(attrs.courier || '').toLowerCase();
    if (!courier.includes('inpost') && !(entityId && entityId.includes('inpost'))) {
      return null;
    }
    const statusKey = String(attrs.status_key || '').toLowerCase();
    if (['delivered', 'returned', 'cancelled'].includes(statusKey)) return null;

    if (attrs.is_multi_compartment === false) return null;
    if (attrs.multi_compartment_uuid) {
      return String(attrs.multi_compartment_uuid);
    }

    const raw = this._parseRawResponse(attrs.raw_response);
    const mc = raw?.multiCompartment;
    if (mc && mc.uuid && mc.collected !== true) {
      return String(mc.uuid);
    }
    return null;
  }

  _getFilteredShipmentEntities() {
    if (!this._hass?.states) return [];
    return Object.keys(this._hass.states).filter((entityId) => {
      if (!entityId.startsWith("sensor.")) return false;
      const stateObj = this._hass.states[entityId];
      if (!stateObj || stateObj.state === 'unavailable') return false;
      return stateObj.attributes?.integration_domain === "polish_shipment_tracking"
        && this._passesFilters(stateObj.attributes);
    });
  }

  _getMcItems(mcUuid) {
    if (!mcUuid || !this._hass?.states) return [];
    return this._getFilteredShipmentEntities()
      .filter((id) => this._getMcUuid(this._hass.states[id]?.attributes, id) === mcUuid)
      .map((id) => this._hass.states[id])
      .filter(Boolean);
  }

  _parseExpiryMs(expiryStr) {
    if (!expiryStr) return Infinity;
    if (typeof expiryStr === 'number') return expiryStr > 1e11 ? expiryStr : expiryStr * 1000;
    const clean = String(expiryStr).trim().replace(' ', 'T');
    const t = new Date(clean).getTime();
    return Number.isNaN(t) ? Infinity : t;
  }

  _getSortKeyForAttrs(attrs) {
    const key = String(attrs?.status_key || '').toLowerCase();
    const isPickup = key === 'waiting_for_pickup' || Boolean(attrs?.open_code || attrs?.pickup_code);
    const isTransit = key === 'handed_out_for_delivery' || key === 'in_transport';
    const score = isPickup ? 0 : (isTransit ? 1 : 2);
    const expiryMs = score === 0 ? this._parseExpiryMs(attrs?.expiry_date) : Infinity;
    return { score, expiryMs };
  }

  _getSortKeyForGroup(group) {
    const entityIds = group.type === 'multicompartment' ? group.entityIds : [group.entityId];
    let bestScore = 2;
    let bestExpiry = Infinity;
    entityIds.forEach((entityId) => {
      const attrs = this._hass?.states?.[entityId]?.attributes;
      if (!attrs) return;
      const { score, expiryMs } = this._getSortKeyForAttrs(attrs);
      if (score < bestScore) {
        bestScore = score;
        bestExpiry = expiryMs;
      } else if (score === bestScore && expiryMs < bestExpiry) {
        bestExpiry = expiryMs;
      }
    });
    return { score: bestScore, expiryMs: bestExpiry };
  }

  _selectPrimaryMcItem(items) {
    if (!items.length) return null;
    const scoreItem = (item) => {
      const attrs = item.attributes || {};
      const raw = this._parseRawResponse(attrs.raw_response);
      const key = String(attrs.status_key || '').toLowerCase();
      const isWaiting = key === 'waiting_for_pickup';
      const hasPresentation = attrs.multi_compartment_presentation === true || raw?.multiCompartment?.presentation === true;
      const hasCode = Boolean(attrs.open_code || attrs.pickup_code || raw?.openCode);
      const hasList = (Array.isArray(attrs.multi_compartment_shipments) && attrs.multi_compartment_shipments.length > 0)
        || (Array.isArray(raw?.multiCompartment?.shipmentNumbers) && raw.multiCompartment.shipmentNumbers.length > 0);
      const { score } = this._getSortKeyForAttrs(attrs);
      return (isWaiting ? 1000 : 0)
        + (hasPresentation ? 200 : 0)
        + (hasCode ? 100 : 0)
        + (hasList ? 50 : 0)
        - score * 10;
    };
    return [...items].sort((a, b) => scoreItem(b) - scoreItem(a))[0];
  }

  _resolveMcGroupData(items) {
    const primaryItem = this._selectPrimaryMcItem(items);
    const ordered = [primaryItem, ...items.filter((it) => it !== primaryItem)].filter(Boolean);
    const primaryAttrs = primaryItem?.attributes || {};
    const primaryRaw = this._parseRawResponse(primaryAttrs.raw_response);

    let openCode = '';
    let qrCode = '';
    let location = '';
    let pickUpPoint = null;
    let earliestProgressAttrs = null;
    let earliestExpiry = Infinity;

    ordered.forEach((item) => {
      const attrs = item.attributes || {};
      const raw = this._parseRawResponse(attrs.raw_response);
      if (!openCode) {
        openCode = attrs.open_code || attrs.pickup_code || raw.openCode || '';
      }
      if (!qrCode && raw.qrCode) {
        qrCode = raw.qrCode;
      }
      if (!location && (attrs.location || attrs.current_location)) {
        location = attrs.location || attrs.current_location;
      }
      if (!pickUpPoint && raw.pickUpPoint) {
        pickUpPoint = raw.pickUpPoint;
      }
      const exp = this._parseExpiryMs(attrs.expiry_date);
      if (attrs.expiry_date && exp < earliestExpiry) {
        earliestExpiry = exp;
        earliestProgressAttrs = attrs;
      }
    });

    if (!earliestProgressAttrs && primaryAttrs.expiry_date) {
      earliestProgressAttrs = primaryAttrs;
    }

    return {
      primaryItem,
      primaryAttrs,
      primaryRaw,
      openCode,
      qrCode,
      location,
      pickUpPoint,
      progressAttrs: earliestProgressAttrs || primaryAttrs,
    };
  }

  _groupEntities(entitiesToShow) {
    if (!this._isEnabled("group_multicompartment")) {
      return entitiesToShow.map((id) => ({ type: "single", entityId: id }));
    }

    const mcGroups = new Map();
    entitiesToShow.forEach((entityId) => {
      const stateObj = this._hass.states[entityId];
      const uuid = this._getMcUuid(stateObj?.attributes, entityId);
      if (uuid) {
        if (!mcGroups.has(uuid)) {
          mcGroups.set(uuid, []);
        }
        mcGroups.get(uuid).push(entityId);
      }
    });

    const result = [];
    const seenMcUuids = new Set();

    entitiesToShow.forEach((entityId) => {
      const stateObj = this._hass.states[entityId];
      const uuid = this._getMcUuid(stateObj?.attributes, entityId);
      if (uuid && mcGroups.get(uuid).length > 1) {
        if (!seenMcUuids.has(uuid)) {
          seenMcUuids.add(uuid);
          result.push({
            type: "multicompartment",
            uuid,
            entityIds: mcGroups.get(uuid),
          });
        }
      } else {
        result.push({
          type: "single",
          entityId,
        });
      }
    });

    return result;
  }

  openMulticompartmentDialog(mcUuid, options = {}) {
    const { reopen = true } = options;
    if (!this._hass || !mcUuid) return;
    this._openDialogMcUuid = mcUuid;
    this._openDialogEntityId = null;
    this._fromMcUuid = null;

    const items = this._getMcItems(mcUuid);
    if (!items.length) {
      this._closeDialog();
      return;
    }
    if (items.length === 1) {
      this.openDialog(items[0].entity_id, { reopen, fromMcUuid: null });
      return;
    }

    const {
      primaryAttrs,
      openCode: primaryOpenCode,
      qrCode: qrPayload,
      location: rawLocation,
      pickUpPoint,
      progressAttrs,
    } = this._resolveMcGroupData(items);

    const count = items.length;
    const countText = this._formatShipmentsCount(count);
    const titleEl = this.querySelector('#modal-title');
    const dialogTitle = `${this._localize("dialog.multicompartment_title")} (${countText})`;
    if (titleEl.innerText !== dialogTitle) titleEl.innerText = dialogTitle;

    const refreshButtonIds = Array.from(new Set(
      items
        .map((item) => this._getRefreshShipmentButtonId(item.attributes))
        .filter(Boolean)
    ));
    let headerActionsHtml = '';
    if (refreshButtonIds.length) {
      headerActionsHtml += `<button class="header-icon-btn" data-mc-refresh="${this._escapeHtml(mcUuid)}" title="${this._localize("dialog.refresh_shipment")}"><ha-icon icon="mdi:refresh"></ha-icon></button>`;
    }

    const headerDynamicContainer = this.querySelector('#header-dynamic-actions');
    const headerChanged = this._lastModalHeaderHtml !== headerActionsHtml;
    if (headerDynamicContainer && headerChanged) {
      headerDynamicContainer.innerHTML = headerActionsHtml;
    }
    this._lastModalHeaderHtml = headerActionsHtml;

    if (headerChanged) {
      const refreshBtn = this.querySelector('[data-mc-refresh]');
      if (refreshBtn) {
        refreshBtn.addEventListener('click', async () => {
          const currentItems = this._getMcItems(mcUuid);
          const ids = Array.from(new Set(
            currentItems.map((item) => this._getRefreshShipmentButtonId(item.attributes)).filter(Boolean)
          ));
          if (!ids.length) return;
          refreshBtn.classList.add('loading');
          try {
            await Promise.all(ids.map((id) => this._pressButtonEntity(id)));
          } finally {
            setTimeout(() => refreshBtn.classList.remove('loading'), 400);
          }
        });
      }
    }

    let infoHtml = `<div class="modal-info-block">`;

    if (this._isEnabled("show_dialog_pickup_code") && primaryOpenCode) {
      infoHtml += `
        <div class="modal-info-block-row" style="align-items: center;">
          <strong>${this._localize("dialog.pickup_code")}:</strong>
          <span class="val" style="font-size: 1.4rem; font-weight: bold; letter-spacing: 2px; color: var(--primary-color);">${this._escapeHtml(primaryOpenCode)}</span>
        </div>
      `;
    }

    let locationName = rawLocation;
    if (locationName && pickUpPoint?.locationDescription) {
      locationName += ` (${pickUpPoint.locationDescription})`;
    }
    if (this._isEnabled("show_dialog_pickup_point") && locationName) {
      let locationContent = `<span class="val">${this._escapeHtml(locationName)}`;
      if (this._isEnabled("show_dialog_navigation") && pickUpPoint?.location?.latitude && pickUpPoint?.location?.longitude) {
        const lat = encodeURIComponent(pickUpPoint.location.latitude);
        const lon = encodeURIComponent(pickUpPoint.location.longitude);
        locationContent += `<br><a href="https://maps.google.com/?q=${lat},${lon}" target="_blank" rel="noopener noreferrer" class="modal-nav-link"><ha-icon icon="mdi:map-marker-path"></ha-icon> ${this._localize("dialog.navigate")}</a>`;
      }
      locationContent += `</span>`;
      infoHtml += `<div class="modal-info-block-row" style="margin-top: 8px;"><strong>${this._localize("dialog.pickup_point")}:</strong> ${locationContent}</div>`;
      const progressBarModal = this._renderInPostProgressBar(progressAttrs);
      if (progressBarModal) {
        infoHtml += `<div class="modal-info-block-row modal-progress-row">${progressBarModal}</div>`;
      }
    }

    if (this._isEnabled("show_dialog_qr_code") && qrPayload && primaryAttrs.status_key === 'waiting_for_pickup') {
      const qrUrlSmall = `https://quickchart.io/qr?text=${encodeURIComponent(qrPayload)}&size=150&margin=0&ecLevel=H`;
      const qrUrlLarge = `https://quickchart.io/qr?text=${encodeURIComponent(qrPayload)}&size=500&margin=0&ecLevel=H`;
      infoHtml += `
        <div class="qr-code-container" data-large-qr="${qrUrlLarge}">
          <img src="${qrUrlSmall}" alt="QR Code" />
          <div class="qr-code-label">${this._localize("dialog.scan_qr")}</div>
        </div>
      `;
    }

    infoHtml += `</div>`;

    infoHtml += `<div class="modal-section-title">${this._localize("dialog.multicompartment_shipments")} (${count})</div>`;
    infoHtml += `<div class="modal-mc-list">`;

    const sizeLabel = this._localize("labels.size_short");
    const detailsLabel = this._localize("dialog.shipment_details");
    const hideLabel = this._localize("dialog.hide_shipment");

    items.forEach((item, idx) => {
      const attrs = item.attributes || {};
      const raw = this._parseRawResponse(attrs.raw_response);
      const sender = attrs.sender || attrs.sender_name || attrs.recipient_name || attrs.tracking_number;
      const code = attrs.open_code || attrs.pickup_code || raw.openCode || '';
      const size = this._getParcelSize(attrs, raw);
      const sizeText = size ? `${sizeLabel} ${size}` : '';
      const itemStatus = this.getStatusInfo(item);
      const allegroHtml = this._renderAllegroInfo(attrs);
      const hideBtnId = this._getHideShipmentButtonId(attrs);

      infoHtml += `
        <div class="modal-mc-item">
          <div class="modal-mc-item-header">
            <div class="modal-mc-item-num">${idx + 1}.</div>
            <div class="modal-mc-item-main">
              <div class="modal-mc-item-sender">${this._escapeHtml(sender)}</div>
              <div class="modal-mc-item-tracking">${this._escapeHtml(attrs.tracking_number || '')}</div>
            </div>
            <div class="modal-mc-item-badges">
              <span class="subitem-status ${itemStatus.class}">${this._escapeHtml(itemStatus.text)}</span>
              ${sizeText ? `<span class="modal-mc-size-badge">${this._escapeHtml(sizeText)}</span>` : ''}
              ${code ? `<span class="modal-mc-code-badge">${this._escapeHtml(code)}</span>` : ''}
            </div>
          </div>
          ${allegroHtml ? `<div class="modal-mc-allegro">${allegroHtml}</div>` : ''}
          <div class="modal-mc-item-footer">
            ${hideBtnId ? `
            <button type="button" class="modal-mc-view-btn" data-hide-sub-btn="${this._escapeHtml(hideBtnId)}" title="${hideLabel}">
              <ha-icon icon="mdi:eye-off-outline"></ha-icon>
              <span>${hideLabel}</span>
            </button>
            ` : ''}
            <button type="button" class="modal-mc-view-btn" data-open-sub-entity="${this._escapeHtml(item.entity_id)}">
              <ha-icon icon="mdi:open-in-new"></ha-icon>
              <span>${detailsLabel}</span>
            </button>
          </div>
        </div>
      `;
    });

    infoHtml += `</div>`;

    const modalContent = this.querySelector('#modal-content');
    if (this._lastModalContentHtml !== infoHtml) {
      this._lastModalContentHtml = infoHtml;
      modalContent.innerHTML = infoHtml;

      const qrContainer = modalContent.querySelector('.qr-code-container');
      if (qrContainer) {
        qrContainer.addEventListener('click', () => {
          const largeUrl = qrContainer.getAttribute('data-large-qr');
          const fullscreenOverlay = this.querySelector('#qr-fullscreen');
          this.querySelector('#qr-fullscreen-img').src = largeUrl;
          fullscreenOverlay.classList.add('open');
        });
      }

      modalContent.querySelectorAll('[data-open-sub-entity]').forEach((btn) => {
        btn.addEventListener('click', (e) => {
          e.stopPropagation();
          const eid = btn.getAttribute('data-open-sub-entity');
          if (eid) {
            this.openDialog(eid, { fromMcUuid: mcUuid });
          }
        });
      });

      modalContent.querySelectorAll('[data-hide-sub-btn]').forEach((btn) => {
        btn.addEventListener('click', async (e) => {
          e.stopPropagation();
          const hideId = btn.getAttribute('data-hide-sub-btn');
          if (!hideId) return;
          if (!window.confirm(this._localize("dialog.hide_shipment_confirm"))) return;
          await this._pressButtonEntity(hideId);
        });
      });
    }

    if (reopen) {
      this.querySelector('#modal-overlay').classList.add('open');
    }
  }

  updateContent() {
    if (!this.content || !this._hass) return;

    const entitiesToShow = this._getFilteredShipmentEntities();

    entitiesToShow.sort((a, b) => {
      const keyA = this._getSortKeyForAttrs(this._hass.states[a]?.attributes);
      const keyB = this._getSortKeyForAttrs(this._hass.states[b]?.attributes);
      if (keyA.score !== keyB.score) return keyA.score - keyB.score;
      if (keyA.expiryMs !== keyB.expiryMs) return keyA.expiryMs - keyB.expiryMs;
      return 0;
    });

    const signatureParts = [];
    entitiesToShow.forEach((entityId) => {
      const stateObj = this._hass.states[entityId];
      if (!stateObj) return;
      const attrs = stateObj.attributes || {};
      signatureParts.push([
        entityId,
        stateObj.state || '',
        attrs.status_key || '',
        attrs.status_raw || '',
        attrs.sender || '',
        attrs.sender_name || '',
        attrs.recipient_name || '',
        attrs.tracking_number || '',
        attrs.courier || '',
        attrs.location || '',
        attrs.current_location || '',
        attrs.open_code || '',
        attrs.pickup_code || '',
        attrs.expiry_date || '',
        attrs.stored_date || '',
        attrs.parcel_size || '',
        this._allegroItems(attrs).join(','),
        this._getMcUuid(attrs, entityId) || '',
      ].join('|'));
    });

    this._expandedMulticompartments = this._expandedMulticompartments || new Set();
    const configSignature = [
      this._isEnabled("show_list_sender"),
      this._isEnabled("show_list_pickup_code"),
      this._isEnabled("show_list_location"),
      this._isEnabled("show_list_allegro_items"),
      this._isEnabled("group_multicompartment"),
      Array.from(this._expandedMulticompartments).sort().join(','),
    ].join('|');
    const signature = `${configSignature}||${signatureParts.join('||')}`;
    if (this._lastSignature === signature) {
      this._refreshOpenDialog();
      return;
    }
    this._lastSignature = signature;

    let html = '';
    const pickupCodeLabel = this._localize("labels.pickup_code");
    const pickupPointLabel = this._localize("labels.pickup_point");
    const defaultCourier = this._localize("labels.courier_default");
    const sizeLabel = this._localize("labels.size_short");

    const groupedItems = this._groupEntities(entitiesToShow);
    groupedItems.sort((a, b) => {
      const keyA = this._getSortKeyForGroup(a);
      const keyB = this._getSortKeyForGroup(b);
      if (keyA.score !== keyB.score) return keyA.score - keyB.score;
      if (keyA.expiryMs !== keyB.expiryMs) return keyA.expiryMs - keyB.expiryMs;
      return 0;
    });

    groupedItems.forEach((item) => {
      if (item.type === 'single') {
        const entityId = item.entityId;
        const stateObj = this._hass.states[entityId];
        if (!stateObj || stateObj.state === 'unavailable') return;

        const attributes = stateObj.attributes;
        const friendlyName = this._isEnabled("show_list_sender")
          ? (attributes.sender || attributes.sender_name || attributes.recipient_name || attributes.tracking_number)
          : attributes.tracking_number;
        const courier = attributes.courier || attributes.attribution || (entityId.includes('inpost') ? 'InPost' : defaultCourier);
        
        const isTrackingName = friendlyName === attributes.tracking_number;
        let nameClass = "name";
        let displayFriendlyName = this._escapeHtml(friendlyName);

        if (isTrackingName) {
          nameClass += " truncate-left";
          displayFriendlyName = `<span dir="ltr">${this._escapeHtml(friendlyName)}</span>`;
        }

        let line2 = isTrackingName ? "" : attributes.tracking_number;
        if (String(attributes.courier || '').toLowerCase() === 'allegro') {
          // Show the waybill instead of the long order UUID.
          line2 = attributes.waybill || "";
          if (line2 && attributes.parcel_count) line2 += ` (${attributes.parcel_index}/${attributes.parcel_count})`;
        }
        const displayLine2 = line2 ? `<span dir="ltr">${this._escapeHtml(line2)}</span>` : "";

        // Allegro orders are delivered by another carrier; show that carrier's logo.
        // A logo configured for the account's own courier still wins.
        const ownLogo = this.config.courier_logos?.[courier.toLowerCase()];
        const logoSource = (!ownLogo && attributes.delivered_by) || courier;
        const imageUrl = this.getCourierImage(logoSource);
        const iconMdi = attributes.icon || this.getCourierIcon(logoSource);

        let iconHtml;
        if (imageUrl) {
          iconHtml = `<img src="${this._escapeHtml(imageUrl)}" alt="${this._escapeHtml(courier)}" class="courier-logo" onerror="this.style.display='none'; this.nextElementSibling.style.display='block';">
                      <ha-icon icon="${iconMdi}" style="display:none;"></ha-icon>`;
        } else {
          iconHtml = `<ha-icon icon="${iconMdi}"></ha-icon>`;
        }

        const statusInfo = this.getStatusInfo(stateObj);
        const location = attributes.location || attributes.current_location || '';
        const pickupCode = attributes.open_code || attributes.pickup_code || '';

        let extraInfoHtml = '';
        if (this._isEnabled("show_list_pickup_code") && pickupCode) {
          extraInfoHtml += `<div class="pickup-code">${pickupCodeLabel}: ${this._escapeHtml(pickupCode)}</div>`;
        }
        if (this._isEnabled("show_list_location") && location) {
          extraInfoHtml += `<div class="extra-info-text">${pickupPointLabel}: ${this._escapeHtml(location)}</div>`;
        }
        const progressBarHtml = this._renderInPostProgressBar(attributes);
        if (progressBarHtml) {
          extraInfoHtml += progressBarHtml;
        }
        const allegroItems = this._allegroItems(attributes);
        if (allegroItems.length && this._isEnabled("show_list_allegro_items")) {
          const more = allegroItems.length > 1 ? ` (+${allegroItems.length - 1})` : '';
          extraInfoHtml += `<div class="extra-info-text">Allegro: ${this._escapeHtml(allegroItems[0])}${more}</div>`;
        }

        html += `
          <div class="shipment-item" data-entity-id="${this._escapeHtml(entityId)}">
            <div class="icon-wrapper">
              <div class="icon-container">
                ${iconHtml}
              </div>
            </div>

            <div class="content-right">
                <div class="row-top">
                    <div class="info-main">
                        <div class="${nameClass}">${displayFriendlyName}</div>
                        <div class="courier truncate-left">${displayLine2}</div>
                    </div>
                    <div class="status-badge ${statusInfo.class}">
                        ${this._escapeHtml(statusInfo.text)}
                    </div>
                </div>

                <div class="row-bottom">
                    <div class="extra-info">
                        ${extraInfoHtml}
                    </div>
                </div>
            </div>
          </div>
        `;
      } else if (item.type === 'multicompartment') {
        const items = item.entityIds.map((id) => this._hass.states[id]).filter(Boolean);
        if (!items.length) return;
        const count = items.length;
        const {
          primaryItem,
          primaryAttrs,
          openCode: primaryOpenCode,
          location,
          progressAttrs,
        } = this._resolveMcGroupData(items);

        const courier = primaryAttrs.courier || primaryAttrs.attribution || 'InPost';
        const imageUrl = this.getCourierImage(courier);
        const iconMdi = 'mdi:locker-multiple';

        let iconHtml;
        if (imageUrl) {
          iconHtml = `<img src="${this._escapeHtml(imageUrl)}" alt="${this._escapeHtml(courier)}" class="courier-logo" onerror="this.style.display='none'; this.nextElementSibling.style.display='block';">
                      <ha-icon icon="${iconMdi}" style="display:none;"></ha-icon>`;
        } else {
          iconHtml = `<ha-icon icon="${iconMdi}"></ha-icon>`;
        }

        const statusInfo = this.getStatusInfo(primaryItem);
        const senders = [];
        items.forEach((it) => {
          const s = this._isEnabled("show_list_sender")
            ? (it.attributes?.sender || it.attributes?.sender_name || it.attributes?.recipient_name || it.attributes?.tracking_number)
            : it.attributes?.tracking_number;
          if (s && !senders.includes(s)) senders.push(s);
        });
        const sendersSummary = senders.slice(0, 3).join(', ') + (senders.length > 3 ? ` +${senders.length - 3}` : '');

        const isExpanded = this._expandedMulticompartments.has(item.uuid);
        const mcTitle = `${this._localize("labels.multicompartment")} (${count})`;
        const countTooltip = this._formatShipmentsCount(count);
        const toggleTitle = isExpanded ? this._localize("labels.collapse") : this._localize("labels.expand");

        let extraInfoHtml = '';
        if (this._isEnabled("show_list_pickup_code") && primaryOpenCode) {
          extraInfoHtml += `<div class="pickup-code">${pickupCodeLabel}: ${this._escapeHtml(primaryOpenCode)}</div>`;
        }
        if (this._isEnabled("show_list_location") && location) {
          extraInfoHtml += `<div class="extra-info-text">${pickupPointLabel}: ${this._escapeHtml(location)}</div>`;
        }
        const progressBarHtml = this._renderInPostProgressBar(progressAttrs);
        if (progressBarHtml) {
          extraInfoHtml += progressBarHtml;
        }
        if (this._isEnabled("show_list_allegro_items")) {
          const allAllegro = items.flatMap((it) => this._allegroItems(it.attributes || {}));
          if (allAllegro.length) {
            const more = allAllegro.length > 1 ? ` (+${allAllegro.length - 1})` : '';
            extraInfoHtml += `<div class="extra-info-text">Allegro: ${this._escapeHtml(allAllegro[0])}${more}</div>`;
          }
        }

        let subItemsHtml = '';
        if (isExpanded) {
          subItemsHtml = `
            <div class="multicompartment-subitems">
              ${items.map((subItem) => {
                const subAttrs = subItem.attributes || {};
                const subRaw = this._parseRawResponse(subAttrs.raw_response);
                const subId = subItem.entity_id;
                const subSender = this._isEnabled("show_list_sender")
                  ? (subAttrs.sender || subAttrs.sender_name || subAttrs.recipient_name || subAttrs.tracking_number)
                  : subAttrs.tracking_number;
                const subSize = this._getParcelSize(subAttrs, subRaw);
                const subStatus = this.getStatusInfo(subItem);

                let subMetaHtml = `<span class="subitem-status ${subStatus.class}">${this._escapeHtml(subStatus.text)}</span>`;
                if (subSize) {
                  subMetaHtml += `<span class="subitem-size">${this._escapeHtml(sizeLabel)} ${this._escapeHtml(subSize)}</span>`;
                }

                const allegroItems = this._allegroItems(subAttrs);
                let subAllegroHtml = '';
                if (allegroItems.length && this._isEnabled("show_list_allegro_items")) {
                  const more = allegroItems.length > 1 ? ` (+${allegroItems.length - 1})` : '';
                  subAllegroHtml = `<div class="subitem-allegro">Allegro: ${this._escapeHtml(allegroItems[0])}${more}</div>`;
                }

                return `
                  <div class="multicompartment-subitem" data-entity-id="${this._escapeHtml(subId)}">
                    <div class="subitem-icon">
                      <ha-icon icon="mdi:package-variant-closed"></ha-icon>
                    </div>
                    <div class="subitem-content">
                      <div class="subitem-row-top">
                        <div class="subitem-name">${this._escapeHtml(subSender)}</div>
                        <div class="subitem-meta">
                          ${subMetaHtml}
                        </div>
                      </div>
                      <div class="subitem-row-bottom">
                        <div class="subitem-tracking">${this._escapeHtml(subAttrs.tracking_number || '')}</div>
                        ${subAllegroHtml}
                      </div>
                    </div>
                  </div>
                `;
              }).join('')}
            </div>
          `;
        }

        html += `
          <div class="multicompartment-wrapper">
            <div class="shipment-item multicompartment-header ${isExpanded ? 'expanded' : ''}" data-mc-uuid="${this._escapeHtml(item.uuid)}">
              <div class="icon-wrapper">
                <div class="icon-container">
                  ${iconHtml}
                </div>
                <div class="multicompartment-badge" title="${this._escapeHtml(countTooltip)}">${count}</div>
              </div>

              <div class="content-right">
                  <div class="row-top">
                      <div class="info-main">
                          <div class="name">${this._escapeHtml(mcTitle)}</div>
                          <div class="courier">${this._escapeHtml(sendersSummary)}</div>
                      </div>
                      <div class="multicompartment-header-actions">
                          <div class="status-badge ${statusInfo.class}">
                              ${this._escapeHtml(statusInfo.text)}
                          </div>
                          <button type="button" class="multicompartment-expand-btn ${isExpanded ? 'open' : ''}" data-toggle-mc="${this._escapeHtml(item.uuid)}" title="${this._escapeHtml(toggleTitle)}" aria-expanded="${isExpanded}">
                              <ha-icon icon="${isExpanded ? 'mdi:chevron-up' : 'mdi:chevron-down'}"></ha-icon>
                          </button>
                      </div>
                  </div>

                  <div class="row-bottom">
                      <div class="extra-info">
                          ${extraInfoHtml}
                      </div>
                  </div>
              </div>
            </div>
            ${subItemsHtml}
          </div>
        `;
      }
    });

    if (html === '') {
      html = `<div class="empty-state">${this._localize("empty_state")}</div>`;
    }

    this.content.innerHTML = html;

    this.content.querySelectorAll('[data-toggle-mc]').forEach((btn) => {
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        const uuid = btn.getAttribute('data-toggle-mc');
        if (!uuid) return;
        this._expandedMulticompartments = this._expandedMulticompartments || new Set();
        if (this._expandedMulticompartments.has(uuid)) {
          this._expandedMulticompartments.delete(uuid);
        } else {
          this._expandedMulticompartments.add(uuid);
        }
        this._lastSignature = null;
        this.updateContent();
      });
    });

    this.content.querySelectorAll('.multicompartment-header').forEach((header) => {
      header.addEventListener('click', () => {
        const uuid = header.getAttribute('data-mc-uuid');
        if (uuid) {
          this.openMulticompartmentDialog(uuid);
        }
      });
    });

    this.content.querySelectorAll('.multicompartment-subitem').forEach((subitem) => {
      subitem.addEventListener('click', (e) => {
        e.stopPropagation();
        const entityId = subitem.getAttribute('data-entity-id');
        const wrapper = subitem.closest('.multicompartment-wrapper');
        const mcUuid = wrapper?.querySelector('.multicompartment-header')?.getAttribute('data-mc-uuid');
        if (entityId) {
          this.openDialog(entityId, { fromMcUuid: mcUuid });
        }
      });
    });

    this.content.querySelectorAll('.shipment-item:not(.multicompartment-header)').forEach((item) => {
      item.addEventListener('click', () => {
        this.openDialog(item.getAttribute('data-entity-id'));
      });
    });

    this._refreshOpenDialog();
  }
}

class ShipmentTrackingCardEditor extends HTMLElement {
  set hass(hass) {
    this._hass = hass;
    this._loadEntries();
    this._render();
  }

  async _loadEntries() {
    // Account list for the "show only these accounts" filter.
    if (this._entriesRequested || !this._hass?.callWS) return;
    this._entriesRequested = true;
    try {
      const entries = await this._hass.callWS({ type: "config_entries/get", domain: "polish_shipment_tracking" });
      this._entries = (entries || []).sort((a, b) => String(a.title).localeCompare(String(b.title)));
      this._render();
    } catch (e) {
      console.warn("Shipment Tracking Card: cannot list accounts", e);
    }
  }

  setConfig(config) {
    this._config = { ...(config || {}) };
    this._render();
  }

  _localize(key) {
    return localize(this._hass, key);
  }

  _render() {
    if (!this._hass || !this._config) return;

    if (!this._form) {
      this.innerHTML = "";
      this._form = document.createElement("ha-form");
      this._form.addEventListener("value-changed", (event) => this._handleChange(event));
      this._form.computeLabel = (schema) => schema.label || schema.name;
      this.appendChild(this._form);
    }

    const schema = [
      {
        name: "title",
        label: this._localize("editor.title"),
        selector: { text: {} }
      },
      {
        name: "show_list_sender",
        label: this._localize("editor.show_list_sender"),
        selector: { boolean: {} }
      },
      {
        name: "show_list_pickup_code",
        label: this._localize("editor.show_list_pickup_code"),
        selector: { boolean: {} }
      },
      {
        name: "show_list_location",
        label: this._localize("editor.show_list_location"),
        selector: { boolean: {} }
      },
      {
        name: "group_multicompartment",
        label: this._localize("editor.group_multicompartment"),
        selector: { boolean: {} }
      },
      {
        name: "show_dialog_tracking_number",
        label: this._localize("editor.show_dialog_tracking_number"),
        selector: { boolean: {} }
      },
      {
        name: "show_dialog_courier",
        label: this._localize("editor.show_dialog_courier"),
        selector: { boolean: {} }
      },
      {
        name: "show_dialog_sender",
        label: this._localize("editor.show_dialog_sender"),
        selector: { boolean: {} }
      },
      {
        name: "show_dialog_account_contact",
        label: this._localize("editor.show_dialog_account_contact"),
        selector: { boolean: {} }
      },
      {
        name: "show_dialog_recipient",
        label: this._localize("editor.show_dialog_recipient"),
        selector: { boolean: {} }
      },
      {
        name: "show_dialog_pickup_code",
        label: this._localize("editor.show_dialog_pickup_code"),
        selector: { boolean: {} }
      },
      {
        name: "show_dialog_pickup_point",
        label: this._localize("editor.show_dialog_pickup_point"),
        selector: { boolean: {} }
      },
      {
        name: "show_dialog_navigation",
        label: this._localize("editor.show_dialog_navigation"),
        selector: { boolean: {} }
      },
      {
        name: "show_dialog_delivery_address",
        label: this._localize("editor.show_dialog_delivery_address"),
        selector: { boolean: {} }
      },
      {
        name: "show_dialog_package_type",
        label: this._localize("editor.show_dialog_package_type"),
        selector: { boolean: {} }
      },
      {
        name: "show_dialog_courier_contact",
        label: this._localize("editor.show_dialog_courier_contact"),
        selector: { boolean: {} }
      },
      {
        name: "show_dialog_delivery_method",
        label: this._localize("editor.show_dialog_delivery_method"),
        selector: { boolean: {} }
      },
      {
        name: "show_dialog_parcel_shop_type",
        label: this._localize("editor.show_dialog_parcel_shop_type"),
        selector: { boolean: {} }
      },
      {
        name: "show_dialog_live_tracking",
        label: this._localize("editor.show_dialog_live_tracking"),
        selector: { boolean: {} }
      },
      {
        name: "show_dialog_cod",
        label: this._localize("editor.show_dialog_cod"),
        selector: { boolean: {} }
      },
      {
        name: "show_dialog_delivery_date",
        label: this._localize("editor.show_dialog_delivery_date"),
        selector: { boolean: {} }
      },
      {
        name: "show_dialog_parcel_size",
        label: this._localize("editor.show_dialog_parcel_size"),
        selector: { boolean: {} }
      },
      {
        name: "show_dialog_qr_code",
        label: this._localize("editor.show_dialog_qr_code"),
        selector: { boolean: {} }
      },
      {
        name: "show_dialog_timeline",
        label: this._localize("editor.show_dialog_timeline"),
        selector: { boolean: {} }
      },
      {
        name: "show_dialog_manage_button",
        label: this._localize("editor.show_dialog_manage_button"),
        selector: { boolean: {} }
      },
      {
        name: "show_dialog_entity_button",
        label: this._localize("editor.show_dialog_entity_button"),
        selector: { boolean: {} }
      },
      {
        name: "show_list_allegro_items",
        label: this._localize("editor.show_list_allegro_items"),
        selector: { boolean: {} }
      },
      {
        name: "show_dialog_allegro_items",
        label: this._localize("editor.show_dialog_allegro_items"),
        selector: { boolean: {} }
      },
      {
        name: "show_dialog_allegro_images",
        label: this._localize("editor.show_dialog_allegro_images"),
        selector: { boolean: {} }
      },
      {
        name: "show_dialog_allegro_prices",
        label: this._localize("editor.show_dialog_allegro_prices"),
        selector: { boolean: {} }
      },
      {
        name: "show_dialog_allegro_seller",
        label: this._localize("editor.show_dialog_allegro_seller"),
        selector: { boolean: {} }
      },
      {
        name: "show_dialog_allegro_total",
        label: this._localize("editor.show_dialog_allegro_total"),
        selector: { boolean: {} }
      },
      {
        name: "show_dialog_allegro_order_date",
        label: this._localize("editor.show_dialog_allegro_order_date"),
        selector: { boolean: {} }
      },
      {
        name: "show_dialog_allegro_shipment",
        label: this._localize("editor.show_dialog_allegro_shipment"),
        selector: { boolean: {} }
      },
      {
        type: "expandable",
        name: "",
        flatten: true,
        title: this._localize("editor.filters"),
        schema: [
          {
            name: "entries",
            label: this._localize("editor.entries"),
            selector: {
              select: {
                multiple: true,
                mode: "list",
                options: (this._entries || []).map((entry) => ({ value: entry.entry_id, label: entry.title })),
              }
            }
          },
          {
            name: "contacts",
            label: this._localize("editor.contacts"),
            selector: { text: { multiple: true } }
          }
        ]
      }
    ];

    const data = { ...this._config };
    const booleanDefaults = [
      "show_list_sender",
      "show_list_pickup_code",
      "show_list_location",
      "group_multicompartment",
      "show_dialog_tracking_number",
      "show_dialog_courier",
      "show_dialog_sender",
      "show_dialog_account_contact",
      "show_dialog_recipient",
      "show_dialog_pickup_code",
      "show_dialog_pickup_point",
      "show_dialog_navigation",
      "show_dialog_delivery_address",
      "show_dialog_package_type",
      "show_dialog_courier_contact",
      "show_dialog_delivery_method",
      "show_dialog_parcel_shop_type",
      "show_dialog_live_tracking",
      "show_dialog_cod",
      "show_dialog_delivery_date",
      "show_dialog_parcel_size",
      "show_dialog_qr_code",
      "show_dialog_timeline",
      "show_dialog_manage_button",
      "show_dialog_entity_button",
      "show_list_allegro_items",
      "show_dialog_allegro_items",
      "show_dialog_allegro_images",
      "show_dialog_allegro_prices",
      "show_dialog_allegro_seller",
      "show_dialog_allegro_total",
      "show_dialog_allegro_order_date",
      "show_dialog_allegro_shipment"
    ];
    booleanDefaults.forEach((key) => {
      if (data[key] === undefined) data[key] = true;
    });

    this._form.hass = this._hass;
    this._form.schema = schema;
    this._form.data = data;
  }

  _handleChange(event) {
    const newConfig = { ...event.detail.value };
    // Keep the YAML clean when a filter is emptied.
    ["entries", "contacts"].forEach((key) => {
      if (Array.isArray(newConfig[key]) && !newConfig[key].filter(Boolean).length) delete newConfig[key];
    });
    this._config = newConfig;
    this.dispatchEvent(new CustomEvent("config-changed", {
      detail: { config: newConfig },
      bubbles: true,
      composed: true
    }));
  }
}

if (!customElements.get('shipment-tracking-card')) {
  customElements.define('shipment-tracking-card', ShipmentTrackingCard);
}
if (!customElements.get('shipment-tracking-card-editor')) {
  customElements.define('shipment-tracking-card-editor', ShipmentTrackingCardEditor);
}

window.customCards = window.customCards || [];
if (!window.customCards.find((card) => card.type === 'shipment-tracking-card')) {
  window.customCards.push({
    type: 'shipment-tracking-card',
    name: localize(null, "meta.name"),
    description: localize(null, "meta.description")
  });
}
