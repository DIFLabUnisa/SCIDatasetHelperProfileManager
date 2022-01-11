from Models import SDCHProfiles, SDCHProfile, CameraPositions, CameraTypes, OutputFormats
from typing import Optional
from pprint import pprint


def parse_profiles(data: dict) -> SDCHProfiles:
    profiles = data["profiles"]
    default_profile = data["default_profile"]
    sdch_profile = SDCHProfiles(default_profile=default_profile, profiles=[])

    for p in profiles:
        profile = SDCHProfile()
        profile.id = p["id"]
        profile.name = p["name"]
        profile.output_formats = []
        profile.camera_types = []
        profile.positions = get_camera_positions_from_string(p["positions"])
        output_formats = p["output_formats"]
        for o in output_formats:
            tmp = get_output_formats_from_string(o)
            if tmp is not None:
                profile.output_formats.append(tmp)

        for c in p["camera_types"]:
            tmp = get_camera_types_from_string(c)
            if tmp is not None:
                profile.camera_types.append(tmp)

        if "description" in p.keys():
            profile.description = p["description"]

        profile.enrollment = p["enrollment"]
        profile.training = p["training"]
        profile.active = p["active"]

        sdch_profile.profiles.append(profile)

    return sdch_profile


def get_camera_positions_from_string(raw_camera_position: str) -> CameraPositions:
    if raw_camera_position == CameraPositions.Front.value:
        return CameraPositions.Front

    if raw_camera_position == CameraPositions.Back.value:
        return CameraPositions.Back

    return CameraPositions.Unspecified


def get_camera_types_from_string(raw_camera_type: str) -> Optional[CameraTypes]:
    if raw_camera_type == CameraTypes.Telephoto.value:
        return CameraTypes.Telephoto

    if raw_camera_type == CameraTypes.UltraWide.value:
        return CameraTypes.UltraWide

    if raw_camera_type == CameraTypes.WideAngle.value:
        return CameraTypes.WideAngle

    return None


def get_output_formats_from_string(raw_output_formats: str) -> Optional[OutputFormats]:
    if raw_output_formats == OutputFormats.HEIC.value:
        return OutputFormats.HEIC

    if raw_output_formats == OutputFormats.RAW.value:
        return OutputFormats.RAW

    if raw_output_formats == OutputFormats.JPEG.value:
        return OutputFormats.JPEG

    return None
