import aiohttp
import voluptuous as vol
import uuid
import json
import logging
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import TextSelector, TextSelectorConfig

from .const import (
    DOMAIN,
    CONF_COURIER,
    CONF_PHONE,
    CONF_EMAIL,
    CONF_PASSWORD,
    CONF_TOKEN,
    CONF_REFRESH_TOKEN,
    CONF_TOKEN_EXPIRES_AT,
    CONF_REFRESH_EXPIRES_AT,
    CONF_DEVICE_UID,
    CONF_ID_TOKEN,
    CONF_SESSION_ID,
    CONF_SESSION_REGISTERED,
    CONF_COOKIE,
    CONF_LOGIN,
    CONF_CALLBACK_URL,
    CONF_INCLUDE_RECIPIENTS,
    CONF_EXCLUDE_RECIPIENTS,
    CONF_HIDDEN_SHIPMENTS,
)
from .api_helpers import normalize_phone
from .helpers import get_account_label

_LOGGER = logging.getLogger(__name__)

COURIERS = ["inpost", "dpd", "dhl", "pocztex", "gls", "allegro"]

# hassfest rejects URLs inside translation strings.
ALLEGRO_PLACEHOLDERS = {"allegro_url": "https://allegro.pl"}


async def _async_validate_allegro_cookie(hass, cookie: str) -> str:
    """Return the Allegro login for a QXLSESSID cookie, raising when invalid."""
    from .api_allegro import AllegroApi
    api = AllegroApi(async_get_clientsession(hass), cookie)
    return await api.get_login()


def _clean_cookie(value) -> str:
    """Accept both the bare value and a pasted "QXLSESSID=..." pair."""
    cookie = str(value or "").strip()
    if cookie.upper().startswith("QXLSESSID="):
        cookie = cookie.split("=", 1)[1]
    return cookie.split(";", 1)[0].strip()

class ShipmentTrackingConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    def __init__(self):
        self.courier = None
        self.phone = None
        self.api_instance = None
        self.temp_data = {}
        self.device_uid = uuid.uuid4().hex
        self.inpost_login = None

    async def async_step_user(self, user_input=None):
        errors = {}
        
        if user_input is not None:
            self.courier = user_input[CONF_COURIER]
            if self.courier == "pocztex":
                return await self.async_step_pocztex_credentials()
            if self.courier == "gls":
                return await self.async_step_gls_credentials()
            if self.courier == "allegro":
                return await self.async_step_allegro_cookie()
            if self.courier == "inpost":
                return await self.async_step_inpost_login()
            return await self.async_step_phone()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_COURIER, default="inpost"): vol.In(COURIERS),
            }),
            errors=errors,
        )

    async def async_step_phone(self, user_input=None):
        errors = {}

        if user_input is not None:
            raw_phone = str(user_input[CONF_PHONE])
            self.phone = normalize_phone(raw_phone)

            session = async_get_clientsession(self.hass)

            try:
                if self.courier == "dpd":
                    from .api_dpd import DpdApi
                    self.api_instance = DpdApi(session)
                    await self.api_instance.send_sms_code(self.phone)

                elif self.courier == "dhl":
                    from .api_dhl import DhlApi
                    self.api_instance = DhlApi(session)
                    await self.api_instance.generate_code(self.phone)

                return await self.async_step_sms()

            except Exception as e:
                _LOGGER.exception("Login failed for %s: %s", self.courier, e)
                errors["base"] = "auth_error"

        return self.async_show_form(
            step_id="phone",
            data_schema=vol.Schema({
                vol.Required(CONF_PHONE): str,
            }),
            errors=errors,
            description_placeholders={"courier": self.courier.upper() if self.courier else ""},
        )

    async def async_step_pocztex_credentials(self, user_input=None):
        errors = {}

        if user_input is not None:
            email = str(user_input[CONF_EMAIL]).strip()
            password = str(user_input[CONF_PASSWORD])

            session = async_get_clientsession(self.hass)
            try:
                from .api_pocztex import PocztexApi
                api = PocztexApi(session)
                data = await api.login(email, password)

                return self.async_create_entry(
                    title=f"{self.courier.upper()} ({email})",
                    data={
                        CONF_COURIER: self.courier,
                        CONF_EMAIL: email,
                        CONF_TOKEN: data.get("access_token"),
                        CONF_REFRESH_TOKEN: data.get("refresh_token"),
                        CONF_TOKEN_EXPIRES_AT: api._expires_at,
                        CONF_REFRESH_EXPIRES_AT: api._refresh_expires_at,
                    }
                )
            except Exception as e:
                _LOGGER.exception("Pocztex login failed: %s", e)
                errors["base"] = "auth_error"

        return self.async_show_form(
            step_id="pocztex_credentials",
            data_schema=vol.Schema({
                vol.Required(CONF_EMAIL): str,
                vol.Required(CONF_PASSWORD): str,
            }),
            errors=errors,
        )

    async def async_step_gls_credentials(self, user_input=None):
        errors = {}

        if user_input is not None:
            raw_phone = str(user_input[CONF_PHONE])
            phone = normalize_phone(raw_phone)
            password = str(user_input[CONF_PASSWORD])

            try:
                from .api_gls import GlsApi
                async with aiohttp.ClientSession(cookie_jar=aiohttp.DummyCookieJar()) as gls_session:
                    api = GlsApi(gls_session, session_id=str(uuid.uuid4()))
                    data = await api.login(phone, password)

                return self.async_create_entry(
                    title=f"{self.courier.upper()} ({phone})",
                    data={
                        CONF_COURIER: self.courier,
                        CONF_PHONE: phone,
                        CONF_TOKEN: data.get("access_token"),
                        CONF_REFRESH_TOKEN: data.get("refresh_token"),
                        CONF_ID_TOKEN: data.get("id_token"),
                        CONF_TOKEN_EXPIRES_AT: data.get("token_expires_at"),
                        CONF_SESSION_ID: data.get("session_id"),
                        CONF_SESSION_REGISTERED: data.get("session_registered"),
                    }
                )
            except Exception as e:
                _LOGGER.exception("GLS login failed: %s", e)
                errors["base"] = "auth_error"

        return self.async_show_form(
            step_id="gls_credentials",
            data_schema=vol.Schema({
                vol.Required(CONF_PHONE): str,
                vol.Required(CONF_PASSWORD): str,
            }),
            errors=errors,
        )

    async def async_step_reauth(self, entry_data):
        """Started by HA when an Allegro cookie or an InPost session stops working."""
        self.courier = entry_data.get(CONF_COURIER)
        if self.courier == "inpost":
            self.phone = entry_data.get(CONF_PHONE)
            self.device_uid = entry_data.get(CONF_DEVICE_UID) or self.device_uid
            return await self.async_step_inpost_reauth()
        return await self.async_step_reauth_confirm()

    async def async_step_inpost_reauth(self, user_input=None):
        """Tell the user the InPost session expired, then show the sign-in step."""
        if user_input is not None:
            return await self.async_step_inpost_login()
        return self.async_show_form(
            step_id="inpost_reauth",
            description_placeholders={"phone": self.phone or ""},
        )

    async def async_step_inpost_login(self, user_input=None):
        """Sign in to InPost in the browser and paste the URL it ends on."""
        from .api_inpost import InPostApi, InPostAuthError, InPostLogin, token_phone

        errors = {}
        if self.inpost_login is None:
            self.inpost_login = InPostLogin()

        if user_input is not None:
            try:
                code = self.inpost_login.extract_code(user_input[CONF_CALLBACK_URL])
            except ValueError as err:
                errors["base"] = {
                    "sms": "inpost_sms_code",
                    "state": "inpost_wrong_attempt",
                }.get(str(err), "inpost_no_code")
            else:
                api = InPostApi(async_get_clientsession(self.hass), device_uid=self.device_uid)
                try:
                    await api.exchange_code(code, self.inpost_login.verifier)
                except InPostAuthError as err:
                    _LOGGER.warning("InPost rejected the authorization code: %s", err)
                    errors["base"] = "inpost_code_expired"
                except Exception as err:
                    _LOGGER.exception("InPost sign-in failed: %s", err)
                    errors["base"] = "auth_error"
                else:
                    phone = token_phone(api._token)
                    if (
                        self.source == config_entries.SOURCE_REAUTH
                        and phone
                        and self.phone
                        and normalize_phone(self.phone) != phone
                    ):
                        errors["base"] = "inpost_wrong_account"
                    else:
                        return self._async_finish_inpost_login(api, phone)
            if errors.get("base") in ("inpost_code_expired", "inpost_wrong_account"):
                # The code was used up with this PKCE secret: start over.
                self.inpost_login = InPostLogin()

        return self.async_show_form(
            step_id="inpost_login",
            data_schema=vol.Schema({
                vol.Required(CONF_CALLBACK_URL): str,
            }),
            errors=errors,
            description_placeholders={"login_url": self.inpost_login.url},
        )

    def _async_finish_inpost_login(self, api, phone):
        tokens = {
            CONF_TOKEN: api._token,
            CONF_REFRESH_TOKEN: api._refresh_token,
            CONF_TOKEN_EXPIRES_AT: api._expires_at,
            CONF_DEVICE_UID: self.device_uid,
        }
        if self.source == config_entries.SOURCE_REAUTH:
            entry = self._get_reauth_entry()
            if phone:
                tokens[CONF_PHONE] = phone
            return self.async_update_reload_and_abort(entry, data_updates=tokens)

        return self.async_create_entry(
            title=f"INPOST ({phone})" if phone else "INPOST",
            data={
                CONF_COURIER: self.courier,
                CONF_PHONE: phone,
                **tokens,
            },
        )

    async def async_step_reauth_confirm(self, user_input=None):
        errors = {}

        if user_input is not None:
            cookie = _clean_cookie(user_input[CONF_COOKIE])
            try:
                await _async_validate_allegro_cookie(self.hass, cookie)
            except Exception as e:
                _LOGGER.warning("Allegro cookie validation failed: %s", e)
                errors["base"] = "auth_error"
            else:
                return self.async_update_reload_and_abort(
                    self._get_reauth_entry(),
                    data_updates={CONF_COOKIE: cookie},
                )

        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=vol.Schema({
                vol.Required(CONF_COOKIE): str,
            }),
            errors=errors,
            description_placeholders=ALLEGRO_PLACEHOLDERS,
        )

    async def async_step_allegro_cookie(self, user_input=None):
        errors = {}

        if user_input is not None:
            cookie = _clean_cookie(user_input[CONF_COOKIE])
            try:
                login = await _async_validate_allegro_cookie(self.hass, cookie)
            except Exception as e:
                _LOGGER.warning("Allegro cookie validation failed: %s", e)
                errors["base"] = "auth_error"
            else:
                label = get_account_label({CONF_LOGIN: login})
                return self.async_create_entry(
                    title=f"ALLEGRO ({label})" if label else "ALLEGRO",
                    data={
                        CONF_COURIER: self.courier,
                        CONF_LOGIN: login,
                        CONF_COOKIE: cookie,
                    },
                )

        return self.async_show_form(
            step_id="allegro_cookie",
            data_schema=vol.Schema({
                vol.Required(CONF_COOKIE): str,
            }),
            errors=errors,
            description_placeholders=ALLEGRO_PLACEHOLDERS,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return ShipmentTrackingOptionsFlow()

    async def async_step_sms(self, user_input=None):
        errors = {}
        
        if user_input is not None:
            code = user_input["code"]
            session = async_get_clientsession(self.hass)
            
            try:
                tokens = {}

                if self.courier == "dpd":
                    from .api_dpd import DpdApi
                    api = DpdApi(session)
                    data = await api.register_with_code(self.phone, code)
                    tokens = {
                        CONF_TOKEN: data.get("access_token"),
                        CONF_REFRESH_TOKEN: data.get("refresh_token"),
                        CONF_TOKEN_EXPIRES_AT: api._expires_at,
                    }
                
                elif self.courier == "dhl":
                    from .api_dhl import DhlApi
                    api = DhlApi(session)
                    await api.validate_code(self.phone, code, self.device_uid)

                    # Persist cookies so they survive restarts.
                    cookies_json = json.dumps(api._cookies)
                    tokens = {
                        CONF_TOKEN: api._token,
                        "cookies": cookies_json
                    }

                return self.async_create_entry(
                    title=f"{self.courier.upper()} ({self.phone})",
                    data={
                        CONF_COURIER: self.courier,
                        CONF_PHONE: self.phone,
                        CONF_DEVICE_UID: self.device_uid,
                        **tokens
                    }
                )

            except Exception as e:
                _LOGGER.exception("SMS verification failed: %s", e)
                errors["base"] = "invalid_code"

        return self.async_show_form(
            step_id="sms",
            data_schema=vol.Schema({
                vol.Required("code"): str,
            }),
            errors=errors,
            description_placeholders={"phone": self.phone}
        )


class ShipmentTrackingOptionsFlow(config_entries.OptionsFlow):
    """Per-account options: recipient filters, hidden shipments, Allegro cookie."""

    async def async_step_init(self, user_input=None):
        errors = {}
        entry = self.config_entry
        is_allegro = entry.data.get(CONF_COURIER) == "allegro"

        if user_input is not None:
            new_cookie = _clean_cookie(user_input.pop(CONF_COOKIE, ""))
            if is_allegro and new_cookie:
                try:
                    await _async_validate_allegro_cookie(self.hass, new_cookie)
                except Exception as e:
                    _LOGGER.warning("Allegro cookie validation failed: %s", e)
                    errors["base"] = "auth_error"
                else:
                    self.hass.config_entries.async_update_entry(
                        entry, data={**entry.data, CONF_COOKIE: new_cookie}
                    )
            if not errors:
                return self.async_create_entry(
                    title="",
                    data={
                        CONF_INCLUDE_RECIPIENTS: user_input.get(CONF_INCLUDE_RECIPIENTS, "").strip(),
                        CONF_EXCLUDE_RECIPIENTS: user_input.get(CONF_EXCLUDE_RECIPIENTS, "").strip(),
                        CONF_HIDDEN_SHIPMENTS: user_input.get(CONF_HIDDEN_SHIPMENTS, "").strip(),
                    },
                )

        # suggested_value rather than default: with a default, clearing the
        # field submits nothing and the old value comes back.
        multiline = TextSelector(TextSelectorConfig(multiline=True))
        schema = {
            vol.Optional(
                CONF_INCLUDE_RECIPIENTS,
                description={"suggested_value": entry.options.get(CONF_INCLUDE_RECIPIENTS, "")},
            ): multiline,
            vol.Optional(
                CONF_EXCLUDE_RECIPIENTS,
                description={"suggested_value": entry.options.get(CONF_EXCLUDE_RECIPIENTS, "")},
            ): multiline,
            vol.Optional(
                CONF_HIDDEN_SHIPMENTS,
                description={"suggested_value": entry.options.get(CONF_HIDDEN_SHIPMENTS, "")},
            ): multiline,
        }
        if is_allegro:
            schema[vol.Optional(CONF_COOKIE)] = str

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(schema),
            errors=errors,
        )
