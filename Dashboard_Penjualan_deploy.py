import streamlit as st # type: ignore
import pandas as pd # type: ignore
import numpy as np # type: ignore
import os
import plotly.express as px # type: ignore # Import module Plotly untuk grafik interaktif

# === KONFIGURASI PATH ===
# Pilih salah satu path di bawah ini (komen yang tidak dipakai)

# 1. Path LOKAL (untuk uji coba di komputer lu)
# PENJUALAN_FOLDER = r"D:\Soega Store\Laporan penjualan\Penjualan"  # Pakai 'r' di depan string biar path Windows kebaca
# IKLAN_FOLDER = r"D:\Soega Store\Laporan penjualan\Iklan"

# 2. Path DEPLOY (untuk di GitHub dan Streamlit)
PENJUALAN_FOLDER = "Penjualan"
IKLAN_FOLDER = "Iklan"

# Set judul aplikasi
st.set_page_config(
    page_title="Dashboard Soega",
    page_icon="📈",
    layout="wide"
)

st.title("📈 Dashboard Penjualan Itemku - Soega")
st.write("Selamat datang di dashboard penjualan Soega, sehat-sehat gen z")

# Bagian pemilih file dari folder
st.header("1. Pilih Data Penjualan dari Repository")

df = None # Inisialisasi DataFrame utama
df_transaksi = None
df_detail = None

# --- Fungsi untuk mendapatkan daftar file di folder ---
def get_data_files(folder_path):
    """Mendapatkan daftar file .xlsx atau .csv di folder tertentu."""
    files = []
    if os.path.exists(folder_path):
        for f_name in os.listdir(folder_path):
            if os.path.isfile(os.path.join(folder_path, f_name)) and f_name.lower().endswith(('.xlsx', '.csv')):
                files.append(f_name)
    return sorted(files)

# --- Pilihan File Transaksi ---
st.subheader("Pilih File Transaksi")
transaksi_files = get_data_files(PENJUALAN_FOLDER)

if transaksi_files:
    selected_transaksi_file = st.selectbox(
        "Pilih file laporan penjualan:",
        transaksi_files,
        key='select_transaksi_file'
    )
    TRANSAKSI_FILE_PATH_FULL = os.path.join(PENJUALAN_FOLDER, selected_transaksi_file)

    try:
        if TRANSAKSI_FILE_PATH_FULL.lower().endswith('.csv'):
            df_transaksi = pd.read_csv(TRANSAKSI_FILE_PATH_FULL)
        elif TRANSAKSI_FILE_PATH_FULL.lower().endswith('.xlsx'):
            df_transaksi = pd.read_excel(TRANSAKSI_FILE_PATH_FULL)
        
        st.success(f"File laporan penjualan '{selected_transaksi_file}' udah dimuat.")
        
        # Konversi kolom tanggal ke datetime di df_transaksi
        datetime_columns_transaksi = [
            'Tanggal_Dibuat',
            'Tanggal_Dibayar_Pembeli',
            'Tanggal_Dikirim',
            'Tanggal_Pesanan_Selesai'
        ]
        for col in datetime_columns_transaksi:
            if col in df_transaksi.columns:
                df_transaksi[col] = pd.to_datetime(df_transaksi[col], errors='coerce')
        
        # Rename 'Nomor_Pesanan' to 'No_Pesanan' di df_transaksi agar sesuai dengan df_detail
        if 'Nomor_Pesanan' in df_transaksi.columns:
            df_transaksi.rename(columns={'Nomor_Pesanan': 'No_Pesanan'}, inplace=True)

        st.session_state['df_transaksi'] = df_transaksi
    except Exception as e:
        st.error(f"Waduh, ada error pas baca file transaksi '{selected_transaksi_file}' nih, bos: {e}")
        st.info(f"Cek lagi format file '{selected_transaksi_file}' lu ya.")
else:
    st.error(f"Folder '{PENJUALAN_FOLDER}' gak ketemu atau kosong, bos!")
    st.info(f"Pastikan lu udah bikin folder **'{PENJUALAN_FOLDER}'** dan udah ada file data di dalamnya.")


st.write("---")

# --- Pilihan File Iklan ---
st.subheader("Pilih File Iklan")
iklan_files = get_data_files(IKLAN_FOLDER)

