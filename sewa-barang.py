import json
import time
import re
import urllib.request
import urllib.error
import uuid
import os
from datetime import datetime
from zoneinfo import ZoneInfo
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import chromedriver_autoinstaller

DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1552880010107559956/ZoQc5fW9HaJixABKeb9Lb8TwztGiN2qiVEe7ABaTp411KFVr-dOImDTxH-7X7p3Cuwb5"

# Gambar status: taruh file-nya di folder assets/status/
GAMBAR_STATUS = {
    "berhasil": "assets/status/berhasil.png",
    "sudah_absen": "assets/status/sudah_absen.png",
    "belum_waktunya": "assets/status/belum_waktunya.png",
    "tidak_terverifikasi": "assets/status/tidak_terverifikasi.png",
    "gagal": "assets/status/gagal.png",
}

LABEL_STATUS = {
    "berhasil": "✅ Absen Berhasil",
    "sudah_absen": "✅ Sudah Absen Sebelumnya",
    "belum_waktunya": "⏳ Belum Waktunya",
    "tidak_terverifikasi": "⚠️ Tidak Terverifikasi",
    "gagal": "❌ Absen Gagal",
}

PRIORITAS_STATUS = ["berhasil", "sudah_absen", "tidak_terverifikasi", "belum_waktunya", "gagal"]
STATUS_KURANG_MULUS = ["tidak_terverifikasi", "belum_waktunya", "gagal"]

WIB = ZoneInfo("Asia/Jakarta")

SCREENSHOTS = {}  # {nama_akun: path_file_screenshot}

def log_proses(pesan):
    waktu = datetime.now(WIB).strftime("%H:%M:%S")
    print(f"[{waktu}] {pesan}", flush=True)

def load_config():
    with open('src/config.json', 'r') as f:
        return json.load(f)

def get_day_name():
    return datetime.now(WIB).strftime('%A').lower()

def kirim_discord(pesan):
    """Kirim pesan teks ke Discord lewat webhook."""
    try:
        data = json.dumps({"content": pesan}).encode('utf-8')
        req = urllib.request.Request(
            DISCORD_WEBHOOK_URL,
            data=data,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            },
            method="POST"
        )
        urllib.request.urlopen(req, timeout=15)
        log_proses("📨 Notifikasi Discord terkirim.")
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8', errors='ignore')
        log_proses(f"⚠️ Gagal mengirim notifikasi Discord: HTTP {e.code} - {body}")
    except Exception as e:
        log_proses(f"⚠️ Gagal mengirim notifikasi Discord: {e}")

def kirim_discord_file(pesan, path_file):
    """Kirim pesan + 1 file gambar ke Discord lewat webhook (multipart/form-data)."""
    try:
        boundary = uuid.uuid4().hex
        nama_file = os.path.basename(path_file)
        with open(path_file, "rb") as f:
            isi_file = f.read()

        payload_json = json.dumps({"content": pesan}).encode("utf-8")
        crlf = b"\r\n"
        body = b""
        body += f"--{boundary}".encode() + crlf
        body += b'Content-Disposition: form-data; name="payload_json"' + crlf
        body += b"Content-Type: application/json" + crlf + crlf
        body += payload_json + crlf
        body += f"--{boundary}".encode() + crlf
        body += f'Content-Disposition: form-data; name="files[0]"; filename="{nama_file}"'.encode() + crlf
        body += b"Content-Type: image/png" + crlf + crlf
        body += isi_file + crlf
        body += f"--{boundary}--".encode() + crlf

        req = urllib.request.Request(
            DISCORD_WEBHOOK_URL,
            data=body,
            headers={
                "Content-Type": f"multipart/form-data; boundary={boundary}",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            },
            method="POST"
        )
        urllib.request.urlopen(req, timeout=30)
        log_proses(f"📨 File terkirim ke Discord: {nama_file}")
    except urllib.error.HTTPError as e:
        body_err = e.read().decode('utf-8', errors='ignore')
        log_proses(f"⚠️ Gagal mengirim file ke Discord: HTTP {e.code} - {body_err}")
    except Exception as e:
        log_proses(f"⚠️ Gagal mengirim file ke Discord: {e}")

