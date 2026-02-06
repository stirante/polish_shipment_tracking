import voluptuous as vol
import uuid
import json
import logging
from homeassistant import config_entries
from homeassistant.helpers.aiohttp_client import async_get_clientsession

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
)
from .api_helpers import normalize_phone

_LOGGER = logging.getLogger(__name__)

COURIERS = ["inpost", "dpd", "dhl", "pocztex"]

class ShipmentTrackingConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    def __init__(self):
        self.courier = None
        self.phone = None
        self.api_instance = None
        self.temp_data = {}
        self.device_uid = uuid.uuid4().hex

    async def async_step_user(self, user_input=None):
        errors = {}
        
        if user_input is not None:
            self.courier = user_input[CONF_COURIER]
            if self.courier == "pocztex":
                return await self.async_step_pocztex_credentials()
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
                if self.courier == "inpost":
                    from .api_inpost import InPostApi
                    self.api_instance = InPostApi(session, device_uid=self.device_uid)
                    await self.api_instance.send_sms_code(self.phone)

                elif self.courier == "dpd":
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

    async def async_step_sms(self, user_input=None):
        errors = {}
        
        if user_input is not None:
            code = user_input["code"]
            session = async_get_clientsession(self.hass)
            
            try:
                tokens = {}
                
                if self.courier == "inpost":
                    from .api_inpost import InPostApi
                    api = InPostApi(session, device_uid=self.device_uid)
                    data = await api.confirm_sms_code(self.phone, code)
                    tokens = {
                        CONF_TOKEN: data.get("authToken"),
                        CONF_REFRESH_TOKEN: data.get("refreshToken")
                    }

                elif self.courier == "dpd":
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
                    data = await api.validate_code(self.phone, code, self.device_uid)
                    token = data.get("accessToken") or data.get("data", {}).get("accessToken")
                    
                    # Persist cookies so they survive restarts.
                    cookies_json = json.dumps(api._cookies)
                    tokens = {
                        CONF_TOKEN: token,
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