if iklan_files:
    selected_detail_file = st.selectbox(
        "Pilih file detail iklan:",
        iklan_files,
        key='select_detail_file'
    )
    DETAIL_FILE_PATH_FULL = os.path.join(IKLAN_FOLDER, selected_detail_file)

    try:
        if DETAIL_FILE_PATH_FULL.lower().endswith('.csv'):
            df_detail = pd.read_csv(DETAIL_FILE_PATH_FULL)
        elif DETAIL_FILE_PATH_FULL.lower().endswith('.xlsx'):
            df_detail = pd.read_excel(DETAIL_FILE_PATH_FULL)
        
        st.success(f"File iklan '{selected_detail_file}' nya dah dimuat.")
        
        st.session_state['df_detail'] = df_detail
    except Exception as e:
        st.error(f"Waduh, ada error pas baca file detail iklan/produk '{selected_detail_file}' nih, bos: {e}")
        st.info(f"Cek lagi format file '{selected_detail_file}' lu ya.")
else:
    st.error(f"Folder '{IKLAN_FOLDER}' gak ketemu atau kosong, bos!")
    st.info(f"Pastikan lu udah bikin folder **'{IKLAN_FOLDER}'** dan udah ada file data di dalamnya.")


# --- Proses Penggabungan Data jika kedua file sudah di-load ---
# Kondisi ini akan dijalankan hanya jika kedua df_transaksi dan df_detail berhasil di-load
if 'df_transaksi' in st.session_state and 'df_detail' in st.session_state:
    df_transaksi = st.session_state['df_transaksi']
    df_detail = st.session_state['df_detail']

    # Pastikan kedua DataFrame tidak kosong setelah di-load
    if df_transaksi is not None and not df_transaksi.empty and \
       df_detail is not None and not df_detail.empty:
        try:
            # Pastikan kolom kunci 'No_Pesanan' ada di kedua DataFrame
            if 'No_Pesanan' in df_transaksi.columns and 'No_Pesanan' in df_detail.columns:
                # Merge (gabungkan) kedua DataFrame pake 'No_Pesanan' sebagai kuncinya
                df_merged = pd.merge(df_transaksi, df_detail, on='No_Pesanan', how='left')

                # Konversi kolom boolean di df_merged jika ada
                boolean_columns = ['Pembeli_Premium', '10_Menit_Kirim', 'Pengiriman_Instan']
                for col in boolean_columns:
                    if col in df_merged.columns:
                        df_merged[col] = df_merged[col].astype(str).str.lower().map({'true': True, 'false': False}).fillna(False)

                # --- MODIFIKASI PENTING: Konversi kolom 'Iklan' ke tipe numerik dan isi NaN dengan 0 ---
                if 'Iklan' in df_merged.columns:
                    df_merged['Iklan'] = pd.to_numeric(df_merged['Iklan'], errors='coerce')
                    df_merged['Iklan'] = df_merged['Iklan'].fillna(0)

                st.success("Dua file berhasil digabungkan, bos!")
                st.write("Ini dia data yang udah digabung dan dirapihin (preview 5 baris pertama):")
                st.dataframe(df_merged.head())
                st.session_state['data_merged'] = df_merged # Simpan DataFrame hasil merge di session_state

            else:
                st.warning("Waduh, salah satu atau kedua file gak punya kolom 'No_Pesanan' nih, bos. Gak bisa digabungin.")
                st.info("Pastikan kolom 'No_Pesanan' ada dan namanya sama persis di kedua file ya.")

        except Exception as e:
            st.error(f"Ada error pas ngegabungin data nih, bos: {e}")
            st.info("Cek lagi format dan nama kolom 'No_Pesanan' di kedua file lu ya.")
    else:
        st.warning("Salah satu atau kedua file yang dimuat dari repo kosong atau gagal dibaca, bos.")
        st.session_state['data_merged'] = None # Pastikan data_merged direset jika ada masalah
else:
    st.info("Pilih file transaksi dan file iklan di atas untuk memulai analisis, bos!")


