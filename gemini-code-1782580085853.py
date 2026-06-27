import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime

# 1. Konfigurasi Halaman
st.set_page_config(
    page_title="CatatBahan & Penjualan PRO", 
    page_icon="📦",
    layout="wide"
)

# Link Google Sheets Anda
URL_SPREADSHEET = "https://docs.google.com/spreadsheets/d/1SxJgaORreVzDi1bW0Fg1iW7h6xNwlDLfLNR3u2DuUB8/edit?usp=sharing"

# Koneksi ke Google Sheets (Membaca Sheet1 untuk Bahan & Sheet Penjualan)
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    # Membaca Data Bahan (Sheet1)
    df_bahan = conn.read(spreadsheet=URL_SPREADSHEET, worksheet="Sheet1", ttl="0d")
    df_bahan['Stok (Unit)'] = pd.to_numeric(df_bahan['Stok (Unit)'], errors='coerce').fillna(0)
    df_bahan['Harga per Unit (Rp)'] = pd.to_numeric(df_bahan['Harga per Unit (Rp)'], errors='coerce').fillna(0)
    
    # Membaca Data Penjualan (Sheet Penjualan)
    df_sales = conn.read(spreadsheet=URL_SPREADSHEET, worksheet="Penjualan", ttl="0d")
except Exception as e:
    st.error("🔒 Gagal terhubung ke Google Sheets. Pastikan akses 'Editor' aktif dan nama Worksheet sesuai ('Sheet1' dan 'Penjualan').")
    st.stop()

# 2. Desain Header / Banner Aplikasi
st.markdown("""
    <div style="background-color:#1E1E2F; padding:20px; border-radius:10px; margin-bottom:25px; text-align:center;">
        <h1 style="color:#FFFFFF; margin:0;">✨ Dashboard Manajemen & Penjualan Piscok</h1>
        <p style="color:#A3A3C2; margin:5px 0 0 0;">Catat Bahan Baku, Hitung Produksi, dan Pantau Omzet Penjualan Harian</p>
    </div>
""", unsafe_allow_html=True)

# 3. Membuat Menu Navigasi Tab (3 Tab)
tab1, tab2, tab3 = st.tabs(["📦 Inventaris Bahan", "🧮 Kalkulator Produksi", "💰 Catat & Rekap Penjualan"])

# =============================================================
# TAB 1: INVENTARIS BAHAN
# =============================================================
with tab1:
    col_input, col_tabel = st.columns([1, 2], gap="large")
    with col_input:
        st.subheader("➕ Input / Update Bahan")
        with st.form("form_bahan", clear_on_submit=True):
            nama = st.text_input("Nama Bahan Baku", placeholder="Contoh: Kulit Lumpia").strip()
            stok = st.number_input("Jumlah Stok Saat Ini", min_value=0.0, step=1.0)
            harga = st.number_input("Harga per Unit (Rp)", min_value=0, step=500)
            submit_button = st.form_submit_button(label="💾 Simpan Bahan", use_container_width=True)
            
        if submit_button and nama:
            df_update = df_bahan.copy()
            if nama in df_update['Nama Bahan'].values:
                df_update.loc[df_update['Nama Bahan'] == nama, ['Stok (Unit)', 'Harga per Unit (Rp)']] = [stok, harga]
            else:
                new_row = pd.DataFrame({'Nama Bahan': [nama], 'Stok (Unit)': [stok], 'Harga per Unit (Rp)': [harga]})
                df_update = pd.concat([df_update, new_row], ignore_index=True)
            conn.update(spreadsheet=URL_SPREADSHEET, worksheet="Sheet1", data=df_update)
            st.toast(f"✅ Data {nama} berhasil diperbarui!", icon="🎉")
            st.rerun()

    with col_tabel:
        st.subheader("📋 Daftar Stok Terkini")
        if not df_bahan.empty:
            st.dataframe(df_bahan, use_container_width=True, hide_index=True)
        else:
            st.info("Belum ada data bahan baku.")

# =============================================================
# TAB 2: KALKULATOR PRODUKSI
# =============================================================
with tab2:
    st.subheader("🧮 Hitung Estimasi Biaya Produksi")
    if df_bahan.empty:
        st.warning("Silakan isi data bahan baku terlebih dahulu di tab Inventaris.")
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
# TAB 3: CATAT & REKAP PENJUALAN (FITUR BARU)
# =============================================================
with tab3:
    col_order, col_rekap = st.columns([1, 2], gap="large")
    
    with col_order:
        st.subheader("📝 Input Pesanan Baru")
        with st.form("form_penjualan", clear_on_submit=True):
            customer = st.text_input("Nama Pemesan / Pelanggan", placeholder="Contoh: Budi").strip()
            tgl_pesan = st.date_input("Tanggal Pesanan", datetime.now())
            varian = st.text_input("Varian Piscok / Catatan", placeholder="Contoh: Piscok Cokelat Keju")
            qty = st.number_input("Jumlah Pesanan (Porsi/Mika/Pcs)", min_value=1, step=1)
            total_harga = st.number_input("Total Harga yang Dibayar (Rp)", min_value=0, step=1000)
            
            submit_sales = st.form_submit_button(label="🔔 Catat Transaksi", use_container_width=True)
            
        if submit_sales and customer:
            df_sales_update = df_sales.copy()
            # Format tanggal menjadi teks YYYY-MM-DD agar rapi di excel
            tgl_str = tgl_pesan.strftime("%Y-%m-%d")
            
            new_sales = pd.DataFrame({
                'Nama Pemesan': [customer],
                'Tanggal': [tgl_str],
                'Varian Piscok': [varian],
                'Total Harga (Rp)': [total_harga],
                'Jumlah Penjualan': [qty]
            })
            
            df_sales_update = pd.concat([df_sales_update, new_sales], ignore_index=True)
            conn.update(spreadsheet=URL_SPREADSHEET, worksheet="Penjualan", data=df_sales_update)
            st.toast(f"💰 Pesanan {customer} berhasil dicatat!", icon="🚀")
            st.rerun()

    with col_rekap:
        st.subheader("📊 Kalkulator & Filter Penjualan")
        
        # Filter Tanggal Hari Ini secara default
        hari_ini_str = datetime.now().strftime("%Y-%m-%d")
        pilihan_tgl = st.date_input("Pilih Tanggal Evaluasi Omzet:", datetime.now())
        tgl_filter = pilihan_tgl.strftime("%Y-%m-%d")
        
        if not df_sales.empty:
            # Pastikan tipe data angka benar
            df_sales['Total Harga (Rp)'] = pd.to_numeric(df_sales['Total Harga (Rp)'], errors='coerce').fillna(0)
            df_sales['Jumlah Penjualan'] = pd.to_numeric(df_sales['Jumlah Penjualan'], errors='coerce').fillna(0)
            
            # Filter dataframe berdasarkan tanggal yang dipilih pengguna
            df_hari_ini = df_sales[df_sales['Tanggal'] == tgl_filter]
            
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
                st.info(f"Belum ada transaksi yang tercatat pada tanggal {tgl_filter}.")
                
            # Log Sederhana Semua Riwayat (Expander)
            with st.expander("📖 Lihat Semua Riwayat Transaksi (Semua Tanggal)"):
                st.dataframe(df_sales, use_container_width=True, hide_index=True)
        else:
            st.info("Belum ada riwayat penjualan yang tercatat di Google Sheets.")
