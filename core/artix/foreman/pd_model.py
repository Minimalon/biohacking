import json
from pathlib import Path

from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Union

import config


class ForemanCash(BaseModel):
    shopcode: Union[None, int] = Field(0, alias='artix_shopcode')
    cashcode: Union[None, int] = Field(0, alias='artix_cashcode')
    artix_shopname: Union[None, str] = Field("", alias='artix_shopname')
    inn: Union[None, str] = Field("", alias='artix_inn')
    kpp: Union[None, str] = Field("", alias='artix_kpp')
    fsrar: Union[None, str] = Field("", alias='artix_fsrar_id_1')
    xapikey: Union[None, str] = Field("", alias='xapikey')
    address: Union[None, str] = Field("", alias='artix_address')
    artix_shopname2: Union[None, str] = Field("", alias='artix_shopname2')
    inn2: Union[None, str] = Field("", alias='artix_inn2')
    kpp2: Union[None, str] = Field("", alias='artix_kpp2')
    fsrar2: Union[None, str] = Field("", alias='artix_fsrar_id_2')
    address2: Union[None, str] = Field("", alias='artix_address2')
    artix_version: Union[None, str] = Field("", alias='artix_version')
    tun0: Union[None, str] = Field("", alias='ipaddress_tun0')
    tun1: Union[None, str] = Field("", alias='ipaddress_tun1')
    os_name: Union[None, str] = Field("", alias='lsbdistcodename')
    gui_interface: Union[None, str] = Field("keyboard", alias='artix_gui_interface')
    kkm1_name: Union[None, str] = Field("", alias='artix_kkm_1_producer_name')
    kkm1_number: Union[None, str] = Field("", alias='artix_kkm_1_number')
    kkm1_firmware: Union[None, str] = Field("", alias='artix_kkm_1_firmware')
    kkm1_departs: Union[None, str] = Field("", alias='artix_kkm1_departmapping')
    kkm1_ffd_version: Union[None, str] = Field("", alias='artix_kkm_1_ffd_version')
    kkm1_fn_number: Union[None, str] = Field("", alias='artix_kkm_1_fn_number')
    kkm1_fn_date_end: Union[None, str] = Field("", alias='artix_kkm_1_fn_time_end')
    kkm2_name: Union[None, str] = Field("", alias='artix_kkm_2_producer_name')
    kkm2_number: Union[None, str] = Field("", alias='artix_kkm_2_number')
    kkm2_firmware: Union[None, str] = Field("", alias='artix_kkm_2_firmware')
    kkm2_departs: Union[None, str] = Field("", alias='artix_kkm2_departmapping')
    kkm2_fn_number: Union[None, str] = Field("", alias='artix_kkm_2_fn_number')
    kkm2_ffd_version: Union[None, str] = Field("", alias='artix_kkm_2_ffd_version')
    kkm2_fn_date_end: Union[None, str] = Field("", alias='artix_kkm_2_fn_time_end')
    gost1_date_end: Union[None, str] = Field("", alias='artix_gost_1')
    pki1_date_end: Union[None, str] = Field("", alias='artix_pki_1')
    gost2_date_end: Union[None, str] = Field("", alias='artix_gost_2')
    pki2_date_end: Union[None, str] = Field("", alias='artix_pki_2')
    is_bar: bool = Field(False, alias='is_bar')

    def ip(self) -> str:
        return self.tun0 if self.tun0.startswith('10.8') else self.tun1

    @field_validator('artix_shopname')
    def check_name1(cls, v):
        if v == 'NAME':
            return ''
        return v

    @field_validator('artix_shopname2')
    def check_name2(cls, v):
        if v == 'NAME':
            return ''
        return v

    @field_validator('kkm1_name')
    def fr_name(cls, v):
        if v == 'Кристалл':
            return 'Вики Принт'
        return v

    @field_validator('kkm2_name')
    def fr_name2(cls, v):
        if v == 'Кристалл':
            return 'Вики Принт'
        return v

    def degustation_file_path(self, message_id) -> Path:
        dir = Path(config.server_path, 'degustation', str(self.shopcode))
        dir.mkdir(parents=True, exist_ok=True)
        return dir / f'{message_id}.json'

    def ref_payload(self, ref_id: str):
        return '/'.join([
            str(self.shopcode),
            str(self.cashcode),
            ref_id,
        ])
    def get_IP_inn(self) -> Union[None, str]:
        if self.inn2 is not None:
            if len(self.inn2) == 12:
                return self.inn2
        if self.inn is not None:
            if len(self.inn) == 12:
                return self.inn

class Deeplink(BaseModel):
    shopcode: int
    cashcode: int
    ref_id: str