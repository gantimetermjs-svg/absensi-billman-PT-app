# (Pada aplikasi produksi, dipadukan dengan LocationManager Android)
            self.koordinat_gps = "-7.5400, 112.5400" 
            self.root.ids.label_gps.text = f"GPS: {self.koordinat_gps}"
        else:
            # Mode Pengujian di PC Laptop
            self.koordinat_gps = "-7.5400, 112.5400 (Mode PC)"
            self.root.ids.label_gps.text = f"GPS: {self.koordinat_gps}"

    def ambil_foto(self):
        if hasattr(self, 'current_frame'):
            # Encoding gambar ke format JPG base64 untuk dikirim ke Google Sheets
            _, buffer = cv2.imencode('.jpg', self.current_frame)
            import base64
            self.foto_base64 = "data:image/jpeg;base64," + base64.b64encode(buffer).decode('utf-8')
            self.tampilkan_dialog("Sukses", "Foto berhasil diambil!")

    def kirim_absen(self):
        nama = self.root.ids.input_nama.text.strip()
        
        if not nama:
            self.tampilkan_dialog("Peringatan", "Nama wajib diisi!")
            return
        if not self.foto_base64:
            self.tampilkan_dialog("Peringatan", "Harap ambil foto terlebih dahulu!")
            return
        if self.is_fake_gps:
            self.tampilkan_dialog("Akses Ditolak", "Aplikasi pemalsu lokasi terdeteksi!")
            return

        payload = {
            "nama": nama,
            "waktu": self.root.ids.label_waktu.text.replace("Waktu: ", ""),
            "gps": self.koordinat_gps,
            "foto": self.foto_base64
        }

        try:
            response = requests.post(SCRIPT_URL, data=json.dumps(payload), timeout=10)
            if response.status_code == 200:
                self.tampilkan_dialog("Berhasil", "Absen Anda telah tersimpan di Google Sheets.")
            else:
                self.tampilkan_dialog("Gagal", "Terjadi kesalahan pada server.")
        except Exception as e:
            self.tampilkan_dialog("Error", f"Koneksi gagal: {str(e)}")

    def tampilkan_dialog(self, judul, pesan):
        dialog = MDDialog(
            title=judul,
            text=pesan,
            buttons=[MDFlatButton(text="OK", on_release=lambda x: dialog.dismiss())]
        )
        dialog.open()

if name == 'main':
    AbsensiApp().run() 