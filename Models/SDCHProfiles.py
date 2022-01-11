from dataclasses import dataclass
from Models import SDCHProfile


@dataclass
class SDCHProfiles:
    profiles: [SDCHProfile] = ()
    default_profile: int = -1
