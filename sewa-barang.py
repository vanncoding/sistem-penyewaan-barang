kendaraan = []

print ("1. Sewa Kendaraan")
print ("2. List Kendaraan")
print ("4. Exit")
print ("=" * 20)
pilih_menu = int(input("Masukan Menu :"))

if pilih_menu == 1:
    print("1. Totoyota")
    print("2. BMW")
    print("3. Daihatsu")
    kode = int(input("Masukan Kode Kendaraan: "))
    if kode == 1:
        print("1. Avanza")
        print("2. Inova")
        print("3. Calya")
        print("4. Agya")
        print("=" * 20)
        kode_toyota = int(input("Masukan No Sewa :"))
    else :
        print("KODE YANG ANDA MASUKAN SALAH")
else:
    print("Masukan Kode :")