def kirim_gambar_status_gabungan(semua_hasil):
    """Kirim SATU gambar sticker mewakili SEMUA hasil (semua kelas, semua akun)
    di run ini. Gambar dipilih dari status yang paling banyak terjadi across
    seluruh baris hasil. Status 'kurang mulus' (gagal/belum_waktunya/
    tidak_terverifikasi) -- baik minoritas maupun mayoritas -- selalu
    disebutkan sebagai baris "YAHH TAPI (status) (jumlah) BOSKYUH"."""
    counts = {}
    detail = {}  # status -> [(nama_akun, kelas), ...]
    for nama_akun, daftar_kelas in semua_hasil.items():
        for item in daftar_kelas:
            st = item["status"]
            counts[st] = counts.get(st, 0) + 1
            detail.setdefault(st, []).append((nama_akun, item["kelas"]))

    if not counts:
        log_proses("⚠️ Tidak ada hasil sama sekali untuk dikirim gambar status gabungan.")
        return

    def urutan(st):
        return PRIORITAS_STATUS.index(st) if st in PRIORITAS_STATUS else 99

    status_mayoritas = max(counts.items(), key=lambda kv: (kv[1], -urutan(kv[0])))[0]

    path_gambar = GAMBAR_STATUS.get(status_mayoritas)
    if not path_gambar or not os.path.exists(path_gambar):
        log_proses(f"⚠️ Gambar status untuk '{status_mayoritas}' tidak ditemukan ({path_gambar}), lewati kirim gambar gabungan.")
        return

    baris = [LABEL_STATUS.get(status_mayoritas, status_mayoritas)]
    for st in STATUS_KURANG_MULUS:
        if st in counts:
            label_upper = LABEL_STATUS.get(st, st).split(" ", 1)[-1].upper()
            baris.append(f"YAHH TAPI {label_upper} {counts[st]} BOSKYUH")
            for nama_akun, kelas in detail[st]:
                baris.append(f"  • {nama_akun} — `{kelas}`")

    caption = "\n".join(baris)
    kirim_discord_file(caption, path_gambar)


def ambil_screenshot(driver, nama_akun):
    """Ambil screenshot halaman terakhir milik satu akun (full page, tinggi dibatasi)."""
    try:
        tinggi = driver.execute_script(
            "return Math.max(document.body.scrollHeight, document.documentElement.scrollHeight);"
        )
        driver.set_window_size(1280, min(max(int(tinggi), 800), 3000))
        time.sleep(1)
        nama_aman = re.sub(r'[^A-Za-z0-9_-]+', '_', nama_akun).strip('_') or "akun"
        path = f"ss_{nama_aman}.png"
        driver.save_screenshot(path)
        SCREENSHOTS[nama_akun] = path
        log_proses(f"📸 Screenshot akun disimpan: {path}")
    except Exception as e:
        log_proses(f"⚠️ Gagal mengambil screenshot akun {nama_akun}: {e}")

def solve_captcha(driver):
    """Cari pertanyaan captcha, ekstrak angka & operator, hitung hasilnya."""
    captcha_selectors = [
        "label[for='captcha']",
        ".captcha-text",
        ".verifikasi-text",
        "label:contains('hasil')",
        "//label[contains(text(),'hasil')]",
        "//p[contains(text(),'hasil')]",
        "//div[contains(text(),'hasil')]",
        "//span[contains(text(),'hasil')]"
    ]
    question_text = None
    for sel in captcha_selectors:
        try:
            if sel.startswith('//'):
                elem = driver.find_element(By.XPATH, sel)
            else:
                elem = driver.find_element(By.CSS_SELECTOR, sel)
            question_text = elem.text.strip()
            if question_text:
                break
        except:
            continue

    if not question_text:
        page_text = driver.page_source
        match = re.search(r'hasil dari\s*([\d\s\+\-\*\/]+)\s*\?', page_text, re.IGNORECASE)
        if match:
            question_text = match.group(0)
        else:
            match = re.search(r'(\d+)\s*([+\-*/])\s*(\d+)\s*=\s*\?', page_text)
            if match:
                question_text = match.group(0)
            else:
                return None

    log_proses(f"🧮 Pertanyaan captcha: {question_text}")

    match = re.search(r'(\d+)\s*([+\-*/])\s*(\d+)', question_text)
    if not match:
        numbers = re.findall(r'\d+', question_text)
        if len(numbers) >= 2:
            a = int(numbers[0])
            b = int(numbers[1])
            op_match = re.search(r'[+\-*/]', question_text)
            op = op_match.group(0) if op_match else '+'
        else:
            return None
    else:
        a = int(match.group(1))
        op = match.group(2)
        b = int(match.group(3))

    if op == '+':
        result = a + b
    elif op == '-':
        result = a - b
    elif op == '*':
        result = a * b
    elif op == '/':
        result = a // b if b != 0 else 0
    else:
        result = a + b

    log_proses(f"✅ Jawaban captcha: {result}")
    return str(result)


