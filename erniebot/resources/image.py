# Copyright (c) 2023 PaddlePaddle Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from typing import (Any, Dict, Optional, Tuple)

from typing_extensions import TypeAlias

import erniebot.errors as errors
from erniebot.api_types import APIType
from erniebot.response import EBResponse
from erniebot.types import (ParamsType, HeadersType)
from .resource import EBResource


class _Image(EBResource):
    @classmethod
    def create(cls, **create_kwargs: Any) -> EBResponse:
        resource = cls.new_object()
        return resource.create_resource(**create_kwargs)

    @classmethod
    async def acreate(cls, **create_kwargs: Any) -> EBResponse:
        resource = cls.new_object()
        resp = await resource.acreate_resource(**create_kwargs)
        return resp

    def create_resource(self, **kwargs: Any) -> EBResponse:
        url, params, headers, request_timeout = self._prepare_paint(kwargs)
        resp_p = self.request(
            method='POST',
            url=url,
            stream=False,
            params=params,
            headers=headers,
            files=None,
            request_timeout=request_timeout)
        assert isinstance(resp_p, EBResponse)

        url, params, headers = self._prepare_fetch(resp_p)
        resp_f = self.poll(
            until=self._check_status,
            method='POST',
            url=url,
            params=params,
            headers=headers,
            # XXX: Reuse `request_timeout`. Should we implement finer-grained control?
            request_timeout=request_timeout)

        return resp_f

    async def acreate_resource(self, **kwargs: Any) -> EBResponse:
        url, params, headers, request_timeout = self._prepare_paint(kwargs)
        resp_p = await self.arequest(
            method='POST',
            url=url,
            stream=False,
            params=params,
            headers=headers,
            files=None,
            request_timeout=request_timeout)
        assert isinstance(resp_p, EBResponse)

        url, params, headers = self._prepare_fetch(resp_p)
        resp_f = await self.apoll(
            until=self._check_status,
            method='POST',
            url=url,
            params=params,
            headers=headers,
            # XXX: Reuse `request_timeout`. Should we implement finer-grained control?
            request_timeout=request_timeout)

        return resp_f

    def _prepare_paint(self,
                       kwargs: Dict[str, Any]) -> Tuple[str,
                                                        Optional[ParamsType],
                                                        Optional[HeadersType],
                                                        Optional[float],
                                                        ]:
        raise NotImplementedError

    def _prepare_fetch(self, resp_p: EBResponse) -> Tuple[str,
                                                          Optional[ParamsType],
                                                          Optional[HeadersType],
                                                          ]:
        raise NotImplementedError

    @staticmethod
    def _check_status(resp: EBResponse) -> bool:
        raise NotImplementedError


class ImageV1(_Image):
    """Generate a new image based on a given prompt."""

    def _prepare_paint(self,
                       kwargs: Dict[str, Any]) -> Tuple[str,
                                                        Optional[ParamsType],
                                                        Optional[HeadersType],
                                                        Optional[float],
                                                        ]:
        def _set_val_if_key_exists(src: dict, dst: dict, key: str) -> None:
            if key in src:
                dst[key] = src[key]

        VALID_KEYS = {
            'text', 'resolution', 'style', 'num', 'headers', 'request_timeout'
        }

        invalid_keys = kwargs.keys() - VALID_KEYS

        if len(invalid_keys) > 0:
            raise errors.InvalidArgumentError(
                f"Invalid keys found in `kwargs`: {list(invalid_keys)}")

        # text
        if 'text' not in kwargs:
            raise errors.ArgumentNotFoundError("`text` is not found.")
        text = kwargs['text']

        # resolution
        if 'resolution' not in kwargs:
            raise errors.ArgumentNotFoundError(f"`resolution` is not found.")
        resolution = kwargs['resolution']

        # style
        if 'style' not in kwargs:
            raise errors.ArgumentNotFoundError(f"`style` is not found.")
        style = kwargs['style']

        # url
        if self.api_type is APIType.YINIAN:
            url = "/txt2img"
        else:
            raise errors.UnsupportedAPITypeError

        # params
        params = {}
        params['text'] = text
        params['resolution'] = resolution
        params['style'] = style
        _set_val_if_key_exists(kwargs, params, 'num')

        # headers
        headers = kwargs.get('headers', {'Accept': 'application/json'})

        # request_timeout
        request_timeout = kwargs.get('request_timeout', None)

        return url, params, headers, request_timeout

    def _prepare_fetch(self, resp_p: EBResponse) -> Tuple[str,
                                                          Optional[ParamsType],
                                                          Optional[HeadersType],
                                                          ]:
        # url
        if self.api_type is APIType.YINIAN:
            url = "/getImg"
        else:
            raise errors.UnsupportedAPITypeError

        # params
        params = {}
        params['taskId'] = resp_p.data['taskId']

        # headers
        headers = {'Accept': 'application/json'}

        return url, params, headers

    @staticmethod
    def _check_status(resp: EBResponse) -> bool:
        status = resp.data['status']
        return status == 1


