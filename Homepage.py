import streamlit as st
import datetime
from sqlalchemy import func, create_engine
from module.models import Base, BarangMasuk,Persediaan, Item, BarangKeluar, Letak
from module.createdb import engine
from sqlalchemy.orm import Session
import pandas as pd
from streamlit.web import cli


#create sesi
sesi = Session(bind=engine)

st.set_page_config(layout="wide",page_icon="📦")

def main():
    barang_masuk = sesi.query(BarangMasuk.part_number,BarangMasuk.item_id,func.sum(BarangMasuk.jumlah).label("jumlah")).group_by(BarangMasuk.part_number,BarangMasuk.item_id)
    datamasuk = pd.DataFrame([(item.part_number, item.item_id,item.jumlah)for item in barang_masuk], columns=["part num","item id","jumlah"])


    #query barang keluar

    barang_keluar = sesi.query(BarangKeluar.part_number, BarangKeluar.item_id,func.sum(BarangKeluar.jumlah).label("jumlah_keluar")).group_by(BarangKeluar.part_number, BarangKeluar.item_id)
    datakeluar = pd.DataFrame([(item.part_number, item.item_id, item.jumlah_keluar)for item in barang_keluar], columns=["part num","item id","jumlah"])



    #operasi aritmatik

    # Merge DataFrame barang_masuk dan barang_keluar berdasarkan kolom "part num" dan "item id"
    merged_df = pd.merge(datamasuk, datakeluar, on=['part num', 'item id'], how='outer', suffixes=('_masuk', '_keluar'))

    # Menghitung selisih antara jumlah masuk dan jumlah keluar
    merged_df['selisih_jumlah'] = merged_df['jumlah_masuk'].fillna(0) - merged_df['jumlah_keluar'].fillna(0)

    now = datetime.date.today()
    tgl = now.strftime("%Y %m %d")
    with st.container():
        st.markdown('<div style="text-align: center; margin-top:0px;"><h2>Selamat Datang !</h2></div>', unsafe_allow_html=True)
        st.write(now.strftime("%A, %B %d, %Y"))
    st.divider()

    #jumlah barang by masuk, keluar, persediaan
    st.markdown(
        """
        <style>
            div[data-testid="column"]
            {
                border:1px solid white;
                border-radius : 50px 10px 50px 10px;
                padding : 25px;          
            } 
        
        
        </style>
        """,unsafe_allow_html=True
    )
    col1, col2, col3 = st.columns(3)
    barang_masukQty = sesi.query(func.sum(BarangMasuk.jumlah)).scalar()
    barang_keluarQty = sesi.query(func.sum(BarangKeluar.jumlah)).scalar()
    persediaanQty = sesi.query(func.sum(Persediaan.jumlah)).scalar()
    with col1:
        st.write(f"### Barang Masuk\nTotal: {barang_masukQty}" if barang_masukQty is not None else "### Barang Masuk\nTotal: 0")
    with col2:
        st.write(f"### Barang Keluar\nTotal: {barang_keluarQty}" if barang_keluarQty is not None else "### Barang Keluar\nTotal: 0")
    with col3:
        st.write(f"### Persediaan\nTotal: {persediaanQty}" if persediaanQty is not None else "### Persediaan\nTotal: 0")

    st.divider()
    """### Barang Masuk"""


    #menampilkan data barang masuk
    query_result = sesi.query(BarangMasuk).join(Item).all()

    # Mengonversi hasil query ke Pandas DataFrame
    df = pd.DataFrame([(data.part_number, data.asal, data.item.item, data.no_po, data.jumlah,data.hargaBeli, data.tanggal, data.letak.nama, data.keterangan) for data in query_result],
                    columns=['Part Number', 'Asal', 'Kategori', 'No PO', 'Jumlah','harga beli', 'Tanggal', 'Letak', 'Keterangan'])

    st.markdown(
        """
        <style>
            div[data-testid="stDataFrame"]{
                width: 100%;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    #-----------show data by date --------------
    # Convert 'tanggal' column to datetime format
    df['Tanggal'] = pd.to_datetime(df['Tanggal'])
    


    # Widget input tanggal
    selected_date = st.date_input("Pilih Tanggal", key ='date_input_1')

    #how to work a code 
    boolean_series = df['Tanggal'].dt.date == pd.to_datetime(selected_date).date()
    #st.write(boolean_series)

    # konversi tipe data df['tanggal] to datetime
    filtered_df = df[df['Tanggal'].dt.date == pd.to_datetime(selected_date).date()]
    filtered_df = filtered_df.set_index("Part Number")
    st.write(filtered_df)
       


    #barang keluar
    st.divider()
    """### Barang Keluar"""

    barangKeluar = sesi.query(BarangKeluar).join(Item).all()

    dkel = pd.DataFrame([(data.part_number,data.itemNumber, data.tujuan, data.item.item,data.jumlah,data.hargaJual, data.tanggal, data.letak.nama, data.keterangan)for data in barangKeluar],
                        columns = ['Part Number','item number','tujuan','Item','jumlah keluar','harga jual','tanggal','letak','keterangan'])

    #-----------show data by date --------------
    # Convert 'tanggal' column to datetime format
    dkel['tanggal'] = pd.to_datetime(dkel['tanggal'])
    


    # Widget input tanggal
    selected = st.date_input("Pilih Tanggal", key='date_input_2')

    #how to work a codet
    boolean_series = dkel['tanggal'].dt.date == pd.to_datetime(selected_date).date()
    #st.write(boolean_series)

    # konversi tipe data df['tanggal] to datetime
    filtered_df = dkel[dkel['tanggal'].dt.date == pd.to_datetime(selected).date()]
    filtered_df = filtered_df.set_index("Part Number")
    st.write(filtered_df)

    st.divider()
    """ ### Persediaan"""
    persediaan = sesi.query(Persediaan).join(Item).join(Letak).all()
    dfpersediaan  = pd.DataFrame([(data.part_number,data.item.item,data.letak.nama,data.jumlah,data.jumlah_masuk, data.jumlah_keluar,data.harga_beli,data.harga_jual)for data in persediaan],
                        columns = ['Part Num','item','letak','jumlah','jumlah masuk','jumlah keluar','Harga beli','Harga jual'])


    st.write(dfpersediaan)

if __name__=="__main__":
    Base.metadata.create_all(bind=engine)
    main()