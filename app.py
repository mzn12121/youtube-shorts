import streamlit as st
import yt_dlp as youtube_dl
import whisper
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
import os
import uuid

st.set_page_config(page_title="YouTube Shorts Maker", layout="centered")
st.title("🎬 تحويل فيديو يوتيوب إلى شورت احترافي")

def download_video(url, output_path):
    filename = os.path.join(output_path, f"{uuid.uuid4()}.mp4")
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': filename,
        'merge_output_format': 'mp4',
        'quiet': True,
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    return filename

def transcribe_audio(video_path):
    model = whisper.load_model("base")
    result = model.transcribe(video_path, language="ar")
    return result["text"]

def create_short(video_path, subtitles, output_path):
    clip = VideoFileClip(video_path).subclip(0, 60).resize(height=1080)
    txt_clip = TextClip(
        subtitles,
        fontsize=60,
        font="Tajawal-Black",
        color="white",
        method="caption",
        size=(clip.w, None),
    ).set_position(("center", "bottom")).set_duration(clip.duration)

    final = CompositeVideoClip([clip, txt_clip])
    short_path = os.path.join(output_path, f"{uuid.uuid4()}_short.mp4")
    final.write_videofile(short_path, codec="libx264", audio_codec="aac")
    return short_path

st.markdown("أدخل رابط فيديو يوتيوب بالعربية، وسنحوّله إلى شورت رأسي مع ترجمة تلقائية.")

url = st.text_input("🔗 رابط فيديو يوتيوب")

if st.button("ابدأ التحويل") and url:
    try:
        with st.spinner("📥 جارٍ تحميل الفيديو..."):
            video_path = download_video(url, ".")

        st.success("✅ تم تحميل الفيديو!")

        with st.spinner("🧠 جارٍ استخراج الترجمة..."):
            transcription = transcribe_audio(video_path)

        with st.spinner("🎞️ جارٍ تجهيز الشورت..."):
            short_path = create_short(video_path, transcription, ".")

        st.success("✅ تم تجهيز الفيديو القصير!")
        st.video(short_path)

    except Exception as e:
        st.error(f"❌ حدث خطأ: {e}")