class ImageV2(_Image):
    """Generate a new image based on a given prompt."""

    def _prepare_paint(self,
                       kwargs: Dict[str, Any]) -> Tuple[str,
                                                        Optional[ParamsType],
                                                        Optional[HeadersType],
                                                        Optional[float],
                                                        ]:
        def _set_val_if_key_exists(src: dict, dst: dict, key: str) -> None:
            if key in src:
                dst[key] = src[key]

        VALID_KEYS = {
            'model', 'prompt', 'width', 'height', 'version', 'image_num',
            'headers', 'request_timeout'
        }

        invalid_keys = kwargs.keys() - VALID_KEYS

        if len(invalid_keys) > 0:
            raise errors.InvalidArgumentError(
                f"Invalid keys found in `kwargs`: {list(invalid_keys)}")

        # model
        if 'model' not in kwargs:
            raise errors.ArgumentNotFoundError("`model` is not found.")
        model = kwargs['model']

        # prompt
        if 'prompt' not in kwargs:
            raise errors.ArgumentNotFoundError("`prompt` is not found.")
        prompt = kwargs['prompt']

        # width
        if 'width' not in kwargs:
            raise errors.ArgumentNotFoundError(f"`width` is not found.")
        width = kwargs['width']

        # height
        if 'height' not in kwargs:
            raise errors.ArgumentNotFoundError(f"`height` is not found.")
        height = kwargs['height']

        # url
        if self.api_type is APIType.YINIAN:
            url = "/txt2imgv2"
            if model != 'ernie-vilg-v2':
                raise errors.InvalidArgumentError(
                    f"{repr(model)} is not a supported model.")
        else:
            raise errors.UnsupportedAPITypeError

        # params
        params = {}
        params['prompt'] = prompt
        params['width'] = width
        params['height'] = height
        _set_val_if_key_exists(kwargs, params, 'version')
        _set_val_if_key_exists(kwargs, params, 'image_num')

        # headers
        headers = kwargs.get('headers', {'Accept': 'application/json'})

        # request_timeout
        request_timeout = kwargs.get('request_timeout', None)

        return url, params, headers, request_timeout

    def _prepare_fetch(self, resp_p: EBResponse) -> Tuple[str,
                                                          Optional[ParamsType],
                                                          Optional[HeadersType],
                                                          ]:
        # url
        if self.api_type is APIType.YINIAN:
            url = "/getImgv2"
        else:
            raise errors.UnsupportedAPITypeError

        # params
        params = {}
        params['task_id'] = resp_p.data['task_id']

        # headers
        headers = {'Accept': 'application/json'}

        return url, params, headers

    @staticmethod
    def _check_status(resp: EBResponse) -> bool:
        status = resp.data['task_status']
        if status == 'FAILED':
            raise errors.APIError("Image generation failed.")
        return status == 'SUCCESS'


Image: TypeAlias = ImageV2
