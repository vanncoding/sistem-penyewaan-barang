import os

# --- 1. INISIALISASI DATA (DATABASE SEDERHANA) ---
# Kita menggunakan List yang berisi Dictionary
inventory = [
    {'id': 1, 'nama': 'Toyota Avanza', 'harga': 300000, 'tersedia': True},
    {'id': 2, 'nama': 'Honda Brio',    'harga': 250000, 'tersedia': True},
    {'id': 3, 'nama': 'Toyota Innova', 'harga': 500000, 'tersedia': True},
    {'id': 4, 'nama': 'Mitsubishi Pajero', 'harga': 800000, 'tersedia': False} # Contoh sedang disewa
]

# --- 2. DEFINISI FUNGSI-FUNGSI ---

def clear_screen():
    """Membersihkan layar terminal agar rapi"""
    os.system('cls' if os.name == 'nt' else 'clear')

def tampilkan_kendaraan():
    """Menampilkan semua kendaraan dalam bentuk tabel rapi"""
    print("\n=== DAFTAR KENDARAAN ===")
    print(f"{'ID':<5} {'Nama Kendaraan':<20} {'Harga/Hari':<15} {'Status'}")
    print("-" * 55)
    
    for mobil in inventory:
        status = "Tersedia" if mobil['tersedia'] else "Sedang Disewa"
        # Format harga dengan pemisah ribuan (contoh: 300,000)
        print(f"{mobil['id']:<5} {mobil['nama']:<20} Rp {mobil['harga']:,:<12} {status}")
    print("-" * 55)

def sewa_kendaraan():
    """Logika untuk menyewa kendaraan"""
    tampilkan_kendaraan()
    try:
        id_sewa = int(input("\nMasukkan ID kendaraan yang ingin disewa: "))
        
        ditemukan = False
        for mobil in inventory:
            if mobil['id'] == id_sewa:
                ditemukan = True
                if mobil['tersedia']:
                    mobil['tersedia'] = False
                    print(f"\n[SUKSES] Anda berhasil menyewa {mobil['nama']}.")
                else:
                    print(f"\n[GAGAL] Maaf, {mobil['nama']} sedang disewa orang lain.")
                break
        
        if not ditemukan:
            print("\n[ERROR] ID kendaraan tidak ditemukan.")
            
    except ValueError:
        print("\n[ERROR] Masukkan input angka yang valid!")

def kembalikan_kendaraan():
    """Logika pengembalian dan perhitungan biaya"""
    print("\n=== PENGEMBALIAN KENDARAAN ===")
    try:
        id_kembali = int(input("Masukkan ID kendaraan yang dikembalikan: "))
        
        ditemukan = False
        for mobil in inventory:
            if mobil['id'] == id_kembali:
                ditemukan = True
                if not mobil['tersedia']: # Jika statusnya False (Sedang disewa)
                    lama = int(input("Berapa hari mobil disewa? "))
                    total_biaya = mobil['harga'] * lama
                    
                    # Reset status menjadi tersedia
                    mobil['tersedia'] = True
                    
                    print("\n" + "="*30)
                    print(f"Detail Pembayaran")
                    print(f"Kendaraan  : {mobil['nama']}")
                    print(f"Lama Sewa  : {lama} hari")
                    print(f"Total Biaya: Rp {total_biaya:,}")
                    print("="*30)
                    print("[INFO] Kendaraan telah dikembalikan ke garasi.")
                else:
                    print("\n[INFO] Mobil ini memang sedang tersedia di garasi (belum disewa).")
                break
        
        if not ditemukan:
            print("\n[ERROR] ID kendaraan tidak ditemukan.")

    except ValueError:
        print("\n[ERROR] Masukkan input angka yang valid!")

# --- 3. PROGRAM UTAMA (MAIN LOOP) ---

def main():
    while True:
        print("\n" + "="*25)
        print(" SISTEM RENTAL MOBIL")
        print("="*25)
        print("1. Lihat Daftar Kendaraan")
        print("2. Sewa Kendaraan")
        print("3. Kembalikan Kendaraan")
        print("4. Keluar")
        
        pilihan = input("\nPilih menu (1-4): ")
        
        if pilihan == '1':
            clear_screen()
            tampilkan_kendaraan()
        elif pilihan == '2':
            clear_screen()
            sewa_kendaraan()
        elif pilihan == '3':
            clear_screen()
            kembalikan_kendaraan()
        elif pilihan == '4':
            print("\nTerima kasih telah menggunakan sistem rental kami!")
            break
        else:
            print("\nPilihan tidak valid, silakan coba lagi.")

# Menjalankan program
if __name__ == "__main__":
    main()