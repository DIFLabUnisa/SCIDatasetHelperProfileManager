import json
import posixpath
import urllib.request
from pprint import pprint
from Utils import parse_profiles, getch, file_path_to_url, EnhancedJSONEncoder, sdchprofiles_to_dict
from Models import SDCHProfiles, SDCHProfile, CameraPositions, CameraTypes, OutputFormats
from sys import stdin
from dotenv import load_dotenv
from pathlib import Path
import os
import shutil
from datetime import datetime

url_profile = ""
max_id = -1
profiles: SDCHProfiles = SDCHProfiles(default_profile=-1, profiles=[])


def get_description() -> str:
    ret = ""
    for line in stdin:
        ret += line
    return ret


def get_camera_position(current_position: CameraPositions | None) -> CameraPositions:
    idx = 0
    positions: [CameraPositions] = []
    if current_position is not None:
        print(f"{idx}) Conferma attuale {current_position.name}")
        idx += 1
        positions.append(current_position)

    for p in CameraPositions:
        print(f"{idx}) {p.name}")
        positions.append(p)
        idx += 1
    p = int(getch())
    return positions[p]


def get_camera_types(current_types: [CameraTypes]) -> [CameraTypes]:
    idx = 0
    prev = "".join([c.name for c in current_types])
    print(f"{idx}) Conferma attuale [{prev}]")
    idx += 1
    types: [CameraTypes] = [CameraTypes.WideAngle]
    for p in CameraTypes:
        print(f"{idx}) {p.name}")
        types.append(p)
        idx += 1
    print("Seleziona tutti i tipi da inserire nel profilo (usa , per separare i diversi profili)")
    input1 = input()
    selections = [a.strip() for a in input1.split(sep=",")]
    if "0" in selections:
        return current_types

    return [types[i] for i in selections]


def get_output_formats(current_formats: [OutputFormats]) -> [OutputFormats]:
    idx = 0
    prev = "".join([c.name for c in current_formats])
    print(f"{idx}) Conferma attuale [{prev}]")
    idx += 1
    types: [OutputFormats] = [OutputFormats.HEIC]
    for p in OutputFormats:
        print(f"{idx}) {p.name}")
        types.append(p)
        idx += 1
    print("Seleziona tutti gli output da inserire nel profilo (usa , per separare i diversi profili)")
    input1 = input()
    selections = [a.strip() for a in input1.split(sep=",")]
    if "0" in selections:
        return current_formats

    return [types[i] for i in selections]


def add_or_edit_profile(original_profile: SDCHProfile | None) -> SDCHProfile:
    global max_id
    if original_profile is None:
        original_profile = SDCHProfile()
        max_id += 1
        original_profile.id = max_id
        original_profile.output_formats = []
        original_profile.camera_types = []

    print(f"Inserisci nome del profilo [{original_profile.name}]")
    input1 = input()
    if input1.strip() != "":
        original_profile.name = input1

    print(f"Inserisci descrizione del profilo CTRL-D per terminare")
    print(f"[{original_profile.description}]")
    input1 = get_description()
    if input1.strip() != "":
        original_profile.description = input1

    original_profile.positions = get_camera_position(current_position=original_profile.positions)

    original_profile.camera_types = get_camera_types(current_types=original_profile.camera_types)

    original_profile.output_formats = get_output_formats(current_formats=original_profile.output_formats)

    print("Inserire il numero di immagini di enrollment:")
    original_profile.enrollment = int(input())
    print("Inserire il numero di immagini di training:")
    original_profile.training = int(input())

    print("Inserire N per disattivare il profilo")
    original_profile.training = getch().lower() != "n"

    return original_profile


def print_profile_names(p: SDCHProfile):
    print(f"** ID: {p.id} - Nome: {p.name} - Attivo {'SI' if p.active else 'NO'}**")


def print_profile(p: SDCHProfile):
    print(f"ID:\t {p.id}")
    print(f"Nome:\t {p.name}")
    if p.description is not None:
        print(f"Descrzione:\t {p.description}")
    print(f"Posizioni:\t {p.positions}")

    print("Tipi di camera:\t [")
    for camera in p.camera_types:
        print(f"\t\t {camera.name}")
    print("\t]")

    print("Formati di output:\t [")
    for camera in p.camera_types:
        print(f"\t\t {camera.name}")
    print("\t]")

    print(f"Immagini di enrollment:\t {p.enrollment}")
    print(f"Immagini di training:\t {p.training}")
    print(f"Attivo:\t {'Si' if p.active else 'No'}")


def add_profile():
    global profiles
    prof = add_or_edit_profile(None)
    profiles.profiles.append(prof)
    if profiles.default_profile == -1:
        profiles.default_profile = prof.id


