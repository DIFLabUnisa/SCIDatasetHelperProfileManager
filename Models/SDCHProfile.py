from dataclasses import dataclass
import enum
from typing import Optional


@dataclass
class CameraPositions(enum.Enum):
    Front = "front-cameras"
    Back = "back-cameras"
    Unspecified = "unspecified-cameras"


@dataclass
class CameraTypes(enum.Enum):
    WideAngle = "wide"
    UltraWide = "ultra-wide"
    Telephoto = "telephoto"


@dataclass
class OutputFormats(enum.Enum):
    HEIC = "heic"
    JPEG = "jpeg"
    RAW = "raw"


@dataclass
class SDCHProfile:
    id: int = -1
    name: str = ""
    enrollment: int = -1
    training: int = -1
    positions: CameraPositions = CameraPositions.Unspecified
    camera_types: [CameraTypes] = ()
    description: Optional[str] = None
    output_formats: [OutputFormats] = ()
    active: bool = True