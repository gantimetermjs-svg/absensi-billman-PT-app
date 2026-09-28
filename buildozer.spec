import base64
import io
import json
import threading
from datetime import datetime

import requests
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.utils import platform
from kivymd.app import MDApp
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from PIL import Image

# GANTI dengan URL Web App Google Apps Script Anda
SCRIPT_URL = "https://script.google.com/macros/s/GANTI_DENGAN_ID_SCRIPT/exec"

# Jika foto tampil miring di Google Sheets, ubah ke 90, 180, atau 270
ROTASI_FOTO = 0

KV = """
MDScreen:
    MDBoxLayout:
        orientation: "vertical"
        padding: dp(12)
        spacing: dp(10)

        MDTopAppBar:
            title: "Absensi Billman"
            elevation: 2

        Camera:
            id: kamera
            resolution: (640, 480)
            play: False
            allow_stretch: True
            keep_ratio: True

        MDLabel:
            id: label_waktu
            text: "Waktu: -"
            size_hint_y: None
            height: dp(24)

        MDLabel:
            id: label_gps
            text: "GPS: mencari lokasi..."
            size_hint_y: None
            height: dp(24)

        MDTextField:
            id: input_nama
            hint_text: "Nama lengkap"
            mode: "rectangle"
            size_hint_y: None
            height: dp(56)

        MDBoxLayout:
            size_hint_y: None
            height: dp(52)
            spacing: dp(10)

            MDRaisedButton:
                text: "AMBIL FOTO"
                size_hint_x: 0.5
                on_release: app.ambil_foto()

            MDRaisedButton:
                id: tombol_kirim
                text: "KIRIM ABSEN"
                size_hint_x: 0.5
                on_release: app.kirim_absen()
"""


