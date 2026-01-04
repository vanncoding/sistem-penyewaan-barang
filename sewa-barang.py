import os
import datetime
import pandas as pd

inventory = [
    {'id': 1, 'nama': 'Toyota Avanza', 'harga': 300000, 'tersedia': True},
    {'id': 2, 'nama': 'Honda Brio',    'harga': 250000, 'tersedia': True},
    {'id': 3, 'nama': 'Toyota Innova', 'harga': 500000, 'tersedia': True},
    {'id': 4, 'nama': 'Mitsubishi Pajero', 'harga': 800000, 'tersedia': True}, # Contoh sedang disewa
    {'id': 5, 'nama': 'Mazda CX3', 'harga': 700000, 'tersedia': True},
    {'id': 6, 'nama': 'Daihatsu Sigra', 'harga': 200000, 'tersedia': True},
    {'id': 7, 'nama': 'Toyota Agya', 'harga': 160000, 'tersedia': True},
    {'id': 8, 'nama': 'Daihatsu Xenia', 'harga': 300000, 'tersedia': True},
    {'id': 9, 'nama': 'Toyota Raize', 'harga': 400000, 'tersedia': True},
    {'id': 10, 'nama': 'Lamborghini Revuelto ', 'harga': 10000000, 'tersedia': True},
]

riwayat_transaksi = []

def clear_screen():
    """Membersihkan layar terminal agar rapi"""
    os.system('cls' if os.name == 'nt' else 'clear')

def tampilkan_kendaraan():
    """Menampilkan semua kendaraan dalam bentuk tabel (Coba bagian ini bisa pke pandas ga ya?)"""
    print("\n=== DAFTAR KENDARAAN ===")

    df = pd.DataFrame(inventory)

    df['status'] = df ['tersedia'].apply(lambda x: 'tersedia' if x else 'sedang disewa')

    df['Harga/Hari'] = df['harga'].apply(lambda x: f"Rp {x:,}")

    df_tampil = df[['id','nama','Harga/Hari','status']]
    df_tampil.columns = ['ID','Nama Kendaraan', 'Harga/Hari', 'Status']

    print(df_tampil.to_string(index=False))  
    print("-" * 55)
    
    



def sewa_kendaraan():
    """Logika sewa dengan form pembayaran dan struk"""
    tampilkan_kendaraan()
    try:
        id_sewa = int(input("\nMasukkan ID kendaraan yang ingin disewa: "))
        
        ditemukan = False
        for mobil in inventory:
            if mobil['id'] == id_sewa:
                ditemukan = True
                # cek ketersediaan
                if mobil['tersedia']:
                    print(f"\n--- FORM PEMBAYARAN: {mobil['nama']} ---")
                    # 1. input data penyewa
                    nama_penyewa = input("Nama Penyewa      : ")
                    lama_sewa = int(input("Lama Sewa (hari)  : "))
                    # 2. hitung biaya
                    total_biaya = mobil['harga'] * lama_sewa
                    print(f"Total Biaya       : Rp {total_biaya:,}")
                    # 3. konfirmasi pembayaran
                    # tar disini tambah munculin gambar qris
                    konfirmasi = input("Konfirmasi pembayaran? (y/n): ").lower()
                    
                    if konfirmasi == 'y':
                        # ubah status mobil
                        mobil['tersedia'] = False

                        # 4. buat data struk
                        no_transaksi = len(riwayat_transaksi) + 1
                        struk = {
                            'no_trx': no_transaksi,
                            'tanggal': datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                            'penyewa': nama_penyewa,
                            'mobil': mobil['nama'],
                            'lama': lama_sewa,
                            'total': total_biaya
                        }

                        # 5. simpan ke list riwayat
                        riwayat_transaksi.append(struk)
                        
                        # 6. cetak struk ke layar
                        print("\n" + "="*40)
                        print("          STRUK BUKTI RENTAL")
                        print("="*40)
                        print(f"No Transaksi : #TRX-{struk['no_trx']:03d}")
                        print(f"Tanggal      : {struk['tanggal']}")
                        print(f"Penyewa      : {struk['penyewa']}")
                        print(f"Kendaraan    : {struk['mobil']}")
                        print(f"Durasi       : {struk['lama']} Hari")
                        print("-" * 40)
                        print(f"TOTAL BAYAR  : Rp {struk['total']:,}")
                        print("="*40)
                        print("[SUKSES] Transaksi berhasil disimpan!")
                        
                    else:
                        print("[BATAL] Pembayaran dibatalkan.")
                
                else:
                    print(f"\n[GAGAL] Maaf, {mobil['nama']} sedang disewa orang lain.")
                break
        
        if not ditemukan:
            print("\n[ERROR] ID kendaraan tidak ditemukan.")
            
    except ValueError:
        print("\n[ERROR] Input tidak valid (pastikan angka dimasukkan dengan benar)!")

def lihat_riwayat():
    """Menampilkan daftar riwayat transaksi"""
    print("\n=== RIWAYAT TRANSAKSI ===")
    if not riwayat_transaksi:
        print("Belum ada transaksi yang tercatat.")
    else:
        # header tabel
        # nanti coba yg tabel gtu di ganti pke pandas
        print(f"{'No':<5} {'Tanggal':<18} {'Penyewa':<15} {'Mobil':<15} {'Hari':<15} {'Total (Rp)'}")
        print("-" * 65)
        
        for trx in riwayat_transaksi:
            print(f"#{trx['no_trx']:<4} {trx['tanggal']:<18} {trx['penyewa']:<15} {trx['mobil']:<15} {trx['lama']:<15} {trx['total']:,}")
        print("-" * 65)

def kembalikan_kendaraan():
    """Logika pengembalian dan perhitungan biaya"""
    lihat_riwayat()
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

def main():
    while True:
        print("\n" + "="*25)
        print(" SISTEM RENTAL MOBIL")
        print("="*25)
        print("1. Lihat Daftar Kendaraan")
        print("2. Sewa Kendaraan")
        print("3. Kembalikan Kendaraan")
        print("4. Riwayat Transaksi")
        print("5. Keluar")
        
        pilihan = input("\nPilih menu (1-5): ")
        
        if pilihan == '1':
            clear_screen()
            tampilkan_kendaraan()
        elif pilihan == '2':
            clear_screen()
            sewa_kendaraan()
        elif pilihan == '3':
            kembalikan_kendaraan()
        elif pilihan == '4':
            clear_screen()
            lihat_riwayat()
        elif pilihan == '5':
            print("\nTerima kasih telah menggunakan sistem rental kami!")
            break
        else:
            clear_screen()
            print("\nPilihan tidak valid, silakan coba lagi.")


main()