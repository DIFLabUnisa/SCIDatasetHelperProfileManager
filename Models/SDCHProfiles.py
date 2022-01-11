from dataclasses import dataclass,field
from Models import SDCHProfile


@dataclass
class SDCHProfiles:
    profiles: [SDCHProfile] = field(default_factory=list)
    default_profile: int = -1