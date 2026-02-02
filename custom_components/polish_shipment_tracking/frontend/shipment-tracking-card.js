const CARD_TRANSLATIONS = {
  en: {
    "card.title": "Shipments",
    "labels.pickup_code": "CODE",
    "labels.pickup_point": "Pickup point",
    "labels.courier_default": "Courier",
    "empty_state": "No active shipments",
    "meta.name": "Shipment Tracking Card",
    "meta.description": "Displays shipment tracking sensors with status badges.",
    "editor.title": "Title"
  },
  pl: {
    "card.title": "Przesyłki",
    "labels.pickup_code": "KOD",
    "labels.pickup_point": "Punkt odbioru",
    "labels.courier_default": "Kurier",
    "empty_state": "Brak aktywnych przesyłek",
    "meta.name": "Karta śledzenia przesyłek",
    "meta.description": "Wyświetla sensory śledzenia przesyłek z etykietami statusu.",
    "editor.title": "Tytuł"
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
            display: flex;
            align-items: center;
            gap: 5px;
          }
          .row-bottom {
            display: block;
            width: 100%;
          }
          .extra-info {
            font-size: 0.75rem;
            color: var(--secondary-text-color);
            margin-top: 6px;
            opacity: 0.9;
            white-space: normal;
            line-height: 1.3;
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
            margin-top: 6px;
            background-color: var(--primary-color);
            color: var(--text-primary-color, white);
            padding: 3px 8px;
            border-radius: 6px;
            font-weight: bold;
            font-size: 0.85rem;
            letter-spacing: 1px;
            margin-right: 8px;
            vertical-align: middle;
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
        </style>
        <ha-card>
          <div class="header">
            <span id="card-title"></span>
            <ha-icon icon="mdi:truck-delivery-outline"></ha-icon>
          </div>
          <div class="shipment-list" id="shipment-list">
            </div>
        </ha-card>
      `;
      this.content = this.querySelector("#shipment-list");
      this.titleElement = this.querySelector("#card-title");
    }
    this._updateTitle();
    this.updateContent();
  }

  setConfig(config) {
    this.config = { ...(config || {}) };
    this._updateTitle();
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
  }

  getStatusInfo(state, attributes = {}) {
    const statusKey = (attributes.status_key || '').toString().toLowerCase();
    const raw = (attributes.status_raw || '').toString();

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
    const label = state || raw || statusKey || '';

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

    const signature = signatureParts.join('||');
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
        if (state === 'unavailable' || state === 'unknown') return;

        const attributes = stateObj.attributes;
        const friendlyName = attributes.sender || attributes.sender_name || attributes.recipient_name || attributes.tracking_number;
        const courier = attributes.courier || attributes.attribution || (entityId.includes('inpost') ? 'InPost' : defaultCourier);
        const line2 = friendlyName === attributes.tracking_number ? "" : attributes.tracking_number;

        const imageUrl = this.getCourierImage(courier);
        const iconMdi = attributes.icon || this.getCourierIcon(courier);

        let iconHtml;
        if (imageUrl) {
          iconHtml = `<img src="${imageUrl}" alt="${courier}" class="courier-logo" onerror="this.style.display='none'; this.nextElementSibling.style.display='block';">
                      <ha-icon icon="${iconMdi}" style="display:none;"></ha-icon>`;
        } else {
          iconHtml = `<ha-icon icon="${iconMdi}"></ha-icon>`;
        }

        const statusInfo = this.getStatusInfo(state, attributes);
        const location = attributes.location || attributes.current_location || '';
        const pickupCode = attributes.open_code || attributes.pickup_code || '';

        let codeHtml = '';
        if (pickupCode) {
            codeHtml = `<span class="pickup-code">${pickupCodeLabel}: ${pickupCode}</span>`;
        }

        let detailsHtml = '';
        if (location) {
             detailsHtml = `<span>${pickupPointLabel}: ${location}</span>`;
        }

        html += `
          <div class="shipment-item">
            <div class="icon-container">
              ${iconHtml}
            </div>

            <div class="content-right">
                <div class="row-top">
                    <div class="info-main">
                        <div class="name">${friendlyName}</div>
                        <div class="courier">${line2}</div>
                    </div>
                    <div class="status-badge ${statusInfo.class}">
                        ${statusInfo.text}
                    </div>
                </div>

                <div class="row-bottom">
                    <div class="extra-info">
                        ${codeHtml}${detailsHtml}
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
      this.appendChild(this._form);
    }

    const schema = [
      {
        name: "title",
        label: this._localize("editor.title"),
        selector: { text: {} }
      }
    ];

    this._form.hass = this._hass;
    this._form.schema = schema;
    this._form.data = { ...this._config };
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
