import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# Konfigurasi halaman
st.set_page_config(page_title="CatatBahan - Online", layout="wide")

st.title("📊 CatatBahan: Manajemen & Kalkulator Bisnis (ONLINE)")
st.write("Aplikasi telah online dan terhubung dengan Google Sheets. Bisa diakses dari perangkat mana pun!")

# Masukkan LINK GOOGLE SHEETS Anda yang sudah disalin di sini
URL_SPREADSHEET = https://docs.google.com/spreadsheets/d/1SxJgaORreVzDi1bW0Fg1iW7h6xNwlDLfLNR3u2DuUB8/edit?usp=sharing
# Membuat koneksi ke Google Sheets
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    # Membaca data terbaru dari Google Sheets
    df_bahan = conn.read(spreadsheet=URL_SPREADSHEET, ttl="0d")
    # Memastikan tipe data benar
    df_bahan['Stok (Unit)'] = pd.to_numeric(df_bahan['Stok (Unit)'], errors='coerce').fillna(0)
    df_bahan['Harga per Unit (Rp)'] = pd.to_numeric(df_bahan['Harga per Unit (Rp)'], errors='coerce').fillna(0)
except Exception as e:
    st.error("Gagal terhubung ke Google Sheets. Pastikan Link benar dan aksesnya sudah diatur ke 'Editor' untuk siapa saja.")
    st.stop()

# Membuat Grid Menu
tab1, tab2 = st.tabs(["📦 Inventaris Bahan", "🧮 Kalkulator Produksi"])

# -------------------------------------------------------------
# TAB 1: INVENTARIS BAHAN
# -------------------------------------------------------------
with tab1:
    st.header("Tambah & Update Stok Bahan")
    
    with st.form("form_bahan"):
        col1, col2, col3 = st.columns(3)
        with col1:
            nama = st.text_input("Nama Bahan Baku").strip()
        with col2:
            stok = st.number_input("Jumlah Stok", min_value=0.0, step=1.0)
        with col3:
            harga = st.number_input("Harga per Unit (Rp)", min_value=0, step=500)
            
        submit_button = st.form_submit_button(label="Simpan ke Cloud")
        
    if submit_button:
        if nama:
            # Salin dataframe untuk dimodifikasi
            df_update = df_bahan.copy()
            
            if nama in df_update['Nama Bahan'].values:
                # Update data lama
                df_update.loc[df_update['Nama Bahan'] == nama, ['Stok (Unit)', 'Harga per Unit (Rp)']] = [stok, harga]
                st.success(f"Data {nama} berhasil diperbarui di Cloud!")
            else:
                # Tambah data baru
                new_row = pd.DataFrame({'Nama Bahan': [nama], 'Stok (Unit)': [stok], 'Harga per Unit (Rp)': [harga]})
                df_update = pd.concat([df_update, new_row], ignore_index=True)
                st.success(f"{nama} berhasil ditambahkan ke Cloud!")
            
            # Kirim data kembali ke Google Sheets
            conn.update(spreadsheet=URL_SPREADSHEET, data=df_update)
            st.rerun()
        else:
            st.warning("Nama bahan tidak boleh kosong.")

    # Menampilkan Tabel Inventaris
    st.subheader("Daftar Stok Saat Ini (Live dari Google Sheets)")
    if not df_bahan.empty:
        st.dataframe(df_bahan, use_container_width=True)
        
        if st.button("Hapus Semua Data"):
            df_kosong = pd.DataFrame(columns=['Nama Bahan', 'Stok (Unit)', 'Harga per Unit (Rp)'])
            conn.update(spreadsheet=URL_SPREADSHEET, data=df_kosong)
            st.success("Semua data di Cloud telah dihapus.")
            st.rerun()
    else:
        st.info("Belum ada bahan baku yang tercatat di Google Sheets.")

# -------------------------------------------------------------
# TAB 2: KALKULATOR PRODUKSI
# -------------------------------------------------------------
with tab2:
    st.header("Hitung Kebutuhan Produksi")
    
    if df_bahan.empty:
        st.warning("Silakan isi data bahan baku terlebih dahulu di tab 'Inventaris Bahan'.")
    else:
        st.write("Pilih bahan dan masukkan jumlah yang dibutuhkan:")
        bahan_terpilih = st.multiselect("Pilih Bahan Baku:", df_bahan['Nama Bahan'].tolist())
        
        if bahan_terpilih:
            total_biaya_produksi = 0
            list_kebutuhan = []
            
            for bahan in bahan_terpilih:
                row_bahan = df_bahan[df_bahan['Nama Bahan'] == bahan].iloc[0]
                harga_satuan = row_bahan['Harga per Unit (Rp)']
                stok_ada = row_bahan['Stok (Unit)']
                
                col_b1, col_b2 = st.columns([2, 1])
                with col_b1:
                    jumlah_butuh = st.number_input(f"Jumlah {bahan} yang dibutuhkan (Stok: {stok_ada}):", min_value=0.0, step=1.0, key=f"req_{bahan}")
                
                subtotal = jumlah_butuh * harga_satuan
                total_biaya_produksi += subtotal
                status_stok = "✅ Cukup" if stok_ada >= jumlah_butuh else "❌ Kurang!"
                
                list_kebutuhan.append({
                    "Bahan": bahan,
                    "Dibutuhkan": jumlah_butuh,
                    "Subtotal (Rp)": subtotal,
                    "Status Stok": status_stok
                })
            
            st.write("---")
            st.subheader("Ringkasan Biaya Kebutuhan")
            st.table(pd.DataFrame(list_kebutuhan))
            st.metric(label="Total Estimasi Biaya Produksi", value=f"Rp {total_biaya_produksi:,.0f}")
