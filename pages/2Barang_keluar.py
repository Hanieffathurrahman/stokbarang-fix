import streamlit as st
from module.models import Base, BarangKeluar,Persediaan, Item, Letak
from module.createdb import engine
from sqlalchemy.orm import Session

#create sesi
sesi = Session(bind=engine)


st.subheader("Masukan data barang !")

col1, col2 = st.columns(2)
with col1:
    pN = sesi.query(Persediaan.part_number).all()
    partNumber = st.selectbox("Part_number: ",[i.part_number for i in pN]) #==> dropdown menu
    itemNum = st.text_input("Item Number :")
    tujuan = st.text_input("Tujuan :")
    item = sesi.query(Item).all()
    item_ = st.selectbox("Item : ",[i.item for i in item])
   
    jumlahKeluar= st.number_input("Jumlah Keluar :")

with col2:    
    hargaJual = st.number_input("Harga Jual :")
    tanggal = st.date_input("Tanggal :")
    let = sesi.query(Letak).all()
    letak = st.selectbox("Letak :", [i.nama for i in let])
    ket = st.text_area("Keterangan :")


button = st.button("Submit ")

if button:
    item_terpilih = sesi.query(Item).filter(Item.item == item_).first()
    letak_terpilih = sesi.query(Letak).filter(Letak.nama == letak).first()
    persediaan = sesi.query(Persediaan).filter_by(part_number =partNumber, item=item_terpilih).first()
    if not persediaan:
        st.warning("pastikan input data sesuai dengan yang ada di database!")
    else:
        
        #item_terpilih = sesi.query(Item).filter(Item.item == item_).first()
        barang = BarangKeluar(
            part_number = partNumber,
            itemNumber = itemNum,
            tujuan = tujuan,
            item_id = item_terpilih,
            item = item_terpilih,
            jumlah = jumlahKeluar,
            hargaJual = hargaJual,
            tanggal = tanggal,
            letak_id = letak_terpilih,
            letak = letak_terpilih,
            keterangan = ket
        )
     
        sesi.add(barang)
        sesi.commit()


        # Gunakan langsung objek Item terpilih saat mencari Persediaan
        persediaan = sesi.query(Persediaan).filter_by(part_number=partNumber, item=item_terpilih, letak = letak_terpilih).first()
        if persediaan:
            persediaan.jumlah_keluar += jumlahKeluar
            persediaan.jumlah = persediaan.jumlah_masuk - persediaan.jumlah_keluar
            persediaan.harga_jual = hargaJual
            sesi.commit()

        st.success("Barang berhasil di Update")
        