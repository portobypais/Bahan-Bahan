import streamlit as st
import pandas as pd
from datetime import datetime

# 1. Konfigurasi Halaman & Tema Playful
st.set_page_config(
    page_title="Piscok Dash! 🍌", 
    page_icon="🍫",
    layout="wide"
)

# Kustomisasi CSS untuk UI Modern & Playful (Gradasi, Border Bulat, & Efek Kartu)
st.markdown("""
    <style>
    /* Mengubah font dan background dasar */
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #F7F9FC;
    }
    
    /* Desain Banner Atas yang Playful */
    .playful-banner {
        background: linear-gradient(135deg, #FFDE47 0%, #EA4492 100%);
        padding: 30px;
        border-radius: 20px;
        box-shadow: 0px 10px 20px rgba(234, 68, 146, 0.2);
        margin-bottom: 30px;
        text-align: center;
    }
    .banner-title {
        color: #1E1E2F !important;
        font-family: 'Comic Sans MS', 'Ubuntu', sans-serif;
        font-weight: 800;
        font-size: 32px;
        margin: 0;
    }
    .banner-subtitle {
        color: #FFFFFF;
        font-size: 16px;
        margin-top: 5px;
        font-weight: 500;
    }
    
    /* Desain Kartu Metrik Modern */
    .metric-card {
        background-color: #FFFFFF;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        border-left: 5px solid #EA4492;
        transition: transform 0.2s;
    }
    .metric-card:hover {
        transform: translateY(-5px);
    }
    
    /* Tombol Bergaya Playful */
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #EA4492 0%, #9B51E0 100%);
        color: white;
        border-radius: 12px;
        border: none;
        padding: 10px 20px;
        font-weight: bold;
        box-shadow: 0 4px 10px rgba(234, 68, 146, 0.3);
    }
    div.stButton > button:first-child:hover {
        background: linear-gradient(135deg, #9B51E0 0%, #EA4492 100%);
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# ID Spreadsheet Anda (Konfigurasi CSV stabil)
SPREADSHEET_ID = "1SxJgaORreVzDi1bW0Fg1iW7h6xNwlDLfLNR3u2DuUB8"
URL_SHEET1 = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/gviz/tq?tqx=out:csv&sheet=Sheet1"
URL_PENJUALAN = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/gviz/tq?tqx=out:csv&sheet=Penjualan"

def load_data(url):
    try:
        return pd.read_csv(url)
    except Exception:
        return pd.DataFrame()

# Load Data secara real-time
df_bahan = load_data(URL_SHEET1)
df_sales = load_data(URL_PENJUALAN)

if not df_bahan.empty and 'Stok (Unit)' in df_bahan.columns:
    df_bahan['Stok (Unit)'] = pd.to_numeric(df_bahan['Stok (Unit)'], errors='coerce').fillna(0)
    df_bahan['Harga per Unit (Rp)'] = pd.to_numeric(df_bahan['Harga per Unit (Rp)'], errors='coerce').fillna(0)

# 2. Render Banner Playful
st.markdown("""
    <div class="playful-banner">
        <h1 class="banner-title">🍫 PISCOK DASH! v2.0 🍌</h1>
        <p class="banner-subtitle">Kalkulator Pintar & Rekap Penjualan Real-Time Bisnis Kamu</p>
    </div>
""", unsafe_allow_html=True)

# Tombol Sync dengan style modern
if st.button("🔄 Ambil Data Terkini dari Google Sheets", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

# 3. Struktur Tab Menu yang Bersih
tab1, tab2, tab3 = st.tabs(["📦 Cek Stok Bahan", "🧮 Kalkulator Produksi", "💰 Rekap & Penjualan Hari Ini"])

# =============================================================
# TAB 1: INVENTARIS BAHAN
# =============================================================
with tab1:
    st.markdown("### 📋 Status Gudang Bahan Baku")
    if not df_bahan.empty:
        st.dataframe(
            df_bahan, 
            use_container_width=True, 
            hide_index=True,
            column_config={
                "Nama Bahan": "Nama Bahan ✨",
                "Stok (Unit)": st.column_config.NumberColumn("Sisa Stok", format="%d Pcs"),
                "Harga per Unit (Rp)": st.column_config.NumberColumn("Harga Modal", format="Rp %d")
            }
        )
    else:
        st.info("Belum ada data bahan baku di Google Sheets.")

# =============================================================
# TAB 2: KALKULATOR PRODUKSI (REAL-TIME CALCULATION)
# =============================================================
with tab2:
    st.markdown("### 🧮 Kalkulator Biaya Rencana Produksi")
    if df_bahan.empty or 'Nama Bahan' not in df_bahan.columns:
        st.warning("Silakan isi data bahan baku terlebih dahulu di Google Sheets.")
    else:
        bahan_terpilih = st.multiselect("Pilih bahan yang mau dipakai hari ini:", df_bahan['Nama Bahan'].tolist())
        
        if bahan_terpilih:
            total_biaya_produksi = 0
            list_kebutuhan = []
            
            st.markdown("#### 📥 Geser / Isi Jumlah Kebutuhan (Otomatis Menjumlahkan):")
            
            # Form grid input yang interaktif
            for bahan in bahan_terpilih:
                row_bahan = df_bahan[df_bahan['Nama Bahan'] == bahan].iloc[0]
                harga_satuan = row_bahan['Harga per Unit (Rp)']
                stok_ada = row_bahan['Stok (Unit)']
                
                col_b1, col_b2 = st.columns([3, 1])
                with col_b1:
                    # Menggunakan slider agar UX terasa lebih playful dan interaktif dibanding ngetik angka
                    jumlah_butuh = st.slider(f"Kebutuhan untuk **{bahan}** (Stok Gudang: {stok_ada:.0f})", min_value=0.0, max_value=float(max(stok_ada, 100.0)), step=1.0, key=f"slide_{bahan}")
                
                subtotal = jumlah_butuh * harga_satuan
                total_biaya_produksi += subtotal
                status_stok = "🍏 Cukup" if stok_ada >= jumlah_butuh else "🍎 Stok Kurang!"
                
                list_kebutuhan.append({"Bahan Baku": bahan, "Jumlah": jumlah_butuh, "Subtotal Biaya": subtotal, "Status": status_stok})
            
            st.markdown("---")
            
            # Tampilan Hasil Real-Time Samping-menyamping
            res_col1, res_col2 = st.columns([2, 1], gap="large")
            with res_col1:
                st.markdown("**Detail Nota Produksi:**")
                st.dataframe(
                    pd.DataFrame(list_kebutuhan), 
                    use_container_width=True, 
                    hide_index=True,
                    column_config={"Subtotal Biaya": st.column_config.NumberColumn("Biaya", format="Rp %d")}
                )
            with res_col2:
                # Custom Card untuk Total Biaya agar mencolok
                st.markdown(f"""
                    <div class="metric-card" style="border-left: 5px solid #FFDE47; background-color: #1E1E2F; color: white;">
                        <p style="margin:0; font-size: 14px; color: #A3A3C2;">TOTAL ESTIMASI MODAL</p>
                        <h2 style="margin:5px 0 0 0; color: #FFDE47; font-size: 28px;">Rp {total_biaya_produksi:,.0f}</h2>
                    </div>
                """, unsafe_allow_html=True)

# =============================================================
# TAB 3: CATAT & REKAP PENJUALAN (REAL-TIME REKAP)
# =============================================================
with tab3:
    st.markdown("### 💰 Monitor Penjualan & Hitung Omzet Otomatis")
    
    # Komponen filter tanggal yang estetik
    pilihan_tgl = st.date_input("📅 Pilih Tanggal Evaluasi:", datetime.now())
    tgl_filter = pilihan_tgl.strftime("%Y-%m-%d")
    
    if not df_sales.empty and 'Tanggal' in df_sales.columns:
        df_sales['Total Harga (Rp)'] = pd.to_numeric(df_sales['Total Harga (Rp)'], errors='coerce').fillna(0)
        df_sales['Jumlah Penjualan'] = pd.to_numeric(df_sales['Jumlah Penjualan'], errors='coerce').fillna(0)
        
        # Filter data secara instant/real-time berdasarkan tanggal pilihan
        df_hari_ini = df_sales[df_sales['Tanggal'].astype(str).str.contains(tgl_filter)]
        
        # Kalkulator Penjumlahan Otomatis
        total_omzet = df_hari_ini['Total Harga (Rp)'].sum()
        total_terjual = df_hari_ini['Jumlah Penjualan'].sum()
        total_transaksi = len(df_hari_ini)
        
        # Grid Scorecard Penjualan yang Sangat UI/UX Friendly & Modern
        st.markdown(f"""
            <div style="display: flex; gap: 20px; margin-bottom: 25px;">
                <div class="metric-card" style="flex: 1; border-left: 5px solid #47A8BD;">
                    <p style="margin:0; font-size:12px; color:#888;">💰 TOTAL OMZET HARI INI</p>
                    <h3 style="margin:5px 0 0 0; color:#1E1E2F; font-size:24px;">Rp {total_omzet:,.0f}</h3>
                </div>
                <div class="metric-card" style="flex: 1; border-left: 5px solid #EA4492;">
                    <p style="margin:0; font-size:12px; color:#888;">🍌 PISCOK TERJUAL</p>
                    <h3 style="margin:5px 0 0 0; color:#1E1E2F; font-size:24px;">{total_terjual:.0f} Pcs</h3>
                </div>
                <div class="metric-card" style="flex: 1; border-left: 5px solid #9B51E0;">
                    <p style="margin:0; font-size:12px; color:#888;">👥 TOTAL NOTA/PESANAN</p>
                    <h3 style="margin:5px 0 0 0; color:#1E1E2F; font-size:24px;">{total_transaksi} Transaksi</h3>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"**Daftar Pelanggan & Pesanan Tanggal {tgl_filter}:**")
        if not df_hari_ini.empty:
            st.dataframe(
                df_hari_ini, 
                use_container_width=True, 
                hide_index=True,
                column_config={"Total Harga (Rp)": st.column_config.NumberColumn("Total Bayar", format="Rp %d")}
            )
        else:
            st.info(f"🎈 Belum ada transaksi masuk pada tanggal {tgl_filter}. Data transaksi yang diinput ke Google Sheets Anda akan langsung
