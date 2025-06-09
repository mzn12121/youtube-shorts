import streamlit as st
from pytube import YouTube
import whisper
import moviepy.editor as mp
from moviepy.video.fx.all import resize
from PIL import Image, ImageDraw, ImageFont
import tempfile
import os
import numpy as np

st.set_page_config(page_title="YouTube Shorts AI", layout="centered")
st.title("🎬 YouTube Shorts AI مع ترجمة عربية تلقائية")

# إدخال رابط اليوتيوب
url = st.text_input("📌 ضع رابط فيديو يوتيوب:")

if url:
    try:
        # تحميل الفيديو
        yt = YouTube(url)
        st.success(f"تم تحميل: {yt.title}")
        stream = yt.streams.filter(file_extension='mp4', progressive=True).order_by('resolution').desc().first()

        with st.spinner("📥 جاري التحميل..."):
            tmp_video_path = stream.download(filename="original_video.mp4")

        # تحديد مدة الشورت
        max_duration = 90
        video = mp.VideoFileClip(tmp_video_path).subclip(0, min(max_duration, yt.length))

        # تحويل الأبعاد إلى 9:16
        height = 1920
        width = 1080
        video_resized = video.resize(height=height)

        if video_resized.w < width:
            video_resized = video_resized.resize(width=width)

        # استخراج الصوت للترجمة
        with st.spinner("🧠 استخراج الترجمة باستخدام Whisper..."):
            model = whisper.load_model("base")
            result = model.transcribe(tmp_video_path, language="ar")
            segments = result["segments"]

        # إعداد الترجمة على الفيديو
        font_path = "Tajawal-Black.ttf"  # تأكد من رفع هذا الملف
        font_size = 60
        try:
            font = ImageFont.truetype(font_path, font_size)
        except:
            font = ImageFont.load_default()

        def add_subtitles(clip):
            def draw_subtitles(get_frame, t):
                frame = get_frame(t)
                image = Image.fromarray(frame)
                draw = ImageDraw.Draw(image)

                # إيجاد الترجمة المناسبة
                subtitle = ""
                for seg in segments:
                    if seg["start"] <= t <= seg["end"]:
                        subtitle = seg["text"]
                        break

                if subtitle:
                    w, h = image.size
                    text_w, text_h = draw.textsize(subtitle, font=font)
                    x = (w - text_w) / 2
                    y = h - 200
                    draw.text((x, y), subtitle, font=font, fill=(255, 255, 255))

                return np.array(image)

            return clip.fl(draw_subtitles)

        with st.spinner("🎨 يتم الآن إضافة الترجمة..."):
            subtitled = add_subtitles(video_resized)

        # حفظ الفيديو النهائي
        output_path = os.path.join(tempfile.gettempdir(), "short_output.mp4")
        with st.spinner("📤 جاري تصدير الفيديو النهائي..."):
            subtitled.write_videofile(output_path, codec="libx264", audio_codec="aac", fps=24)

        st.success("✅ تم إنشاء الشورت!")
        st.video(output_path)

    except Exception as e:
        st.error(f"حدث خطأ: {str(e)}")
