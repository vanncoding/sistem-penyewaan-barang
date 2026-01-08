# diskon_service.py

def hitung_diskon(total_biaya, lama_sewa):
    """
    Modul untuk menghitung diskon berdasarkan aturan tertentu:
    - Sewa > 7 hari: Diskon 15%
    - Sewa > 3 hari: Diskon 10%
    - Total Belanja > Rp 2.000.000: Diskon tambahan Rp 50.000
    """
    persentase_diskon = 0
    potongan_tetap = 0

    # Logika berdasarkan durasi
    if lama_sewa >= 7:
        persentase_diskon = 0.15  # 15%
    elif lama_sewa >= 3:
        persentase_diskon = 0.10  # 10%

    # Hitung nilai diskon persentase
    nilai_diskon = total_biaya * persentase_diskon

    # Logika berdasarkan nominal (tambahan)
    if total_biaya > 2000000:
        potongan_tetap = 50000

    total_potongan = nilai_diskon + potongan_tetap
    return total_potongan, (persentase_diskon * 100)