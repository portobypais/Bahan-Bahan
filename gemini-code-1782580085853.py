st.markdown(f"**Daftar Pelanggan & Pesanan Tanggal {tgl_filter}:**")
        if not df_hari_ini.empty:
            st.dataframe(
                df_hari_ini, 
                use_container_width=True, 
                hide_index=True,
                column_config={"Total Harga (Rp)": st.column_config.NumberColumn("Total Bayar", format="Rp %d")}
            )
        else:
            # Baris ini yang sebelumnya terpotong, sekarang sudah diperbaiki:
            st.info(f"🎈 Belum ada transaksi masuk pada tanggal {tgl_filter}.")
            
        with st.expander("📖 Buka Semua Riwayat Catatan Transaksi"):
            st.dataframe(df_sales, use_container_width=True, hide_index=True)
    else:
        st.info("Belum ada riwayat penjualan di Google Sheets.")
