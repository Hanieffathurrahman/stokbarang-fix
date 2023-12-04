import streamlit as st
from module.models import Base, BarangMasuk,Persediaan, Item, Letak
from module.createdb import engine
from sqlalchemy.orm import Session
from sqlalchemy import func,and_,insert, select
import datetime


st.set_page_config(layout="wide",page_icon="📦")

#create sesi
sesi = Session(bind=engine)


#create form
st.subheader("Masukan data barang !")
now = datetime.date.today()
tgl = now.strftime("%Y %m %d")

col1, col2 = st.columns(2)
with col1:
    partNumber = st.text_input("Part Number :")
    asal_ = st.text_input("Asal :")
    item = sesi.query(Item).all()
    item_ = st.selectbox("Item : ",[i.item for i in item]+['Tambah baru'])
    if item_ == 'Tambah baru':
        new_item = st.text_input("Masukan Item baru ! :")

    no_po = st.text_input("No PO :")
    hargaBeli = st.number_input("Harga Beli :")
with col2:
    
    jumlahMasuk = st.number_input("Jumlah masuk :")
    tanggal = st.date_input("Tanggal :",now)
    
    letak_ = sesi.query(Letak).all()
    letak = st.selectbox("Letak :", [i.nama for i in letak_]+['Tambah letak'])

    if letak == 'Tambah letak':
        letakBaru = st.text_input('Masukan Letak baru  :')
    ket = st.text_input("Keterangan :")

st.write('\n')

 
submit = st.button("Submit ")

if submit:
    #add barang masuk, item and persedian by  item and letak 
    #konsisi 1 : item == item baru dan letak == letak baru ==> ketika item dan letak tidak ada dalam database
    if (item_ == 'Tambah baru' and new_item) and (letak == 'Tambah letak' and letakBaru):
        if not sesi.query(Item).filter(Item.item == new_item).first() and not sesi.query(Letak).filter(Letak.nama==letakBaru).first():
            item_baru = Item(item = new_item)
            letak_baru = Letak(nama = letakBaru)        
            barangMasuk = BarangMasuk(
                part_number = partNumber,
                asal = asal_,
                item_id = item_baru,
                item = item_baru,
                no_po = no_po,
                hargaBeli = hargaBeli,
                jumlah = jumlahMasuk,
                tanggal = tanggal,
                letak_id = letak_baru,
                letak = letak_baru,
                keterangan = ket,
            )
            #adding persediaan if part_num and item not available
            stok = Persediaan(
                part_number = partNumber,
                item_id = item_baru,
                item = item_baru,
                jumlah_masuk = jumlahMasuk,
                jumlah_keluar = 0,
                harga_beli = hargaBeli,
                harga_jual = 0,
                letak_id = letak_baru,
                letak = letak_baru
            
            )
            
            stok.jumlah = stok.jumlah_masuk - stok.jumlah_keluar
            sesi.add_all([item_baru,letak_baru,barangMasuk, stok])
            sesi.commit()
            st.success("Data berhasil di masukan !")


    #kondisi 2 : item == item baru dan letak == letak ==> ketika item tidak ada dalam database sedangkan letak ada dalam database
    elif (item_ == 'Tambah baru' and new_item):
        if not sesi.query(Item).filter(Item.item == new_item).first():
            letak_terpilih = sesi.query(Letak).filter(Letak.nama == letak).first()
            item_baru = Item(item = new_item)       
            barangMasuk = BarangMasuk(
                part_number = partNumber,
                asal = asal_,
                item_id = item_baru,
                item = item_baru,
                no_po = no_po,
                hargaBeli = hargaBeli,
                jumlah = jumlahMasuk,
                tanggal = tanggal,
                letak_id = letak_terpilih,
                letak = letak_terpilih,
                keterangan = ket,
            )
            #adding persediaan if part_num and item not available
            stok = Persediaan(
                part_number = partNumber,
                item_id = item_baru,
                item = item_baru,
                jumlah_masuk = jumlahMasuk,
                jumlah_keluar = 0,
                harga_beli = hargaBeli,
                harga_jual = 0,
                letak_id = letak_terpilih,
                letak = letak_terpilih
            
            )
            
            stok.jumlah = stok.jumlah_masuk - stok.jumlah_keluar
            sesi.add_all([item_baru,barangMasuk, stok])
            sesi.commit()
            st.success("Data berhasil di masukan !")

    #kondisi 3 : item == item dan letak == letak baru ==>  ketika item ada didatabase dan letak tidak ada dalam database
    elif (letak == 'Tambah letak' and letakBaru):
        if not sesi.query(Letak).filter(Letak.nama ==letakBaru).first():
            item_terpilih = sesi.query(Item).filter(Item.item == item_).first()
            letak_baru = Letak(nama = letakBaru)
            barangMasuk = BarangMasuk(
                part_number = partNumber,
                asal = asal_,
                item_id = item_terpilih,
                item = item_terpilih,
                no_po = no_po,
                hargaBeli = hargaBeli,
                jumlah = jumlahMasuk,
                tanggal = tanggal,
                letak_id = letak_baru,
                letak = letak_baru,
                keterangan = ket,
            )
            #adding persediaan if part_num and item not available
            stok = Persediaan(
                part_number = partNumber,
                item_id = item_terpilih,
                item = item_terpilih,
                jumlah_masuk = jumlahMasuk,
                jumlah_keluar = 0,
                harga_beli = hargaBeli,
                harga_jual = 0,
                letak_id = letak_baru,
                letak = letak_baru
            
            )
            
            stok.jumlah = stok.jumlah_masuk - stok.jumlah_keluar
            sesi.add_all([letak_baru,barangMasuk, stok])
            sesi.commit()
            st.success("Data berhasil di masukan !")

    #kondisi 4 
    else:
        #add barang masuk if item available in item table
        item_terpilih = sesi.query(Item).filter(Item.item == item_).first()
        letak_terpilih = sesi.query(Letak).filter(Letak.nama == letak).first()
        barangMasuk = BarangMasuk(
            part_number=partNumber,
            asal=asal_,
            item_id=item_terpilih,
            item=item_terpilih,
            no_po=no_po,
            jumlah=jumlahMasuk,
            hargaBeli = hargaBeli,
            tanggal=tanggal,
            letak_id = letak_terpilih,
            letak=letak_terpilih,
            keterangan=ket,
        )
        sesi.add(barangMasuk)
        sesi.commit()
        

        #kondisi ketika part num is not persediaan.part_number
        persediaan = sesi.query(Persediaan).filter_by(part_number =partNumber, item_id=item_terpilih, letak_id = letak_terpilih).first()
        if persediaan:
            persediaan.jumlah_masuk = persediaan.jumlah_masuk + jumlahMasuk
            persediaan.jumlah = persediaan.jumlah_masuk - persediaan.jumlah_keluar  
            sesi.commit()
            st.success("Data berhasil dimasukkan! hehe")

        else: 
            stok = Persediaan(
            part_number=partNumber,
            item_id=item_terpilih,
            item=item_terpilih,
            jumlah_masuk=jumlahMasuk,
            jumlah_keluar=0,
            harga_beli=0,
            harga_jual=0,
            letak_id=letak_terpilih,
            letak=letak_terpilih
        )
            stok.jumlah = stok.jumlah_masuk - stok.jumlah_keluar
            sesi.add(stok)

            st.write("data ditambah")
        