import streamlit as st
from streamlit_option_menu import option_menu
import datetime
from sqlalchemy import func, create_engine, and_, select, insert
from module.models import Base, BarangMasuk,Persediaan, Item, BarangKeluar, Letak
from module.createdb import engine
from sqlalchemy.orm import Session
import pandas as pd



#create sesi
sesi = Session(bind=engine)

st.set_page_config(layout="wide",page_icon="📦")
Base.metadata.create_all(bind=engine)

with st.sidebar:
    selected = option_menu(menu_title=None,
                        options=["Homepage","Barang Masuk", "Barang Keluar", "persediaan"],
                        icons=["house","box-arrow-in-right","box-arrow-right","boxes"],
                        menu_icon="cast",
                        orientation="vertikal",
                        styles={
                                "container": {"padding": "0!important", "background-color": "#0000"},
                                "icon": {"color": "white", "font-size": "15px"},
                                "nav-link": {
                                    "font-size": "15 px",
                                    "text-align": "left",
                                    "margin": "5px",
                                    "--hover-color": "#4c5154",
                                },
                                "nav-link-selected": {"background-color": "#3c3f45"},
            },)

if selected == 'Homepage':
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




#---------------------BARANG MASUK-----------------------------
if selected == 'Barang Masuk':
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
        hargaBeli = st.number_input("Harga Beli :",0)
    with col2:
        
        jumlahMasuk = st.number_input("Jumlah masuk :",0)
        tanggal = st.date_input("Tanggal :",now)
        
        letak_ = sesi.query(Letak).all()
        letak = st.selectbox("Letak :", [i.nama for i in letak_]+['Tambah letak'])

        if letak == 'Tambah letak':
            letakBaru = st.text_input('Masukan Letak baru  :')
        ket = st.text_area("Keterangan :")

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
            

if selected == 'Barang Keluar':
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
        
if selected == 'persediaan':
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

    


