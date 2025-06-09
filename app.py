import streamlit as st
import yt_dlp as youtube_dl
import whisper
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
import os

st.set_page_config(page_title="YouTube Shorts Maker", layout="centered")
st.title("🎬 تحويل فيديو يوتيوب إلى Shorts 9:16 + ترجمة عربية")

url = st.text_input("📥 ضع رابط فيديو يوتيوب:")

if url:
    st.info("⬇️ جارٍ تحميل الفيديو...")
    ydl_opts = {
        'format': 'best[ext=mp4]',
        'outtmpl': 'video.%(ext)s',
    }

    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            st.success("✅ تم تحميل الفيديو!")

        st.warning("🧠 جارٍ استخراج الترجمة...")
        model = whisper.load_model("base")
        result = model.transcribe("video.mp4", language="ar")

        st.success("📝 تم استخراج الترجمة!")

        # قص الفيديو إلى 9:16
        st.info("✂️ قص الفيديو إلى النسبة الطولية 9:16...")
        clip = VideoFileClip("video.mp4").subclip(0, min(60, VideoFileClip("video.mp4").duration))  # أقصى حد 60 ثانية
        width, height = clip.size

        target_aspect = 9 / 16
        new_height = int(width / target_aspect)

        if new_height < height:
            y_center = height // 2
            y1 = y_center - new_height // 2
            y2 = y_center + new_height // 2
            clip_cropped = clip.crop(y1=y1, y2=y2)
        else:
            clip_cropped = clip.resize(height=720).crop(x_center=clip.w / 2, width=405)

        # إضافة الترجمة على الفيديو
        st.info("🔤 إضافة الترجمة على الفيديو...")
        txt = result["text"]
        txt_clip = TextClip(txt, fontsize=48, font="Amiri-Bold", color='white', stroke_color='black', stroke_width=2, method='caption', size=(clip_cropped.w * 0.9, None), align='South')
        txt_clip = txt_clip.set_position(("center", "bottom")).set_duration(clip_cropped.duration)

        final = CompositeVideoClip([clip_cropped, txt_clip])

        output_file = "short.mp4"
        final.write_videofile(output_file, codec="libx264", audio_codec="aac")

        st.success("✅ تم إنشاء الشورت!")

        st.video(output_file)
        with open(output_file, "rb") as f:
            st.download_button("⬇️ تحميل الفيديو النهائي", f, file_name="short.mp4")

    except Exception as e:
        st.error(f"❌ خطأ: {e}")