def edit_profile():
    global profiles
    if profiles.default_profile != -1:
        for prof in profiles.profiles:
            print_profile_names(prof)

        print("Selezionare il profilo da modificare, -1 per tornare al menu precedente:")
        input1 = input()
        if input1 == "-1":
            return
        input1 = int(input1)
        loc_profiles = profiles.profiles
        filtered = list(filter(lambda profile: profile_filter_by_id(profile, input1), loc_profiles))
        if len(filtered) > 0:
            old_profile = filtered[0]
            new_profile = add_or_edit_profile(old_profile)
            profiles.profiles = [new_profile if x.id == old_profile.id else x for x in profiles.profiles]
    else:
        add_profile()


def select_default_profile():
    global profiles
    print(f"Il profilo di default attuale ?? {profiles.default_profile}")
    for prof in profiles.profiles:
        print_profile_names(prof)

    print("Selezionare il profilo da inserire come favorito:")
    input1 = input()
    if input1 == "-1":
        return
    input1 = int(input1)
    loc_profiles = profiles.profiles
    filtered = list(filter(lambda profile: profile_filter_by_id(profile, input1), loc_profiles))
    if len(filtered) > 0:
        profile = filtered[0]
        profiles.default_profile = profile.id


def profiles_list():
    p = parse_json(url_profile)
    if p.default_profile != -1:
        for prof in p.profiles:
            print_profile_names(prof)
    print(f"Profilo di default {p.default_profile}")
    while (True):
        print("Selezionare il profilo di cui vedere i dettagli, -1 per tornare al menu precedente:")
        input1 = input()
        if input1 == "-1":
            return
        input1 = int(input1)
        profiles = p.profiles
        filtered = list(filter(lambda profile: profile_filter_by_id(profile, input1), profiles))
        if len(filtered) > 0:
            print_profile(filtered[0])
        else:
            print(f"Profilo con id {input1} non trovato")


def profile_filter_by_id(profile: SDCHProfile, id: int) -> bool:
    return profile.id == id


def save_to_file():
    default_profiles_folder = os.getenv("PROFILES_PATH", default="./profiles")
    default_profile_files = os.getenv("DEFAULT_PROFILE", default="profiles.latest.json")
    path = Path(os.path.join(default_profiles_folder, default_profile_files))
    absolute_output_file = str(path.absolute())
    now = datetime.now()
    cur_time = now.strftime("%Y%m%d_%H%M%S")
    path = Path(os.path.join(default_profiles_folder, f"profiles.{cur_time}.json"))
    absolute_old_file_path = str(path.absolute())
    shutil.move(absolute_output_file, absolute_old_file_path)
    profiles_as_dict = sdchprofiles_to_dict(profiles)
    output = json.dumps(profiles_as_dict, indent=4, sort_keys=False)
    # print(output)
    with open(absolute_output_file, "w+") as f:
        f.write(output)


def switch_profile_status(profile: SDCHProfile) -> SDCHProfile:
    profile.active = not profile.active
    return profile


def switch_profiles_status():
    global profiles
    print(f"Il profilo di default attuale ?? {profiles.default_profile}")
    for prof in profiles.profiles:
        print_profile_names(prof)

    print("Seleziona tutti i profili di cui cambiare lo stato di attivazione (usa , per separare i diversi profili).")
    print("Inserisci -1 per annullare")
    input1 = input()
    selections = [a.strip() for a in input1.split(sep=",")]
    if "-1" in selections:
        return
    else:
        profiles.profiles = [switch_profile_status(x) if str(x.id) in selections else x for x in profiles.profiles]

    print(f"Il profilo di default attuale ?? {profiles.default_profile}")
    for prof in profiles.profiles:
        print_profile_names(prof)


def main():
    parse_json(profile_url=url_profile)
    while (True):
        print("Selezionare una azione: ")
        print("1) Lista profili attuali")
        print("2) Aggiungi un nuovo profilo")
        print("3) Modifica profilo esistente")
        print("4) Seleziona profilo default")
        print("5) Cambia status profili (attivo/disattivo)")
        print("s) Salva in un nuovo profilo di default")
        print("e) Salva in un nuovo profilo di default ed esci")
        print("q) Esci")
        c = getch()
        if c == '1':
            profiles_list()
        elif c == '2':
            add_profile()
        elif c == '3':
            edit_profile()
        elif c == '4':
            select_default_profile()
        elif c == '5':
            switch_profiles_status()
        elif c == 's':
            save_to_file()
        elif c == 'e':
            save_to_file()
            exit(0)
        elif c == 'q':
            exit(0)
        else:
            print("Selezione non valida")


def parse_json(profile_url, force_reload=False) -> SDCHProfiles:
    global profiles
    if profiles.default_profile == -1 or force_reload:
        with urllib.request.urlopen(profile_url, timeout=10) as url:
            data = url.read().decode()
            json_decoded = json.loads(data)
            profiles = parse_profiles(json_decoded)
    return profiles


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    load_dotenv()
    default_profiles_folder = os.getenv("PROFILES_PATH", default="./profiles")
    default_profile_files = os.getenv("DEFAULT_PROFILE", default="profiles.latest.json")
    path = Path(os.path.join(default_profiles_folder, default_profile_files))
    url_profile = file_path_to_url(path)
    main()
