import requests
from collections import defaultdict
from datetime import timedelta, datetime
import json
import os

kode_wilayah_dict = {
    "u1_tanah_tinggi": "36.71.01.1003",
    "r1_1_kemang": "32.01.12.2003",
    "r1_2_parung": "32.01.10.2001",
    "r1_3_tanjurhalang": "32.01.37.2001",
    
    "u2_tuban": "51.03.01.1001",
    "r2_1_baler_bale_agung": "51.01.01.1006",
    "r2_2_medewi": "51.01.03.2001",
    "r2_3_yehembang": "51.01.02.2008"
}


headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

wilayah_data = {}

today = datetime.today().date()
tomorrow = today + timedelta(days=1)
day_after_tomorrow = today + timedelta(days=2)
tanggal_harian = [str(today), str(tomorrow), str(day_after_tomorrow)]

for key, kode_wilayah_4 in kode_wilayah_dict.items():
    url = f"https://api.bmkg.go.id/publik/prakiraan-cuaca?adm4={kode_wilayah_4}"
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        cuaca_data = data["data"][0]["cuaca"]

        suhu_per_hari = defaultdict(list)
        for entry_group in cuaca_data:
            for entry in entry_group:
                local_datetime = entry["local_datetime"]
                tanggal = local_datetime.split(" ")[0]
                if tanggal in tanggal_harian:
                    suhu_per_hari[tanggal].append(entry["t"])

        rata_rata_suhu = {
            tanggal: sum(suhu_list) / len(suhu_list)
            for tanggal, suhu_list in suhu_per_hari.items()
        }

        wilayah_data[key] = rata_rata_suhu

    except Exception as e:
        print(f"[ERROR] Gagal ambil data untuk {key}: {e}")

uhi_data = {
    "Tanah Tinggi": {
        "kemang": {},
        "parung": {},
        "tanjurhalang": {}
    },
    "Tuban": {
        "baler_bale_agung": {},
        "medewi": {},
        "yehembang": {}
    }
}

for tanggal in tanggal_harian:
    try:
        # Tanah Tinggi
        suhu_u1 = wilayah_data["u1_tanah_tinggi"][tanggal]
        uhi_data["Tanah Tinggi"]["kemang"][tanggal] = suhu_u1 - wilayah_data["r1_1_kemang"].get(tanggal, suhu_u1)
        uhi_data["Tanah Tinggi"]["parung"][tanggal] = suhu_u1 - wilayah_data["r1_2_parung"].get(tanggal, suhu_u1)
        uhi_data["Tanah Tinggi"]["tanjurhalang"][tanggal] = suhu_u1 - wilayah_data["r1_3_tanjurhalang"].get(tanggal, suhu_u1)

        # Tuban
        suhu_u2 = wilayah_data["u2_tuban"][tanggal]
        uhi_data["Tuban"]["baler_bale_agung"][tanggal] = suhu_u2 - wilayah_data["r2_1_baler_bale_agung"].get(tanggal, suhu_u2)
        uhi_data["Tuban"]["medewi"][tanggal] = suhu_u2 - wilayah_data["r2_2_medewi"].get(tanggal, suhu_u2)
        uhi_data["Tuban"]["yehembang"][tanggal] = suhu_u2 - wilayah_data["r2_3_yehembang"].get(tanggal, suhu_u2)

    except KeyError as e:
        print(f"[WARNING] Data suhu tidak lengkap untuk tanggal {tanggal}: {e}")


with open("uhi_result.json", "w") as json_file:
    json.dump(uhi_data, json_file, indent=4)

timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')
with open("uhi_log.txt", "a") as log_file:
    log_file.write(f"Script dijalankan pada: {timestamp}\n")

print("[INFO] Proses selesai. Hasil disimpan ke uhi_result.json dan uhi_log.txt")
