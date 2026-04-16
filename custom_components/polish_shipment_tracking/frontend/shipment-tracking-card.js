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
    "editor.show_list_pickup_code": "Show pickup code in list",
    "editor.show_list_location": "Show pickup point in list",
    "editor.show_dialog_sender": "Show sender in details",
    "editor.show_dialog_account_contact": "Show shipment account in details",
    "editor.show_dialog_recipient": "Show recipient in details",
    "editor.show_dialog_pickup_code": "Show pickup code in details",
    "editor.show_dialog_pickup_point": "Show pickup point in details",
    "editor.show_dialog_navigation": "Show navigation link in details",
    "editor.show_dialog_cod": "Show COD amount in details",
    "editor.show_dialog_delivery_date": "Show planned delivery date in details",
    "editor.show_dialog_parcel_size": "Show parcel size in details",
    "editor.show_dialog_qr_code": "Show QR code in details",
    "editor.show_dialog_timeline": "Show timeline in details",
    "editor.show_dialog_manage_button": "Show manage button in details",
    "editor.show_dialog_entity_button": "Show entity button in details",
    "dialog.sender": "Sender",
    "dialog.account_contact": "Shipment For",
    "dialog.recipient": "Recipient",
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
    "dialog.manage_shipment": "Manage shipment",
    "dialog.close": "Close",
    "card.refresh_all": "Refresh all shipments",
    "dpd.DELIVERED": "Delivered",
    "dpd.HANDED_OVER_FOR_DELIVERY": "Out for delivery",
    "dpd.RECEIVED_IN_DEPOT": "Received in depot",
    "dpd.IN_TRANSPORT": "In transit",
    "dpd.RECEIVED_FROM_SENDER": "Received from sender",
    "dpd.READY_TO_SEND": "Ready to send"
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
    "editor.show_list_pickup_code": "Pokaż kod odbioru na liście",
    "editor.show_list_location": "Pokaż lokalizację na liście",
    "editor.show_dialog_sender": "Pokaż nadawcę w szczegółach",
    "editor.show_dialog_account_contact": "Pokaż dane konta przesyłki w szczegółach",
    "editor.show_dialog_recipient": "Pokaż odbiorcę w szczegółach",
    "editor.show_dialog_pickup_code": "Pokaż kod odbioru w szczegółach",
    "editor.show_dialog_pickup_point": "Pokaż punkt odbioru w szczegółach",
    "editor.show_dialog_navigation": "Pokaż link nawigacji w szczegółach",
    "editor.show_dialog_cod": "Pokaż kwotę pobrania w szczegółach",
    "editor.show_dialog_delivery_date": "Pokaż planowaną datę doręczenia w szczegółach",
    "editor.show_dialog_parcel_size": "Pokaż gabaryt paczki w szczegółach",
    "editor.show_dialog_qr_code": "Pokaż kod QR w szczegółach",
    "editor.show_dialog_timeline": "Pokaż historię przesyłki w szczegółach",
    "editor.show_dialog_manage_button": "Pokaż przycisk zarządzania w szczegółach",
    "editor.show_dialog_entity_button": "Pokaż przycisk encji w szczegółach",
    "dialog.sender": "Nadawca",
    "dialog.account_contact": "Przesyłka na",
    "dialog.recipient": "Odbiorca",
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
    "dialog.manage_shipment": "Zarządzaj przesyłką",
    "dialog.close": "Zamknij",
    "card.refresh_all": "Odśwież wszystkie przesyłki",
    "dpd.DELIVERED": "Dostarczona",
    "dpd.HANDED_OVER_FOR_DELIVERY": "Wydana do doręczenia",
    "dpd.RECEIVED_IN_DEPOT": "Przyjęta w oddziale",
    "dpd.IN_TRANSPORT": "W drodze",
    "dpd.RECEIVED_FROM_SENDER": "Odebrana od nadawcy",
    "dpd.READY_TO_SEND": "Gotowa do wysłania"
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
          .icon-container {
            width: 48px;
            height: 48px;
            border-radius: 50%;
            background: white;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-right: 16px;
            font-size: 24px;
            color: var(--primary-color);
            flex-shrink: 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            overflow: hidden;
            position: relative;
            margin-top: 2px;
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
            box-shadow: 0 4px 12px rgba(0,0,0,0.1); transition: transform 0.2s;
          }
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
    this.querySelector('#modal-overlay')?.classList.remove('open');
  }

  _refreshOpenDialog() {
    if (!this._openDialogEntityId) return;

    const stateObj = this._hass?.states?.[this._openDialogEntityId];
    if (!stateObj) {
      this._closeDialog();
      return;
    }

    this.openDialog(this._openDialogEntityId, { reopen: false });
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
    if (n.includes('pocztex') || n.includes('poczta')) return 'mdi:post-outline';
    return 'mdi:package-variant-closed';
  }

  getCourierImage(name) {
    const n = name.toLowerCase();
    if (this.config.courier_logos && this.config.courier_logos[n]) {
      return this.config.courier_logos[n];
    }

    const LOGOS = {
      'inpost': 'https://upload.wikimedia.org/wikipedia/commons/c/c5/InPost_logo.svg',
      'dhl': 'https://upload.wikimedia.org/wikipedia/commons/a/ac/DHL_Logo.svg',
      'dpd': 'https://upload.wikimedia.org/wikipedia/commons/a/ab/DPD_logo_%282015%29.svg',
      'pocztex': 'https://www.poczta-polska.pl/wp-content/uploads/2023/04/logo-Pocztex-podstawowy.svg',
    };

    for (const [key, url] of Object.entries(LOGOS)) {
      if (n.includes(key)) return url;
    }
    return null;
  }

  openDialog(entityId, options = {}) {
    const { reopen = true } = options;
    const stateObj = this._hass.states[entityId];
    if (!stateObj) return;
    this._openDialogEntityId = entityId;

    const attrs = stateObj.attributes;
    const rawStr = attrs.raw_response;
    const friendlyName = attrs.sender || attrs.sender_name || attrs.recipient_name || attrs.tracking_number;
    
    this.querySelector('#modal-title').innerText = friendlyName;

    // Header Actions Check
    const refreshShipmentButtonId = this._getRefreshShipmentButtonId(attrs);
    let headerActionsHtml = '';
    
    if (this._isEnabled("show_dialog_entity_button")) {
      headerActionsHtml += `<button class="header-icon-btn" data-entity-button="${entityId}" title="${this._localize("dialog.show_entity")}"><ha-icon icon="mdi:information-outline"></ha-icon></button>`;
    }
    if (refreshShipmentButtonId) {
      headerActionsHtml += `<button class="header-icon-btn" data-refresh-button="${refreshShipmentButtonId}" title="${this._localize("dialog.refresh_shipment")}"><ha-icon icon="mdi:refresh"></ha-icon></button>`;
    }
    const headerDynamicContainer = this.querySelector('#header-dynamic-actions');
    if (headerDynamicContainer) {
      headerDynamicContainer.innerHTML = headerActionsHtml;
    }

    // Bind Header Listeners
    const entityBtn = this.querySelector('[data-entity-button]');
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

    const refreshBtn = this.querySelector('[data-refresh-button]');
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

    // Modal Content
    let infoHtml = `<div class="modal-info-block">`;
    
    if (attrs.tracking_number) {
        infoHtml += `<div class="modal-info-block-row"><strong>Numer:</strong> <span class="val" style="flex-grow: 1; user-select: all; -webkit-user-select: all;">${attrs.tracking_number}</span></div>`;
    }
    if (attrs.courier) {
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
    
    let timelineHtml = '';
    let manageShipmentAvailable = false;
    
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

        if (!attrs.courier && courier === 'dpd' && raw.delivery && raw.delivery.courier_name) {
          infoHtml += `<div class="modal-info-block-row"><strong>${this._localize("dialog.courier_name")}:</strong> <span class="val">${raw.delivery.courier_name}</span></div>`;
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

        let locationName = attrs.location || attrs.current_location;
        if (locationName && courier === 'inpost' && raw.pickUpPoint?.locationDescription) {
          locationName += ' (' + raw.pickUpPoint.locationDescription + ')';
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
          
          locationContent += `</span>`;
          infoHtml += `<div class="modal-info-block-row"><strong>${this._localize("dialog.pickup_point")}:</strong> ${locationContent}</div>`;
        }

        if (this._isEnabled("show_dialog_qr_code") && courier === 'inpost' && raw.qrCode && attrs.status_key === 'waiting_for_pickup') {
           const qrUrlSmall = `https://quickchart.io/qr?text=${encodeURIComponent(raw.qrCode)}&size=150&margin=0&ecLevel=H`;
           const qrUrlLarge = `https://quickchart.io/qr?text=${encodeURIComponent(raw.qrCode)}&size=500&margin=0&ecLevel=H`;
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
        }
      } catch (e) {
        console.error("Failed to parse raw_response", e);
      }
    } else {
      if (this._isEnabled("show_dialog_pickup_point") && (attrs.location || attrs.current_location)) {
        infoHtml += `<div class="modal-info-block-row"><strong>${this._localize("dialog.pickup_point")}:</strong> <span class="val">${attrs.location || attrs.current_location}</span></div>`;
      }
    }

    infoHtml += `</div>`;

    const manageShipmentButtonId = this._isEnabled("show_dialog_manage_button") && manageShipmentAvailable
      ? this._getManageShipmentButtonId(attrs)
      : null;
    const manageShipmentUrl = this._getCachedManageUrl(attrs);
    const manageShipmentPending = manageShipmentButtonId && !manageShipmentUrl && this._isManageUrlPending(attrs);
      
    let finalHtml = infoHtml;
    
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
    modalContent.innerHTML = finalHtml;

    const qrContainer = modalContent.querySelector('.qr-code-container');
    if (qrContainer) {
      qrContainer.addEventListener('click', () => {
        const largeUrl = qrContainer.getAttribute('data-large-qr');
        const fullscreenOverlay = this.querySelector('#qr-fullscreen');
        this.querySelector('#qr-fullscreen-img').src = largeUrl;
        fullscreenOverlay.classList.add('open');
      });
    }

    if (reopen) {
      this.querySelector('#modal-overlay').classList.add('open');
    }
  }

  updateContent() {
    if (!this.content || !this._hass) return;

    const entitiesToShow = Object.keys(this._hass.states).filter((entityId) => {
      if (!entityId.startsWith("sensor.")) return false;
      const stateObj = this._hass.states[entityId];
      return stateObj?.attributes?.integration_domain === "polish_shipment_tracking";
    });

    entitiesToShow.sort((a, b) => {
        const keyA = (this._hass.states[a]?.attributes?.status_key || '').toString().toLowerCase();
        const keyB = (this._hass.states[b]?.attributes?.status_key || '').toString().toLowerCase();
        const score = (s) => {
            if (s === 'waiting_for_pickup') return 0;
            if (s === 'handed_out_for_delivery' || s === 'in_transport') return 1;
            return 2;
        };
        return score(keyA) - score(keyB);
    });

    const signatureParts = [];
    entitiesToShow.forEach(entityId => {
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
        attrs.pickup_code || ''
      ].join('|'));
    });

    const configSignature = [
      this._isEnabled("show_list_pickup_code"),
      this._isEnabled("show_list_location")
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

    entitiesToShow.forEach(entityId => {
      const stateObj = this._hass.states[entityId];

      if (stateObj) {
        const state = stateObj.state;
        if (state === 'unavailable') return;

        const attributes = stateObj.attributes;
        const friendlyName = attributes.sender || attributes.sender_name || attributes.recipient_name || attributes.tracking_number;
        const courier = attributes.courier || attributes.attribution || (entityId.includes('inpost') ? 'InPost' : defaultCourier);
        
        const isTrackingName = friendlyName === attributes.tracking_number;
        let nameClass = "name";
        let displayFriendlyName = friendlyName;

        if (isTrackingName) {
            nameClass += " truncate-left";
            displayFriendlyName = `<span dir="ltr">${friendlyName}</span>`;
        }

        const line2 = isTrackingName ? "" : attributes.tracking_number;
        const displayLine2 = line2 ? `<span dir="ltr">${line2}</span>` : "";

        const imageUrl = this.getCourierImage(courier);
        const iconMdi = attributes.icon || this.getCourierIcon(courier);

        let iconHtml;
        if (imageUrl) {
          iconHtml = `<img src="${imageUrl}" alt="${courier}" class="courier-logo" onerror="this.style.display='none'; this.nextElementSibling.style.display='block';">
                      <ha-icon icon="${iconMdi}" style="display:none;"></ha-icon>`;
        } else {
          iconHtml = `<ha-icon icon="${iconMdi}"></ha-icon>`;
        }

        const statusInfo = this.getStatusInfo(stateObj);
        const location = attributes.location || attributes.current_location || '';
        const pickupCode = attributes.open_code || attributes.pickup_code || '';

        let extraInfoHtml = '';
        if (this._isEnabled("show_list_pickup_code") && pickupCode) {
            extraInfoHtml += `<div class="pickup-code">${pickupCodeLabel}: ${pickupCode}</div>`;
        }
        if (this._isEnabled("show_list_location") && location) {
             extraInfoHtml += `<div class="extra-info-text">${pickupPointLabel}: ${location}</div>`;
        }

        html += `
          <div class="shipment-item" data-entity-id="${entityId}">
            <div class="icon-container">
              ${iconHtml}
            </div>

            <div class="content-right">
                <div class="row-top">
                    <div class="info-main">
                        <div class="${nameClass}">${displayFriendlyName}</div>
                        <div class="courier truncate-left">${displayLine2}</div>
                    </div>
                    <div class="status-badge ${statusInfo.class}">
                        ${statusInfo.text}
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
      }
    });

    if (html === '') {
      html = `<div class="empty-state">${this._localize("empty_state")}</div>`;
    }

    this.content.innerHTML = html;

    this.content.querySelectorAll('.shipment-item').forEach(item => {
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
    this._render();
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
      }
    ];

    const data = { ...this._config };
    const booleanDefaults = [
      "show_list_pickup_code",
      "show_list_location",
      "show_dialog_sender",
      "show_dialog_account_contact",
      "show_dialog_recipient",
      "show_dialog_pickup_code",
      "show_dialog_pickup_point",
      "show_dialog_navigation",
      "show_dialog_cod",
      "show_dialog_delivery_date",
      "show_dialog_parcel_size",
      "show_dialog_qr_code",
      "show_dialog_timeline",
      "show_dialog_manage_button",
      "show_dialog_entity_button"
    ];
    booleanDefaults.forEach((key) => {
      if (data[key] === undefined) data[key] = true;
    });

    this._form.hass = this._hass;
    this._form.schema = schema;
    this._form.data = data;
  }

  _handleChange(event) {
    const newConfig = event.detail.value;
    this._config = newConfig;
    this.dispatchEvent(new CustomEvent("config-changed", {
      detail: { config: newConfig },
      bubbles: true,
      composed: true
    }));
  }
}

customElements.define('shipment-tracking-card', ShipmentTrackingCard);
customElements.define('shipment-tracking-card-editor', ShipmentTrackingCardEditor);

window.customCards = window.customCards || [];
if (!window.customCards.find((card) => card.type === 'shipment-tracking-card')) {
  window.customCards.push({
    type: 'shipment-tracking-card',
    name: localize(null, "meta.name"),
    description: localize(null, "meta.description")
  });
}
