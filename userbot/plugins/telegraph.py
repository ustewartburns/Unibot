"""@telegraph Utilitas
Perintah yang tersedia:
.telegraph media saat balas ke media
.telegraph teks saat balas teks yang panjang"""
from telethon import events
import os
from PIL import Image
from datetime import datetime
from telegraph import Telegraph, upload_file, exceptions
from userbot.utils import admin_cmd

telegraph = Telegraph()
r = telegraph.create_account(short_name=Config.TELEGRAPH_SHORT_NAME)
auth_url = r["auth_url"]


@borg.on(admin_cmd("telegraph (media|teks) ?(.*)"))
async def _(event):
    if event.fwd_from:
        return
    if Config.PRIVATE_GROUP_BOT_API_ID is None:
        await event.edit("Silakan atur yang diperlukan environment variable `PRIVATE_GROUP_BOT_API_ID` agar plugin ini berfungsi")
        return
    if not os.path.isdir(Config.TMP_DOWNLOAD_DIRECTORY):
        os.makedirs(Config.TMP_DOWNLOAD_DIRECTORY)
    await borg.send_message(
        Config.PRIVATE_GROUP_BOT_API_ID,
        "Membuat akun Telegraph Baru {} untuk sesi saat ini. \n**Jangan berikan url ini kepada siapa pun, bahkan jika mereka mengatakan itu dari Telegram!**".format(auth_url)
    )
    optional_title = event.pattern_match.group(2)
    if event.reply_to_msg_id:
        start = datetime.now()
        r_message = await event.get_reply_message()
        input_str = event.pattern_match.group(1)
        if input_str == "media":
            downloaded_file_name = await borg.download_media(
                r_message,
                Config.TMP_DOWNLOAD_DIRECTORY
            )
            end = datetime.now()
            ms = (end - start).seconds
            await event.edit("Diunduh dalam {} waktu {} detik.".format(downloaded_file_name, ms))
            if downloaded_file_name.endswith((".webp")):
                resize_image(downloaded_file_name)
            try:
                start = datetime.now()
                media_urls = upload_file(downloaded_file_name)
            except exceptions.TelegraphException as exc:
                await event.edit("ERROR: " + str(exc))
                os.remove(downloaded_file_name)
            else:
                end = datetime.now()
                ms_two = (end - start).seconds
                os.remove(downloaded_file_name)
                await event.edit("Diunggah ke telegra.ph{} dalam {} detik.".format(media_urls[0], (ms + ms_two)), link_preview=True)
        elif input_str == "text":
            user_object = await borg.get_entity(r_message.from_id)
            title_of_page = user_object.first_name # + " " + user_object.last_name
            # apparently, all Users do not have last_name field
            if optional_title:
                title_of_page = optional_title
            page_content = r_message.message
            if r_message.media:
                if page_content != "":
                    title_of_page = page_content
                downloaded_file_name = await borg.download_media(
                    r_message,
                    Config.TMP_DOWNLOAD_DIRECTORY
                )
                m_list = None
                with open(downloaded_file_name, "rb") as fd:
                    m_list = fd.readlines()
                for m in m_list:
                    page_content += m.decode("UTF-8") + "\n"
                os.remove(downloaded_file_name)
            page_content = page_content.replace("\n", "<br>")
            response = telegraph.create_page(
                title_of_page,
                html_content=page_content
            )
            end = datetime.now()
            ms = (end - start).seconds
            await event.edit("Diunggah ke ke https://telegra.ph/{} dalam {} detik.".format(response["path"], ms), link_preview=True)
    else:
        await event.edit("Balas pesan Text atau Media untuk mendapatkan tautan telegra.ph secarapermanen. (Terinspirasi oleh @ControllerBot)")


def resize_image(image):
    im = Image.open(image)
    im.save(image, "PNG")
