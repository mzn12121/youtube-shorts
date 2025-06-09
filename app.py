import streamlit as st import tempfile import os import whisper import yt_dlp import shutil import uuid import subprocess from moviepy.editor import VideoFileClip, CompositeVideoClip, vfx from moviepy.video.fx.crop import crop from moviepy.video.tools.subtitles import SubtitlesClip from moviepy.video.VideoClip import TextClip

إعداد الواجهة

st.set_page_config(page_title="AI Shorts Maker", layout="centered") st.title("🎬 AI Shorts Maker") st.markdown(""" حول فيديوهاتك الأفقية من يوتيوب أو ملفات MP4 إلى فيديوهات عمودية احترافية للـ Shorts, Reels, TikTok 🎯 """)

إدخال رابط أو تحميل ملف

option = st.radio("اختر المصدر:", ["📎 رابط يوتيوب", "📁 رفع فيديو MP4"])

video_path = None if option == "📎 رابط يوتيوب": url = st.text_input("أدخل رابط الفيديو") if url: with st.spinner("جارٍ تحميل الفيديو..."): unique_id = str(uuid.uuid4()) video_path = f"{unique_id}.mp4" ydl_opts = { 'format': 'best[height<=720]', 'outtmpl': video_path, 'quiet': True, 'noplaylist': True } try: with yt_dlp.YoutubeDL(ydl_opts) as ydl: ydl.download([url]) st.success("تم تحميل الفيديو") except Exception as e: st.error(f"❌ فشل التحميل: {str(e)}") video_path = None else: uploaded_file = st.file_uploader("ارفع الفيديو (MP4)", type=["mp4"]) if uploaded_file: temp_dir = tempfile.mkdtemp() video_path = os.path.join(temp_dir, uploaded_file.name) with open(video_path, "wb") as f: f.write(uploaded_file.read()) st.success("✅ تم رفع الفيديو")

إعدادات الترجمة

st.markdown("---") st.subheader("⚙️ إعدادات الترجمة") font_choice = st.selectbox("اختر الخط:", ["Tajwal", "Arial", "Brando بديل"]) font_size = st.slider("حجم الخط", 24, 80, 48) position = st.selectbox("موضع الترجمة", ["الأسفل", "الوسط", "الأعلى"])

تنفيذ المعالجة

if video_path and st.button("🚀 أنشئ الفيديو العمودي"): try: with st.spinner("🧠 جارٍ توليد الترجمة"): model = whisper.load_model("base") result = model.transcribe(video_path)

with st.spinner("🎥 جارٍ المعالجة والتتبع"):
        original = VideoFileClip(video_path)
        duration = min(60, original.duration)
        clip = original.subclip(0, duration).resize(height=1080)

        w, h = clip.size
        target_aspect = 9/16
        new_width = int(h * target_aspect)
        x_center = w // 2
        cropped_clip = crop(clip, x_center=x_center, width=new_width)

        # الترجمة
        def generator(txt):
            return TextClip(txt, fontsize=font_size, font=font_choice, color='white')

        subtitle_data = [(seg['start'], seg['end'], seg['text']) for seg in result['segments']]
        subs = SubtitlesClip(subtitle_data, generator)

        if position == "الأسفل":
            subs = subs.set_position(('center', 'bottom'))
        elif position == "الوسط":
            subs = subs.set_position('center')
        else:
            subs = subs.set_position(('center', 'top'))

        final = CompositeVideoClip([cropped_clip, subs])

        output_path = f"short-{uuid.uuid4()}.mp4"
        final.write_videofile(output_path, fps=30, codec="libx264", audio_codec="aac")

    st.success("✅ تم إنشاء الفيديو")
    st.video(output_path)
    with open(output_path, "rb") as file:
        st.download_button("📥 تحميل الفيديو", file, file_name="short_video.mp4")

    # تنظيف
    if os.path.exists(video_path):
        os.remove(video_path)
    if os.path.exists(output_path):
        os.remove(output_path)

except Exception as e:
    st.error(f"❌ خطأ: {e}")

