import streamlit as st
import yt_dlp as youtube_dl
import whisper
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
import os

st.set_page_config(page_title="YouTube Shorts Maker", layout="centered")

st.title("🎬 صانع YouTube Shorts (بدون دمج تنسيقات)")

video_url = st.text_input("أدخل رابط فيديو يوتيوب")

if st.button("إنشاء شورت") and video_url:
    with st.spinner("جارٍ تحميل الفيديو..."):
        try:
            ydl_opts = {
                'format': 'best',  # تحميل أفضل صيغة فيديو واحدة فقط بدون دمج
                'outtmpl': 'downloaded_video.%(ext)s',
                'quiet': True,
                'no_warnings': True,
            }

            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_url])

            st.success("✅ تم تحميل الفيديو!")

            # استخدم whisper لاستخراج الترجمة
            st.info("🧠 جارٍ استخراج الترجمة...")
            model = whisper.load_model("base")
            result = model.transcribe("downloaded_video.mp4", language="ar")

            subtitles = result["text"]

            # عرض الترجمة
            st.text_area("الترجمة المستخرجة:", subtitles, height=150)

            # تحرير الفيديو لتنسيق 9:16 (شورت)
            st.info("🎥 جارٍ تعديل الفيديو للقياس الطولي (9:16)...")

            videoclip = VideoFileClip("downloaded_video.mp4")
            # تحديد الطول والعرض للقص
            width, height = videoclip.size
            new_width = 720
            new_height = 1280

            # قص الفيديو مركزيًا ليناسب القياس الطولي
            if width / height > new_width / new_height:
                # الفيديو أعرض من اللازم، قص من العرض
                new_clip = videoclip.crop(
                    x_center=width/2, width=height * new_width / new_height, y_center=height/2, height=height
                )
            else:
                # الفيديو أطول من اللازم، قص من الارتفاع
                new_clip = videoclip.crop(
                    x_center=width/2, width=width, y_center=height/2, height=width * new_height / new_width
                )

            # إعادة ضبط حجم الفيديو للقياس النهائي
            final_clip = new_clip.resize((new_width, new_height))

            # إضافة الترجمة على الفيديو (نص في أسفل الشاشة)
            txt_clip = TextClip(subtitles, fontsize=40, color='white', font='Arial-Bold', method='caption', size=(new_width-40, None))
            txt_clip = txt_clip.set_position(('center', new_height - 150)).set_duration(final_clip.duration).margin(bottom=20, opacity=0)

            video_final = CompositeVideoClip([final_clip, txt_clip])
            output_path = "short_video.mp4"
            video_final.write_videofile(output_path, codec="libx264", audio_codec="aac")

            st.success("✅ تم إنشاء الفيديو القصير!")

            # عرض الفيديو النهائي
            st.video(output_path)

            # حذف الملفات المؤقتة
            os.remove("downloaded_video.mp4")
            os.remove(output_path)

        except Exception as e:
            st.error(f"❌ حدث خطأ: {e}")
