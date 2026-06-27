import streamlit as st
import pandas as pd
from datetime import datetime

# 1. Konfigurasi Halaman
st.set_page_config(
    page_title="CatatBahan & Penjualan PRO", 
    page_icon="📦",
    layout="wide"
)

# ID Spreadsheet Anda diambil langsung dari link Anda
SPREADSHEET_ID = "1SxJgaORreVzDi1bW0Fg1iW7h6xNwlDLfLNR3u2DuUB8"

# Mengonversi link menjadi format export CSV langsung yang sangat stabil untuk dibaca Streamlit
URL_SHEET1 = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/gviz/tq?tqx=out:csv&sheet=Sheet1"
URL_PENJUALAN = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/gviz/tq?tqx=out:csv&sheet=Penjualan"

# Fungsi Membaca Data secara Real-Time dengan aman
def load_data(url):
    try:
        # Clear cache dengan mengabaikan index internal pandas agar data selalu fresh
        return pd.read_csv(url)
    except Exception as e:
        return pd.DataFrame()

# Load Data
df_bahan = load_data(URL_SHEET1)
df_sales = load_data(URL_PENJUALAN)

# Validasi awal data jika berhasil terbaca
if not df_bahan.empty and 'Stok (Unit)' in df_bahan.columns:
    df_bahan['Stok (Unit)'] = pd.to_numeric(df_bahan['Stok (Unit)'], errors='coerce').fillna(0)
    df_bahan['Harga per Unit (Rp)'] = pd.to_numeric(df_bahan['Harga per Unit (Rp)'], errors='coerce').fillna(0)

# 2. Desain Header / Banner Aplikasi
st.markdown("""
    <div style="background-color:#1E1E2F; padding:20px; border-radius:10px; margin-bottom:25px; text-align:center;">
        <h1 style="color:#FFFFFF; margin:0;">✨ Dashboard Manajemen & Penjualan Piscok</h1>
        <p style="color:#A3A3C2; margin:5px 0 0 0;">Catat Bahan Baku, Hitung Produksi, dan Pantau Omzet Penjualan Harian</p>
    </div>
""", unsafe_allow_html=True)

# Tombol Sinkronisasi Data Manual untuk Memastikan Data Selalu Fresh
if st.button("🔄 Segarkan & Ambil Data Terbaru dari Google Sheets", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

# 3. Membuat Menu Navigasi Tab (3 Tab)
tab1, tab2, tab3 = st.tabs(["📦 Inventaris Bahan", "🧮 Kalkulator Produksi", "💰 Catat & Rekap Penjualan"])

# =============================================================
# TAB 1: INVENTARIS BAHAN
# =============================================================
with tab1:
    col_input, col_tabel = st.columns([1, 2], gap="large")
    with col_input:
        st.subheader("➕ Input / Update Bahan")
        st.info("💡 Karena aplikasi ini online tanpa login akun Google, Anda bisa langsung menambahkan data atau mengedit stok langsung dari Google Sheets Anda agar otomatis ter-update di sini.")
        
    with col_tabel:
        st.subheader("📋 Daftar Stok Terkini (Live dari Google Sheets)")
        if not df_bahan.empty:
            st.dataframe(df_bahan, use_container_width=True, hide_index=True)
        else:
            st.info("Belum ada data bahan baku di 'Sheet1' atau pastikan Google Sheets Anda sudah diisi.")

# =============================================================
# TAB 2: KALKULATOR PRODUKSI
# =============================================================
with tab2:
    st.subheader("🧮 Hitung Estimasi Biaya Produksi")
    if df_bahan.empty or 'Nama Bahan' not in df_bahan.columns:
        st.warning("Silakan isi data bahan baku terlebih dahulu di tab Inventaris / Google Sheets.")
    else:
        bahan_terpilih = st.multiselect("Pilih bahan baku yang digunakan:", df_bahan['Nama Bahan'].tolist())
        if bahan_terpilih:
            total_biaya_produksi = 0
            list_kebutuhan = []
            for bahan in bahan_terpilih:
                row_bahan = df_bahan[df_bahan['Nama Bahan'] == bahan].iloc[0]
                harga_satuan = row_bahan['Harga per Unit (Rp)']
                stok_ada = row_bahan['Stok (Unit)']
                
                jumlah_butuh = st.number_input(f"Kebutuhan **{bahan}** (Tersedia: {stok_ada:.0f}):", min_value=0.0, step=1.0, key=f"req_{bahan}")
                subtotal = jumlah_butuh * harga_satuan
                total_biaya_produksi += subtotal
                status_stok = "✅ Cukup" if stok_ada >= jumlah_butuh else "❌ Stok Kurang!"
                
                list_kebutuhan.append({"Bahan Baku": bahan, "Jumlah": jumlah_butuh, "Subtotal": subtotal, "Status": status_stok})
            
            st.markdown("---")
            st.dataframe(pd.DataFrame(list_kebutuhan), use_container_width=True, hide_index=True)
            st.metric(label="💰 TOTAL BIAYA PRODUKSI", value=f"Rp {total_biaya_produksi:,.0f}")

# =============================================================
# TAB 3: CATAT & REKAP PENJUALAN
# =============================================================
with tab3:
    st.subheader("📊 Kalkulator & Filter Penjualan Hari Ini")
    
    # Filter Tanggal Hari Ini secara default
    pilihan_tgl = st.date_input("Pilih Tanggal Evaluasi Omzet:", datetime.now())
    tgl_filter = pilihan_tgl.strftime("%Y-%m-%d")
    
    if not df_sales.empty and 'Tanggal' in df_sales.columns:
        # Pastikan tipe data angka benar
        df_sales['Total Harga (Rp)'] = pd.to_numeric(df_sales['Total Harga (Rp)'], errors='coerce').fillna(0)
        df_sales['Jumlah Penjualan'] = pd.to_numeric(df_sales['Jumlah Penjualan'], errors='coerce').fillna(0)
        
        # Filter dataframe berdasarkan tanggal yang dipilih pengguna
        df_hari_ini = df_sales[df_sales['Tanggal'].astype(str).str.contains(tgl_filter)]
        
        # Perhitungan kalkulator otomatis
        total_omzet_hari_ini = df_hari_ini['Total Harga (Rp)'].sum()
        total_piscok_terjual = df_hari_ini['Jumlah Penjualan'].sum()
        total_pesanan = len(df_hari_ini)
        
        # Tampilkan metrik performa hari tersebut
        col_k1, col_k2, col_k3 = st.columns(3)
        with col_k1:
            st.metric(label="💰 Omzet Penjualan", value=f"Rp {total_omzet_hari_ini:,.0f}")
        with col_k2:
            st.metric(label="📦 Total Piscok Terjual", value=f"{total_piscok_terjual:.0f} Pcs/Porsi")
        with col_k3:
            st.metric(label="👥 Jumlah Transaksi", value=f"{total_pesanan} Pesanan")
        
        st.markdown(f"**Daftar Pesanan pada Tanggal {tgl_filter}:**")
        if not df_hari_ini.empty:
            st.dataframe(df_hari_ini, use_container_width=True, hide_index=True)
        else:
            st.info(f"Belum ada transaksi yang tercatat pada tanggal {tgl_filter}. Catat pesanan langsung di Google Sheets untuk melihat perubahannya di sini.")
            
        # Log Sederhana Semua Riwayat (Expander)
        with st.expander("📖 Lihat Semua Riwayat Transaksi (Semua Tanggal)"):
            st.dataframe(df_sales, use_container_width=True, hide_index=True)
    else:
        st.info("Belum ada riwayat penjualan yang tercatat di Google Sheets.")
