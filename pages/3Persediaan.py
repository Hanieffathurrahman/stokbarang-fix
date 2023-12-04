import streamlit as st
import datetime
from sqlalchemy import func
from module.models import Base, BarangMasuk,Persediaan, Item, BarangKeluar
from module.createdb import engine
from sqlalchemy.orm import Session
import pandas as pd

sesi = Session(bind=engine)

"""## Persediaan"""
persediaan = sesi.query(Persediaan).join(Item).all()
dfPersediaan = pd.DataFrame([(data.part_number,data.item.item,data.letak.nama,data.jumlah,data.jumlah_masuk, data.jumlah_keluar, data.harga_beli, data.harga_jual)for data in persediaan],
                             columns = ['Part Number','item','letak','Jumlah','jumlah masuk','jumlah keluar','harga beli (satuan)','harga jual (satuan)'])

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


#fitur select item
col1, col2 = st.columns(2)

with col1:
    items = dfPersediaan['item']
    itemSelect = st.multiselect("Pilih Item yang ingin kamu tampilkan !:",items)
with col2:
    letak = dfPersediaan['letak']
    letakSelect = st.multiselect('pilih letak barang yang ingin kamu tampilkan', letak)



if not itemSelect and not letakSelect:
    pass
    """### Data Persediaan"""
    dfi = dfPersediaan.set_index("Part Number")
    st.write(dfi[:10])
    for index, row in dfi.iterrows():
        if row['Jumlah'] > 2:
            st.toast(f"Jumlah barang {index} melebihi batas minimal")

elif itemSelect:
    st.write(f'filter data by {itemSelect}')
    filtering = dfPersediaan[dfPersediaan['item'].isin(itemSelect) ]

    filIndex = filtering.set_index("Part Number")
    st.write(filIndex)

    for index, row in filIndex.iterrows():
        if row['Jumlah'] > 2:
            st.warning(f"Jumlah barang {index} melebihi batas minimal")

elif letakSelect:
    st.write(f'filter data by {letakSelect}')
    filtering = dfPersediaan[dfPersediaan['letak'].isin(letakSelect) ]
    filIndex = filtering.set_index("Part Number")
    st.write(filIndex)

    for index, row in filIndex.iterrows():
        if row['Jumlah'] > 2:
            st.warning(f"Jumlah barang {index} melebihi batas minimal")

else: 
    st.write(f'filter data by {itemSelect} di letak {letakSelect}')
    filtering = dfPersediaan[dfPersediaan['item'].isin(itemSelect) & dfPersediaan['letak'].isin(letakSelect)]
    
    filIndex = filtering.set_index("Part Number")
    st.write(filIndex)

    for index, row in filIndex.iterrows():
        if row['Jumlah'] > 2:
            st.warning(f"Jumlah barang {index} melebihi batas minimal")

    