class AbsensiApp(MDApp):
    koordinat_gps = None
    foto_base64 = None
    dialog = None

    def build(self):
        self.title = "Absensi Billman"
        self.theme_cls.primary_palette = "Blue"
        return Builder.load_string(KV)

    def on_start(self):
        Clock.schedule_interval(self.update_waktu, 1)
        self.update_waktu(0)

        if platform == "android":
            from android.permissions import Permission, request_permissions

            request_permissions(
                [
                    Permission.CAMERA,
                    Permission.ACCESS_FINE_LOCATION,
                    Permission.ACCESS_COARSE_LOCATION,
                ],
                self.setelah_izin,
            )
        else:
            # Mode pengujian di PC
            self.root.ids.kamera.play = True
            self.koordinat_gps = "-7.5400, 112.5400 (Mode PC)"
            self.root.ids.label_gps.text = f"GPS: {self.koordinat_gps}"

    def on_stop(self):
        if platform == "android":
            try:
                from plyer import gps

                gps.stop()
            except Exception:
                pass

    # ---------------- Izin & GPS ----------------
    def setelah_izin(self, permissions, grants):
        if all(grants):
            self.root.ids.kamera.play = True
            self.mulai_gps()
        else:
            self.tampilkan_dialog(
                "Izin Ditolak",
                "Izin kamera dan lokasi wajib diaktifkan agar bisa absen.",
            )

    def mulai_gps(self):
        try:
            from plyer import gps

            gps.configure(on_location=self.on_location, on_status=self.on_status)
            gps.start(minTime=2000, minDistance=0)
        except NotImplementedError:
            self.root.ids.label_gps.text = "GPS: tidak didukung"
        except Exception as e:
            self.root.ids.label_gps.text = f"GPS error: {e}"

    def on_location(self, **kwargs):
        lat = kwargs.get("lat")
        lon = kwargs.get("lon")
        if lat is None or lon is None:
            return
        self.koordinat_gps = f"{lat:.6f}, {lon:.6f}"
        # Callback plyer berjalan di thread lain, update UI lewat Clock
        Clock.schedule_once(
            lambda dt: setattr(
                self.root.ids.label_gps, "text", f"GPS: {self.koordinat_gps}"
            )
        )

    def on_status(self, stype, status):
        pass

    def deteksi_fake_gps(self):
        """True jika lokasi terakhir berasal dari mock provider (Android)."""
        if platform != "android":
            return False
        try:
            from jnius import autoclass

            PythonActivity = autoclass("org.kivy.android.PythonActivity")
            Context = autoclass("android.content.Context")
            lm = PythonActivity.mActivity.getSystemService(Context.LOCATION_SERVICE)
            for provider in ("gps", "network", "passive"):
                loc = lm.getLastKnownLocation(provider)
                if loc is None:
                    continue
                try:
                    if loc.isFromMockProvider():
                        return True
                except Exception:
                    try:
                        if loc.isMock():
                            return True
                    except Exception:
                        pass
        except Exception:
            pass
        return False

    # ---------------- Waktu ----------------
    def update_waktu(self, dt):
        sekarang = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        self.root.ids.label_waktu.text = f"Waktu: {sekarang}"

    # ---------------- Foto ----------------
    def ambil_foto(self):
        tex = self.root.ids.kamera.texture
        if tex is None:
            self.tampilkan_dialog("Peringatan", "Kamera belum siap.")
            return
        try:
            img = Image.frombytes("RGBA", tex.size, tex.pixels).convert("RGB")
            img = img.transpose(Image.FLIP_TOP_BOTTOM)
            if ROTASI_FOTO:
                img = img.rotate(ROTASI_FOTO, expand=True)
            img.thumbnail((480, 480))
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=65)
            self.foto_base64 = "data:image/jpeg;base64," + base64.b64encode(
                buf.getvalue()
            ).decode("utf-8")
            self.tampilkan_dialog("Sukses", "Foto berhasil diambil!")
        except Exception as e:
            self.tampilkan_dialog("Error", f"Gagal mengambil foto: {e}")

    # ---------------- Kirim ----------------
    def kirim_absen(self):
        nama = self.root.ids.input_nama.text.strip()

        if not nama:
            self.tampilkan_dialog("Peringatan", "Nama wajib diisi!")
            return
        if not self.foto_base64:
            self.tampilkan_dialog("Peringatan", "Harap ambil foto terlebih dahulu!")
            return
        if not self.koordinat_gps:
            self.tampilkan_dialog("Peringatan", "Lokasi belum ditemukan, tunggu sebentar.")
            return
        if self.deteksi_fake_gps():
            self.tampilkan_dialog("Akses Ditolak", "Aplikasi pemalsu lokasi terdeteksi!")
            return

        payload = {
            "nama": nama,
            "waktu": self.root.ids.label_waktu.text.replace("Waktu: ", ""),
            "gps": self.koordinat_gps,
            "foto": self.foto_base64,
        }

        self.root.ids.tombol_kirim.disabled = True
        threading.Thread(target=self._kirim_thread, args=(payload,), daemon=True).start()

    def _kirim_thread(self, payload):
        try:
            resp = requests.post(
                SCRIPT_URL,
                data=json.dumps(payload),
                headers={"Content-Type": "text/plain;charset=utf-8"},
                timeout=30,
            )
            if resp.status_code == 200:
                hasil = ("Berhasil", "Absen Anda telah tersimpan di Google Sheets.")
                self.foto_base64 = None
            else:
                hasil = ("Gagal", f"Terjadi kesalahan pada server ({resp.status_code}).")
        except Exception as e:
            hasil = ("Error", f"Koneksi gagal: {e}")
        Clock.schedule_once(lambda dt: self._selesai_kirim(*hasil))

    def _selesai_kirim(self, judul, pesan):
        self.root.ids.tombol_kirim.disabled = False
        self.tampilkan_dialog(judul, pesan)

    # ---------------- Dialog ----------------
    def tampilkan_dialog(self, judul, pesan):
        if self.dialog:
            self.dialog.dismiss()
        self.dialog = MDDialog(
            title=judul,
            text=pesan,
            buttons=[
                MDFlatButton(text="OK", on_release=lambda x: self.dialog.dismiss())
            ],
        )
        self.dialog.open()


if __name__ == "__main__":
    AbsensiApp().run()
