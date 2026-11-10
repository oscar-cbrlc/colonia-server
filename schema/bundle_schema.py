from pydantic import BaseModel, ConfigDict
from typing import Optional

class BundleBase(BaseModel):
    bundle_name: str
    bundle_image: str

class BundleCreate(BundleBase):
    pass

class BundleUpdate(BaseModel):
    bundle_name: Optional[str]
    bundle_image: Optional[str]

class BundleResponse(BaseModel):
    bundle_id: int
    bundle_name: str
    bundle_image: str
    model_config = ConfigDict(from_attributes=True)
