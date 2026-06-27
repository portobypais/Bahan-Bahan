import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 1. Konfigurasi Halaman & Tema Dasar
st.set_page_config(
    page_title="CatatBahan PRO", 
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Link Google Sheets Anda
URL_SPREADSHEET = "https://docs.google.com/spreadsheets/d/1SxJgaORreVzDi1bW0Fg1iW7h6xNwlDLfLNR3u2DuUB8/edit?usp=sharing"

# Koneksi ke Google Sheets
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df_bahan = conn.read(spreadsheet=URL_SPREADSHEET, ttl="0d")
    df_bahan['Stok (Unit)'] = pd.to_numeric(df_bahan['Stok (Unit)'], errors='coerce').fillna(0)
    df_bahan['Harga per Unit (Rp)'] = pd.to_numeric(df_bahan['Harga per Unit (Rp)'], errors='coerce').fillna(0)
except Exception as e:
    st.error("🔒 Gagal terhubung ke Google Sheets. Pastikan Akses sudah diatur ke 'Editor' untuk semua orang yang memiliki link.")
    st.stop()

# 2. Desain Header / Banner Aplikasi
st.markdown("""
    <div style="background-color:#1E1E2F; padding:20px; border-radius:10px; margin-bottom:25px; text-align:center;">
        <h1 style="color:#FFFFFF; margin:0;">✨ CatatBahan Dashboard</h1>
        <p style="color:#A3A3C2; margin:5px 0 0 0;">Solusi Cerdas Manajemen Stok & Kalkulasi Biaya Produksi Bisnis Anda</p>
    </div>
""", unsafe_allow_html=True)

# Ringkasan Singkat (Metrik Atas)
total_jenis = len(df_bahan)
stok_menipis = len(df_bahan[df_bahan['Stok (Unit)'] < 5])

col_m1, col_m2 = st.columns(2)
with col_m1:
    st.metric(label="Total Jenis Bahan", value=f"{total_jenis} Item")
with col_m2:
    st.metric(label="Bahan Perlu Perhatian (Stok < 5)", value=f"{stok_menipis} Item", delta="- Perlu Restock" if stok_menipis > 0 else "Aman", delta_color="inverse")

st.markdown("---")

# 3. Membuat Menu Navigasi Tab yang Rapi
tab1, tab2 = st.tabs(["📦 Inventaris & Manajemen Stok", "🧮 Kalkulator Biaya Produksi"])

# -------------------------------------------------------------
# TAB 1: INVENTARIS BAHAN
# -------------------------------------------------------------
with tab1:
    col_input, col_tabel = st.columns([1, 2], gap="large")
    
    with col_input:
        st.subheader("➕ Input / Update Bahan")
        with st.form("form_bahan", clear_on_submit=True):
            nama = st.text_input("Nama Bahan Baku", placeholder="Contoh: Tepung Terigu").strip()
            stok = st.number_input("Jumlah Stok Saat Ini", min_value=0.0, step=1.0)
            harga = st.number_input("Harga per Unit (Rp)", min_value=0, step=500)
            
            submit_button = st.form_submit_button(label="💾 Simpan ke Cloud", use_container_width=True)
            
        if submit_button:
            if nama:
                df_update = df_bahan.copy()
                if nama in df_update['Nama Bahan'].values:
                    df_update.loc[df_update['Nama Bahan'] == nama, ['Stok (Unit)', 'Harga per Unit (Rp)']] = [stok, harga]
                    st.toast(f"🔄 {nama} berhasil diperbarui!", icon="✅")
                else:
                    new_row = pd.DataFrame({'Nama Bahan': [nama], 'Stok (Unit)': [stok], 'Harga per Unit (Rp)': [harga]})
                    df_update = pd.concat([df_update, new_row], ignore_index=True)
                    st.toast(f"🎉 {nama} berhasil ditambahkan!", icon="✅")
                
                conn.update(spreadsheet=URL_SPREADSHEET, data=df_update)
                st.rerun()
            else:
                st.error("Nama bahan tidak boleh kosong.")

    with col_tabel:
        st.subheader("📋 Daftar Stok Terkini")
        if not df_bahan.empty:
            # Menampilkan tabel data dengan gaya interaktif Streamlit
            st.dataframe(
                df_bahan, 
                use_container_width=True,
                column_config={
                    "Nama Bahan": st.column_config.TextColumn("Nama Bahan Baku"),
                    "Stok (Unit)": st.column_config.NumberColumn("Sisa Stok", format="%.0f"),
                    "Harga per Unit (Rp)": st.column_config.NumberColumn("Harga Satuan", format="Rp %d")
                },
                hide_index=True
            )
            
            # Tombol Reset diletakkan di expander agar tidak sengaja terpencet
            with st.expander("⚠️ Zona Bahaya (Reset Data)"):
                if st.button("Hapus Semua Data Permanen", type="primary", use_container_width=True):
                    df_kosong = pd.DataFrame(columns=['Nama Bahan', 'Stok (Unit)', 'Harga per Unit (Rp)'])
                    conn.update(spreadsheet=URL_SPREADSHEET, data=df_kosong)
                    st.rerun()
        else:
            st.info("Belum ada data bahan baku. Silakan isi form di sebelah kiri.")

# -------------------------------------------------------------
# TAB 2: KALKULATOR PRODUKSI
# -------------------------------------------------------------
with tab2:
    st.subheader("🧮 Hitung Estimasi Biaya & Cek Ketersediaan Stok")
    
    if df_bahan.empty:
        st.warning("Silakan isi data bahan baku terlebih dahulu di tab Inventaris.")
    else:
        bahan_terpilih = st.multiselect("Pilih bahan baku yang akan digunakan untuk produksi:", df_bahan['Nama Bahan'].tolist())
        
        if bahan_terpilih:
            total_biaya_produksi = 0
            list_kebutuhan = []
            
            st.markdown("#### 📥 Masukkan Jumlah Kebutuhan:")
            # Menggunakan susunan grid agar input tidak memanjang ke bawah terlalu jauh
            for bahan in bahan_terpilih:
                row_bahan = df_bahan[df_bahan['Nama Bahan'] == bahan].iloc[0]
                harga_satuan = row_bahan['Harga per Unit (Rp)']
                stok_ada = row_bahan['Stok (Unit)']
                
                col_b1, col_b2 = st.columns([3, 1])
                with col_b1:
                    jumlah_butuh = st.number_input(f"Berapa unit **{bahan}** yang diperlukan? *(Tersedia: {stok_ada:.0f})*", min_value=0.0, step=1.0, key=f"req_{bahan}")
                
                subtotal = jumlah_butuh * harga_satuan
                total_biaya_produksi += subtotal
                status_stok = "✅ Cukup" if stok_ada >= jumlah_butuh else "❌ Stok Kurang!"
                
                list_kebutuhan.append({
                    "Bahan Baku": bahan,
                    "Jumlah Kebutuhan": jumlah_butuh,
                    "Subtotal": subtotal,
                    "Status Ketersediaan": status_stok
                })
            
            st.markdown("---")
            st.subheader("📊 Ringkasan Estimasi Produksi")
            
            df_ringkasan = pd.DataFrame(list_kebutuhan)
            
            col_tabel_res, col_total_res = st.columns([2, 1], gap="medium")
            
            with col_tabel_res:
                st.dataframe(
                    df_ringkasan,
                    use_container_width=True,
                    column_config={
                        "Subtotal": st.column_config.NumberColumn("Subtotal Biaya", format="Rp %d")
                    },
                    hide_index=True
                )
            
            with col_total_res:
                st.markdown("<br>", unsafe_allow_html=True)
                st.metric(label="💰 TOTAL BIAYA PRODUKSI", value=f"Rp {total_biaya_produksi:,.0f}")
                if "❌ Stok Kurang!" in df_ringkasan['Status Ketersediaan'].values:
                    st.error("Perhatian: Beberapa bahan tidak memiliki stok yang cukup untuk produksi ini!")
                else:
                    st.success("Semua bahan siap dan mencukupi untuk produksi!")
