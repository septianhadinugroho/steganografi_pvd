import streamlit as st
from PIL import Image
from steg_pvd import *

st.title("🔐 Steganografi Gambar dengan PVD")

mode = st.sidebar.selectbox("Mode", ["Sisipkan Gambar", "Sisipkan Teks", "Ekstrak Gambar", "Ekstrak Teks"])

if mode == "Sisipkan Gambar":
    st.header("🖼️ Sisipkan Gambar Rahasia ke dalam Gambar Cover")
    cover_img = st.file_uploader("Upload Gambar Cover (RGB)", type=["png", "jpg", "jpeg"])
    secret_img = st.file_uploader("Upload Gambar Rahasia", type=["png", "jpg", "jpeg"])
    if cover_img and secret_img:
        cover = Image.open(cover_img)
        secret = Image.open(secret_img).resize(cover.size)
        if st.button("🔐 Sisipkan"):
            stego_img = embed_image_in_image(cover, secret)
            st.image(stego_img, caption="Gambar Stego", use_column_width=True)
            stego_img.save("stego_output.png")
            with open("stego_output.png", "rb") as f:
                st.download_button("⬇️ Unduh", f, file_name="stego_output.png")

elif mode == "Ekstrak Gambar":
    st.header("🕵️ Ekstrak Gambar Rahasia")
    stego_img = st.file_uploader("Upload Gambar Stego", type=["png", "jpg", "jpeg"])
    w = st.number_input("Lebar Gambar Rahasia", min_value=1, value=128)
    h = st.number_input("Tinggi Gambar Rahasia", min_value=1, value=128)
    if stego_img and st.button("🔍 Ekstrak"):
        stego = Image.open(stego_img)
        secret = extract_image_from_image(stego, (h, w, 3))
        st.image(secret, caption="Gambar Rahasia", use_column_width=True)
        secret.save("extracted.png")
        with open("extracted.png", "rb") as f:
            st.download_button("⬇️ Unduh Gambar Rahasia", f, file_name="extracted.png")

elif mode == "Sisipkan Teks":
    st.header("✏️ Sisipkan Teks ke dalam Gambar Cover")
    cover_img = st.file_uploader("Upload Gambar Cover", type=["png", "jpg", "jpeg"])
    secret_text = st.text_area("Masukkan Pesan Rahasia")
    if cover_img and secret_text:
        cover = Image.open(cover_img)
        if st.button("🔐 Sisipkan Teks"):
            stego_img = embed_text_in_image(cover, secret_text)
            st.image(stego_img, caption="Gambar Stego", use_column_width=True)
            stego_img.save("stego_text_output.png")
            with open("stego_text_output.png", "rb") as f:
                st.download_button("⬇️ Unduh", f, file_name="stego_text_output.png")

elif mode == "Ekstrak Teks":
    st.header("📤 Ekstrak Teks dari Gambar Stego")
    stego_img = st.file_uploader("Upload Gambar Stego", type=["png", "jpg", "jpeg"])
    if stego_img and st.button("🔍 Ekstrak Teks"):
        stego = Image.open(stego_img)
        secret_text = extract_text_from_image(stego)
        st.success("Pesan Rahasia:")
        st.text(secret_text)
