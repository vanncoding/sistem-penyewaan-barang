import os
import datetime
import pandas as pd
import modul
from diskon_service import hitung_diskon
from PIL import Image

#tugas zuqy (buat modul buat import)
#isi modul nya (1. modul garis, 2. modul variabel diskon)

inventory = [
    {'id': 1, 'nama': 'Toyota Avanza', 'harga': 300000, 'tersedia': True},
    {'id': 2, 'nama': 'Honda Brio',    'harga': 250000, 'tersedia': True},
    {'id': 3, 'nama': 'Toyota Innova', 'harga': 500000, 'tersedia': True},
    {'id': 4, 'nama': 'Mitsubishi Pajero', 'harga': 800000, 'tersedia': True},
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

#ini tugas dapa/ismet (ubah tabel pakai pandas)
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
    
    


#ini tugas revan (munculin qris sebelum verifikasi, abis muncul qris muncul format konfirmasi kirim email, setelah kirim email muncul konfirmasi)
def tampilkan_link_dan_buka(text, url):
    """nampilin link"""
    print(f"\n{text}")
    print(f"Link: {url}")
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
                   # 2. hitung biaya awal
                    biaya_dasar = mobil['harga'] * lama_sewa
                    
                    # HITUNG DISKON MENGGUNAKAN MODUL
                    potongan, persen = hitung_diskon(biaya_dasar, lama_sewa)
                    total_biaya = biaya_dasar - potongan

                    print(f"Harga Dasar     : Rp {biaya_dasar:,}")
                    print(f"Diskon ({persen}%): -Rp {potongan:,}")
                    print(f"Total Bayar      : Rp {total_biaya:,}")

                    #tambahin qris nih disini
                    input("\nSetelah Muncul Qris Silahkan Bayar Sesuai Nominal💸💰!!! \nTekan Tombol Enter Untuk Bayar..... !!")

                    try :
                        qris = r"C:\Users\VANN\Desktop\belajar python\sistem-penyewaan-barang\qris.jpg"
                        img=Image.open(qris)
                        img.show()
                        print("\nQris Berhasil Ditampilkan✅\nSilahkan ScreenShot Bukti Pembayaran📷💰 dan Isi Form di WhatsApp✍ 💌")
                    except FileNotFoundError:
                        print(f"❌ ERROR : File {qris}\n Tidak Ditemukan!!")
                    except Exception as e :
                        print(f"ERROR : {e}")
                    
                    #disini buat otomatis ngisi form di wa gezzzz
                    # 🆕 OTOMATIS ISI FORM WHATSAPP
                    print("\n" + "="*60)
                    print("📱 KIRIM BUKTI PEMBAYARAN VIA WHATSAPP")
                    print("="*60)
                    
                    input("\nTekan ENTER untuk membuka WhatsApp dan isi form konfirmasi...")
                    
                    # Buat pesan WhatsApp otomatis
                    nomor_wa = "6285773840478"  
                    
                    pesan = f"""Halo Admin Rental Mobil! 

Saya ingin mengkonfirmasi pembayaran sewa kendaraan:

━━━━━━━━━━━━━━━━━━━━━━━━
 DATA TRANSAKSI
━━━━━━━━━━━━━━━━━━━━━━━━
 Nama Penyewa    : {nama_penyewa}
 Kendaraan       : {mobil['nama']}
 ID Kendaraan    : {mobil['id']}
 Lama Sewa       : {lama_sewa} Hari
 Total Bayar     : Rp {total_biaya:,}
 Tanggal Booking : {datetime.datetime.now().strftime("%d %B %Y, %H:%M")}
━━━━━━━━━━━━━━━━━━━━━━━━

Mohon cek pembayaran saya dan konfirmasi booking. Terima kasih! 🙏"""
                    
                    # pesan buat URL
                    import urllib.parse
                    pesan_encoded = urllib.parse.quote(pesan)
                    
                    # Buat link WhatsApp
                    wa_link = f"https://wa.me/{nomor_wa}?text={pesan_encoded}"
                    
                    # Buka WhatsApp otomatis
                    import webbrowser
                    print("\n🌐 Membuka WhatsApp...")
                    webbrowser.open(wa_link)
                    print("✓ WhatsApp berhasil dibuka!")
                    print("\n📸 Jangan lupa kirim screenshot bukti pembayaran!")
                    
                    print("="*60)

                    # 3. konfirmasi pembayaran
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
                            'id_mobil': mobil['id'], #tambah id mobil
                            'lama': lama_sewa,
                            'total': total_biaya,
                            'status_rental': 'aktif' #penanda mobil masih di sewa
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
                        print(f"Kendaraan    : {struk['id_mobil']}")
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
        print(f"{'No':<5} {'Tanggal':<18} {'Penyewa':<15} {'Mobil':<15} {'ID Mobil':<15} {'Hari':<15} {'Total (Rp)':<15} {'Status'}")
        print("-" * 85)
        
        for trx in riwayat_transaksi:
            print(f"#{trx['no_trx']:<4} {trx['tanggal']:<18} {trx['penyewa']:<15} {trx['mobil']:<15} {trx['id_mobil']:<15} {trx['lama']:<15} {trx['total']:<15} {trx['status_rental']}")
        print("-" * 85)

#ini tugas fathir (ubah pengembalian)
def kembalikan_kendaraan():
    print("\n=== PENGEMBALIAN KENDARAAN ===")
    # 1. Tampilkan mobil yang sedang disewa saja untuk memudahkan
    print(f"{'ID':<5} {'Nama Kendaraan':<20} {'Status'}")
    print("-" * 40)
    for m in inventory:
        if not m['tersedia']: # Hanya tampilkan yang sedang disewa
            print(f"{m['id']:<5} {m['nama']:<20} Sedang Disewa")
    print("-" * 40)
    
    try:
        # INPUT ID KENDARAAN
        id_kembali = int(input("Masukkan ID kendaraan yang dikembalikan: "))
        
        # Cari data kendaraan
        mobil_target = None
        for mobil in inventory:
            if mobil['id'] == id_kembali:
                mobil_target = mobil
                break
        
        if not mobil_target:
            print("[ERROR] ID Kendaraan tidak ditemukan.")
            return

        # Cek apakah mobil memang sedang disewa
        if mobil_target['tersedia']:
            print("[INFO] Mobil ini statusnya masih tersedia di garasi (belum disewa).")
            return

        # --- LOGIKA OTOMATIS MENCARI DATA TRANSAKSI ---
        # cari di riwayat Transaksi yang id mobilnya cocok dan statusnya masih 'aktif'
        transaksi_aktif = None
        for trx in riwayat_transaksi:
            if trx['id_mobil'] == id_kembali and trx['status_rental'] == 'aktif':
                transaksi_aktif = trx
                break
        
        if not transaksi_aktif:
            print("[ERROR] Data transaksi aktif tidak ditemukan (Mungkin sistem error).")
            return

        # --- TAMPILKAN DATA SEWA ---
        print("\n" + "="*40)
        print("DATA PENYEWA DITEMUKAN")
        print("="*40)
        print(f"Penyewa       : {transaksi_aktif['penyewa']}")
        print(f"Kendaraan     : {transaksi_aktif['mobil']}")
        print(f"Lama Sewa     : {transaksi_aktif['lama']} hari")
        print(f"Total Awal    : Rp {transaksi_aktif['total']:,}")
        print("-" * 40)

        # --- INPUT KETERLAMBATAN & HITUNG DENDA ---
        telat = int(input("Keterlambatan (hari, tulis 0 jika tepat waktu): "))
        
        denda = 0
        if telat > 0:
            # Denda 10% dari total biaya per hari telat
            denda_per_hari = 0.10 * transaksi_aktif['total']
            denda = denda_per_hari * telat
            print(f"\n[INFO] Terlambat {telat} hari.")
            print(f"Denda (10% x Total x Hari): Rp {denda:,.0f}")
        else:
            print("\n[INFO] Pengembalian tepat waktu. Tidak ada denda.")

        total_akhir = transaksi_aktif['total'] + denda

        print("=" * 40)
        print(f"TOTAL YANG HARUS DIBAYAR: Rp {total_akhir:,.0f}")
        print("=" * 40)

        # --- KONFIRMASI AKHIR ---
        konfirmasi = input("\nProses pengembalian & pembayaran? (y/n): ").lower()
        
        if konfirmasi == 'y':
            # 1. Update status mobil jadi tersedia
            mobil_target['tersedia'] = True
            
            # 2. Update status transaksi jadi selesai (biar tidak muncul lagi nanti)
            transaksi_aktif['status_rental'] = 'selesai'
            # Kita juga bisa simpan info denda ke riwayat jika mau
            transaksi_aktif['denda_akhir'] = denda
            transaksi_aktif['total_akhir'] = total_akhir
            
            print("\n[SUKSES] Mobil telah dikembalikan dan status menjadi TERSEDIA.")
        else:
            print("\n[BATAL] Pengembalian dibatalkan.")

    except ValueError:
        print("\n[ERROR] Masukkan angka yang valid!")

def main():
    while True:
        print ()
        print("𝐖𝐄𝐋𝐂𝐎𝐌𝐄")
        print("="*25)
        print("SISTEM RENTAL MOBIL")
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