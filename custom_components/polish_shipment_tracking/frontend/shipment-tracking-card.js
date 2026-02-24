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
    "editor.show_dialog_recipient": "Show recipient in details",
    "editor.show_dialog_pickup_code": "Show pickup code in details",
    "editor.show_dialog_pickup_point": "Show pickup point in details",
    "editor.show_dialog_navigation": "Show navigation link in details",
    "editor.show_dialog_cod": "Show COD amount in details",
    "editor.show_dialog_parcel_size": "Show parcel size in details",
    "editor.show_dialog_qr_code": "Show QR code in details",
    "editor.show_dialog_timeline": "Show timeline in details",
    "editor.show_dialog_entity_button": "Show entity button in details",
    "dialog.sender": "Sender",
    "dialog.recipient": "Recipient",
    "dialog.pickup_code": "Pickup Code",
    "dialog.pickup_point": "Pickup Point",
    "dialog.navigate": "Navigate",
    "dialog.parcel_size": "Size",
    "dialog.max_dimensions": "Max dimensions",
    "dialog.cod": "COD Amount",
    "dialog.courier_name": "Courier Name",
    "dialog.timeline": "Timeline",
    "dialog.no_timeline": "No timeline history available",
    "dialog.scan_qr": "Scan at the parcel locker",
    "dialog.show_entity": "Show entity",
    "dialog.close": "Close",
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
    "editor.show_dialog_recipient": "Pokaż odbiorcę w szczegółach",
    "editor.show_dialog_pickup_code": "Pokaż kod odbioru w szczegółach",
    "editor.show_dialog_pickup_point": "Pokaż punkt odbioru w szczegółach",
    "editor.show_dialog_navigation": "Pokaż link nawigacji w szczegółach",
    "editor.show_dialog_cod": "Pokaż kwotę pobrania w szczegółach",
    "editor.show_dialog_parcel_size": "Pokaż gabaryt paczki w szczegółach",
    "editor.show_dialog_qr_code": "Pokaż kod QR w szczegółach",
    "editor.show_dialog_timeline": "Pokaż historię przesyłki w szczegółach",
    "editor.show_dialog_entity_button": "Pokaż przycisk encji w szczegółach",
    "dialog.sender": "Nadawca",
    "dialog.recipient": "Odbiorca",
    "dialog.pickup_code": "Kod odbioru",
    "dialog.pickup_point": "Punkt odbioru",
    "dialog.navigate": "Nawiguj",
    "dialog.parcel_size": "Gabaryt",
    "dialog.max_dimensions": "Maksymalne wymiary",
    "dialog.cod": "Kwota pobrania",
    "dialog.courier_name": "Kurier",
    "dialog.timeline": "Historia przesyłki",
    "dialog.no_timeline": "Brak historii przesyłki",
    "dialog.scan_qr": "Zeskanuj w paczkomacie",
    "dialog.show_entity": "Pokaż encję",
    "dialog.close": "Zamknij",
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
          .modal-header ha-icon { cursor: pointer; color: var(--secondary-text-color); }
          
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
          .modal-info-block-row strong { color: var(--secondary-text-color); font-weight: 500; min-width: 100px; flex-shrink: 0; }
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
          .parcel-size .box-a { width: 26px; height: 8px; }
          .parcel-size .box-b { width: 26px; height: 18px; }
          .parcel-size .box-c { width: 26px; height: 32px; }
          .parcel-size-info { font-size: 0.8rem; color: var(--secondary-text-color); margin-top: 6px; }

          .modal-nav-link {
            display: inline-flex; align-items: center; gap: 4px;
            color: var(--primary-color); text-decoration: none; font-weight: 500;
            margin-top: 4px; font-size: 0.9rem;
          }
          .modal-nav-link ha-icon { --mdc-icon-size: 16px; }
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
          .modal-actions { margin-top: 18px; display: flex; justify-content: flex-end; }
          .modal-action-btn {
            border: 1px solid var(--primary-color);
            background: transparent;
            color: var(--primary-color);
            border-radius: 8px;
            padding: 8px 12px;
            font-weight: 600;
            cursor: pointer;
          }
        </style>

        <ha-card>
          <div class="header">
            <span id="card-title"></span>
            <ha-icon icon="mdi:truck-delivery-outline"></ha-icon>
          </div>
          <div class="shipment-list" id="shipment-list"></div>
        </ha-card>

        <div class="modal-overlay" id="modal-overlay">
          <div class="modal-surface">
            <div class="modal-header">
              <span id="modal-title"></span>
              <ha-icon icon="mdi:close" id="modal-close"></ha-icon>
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

      this.querySelector('#modal-close').addEventListener('click', () => {
        this.querySelector('#modal-overlay').classList.remove('open');
      });
      this.querySelector('#modal-overlay').addEventListener('click', (e) => {
        if (e.target.id === 'modal-overlay') {
          this.querySelector('#modal-overlay').classList.remove('open');
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
    }
    this._updateTitle();
    this.updateContent();
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
    
    const closeBtn = this.querySelector('#qr-fullscreen-close');
    if (closeBtn) closeBtn.innerText = this._localize("dialog.close");
  }

  _isEnabled(optionName) {
    return this.config?.[optionName] !== false;
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
    if (this._hass?.formatEntityState && stateObj) {
      label = this._hass.formatEntityState(stateObj);
    } else if (this._hass?.localize && statusKey) {
      const key = `component.polish_shipment_tracking.entity.sensor.shipment_status.state.${statusKey}`;
      const localized = this._hass.localize(key);
      if (localized && localized !== key) {
        label = localized;
      }
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

  openDialog(entityId) {
    const stateObj = this._hass.states[entityId];
    if (!stateObj) return;

    const attrs = stateObj.attributes;
    const rawStr = attrs.raw_response;
    const friendlyName = attrs.sender || attrs.sender_name || attrs.recipient_name || attrs.tracking_number;
    
    this.querySelector('#modal-title').innerText = friendlyName;

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
    if (this._isEnabled("show_dialog_recipient") && attrs.recipient_name) {
      infoHtml += `<div class="modal-info-block-row"><strong>${this._localize("dialog.recipient")}:</strong> <span class="val">${attrs.recipient_name}</span></div>`;
    }
    if (this._isEnabled("show_dialog_pickup_code") && (attrs.pickup_code || attrs.open_code)) {
      infoHtml += `<div class="modal-info-block-row"><strong>${this._localize("dialog.pickup_code")}:</strong> <span class="val">${attrs.pickup_code || attrs.open_code}</span></div>`;
    }
    
    let timelineHtml = '';
    
    if (rawStr) {
      try {
        const raw = JSON.parse(rawStr);
        const courier = (attrs.courier || (entityId.includes('inpost') ? 'inpost' : '')).toLowerCase();
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
          const size = raw.parcelSize.toUpperCase();
          const inpostDimensions = {
            'A': '8 x 38 x 64 cm',
            'B': '19 x 38 x 64 cm',
            'C': '41 x 38 x 64 cm'
          };
          const currentDim = inpostDimensions[size] || '';

          infoHtml += `
            <div style="margin-top: 16px; border-top: 1px solid var(--divider-color, rgba(0,0,0,0.05)); padding-top: 12px;">
              <strong style="display:block; margin-bottom: 4px; color: var(--secondary-text-color);">${this._localize("dialog.parcel_size")}:</strong>
              <div class="parcel-sizes">
                  <div class="parcel-size ${size === 'A' ? 'active' : ''}" title="Gabaryt A: Max 8 x 38 x 64 cm, do 25 kg"><span class="box-a"></span>A</div>
                  <div class="parcel-size ${size === 'B' ? 'active' : ''}" title="Gabaryt B: Max 19 x 38 x 64 cm, do 25 kg"><span class="box-b"></span>B</div>
                  <div class="parcel-size ${size === 'C' ? 'active' : ''}" title="Gabaryt C: Max 41 x 38 x 64 cm, do 25 kg"><span class="box-c"></span>C</div>
              </div>
              ${currentDim ? `<div class="parcel-size-info">${this._localize("dialog.max_dimensions")}: <strong>${currentDim}</strong> (do 25 kg)</div>` : ''}
            </div>`;
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
          raw.history.forEach(event => {
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

    let finalHtml = infoHtml;
    if (this._isEnabled("show_dialog_timeline")) {
      finalHtml += `<div class="modal-section-title">${this._localize("dialog.timeline")}</div>`;
      if (timelineHtml) {
        finalHtml += `<div class="timeline">${timelineHtml}</div>`;
      } else {
        finalHtml += `<div class="timeline-desc">${this._localize("dialog.no_timeline")}</div>`;
      }
    }
    if (this._isEnabled("show_dialog_entity_button")) {
      finalHtml += `
        <div class="modal-actions">
          <button type="button" class="modal-action-btn" data-entity-button="${entityId}">
            ${this._localize("dialog.show_entity")}
          </button>
        </div>
      `;
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
    const entityButton = modalContent.querySelector('[data-entity-button]');
    if (entityButton) {
      entityButton.addEventListener('click', () => {
        this.querySelector('#modal-overlay').classList.remove('open');
        this.dispatchEvent(new CustomEvent("hass-more-info", {
          detail: { entityId },
          bubbles: true,
          composed: true
        }));
      });
    }

    this.querySelector('#modal-overlay').classList.add('open');
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
      "show_dialog_recipient",
      "show_dialog_pickup_code",
      "show_dialog_pickup_point",
      "show_dialog_navigation",
      "show_dialog_cod",
      "show_dialog_parcel_size",
      "show_dialog_qr_code",
      "show_dialog_timeline",
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
