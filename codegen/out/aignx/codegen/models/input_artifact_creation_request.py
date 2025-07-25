# coding: utf-8

"""
    Aignostics Platform API reference

     Pagination is done via `page` and `page_size`. Sorting via `sort` query parameter. The `sort` query parameter can be provided multiple times. The sorting direction can be indicated via `+` (ascending) or `-` (descending) (e.g. `/v1/applications?sort=+name)`.

    The version of the OpenAPI document: 1.0.0
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501


from __future__ import annotations
import pprint
import re  # noqa: F401
import json

from pydantic import BaseModel, ConfigDict, Field, StrictStr
from typing import Any, ClassVar, Dict, List
from typing_extensions import Annotated
from typing import Optional, Set
from typing_extensions import Self

class InputArtifactCreationRequest(BaseModel):
    """
    InputArtifactCreationRequest
    """ # noqa: E501
    name: StrictStr = Field(description="The artifact name according to the application version. List of required artifacts is returned by `/v1/versions/{application_version_id}`. The artifact names are located in the `input_artifacts.[].name` value")
    download_url: Annotated[str, Field(min_length=1, strict=True, max_length=2083)] = Field(description="[Signed URL](https://cloud.google.com/cdn/docs/using-signed-urls) to the input artifact file. The URL should be valid for at least 6 days from the payload submission time.")
    metadata: Dict[str, Any] = Field(description="The metadata of the artifact, required by the application version. The JSON schema of the metadata can be requested by `/v1/versions/{application_version_id}`. The schema is located in `input_artifacts.[].metadata_schema`")
    __properties: ClassVar[List[str]] = ["name", "download_url", "metadata"]

    model_config = ConfigDict(
        populate_by_name=True,
        validate_assignment=True,
        protected_namespaces=(),
    )


    def to_str(self) -> str:
        """Returns the string representation of the model using alias"""
        return pprint.pformat(self.model_dump(by_alias=True))

    def to_json(self) -> str:
        """Returns the JSON representation of the model using alias"""
        # TODO: pydantic v2: use .model_dump_json(by_alias=True, exclude_unset=True) instead
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_str: str) -> Optional[Self]:
        """Create an instance of InputArtifactCreationRequest from a JSON string"""
        return cls.from_dict(json.loads(json_str))

    def to_dict(self) -> Dict[str, Any]:
        """Return the dictionary representation of the model using alias.

        This has the following differences from calling pydantic's
        `self.model_dump(by_alias=True)`:

        * `None` is only added to the output dict for nullable fields that
          were set at model initialization. Other fields with value `None`
          are ignored.
        """
        excluded_fields: Set[str] = set([
        ])

        _dict = self.model_dump(
            by_alias=True,
            exclude=excluded_fields,
            exclude_none=True,
        )
        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of InputArtifactCreationRequest from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "name": obj.get("name"),
            "download_url": obj.get("download_url"),
            "metadata": obj.get("metadata")
        })
        return _obj


