import dataclasses, json

from Models import SDCHProfile, SDCHProfiles


def sdchprofiles_to_dict(op: SDCHProfiles) -> dict:
    d = dict()
    d["profiles"] = []
    d["default_profile"] = op.default_profile
    profiles = op.profiles
    # print(type(profiles))
    for p in profiles:
        cp = dict()
        cp["id"] = p.id
        cp["name"] = p.name
        cp["enrollment"] = p.enrollment
        cp["training"] = p.training
        cp["positions"] = p.positions.value
        cp["camera_types"] = []
        for c in p.camera_types:
            cp["camera_types"].append(c.value)
        if p.description is not None:
            cp["description"] = p.description
        cp["output_formats"] = []
        for f in p.output_formats:
            cp["output_formats"].append(f.value)
        cp["active"] = p.active
        d["profiles"].append(cp)
    # print(d)
    return d


class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        return super().default(o)
