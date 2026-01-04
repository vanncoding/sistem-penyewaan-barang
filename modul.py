import math

class Garis:
    def __init__(self, x1, y1, x2, y2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

    def hitung_panjang(self):
        """Menghitung jarak antara dua titik (Euclidean Distance)"""
        return math.sqrt((self.x2 - self.x1)**2 + (self.y2 - self.y1)**2)

    def hitung_gradien(self):
        """Menghitung kemiringan garis (m)"""
        try:
            return (self.y2 - self.y1) / (self.x2 - self.x1)
        except ZeroDivisionError:
            return float('inf')  # Garis vertikal tegak lurus

    def info_garis(self):
        return f"Garis dari ({self.x1},{self.y1}) ke ({self.x2},{self.y2})"
    