# --- Bagian Dashboard Utama setelah data siap ---
if 'data_merged' in st.session_state and st.session_state['data_merged'] is not None and not st.session_state['data_merged'].empty:
    df = st.session_state['data_merged'] # Gunakan DataFrame yang sudah digabung

    st.write("---")
    st.header("2. Filter dan Analisis Data Lu")

    st.subheader("Saring Data Penjualan")

    # Filter untuk Status_Pesanan (Dropdown/Multiselect)
    if 'Status_Pesanan' in df.columns:
        status_options = ['Semua'] + list(df['Status_Pesanan'].unique())
        selected_status = st.selectbox("Pilih Status Pesanan:", status_options, key='filter_status')
        if selected_status != 'Semua':
            df = df[df['Status_Pesanan'] == selected_status]

    # Filter untuk Kategori (Dropdown/Multiselect)
    if 'Kategori' in df.columns:
        kategori_options = ['Semua'] + list(df['Kategori'].unique())
        selected_kategori = st.selectbox("Pilih Kategori Produk:", kategori_options, key='filter_kategori')
        if selected_kategori != 'Semua':
            df = df[df['Kategori'] == selected_kategori]
    
    # --- Filter untuk Nama_Produk (Multiselect/Checkbox) ---
    if 'Nama_Produk' in df.columns:
        produk_options = list(df['Nama_Produk'].unique())
        selected_produk = st.multiselect(
            "Pilih Nama Produk:",
            produk_options,
            default=produk_options, # Secara default semua terpilih
            key='filter_produk'
        )
        if selected_produk: # Jika ada produk yang dipilih (list tidak kosong)
            df = df[df['Nama_Produk'].isin(selected_produk)]
        else: # Jika tidak ada produk yang dipilih, tampilkan DataFrame kosong atau pesan
            st.warning("Minimal pilih 1 lah bos, hadeh...")
            df = df[0:0] # Buat DataFrame kosong agar bagian bawah tidak error

    # Filter untuk Tanggal_Dibuat (Rentang Tanggal)
    if 'Tanggal_Dibuat' in df.columns and pd.api.types.is_datetime64_any_dtype(df['Tanggal_Dibuat']):
        # Cek apakah df masih memiliki data valid sebelum mengambil min/max date
        if not df.empty:
            min_date_val = df['Tanggal_Dibuat'].min()
            max_date_val = df['Tanggal_Dibuat'].max()

            min_date = min_date_val.date() if pd.notna(min_date_val) else pd.to_datetime('2020-01-01').date()
            max_date = max_date_val.date() if pd.notna(max_date_val) else pd.to_datetime('2025-12-31').date()
            
            date_range = st.date_input(
                "Pilih Rentang Tanggal Dibuat:",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date,
                key='filter_tanggal'
            )
            if len(date_range) == 2:
                start_date = pd.to_datetime(date_range[0])
                end_date = pd.to_datetime(date_range[1])
                df = df[(df['Tanggal_Dibuat'] >= start_date) & (df['Tanggal_Dibuat'] < end_date + pd.Timedelta(days=1))]
            elif len(date_range) == 1:
                start_date = pd.to_datetime(date_range[0])
                df = df[(df['Tanggal_Dibuat'] >= start_date) & (df['Tanggal_Dibuat'] < start_date + pd.Timedelta(days=1))]
        else:
            st.info("Filter tanggal tidak aktif karena data kosong setelah filter sebelumnya.")
            df = df[0:0] # Pastikan df tetap kosong jika sebelumnya sudah kosong


    # Filter untuk Iklan (Dropdown/Multiselect)
    if 'Iklan' in df.columns:
        # Hanya tampilkan opsi iklan yang ada di data setelah filter sebelumnya
        current_unique_ads = sorted([x for x in df['Iklan'].unique() if x != 0])
        iklan_options_display = ['Semua', 'Hanya Data Beriklan', 'Tidak Ada Iklan'] + [str(x) for x in current_unique_ads]
        
        selected_iklan_display = st.selectbox("Filter Berdasarkan Iklan:", iklan_options_display, key='filter_iklan')
        
        if selected_iklan_display == 'Hanya Data Beriklan':
            df = df[df['Iklan'] != 0]
        elif selected_iklan_display == 'Tidak Ada Iklan':
            df = df[df['Iklan'] == 0]
        elif selected_iklan_display != 'Semua':
            try:
                filter_val = float(selected_iklan_display)
                df = df[df['Iklan'] == filter_val]
            except ValueError:
                st.warning(f"Nilai '{selected_iklan_display}' tidak valid untuk filter iklan numerik.")

    st.write("---")
    st.subheader("Data Penjualan Setelah Difilter:")
    
    if not df.empty:
        # --- MODIFIKASI: Hanya tampilkan kolom yang diminta ---
        columns_to_display = ['No_Pesanan', 'Status_Pesanan', 'Tanggal_Dibuat', 'Nama_Produk', 'Nama_Pembeli', 'Jumlah_Pesanan', 'Total_Pendapatan', 'Iklan']
        
        # Saring kolom yang ada di DataFrame untuk ditampilkan dari list yang diinginkan
        actual_columns_to_show = [col for col in columns_to_display if col in df.columns]
        
        st.dataframe(df[actual_columns_to_show]) # Tambahkan hide_index=True
        st.write(f"Jumlah baris setelah difilter: **{len(df)}**")

        # --- Otomasi Kalkulasi Real-Time (RINGKASAN BARU) ---
        st.subheader("Ringkasan Real-time:")
        
        total_pendapatan = 0
        jumlah_transaksi_total = 0
        total_iklan = 0

        # Menggunakan 3 kolom untuk menampung metrik yang diinginkan
        col_calc1, col_calc2, col_calc3 = st.columns(3) 

        # Total Pendapatan
        if 'Total_Pendapatan' in df.columns:
            total_pendapatan = df['Total_Pendapatan'].sum()
            col_calc1.metric("Total Pendapatan", f"Rp {total_pendapatan:,.0f}".replace(',', '.'))
        else:
            col_calc1.warning("Kolom 'Total_Pendapatan' tidak ditemukan.")

        # Jumlah Transaksi (dari semua baris yang difilter)
        jumlah_transaksi_total = len(df)
        col_calc2.metric("Jumlah Transaksi", f"{int(jumlah_transaksi_total)}")

        # Total Iklan (sum dari kolom 'Iklan')
        if 'Iklan' in df.columns:
            total_iklan = df['Iklan'].sum()
            col_calc3.metric("Total Iklan", f"{total_iklan:,.0f}".replace(',', '.'))
        else:
            col_calc3.warning("Kolom 'Iklan' tidak ditemukan.")

        # --- Grafik Interaktif: Pendapatan dan Iklan Per Hari ---
        st.write("---")
        st.subheader("3. Grafik Tren Harian")

        # Pastikan kolom Tanggal_Dibuat ada dan tipenya datetime
        if 'Tanggal_Dibuat' in df.columns and pd.api.types.is_datetime64_any_dtype(df['Tanggal_Dibuat']):
            # Agregasi data per hari
            # Group by Tanggal_Dibuat (date only) dan sum Total_Pendapatan serta Iklan
            df_daily = df.groupby(df['Tanggal_Dibuat'].dt.date).agg(
                Total_Pendapatan=('Total_Pendapatan', 'sum'),
                Total_Iklan=('Iklan', 'sum')
            ).reset_index()

            # Rename kolom Tanggal_Dibuat menjadi 'Tanggal' agar lebih umum
            df_daily.rename(columns={'Tanggal_Dibuat': 'Tanggal'}, inplace=True)

            # Sort data berdasarkan tanggal
            df_daily = df_daily.sort_values('Tanggal')

            # --- Grafik 1: Tren Pendapatan Harian ---
            st.markdown("##### Tren Total Pendapatan Harian")
            if not df_daily.empty:
                fig_pendapatan = px.line(
                    df_daily, 
                    x='Tanggal', 
                    y='Total_Pendapatan', 
                    title='Total Pendapatan per Hari',
                    labels={'Total_Pendapatan': 'Pendapatan (Rp)', 'Tanggal': 'Tanggal Dibuat'},
                    hover_name="Tanggal",
                    hover_data={'Total_Pendapatan': ':.0f'}
                )
                fig_pendapatan.update_traces(mode='lines+markers') # Tampilkan garis dan titik
                fig_pendapatan.update_layout(hovermode="x unified") # Hover jadi lebih informatif
                st.plotly_chart(fig_pendapatan, use_container_width=True)
            else:
                st.info("Tidak ada data pendapatan harian untuk ditampilkan.")

            # --- Grafik 2: Tren Iklan Harian ---
            st.markdown("##### Tren Biaya Iklan Harian")
            if not df_daily.empty:
                fig_iklan = px.line(
                    df_daily, 
                    x='Tanggal', 
                    y='Total_Iklan', 
                    title='Total Biaya Iklan per Hari',
                    labels={'Total_Iklan': 'Biaya Iklan (Rp)', 'Tanggal': 'Tanggal Dibuat'},
                    hover_name="Tanggal",
                    hover_data={'Total_Iklan': ':.0f'}
                )
                fig_iklan.update_traces(mode='lines+markers') # Tampilkan garis dan titik
                fig_iklan.update_layout(hovermode="x unified") # Hover jadi lebih informatif
                st.plotly_chart(fig_iklan, use_container_width=True)
            else:
                st.info("Tidak ada data biaya iklan harian untuk ditampilkan.")
        else:
            st.warning("Kolom 'Tanggal_Dibuat' tidak ditemukan atau bukan tipe tanggal, tidak bisa bikin grafik harian.")

    else:
        st.warning("Tidak ada data yang cocok dengan filter yang dipilih, bos.")

else:
    st.info("Pilih file transaksi dan file iklan di atas untuk memulai analisis, bos!")