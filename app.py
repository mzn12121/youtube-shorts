import streamlit as st
import yt_dlp as youtube_dl
import whisper
from pytube import YouTube
import cv2
import os

st.set_page_config(page_title="YouTube to Shorts", layout="centered")
st.title("🎬 تحويل فيديو يوتيوب إلى Shorts مع الترجمة بخط تجوال")

url = st.text_input("📥 ضع رابط فيديو يوتيوب:")

if url:
    st.info("⬇️ جارٍ تحميل الفيديو...")
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': 'video.%(ext)s',
        'merge_output_format': 'mp4',
    }

    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            st.success("✅ تم تحميل الفيديو!")

        st.warning("🔄 جارٍ استخراج الصوت وتحويله إلى نص...")

        model = whisper.load_model("base")
        result = model.transcribe("video.mp4", language="ar")

        st.success("📝 تم استخراج الترجمة!")

        # حفظ الترجمة كنص
        with open("subtitle.txt", "w", encoding="utf-8") as f:
            f.write(result["text"])

        st.download_button("📄 تحميل الترجمة", data=result["text"], file_name="subtitle.txt")

        st.video("video.mp4")

    except Exception as e:
        st.error(f"❌ حدث خطأ: {e}")
