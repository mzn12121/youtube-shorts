import streamlit as st
import yt_dlp
import whisper
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
import os

st.set_page_config(page_title="YouTube Shorts Maker", layout="centered")
st.title("🎬 محول فيديوهات يوتيوب إلى Shorts مع ترجمة بخط تجوال")

# تحميل الفيديو من رابط اليوتيوب
url = st.text_input("أدخل رابط فيديو يوتيوب:")

if st.button("ابدأ التحويل") and url:
    try:
        st.info("جارٍ تحميل الفيديو...")

        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4',
            'outtmpl': 'downloaded_video.%(ext)s',
            'merge_output_format': 'mp4',
            'quiet': True,
            'no_warnings': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        st.success("✅ تم تحميل الفيديو!")

        # تحميل نموذج Whisper
        st.info("🧠 جارٍ استخراج الترجمة...")
        model = whisper.load_model("small")  # يمكنك اختيار base, small, medium, large

        result = model.transcribe("downloaded_video.mp4", language="ar")  # اللغة عربية

        st.success("✅ تم استخراج الترجمة!")

        # تجهيز الترجمة النصية (الخط هنا تجوال Black)
        subtitles = result["segments"]
        full_text = result["text"]

        # معالجة الفيديو: قصه ليصبح 9:16 (طولي)
        video = VideoFileClip("downloaded_video.mp4")

        # تحديد أبعاد الفيديو الجديد (على سبيل المثال 1080x1920)
        target_width = 1080
        target_height = 1920

        # قص وسط الفيديو أفقيًا ليناسب الطول
        w, h = video.size
        new_x = max(0, (w - target_width) // 2)
        video_cropped = video.crop(x1=new_x, y1=0, width=target_width, height=h)
        video_resized = video_cropped.resize(height=target_height)

        # إضافة الترجمة كـ TextClip
        clips = [video_resized]

        for segment in subtitles:
            txt = segment["text"].strip()
            start = segment["start"]
            end = segment["end"]

            txt_clip = (
                TextClip(txt, fontsize=48, font="Tajawal-Black", color="white", stroke_color="black", stroke_width=2, method="caption", size=(target_width * 0.9, None))
                .set_start(start)
                .set_duration(end - start)
                .set_position(("center", "bottom"))
            )
            clips.append(txt_clip)

        final_video = CompositeVideoClip(clips)
        output_filename = "output_shorts.mp4"
        final_video.write_videofile(output_filename, fps=video.fps, codec="libx264")

        st.success(f"تم إنشاء الفيديو القصير بنجاح: {output_filename}")
        st.video(output_filename)

        # حذف الملفات المؤقتة
        video.close()
        final_video.close()
        os.remove("downloaded_video.mp4")

    except Exception as e:
        st.error(f"❌ حدث خطأ: {e}")