def buat_browser():
    log_proses("⚙️ Menyiapkan browser (Headless Chrome)...")
    chromedriver_autoinstaller.install()
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36')
    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 15)
    return driver, wait


def run_for_account(account, classes, config):
    """Jalankan proses login + absen untuk SATU akun.
    Return: list of dict {kelas, status, alasan} untuk direkap ke Discord.
    """
    nama_akun = account.get('name', account.get('username', 'Akun'))
    log_proses(f"\n=========== 👤 Memproses akun: {nama_akun} ===========")

    hasil_akun = []  # rekap semua kelas untuk akun ini

    driver, wait = buat_browser()

    try:
        # --- LOGIN ---
        login_url = config.get('login_url', 'http://elearning.bsi.ac.id/login')
        log_proses(f"🔑 Membuka halaman login: {login_url}")
        driver.get(login_url)
        time.sleep(3)

        # Username
        try:
            username_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, config['login_locator']['username_input'])))
            username_input.clear()
            username_input.send_keys(account['username'])
            log_proses("✅ Username diisi")
        except Exception as e:
            log_proses(f"❌ Gagal menemukan input username: {e}")
            hasil_akun.append({"kelas": "-", "status": "gagal", "alasan": "Gagal menemukan input username"})
            return hasil_akun

        # Password
        try:
            password_input = driver.find_element(By.CSS_SELECTOR, config['login_locator']['password_input'])
            password_input.clear()
            password_input.send_keys(account['password'])
            log_proses("✅ Password diisi")
        except Exception as e:
            log_proses(f"❌ Gagal menemukan input password: {e}")
            hasil_akun.append({"kelas": "-", "status": "gagal", "alasan": "Gagal menemukan input password"})
            return hasil_akun

        # CAPTCHA
        captcha_answer = solve_captcha(driver)
        if captcha_answer is None:
            log_proses("⚠️ Gagal membaca captcha. Mungkin tidak ada captcha, lanjutkan...")
        else:
            captcha_input = None
            captcha_selectors = [
                "input[name='captcha']",
                "input[name='captcha_answer']",
                "input[name='verifikasi']",
                "input[id='captcha']",
                "input[id='captcha_answer']",
                "input[id='verifikasi']",
                "input[placeholder*='jawaban' i]",
                "input[placeholder*='verifikasi' i]",
                "input[type='text']:not([name='username']):not([name='password'])"
            ]
            for sel in captcha_selectors:
                try:
                    captcha_input = driver.find_element(By.CSS_SELECTOR, sel)
                    break
                except:
                    continue
            if captcha_input:
                captcha_input.clear()
                captcha_input.send_keys(captcha_answer)
                driver.execute_script("arguments[0].dispatchEvent(new Event('input'));", captcha_input)
                driver.execute_script("arguments[0].dispatchEvent(new Event('change'));", captcha_input)
                time.sleep(1)
                log_proses("✅ Jawaban captcha diisi dan divalidasi")
            else:
                log_proses("❌ Tidak menemukan input untuk captcha")

        # Submit login
        try:
            log_proses("🔄 Mengirimkan data login ke server...")
            login_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            driver.execute_script("arguments[0].click();", login_btn)
            log_proses("✅ Tombol login diklik via JavaScript")
        except Exception as e:
            log_proses(f"❌ Gagal mengeklik tombol login: {e}")
            hasil_akun.append({"kelas": "-", "status": "gagal", "alasan": "Gagal mengeklik tombol login"})
            return hasil_akun

        time.sleep(8)
        log_proses(f"📍 URL setelah login: {driver.current_url}")

        if "login" in driver.current_url.lower():
            log_proses("❌ Login gagal, masih di halaman login.")
            error_msg_text = "Tidak diketahui (tidak ada pesan error di halaman)"
            try:
                error_msg_text = driver.find_element(By.CSS_SELECTOR, ".alert, .invalid-feedback, .error, .text-danger").text
                log_proses(f"📩 Pesan error dari server: {error_msg_text}")
            except:
                log_proses("⚠️ Tidak ditemukan elemen pesan error di halaman.")
            driver.save_screenshot(f"login_failed_{nama_akun}.png")
            log_proses(f"📸 Screenshot: login_failed_{nama_akun}.png")
            with open(f"login_failed_{nama_akun}.html", "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            hasil_akun.append({"kelas": "-", "status": "gagal", "alasan": f"Login gagal: {error_msg_text}"})
            return hasil_akun

        log_proses("🎉 Login berhasil.")

        # --- ABSEN ---
        for cls in classes:
            name = cls.get('name', 'Unknown')
            link = cls.get('link', '')

            if isinstance(name, list) and isinstance(link, list):
                if len(name) != len(link):
                    log_proses(f"⚠️ Jumlah nama ({len(name)}) tidak sama dengan jumlah link ({len(link)}), skip.")
                    continue
                for i in range(len(name)):
                    nama_single = name[i]
                    link_single = link[i]
                    log_proses(f"\n📘 Mengakses Kelas: {nama_single}")
                    log_proses(f"🔗 Buka link: {link_single}")
                    driver.get(link_single)
                    time.sleep(3)
                    status, alasan = proses_absen(driver, wait, config, f"{nama_akun}_{nama_single}")
                    hasil_akun.append({"kelas": nama_single, "status": status, "alasan": alasan})
            else:
                log_proses(f"\n📘 Mengakses Kelas: {name}")
                log_proses(f"🔗 Buka link: {link}")
                driver.get(link)
                time.sleep(3)
                status, alasan = proses_absen(driver, wait, config, f"{nama_akun}_{name}")
                hasil_akun.append({"kelas": name, "status": status, "alasan": alasan})

        log_proses(f"🎯 Selesai untuk akun: {nama_akun}")

    except Exception as e:
        log_proses(f"❌ Error umum untuk akun {nama_akun}: {e}")
        driver.save_screenshot(f"error_{nama_akun}.png")
        hasil_akun.append({"kelas": "-", "status": "gagal", "alasan": f"Error umum: {e}"})
    finally:
        ambil_screenshot(driver, nama_akun)
        log_proses(f"🔌 Menutup browser untuk akun: {nama_akun}")
        driver.quit()

    return hasil_akun


def main():
    config = load_config()
    timetable = config.get('timetable', {})
    today = get_day_name()

    hari_indonesia = {
        'monday': 'Senin', 'tuesday': 'Selasa', 'wednesday': 'Rabu',
        'thursday': 'Kamis', 'friday': 'Jumat', 'saturday': 'Sabtu',
        'sunday': 'Minggu'
    }
    nama_hari = hari_indonesia.get(today, today)
    log_proses(f"📅 Hari ini: {nama_hari}")

    if today not in timetable:
        log_proses("ℹ️ Tidak ada jadwal hari ini.")
        kirim_discord(f"ℹ️ **{nama_hari}** — Tidak ada jadwal absen hari ini.")
        return

    entry = timetable[today]
    if isinstance(entry, dict):
        classes = [entry]
    elif isinstance(entry, list):
        classes = entry
    else:
        log_proses("❌ Format jadwal tidak dikenali.")
        return

    # Dukung config lama (single akun) & config baru (banyak akun)
    accounts = config.get('accounts')
    if not accounts:
        accounts = [{
            "name": config.get('username', 'Akun'),
            "username": config.get('username'),
            "password": config.get('password')
        }]

    semua_hasil = {}  # {nama_akun: [ {kelas, status, alasan}, ... ]}
    for account in accounts:
        nama_akun = account.get('name', account.get('username', 'Akun'))
        semua_hasil[nama_akun] = run_for_account(account, classes, config)

    log_proses("\n🎯🎯 SEMUA AKUN SELESAI DIPROSES 🎯🎯")

    # --- Bangun rekap & kirim ke Discord ---
    waktu_sekarang = datetime.now(WIB).strftime("%d %b %Y, %H:%M")
    baris = [f"📋 **Rekap Absen Otomatis** — {nama_hari}, {waktu_sekarang}"]

    for nama_akun, daftar_kelas in semua_hasil.items():
        baris.append(f"\n**{nama_akun}**")
        if not daftar_kelas:
            baris.append("  ⚠️ Tidak ada data (kemungkinan tidak ada jadwal / error sebelum absen)")
            continue
        garis = "-" * 61
        for no, item in enumerate(daftar_kelas, start=1):
            kelas = item["kelas"]
            status = item["status"]
            alasan = item["alasan"]
            if status == "berhasil":
                baris.append(f"  **{no}.** ✅ **`{kelas}`** — *Berhasil absen*")
            elif status == "sudah_absen":
                baris.append(f"  **{no}.** ✅ **`{kelas}`** — *Sudah absen sebelumnya*")
            elif status == "belum_waktunya":
                baris.append(f"  **{no}.** ⏳ **`{kelas}`** — *{alasan}*")
            elif status == "tidak_terverifikasi":
                baris.append(f"  **{no}.** ⚠️ **`{kelas}`** — Klik terkirim tapi TIDAK terverifikasi. Alasan: *{alasan}*")
            else:  # gagal
                baris.append(f"  **{no}.** ❌ **`{kelas}`** — Gagal. Alasan: *{alasan}*")
            if no < len(daftar_kelas):
                baris.append(garis)

    pesan_akhir = "\n".join(baris)
    kirim_discord(pesan_akhir)

    # --- Kirim screenshot tiap akun (urut sesuai daftar akun) ---
    for nama_akun in semua_hasil.keys():
        path_ss = SCREENSHOTS.get(nama_akun)
        if path_ss and os.path.exists(path_ss):
            time.sleep(1)  # jeda kecil biar tidak kena rate limit webhook
            kirim_discord_file(f"📸 **Screenshot akun {nama_akun}**", path_ss)
        else:
            log_proses(f"⚠️ Tidak ada screenshot untuk akun {nama_akun}")

    # --- Kirim SATU gambar status gabungan (dari semua kelas semua akun) ---
    time.sleep(1)
    kirim_gambar_status_gabungan(semua_hasil)


def proses_absen(driver, wait, config, nama_kelas):
    """Fungsi untuk menangani absen satu kelas (dipanggil per link).
    Return: (status, alasan)
    status salah satu dari: 'sudah_absen', 'belum_waktunya', 'berhasil',
                            'tidak_terverifikasi', 'gagal'
    """
    try:
        page_text = driver.page_source.lower()

        if 'action="/komentar-mhs"' in page_text or "berikan komentar anda" in page_text:
            log_proses("✅ Status: Anda SUDAH ABSEN di kelas ini (Form komentar/rating ditemukan).")
            return "sudah_absen", "Form komentar/rating sudah muncul sebelum diproses"

        elif "sudah selesai" in page_text:
            log_proses("⏳ Status: Waktu kelas Sudah Selesai, tidak bisa absen.")
            return "belum_waktunya", "Waktu kelas sudah selesai"
        elif "belum mulai" in page_text:
            log_proses("⏳ Status: Kelas Belum Mulai, belum waktunya absen.")
            return "belum_waktunya", "Kelas belum mulai"

        else:
            log_proses("🔍 Mencari tombol absen...")
            clicked = False
            try:
                try:
                    attend_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Absen Masuk')]")))
                except:
                    attend_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Absen')]")))
                attend_btn.click()
                log_proses("🖱️ Tombol 'Absen' utama diklik, memverifikasi...")
                clicked = True
            except Exception as e:
                log_proses("⚠️ Tombol absen teks tidak ditemukan, mencoba metode locator cadangan...")
                try:
                    attend_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, config['attend_locator']['ready'])))
                    attend_btn.click()
                    log_proses("🖱️ Tombol absen (locator ready) diklik, memverifikasi...")
                    clicked = True
                except:
                    try:
                        attend_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, config['attend_locator']['not_ready'])))
                        attend_btn.click()
                        log_proses("🖱️ Tombol absen (locator not_ready) diklik, memverifikasi...")
                        clicked = True
                    except Exception as e2:
                        log_proses("❌ Gagal menemukan semua jenis tombol absen.")
                        driver.save_screenshot(f"screenshot_{nama_kelas}.png")
                        log_proses(f"📸 Screenshot tersimpan: screenshot_{nama_kelas}.png")

            if not clicked:
                return "gagal", "Tidak menemukan tombol absen jenis apapun"

            # --- VERIFIKASI ULANG: pastikan status BENAR-BENAR berubah ---
            time.sleep(3)
            driver.refresh()
            time.sleep(3)
            page_text_after = driver.page_source.lower()
            if 'action="/komentar-mhs"' in page_text_after or "berikan komentar anda" in page_text_after:
                log_proses("✅ TERVERIFIKASI: Absen berhasil tercatat di server.")
                return "berhasil", "Terverifikasi setelah refresh"
            else:
                log_proses("⚠️ PERINGATAN: Tombol sempat diklik, TAPI status belum berubah jadi 'sudah absen' setelah refresh.")
                log_proses("⚠️ Kemungkinan penyebab: sesi akun sedang dipakai login manual di tempat lain (single-session), atau klik mengenai tombol yang salah.")
                driver.save_screenshot(f"unverified_{nama_kelas}.png")
                log_proses(f"📸 Screenshot kondisi setelah klik: unverified_{nama_kelas}.png")
                return "tidak_terverifikasi", "Status belum berubah setelah refresh (kemungkinan sesi bentrok / tombol salah)"

    except Exception as e:
        log_proses(f"❌ Error saat memproses halaman absen {nama_kelas}: {e}")
        return "gagal", f"Error: {e}"


if __name__ == '__main__':
    main()
