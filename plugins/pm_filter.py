# THANKS TO NISHANT
# CREDIT @IM_NISHANTT
# PLZ.. DON'T REMOVE THIS CREDIT
# CONTACT FOR DOUBTS ON TG - @IM_NISHANT
#--------------------------------------------------------------------------👻👻👻👻👻👻--------------------------------------------------------------------------
import asyncio
import re
import ast
import math
import random
import os
lock = asyncio.Lock()
import pytz
from datetime import datetime, timedelta, date, time
from telegram import InputMediaPhoto
from pyrogram.errors.exceptions.bad_request_400 import MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty
from Script import script
import pyrogram
from database.connections_mdb import active_connection, all_connections, delete_connection, if_active, make_active, \
    make_inactive
from info import *
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, InputMediaPhoto, InputMediaVideo
from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait, UserIsBlocked, MessageNotModified, PeerIdInvalid
from utils import get_size, is_subscribed, get_poster, temp, get_settings, save_group_settings, get_shortlink, stream_site, get_text, imdb
from database.users_chats_db import db
from database.safari_reffer import sdb
from database.ia_filterdb import Media, get_file_details, get_search_results, get_bad_files

from fuzzywuzzy import process
TIMEZONE = "Asia/Kolkata"

import logging
from urllib.parse import quote_plus
from SAFARI.utils.file_properties import get_name, get_hash, get_media_file_size

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

BUTTONS = {}

@Client.on_message(filters.private & filters.text & filters.incoming)
async def pm_text(bot, message):
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id, message.from_user.first_name)
    await message.react(emoji=random.choice(REACTION), big=True)
    if message.text.startswith("/") or message.text.startswith("#"): return
    if await db.get_setting("PM_FILTER", default=PM_FILTER) or await db.has_premium_access(message.from_user.id):
        await auto_filter(bot, message)
    else:
        await message.reply_text("<b>ɪғ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ᴛᴀᴋᴇ ᴀ ᴍᴏᴠɪᴇ ғʀᴏᴍ ᴛʜᴇ ʙᴏᴛ ᴛʜᴇɴ ʏᴏᴜ ᴡɪʟʟ ʜᴀᴠᴇ ᴛᴏ ᴘᴀʏ ᴛʜᴇ ᴘʀᴇᴍɪᴜᴍ ғᴏʀ ᴛʜᴇ ʙᴏᴛ, ᴏᴛʜᴇʀᴡɪsᴇ ʏᴏᴜ ᴄᴀɴ ᴛᴀᴋᴇ ᴛʜᴇ ᴍᴏᴠɪᴇ ғʀᴏᴍ ᴛʜᴇ ɢʀᴏᴜᴘ</b>", reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Gʀᴏᴜᴘ Hᴇʀᴇ", url=GRP_LNK)],
            [InlineKeyboardButton('✨ Bʏ Pʀᴇᴍɪᴜᴍ : Sᴇᴀʀᴄʜ Pᴍ 🔎', callback_data=f'premium_info')]]))


@Client.on_message(filters.group & filters.text & filters.incoming)
async def give_filter(bot, message):
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id, message.from_user.first_name)  
    await message.react(emoji=random.choice(REACTION), big=True)
    is_verified = await db.check_group_verification(message.chat.id)
    is_rejected = await db.rejected_group(message.chat.id)
    user = await bot.get_chat_member(message.chat.id, message.from_user.id)
    total=await bot.get_chat_members_count(message.chat.id)
    owner=user.status in [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER] or str(message.from_user.id) in ADMINS
    if message.text.startswith("/") or message.text.startswith("#"): return 
    if not is_rejected:
        if is_verified:
            settings = await get_settings(message.chat.id)
            if settings['auto_ffilter']:
                await auto_filter(bot, message)
        else:
            if owner:
                await message.reply_text(text=f"Tʜɪs Gʀᴏᴜᴘ ɪs Nᴏᴛ Vᴇʀɪғɪᴇᴅ. Pʟᴇᴀsᴇ Usᴇ Tʜɪs /verify Cᴏᴍᴍᴀɴᴅ ᴛᴏ Vᴇʀɪғʏ Tʜᴇ Gʀᴏᴜᴘ.")
            else:
                await message.reply_text(text=f" I Cᴀɴɴᴏᴛ Gɪᴠᴇ Mᴏᴠɪᴇs ɪɴ Tʜɪs Gʀᴏᴜᴘ Bᴇᴄᴀᴜsᴇ Tʜɪs Gʀᴏᴜᴘ ɪs Nᴏᴛ Vᴇʀɪғɪᴇᴅ.")
    else:
        if owner:
            await message.reply_text(text=f"ʏᴏᴜʀ ɢʀᴏᴜᴘ ʜᴀs ʙᴇᴇɴ ʀᴇᴊᴇᴄᴛᴇᴅ. ᴄᴏɴᴛᴀᴄᴛ ᴍʏ ᴀᴅᴍɪɴ.\n@Safaridev")
        else:
            await message.reply_text(text=f"ᴛʜɪs ɢʀᴏᴜᴘ ɴᴏᴛ ᴠᴇʀɪғɪᴇᴅ")
        


@Client.on_callback_query(filters.regex(r"^next"))
async def next_page(bot, query):
    try:
        curr_time = datetime.now(pytz.timezone('Asia/Kolkata')).time()
        ident, req, key, offset = query.data.split("_")
        if int(req) not in [query.from_user.id, 0]:
            return await query.answer(script.ALRT_TXT.format(query.from_user.first_name), show_alert=True)
        try:
            offset = int(offset)
        except:
            offset = 0
        search = BUTTONS.get(key)
        files, n_offset, total = await get_search_results(query.message.chat.id, search, offset=offset, filter=True)
        try:
            n_offset = int(n_offset)
        except:
            n_offset = 0
    
        if not files:
            return
        settings = await get_settings(query.message.chat.id)
        temp.GETALL[key] = files
        temp.CHAT[query.from_user.id] = query.message.chat.id
        if not settings['button']:
            btn = [
                [
                    InlineKeyboardButton(
                        text=f"📁 [{get_size(file.file_size)}] ▷ {file.file_name}", callback_data=f'files#{file.file_id}'
                    ),
                ]
                for file in files
            ]
            btn.insert(0, [
                InlineKeyboardButton("♨️ ꜱᴇɴᴅ ᴀʟʟ ♨️", callback_data=f"sendfiles#{key}")
            ])
            btn.insert(0, [
                InlineKeyboardButton("sᴇᴀꜱᴏɴ", callback_data=f"seas#{req}"), 
                InlineKeyboardButton("ʏᴇᴀʀ", callback_data=f"select_year#{req}")
            ])
            btn.insert(0, [
                InlineKeyboardButton("ʟᴀɴɢᴜᴀɢᴇ", callback_data=f"select_lang#{req}"),
                InlineKeyboardButton("ǫᴜᴀʟɪᴛʏ", callback_data=f"quality#{req}")
            ])
        else:
            btn = []
            btn.insert(0, [
                InlineKeyboardButton("♨️ ꜱᴇɴᴅ ᴀʟʟ ♨️", callback_data=f"sendfiles#{key}")
            ])
            btn.insert(0, [
                InlineKeyboardButton("sᴇᴀꜱᴏɴ", callback_data=f"seas#{req}"), 
                InlineKeyboardButton("ʏᴇᴀʀ", callback_data=f"select_year#{req}")
            ])
            btn.insert(0, [
                InlineKeyboardButton("ʟᴀɴɢᴜᴀɢᴇ", callback_data=f"select_lang#{req}"),
                InlineKeyboardButton("ǫᴜᴀʟɪᴛʏ", callback_data=f"quality#{req}")
            ])
        try:
            if settings['max_btn']:
                if 0 < offset <= 10:
                    off_set = 0
                elif offset == 0:
                    off_set = None
                else:
                    off_set = offset - 10
                if n_offset == 0:
                    btn.append(
                        [InlineKeyboardButton("⌫ 𝐁𝐀𝐂𝐊", callback_data=f"next_{req}_{key}_{off_set}"), InlineKeyboardButton(f"{math.ceil(int(offset)/10)+1} / {math.ceil(total/10)}", callback_data="pages")]
                    )
                elif off_set is None:
                    btn.append([InlineKeyboardButton("𝐏𝐀𝐆𝐄", callback_data="pages"), InlineKeyboardButton(f"{math.ceil(int(offset)/10)+1} / {math.ceil(total/10)}", callback_data="pages"), InlineKeyboardButton("𝐍𝐄𝐗𝐓 ➪", callback_data=f"next_{req}_{key}_{n_offset}")])
                else:
                    btn.append(
                        [
                            InlineKeyboardButton("⌫ 𝐁𝐀𝐂𝐊", callback_data=f"next_{req}_{key}_{off_set}"),
                            InlineKeyboardButton(f"{math.ceil(int(offset)/10)+1} / {math.ceil(total/10)}", callback_data="pages"),
                            InlineKeyboardButton("𝐍𝐄𝐗𝐓 ➪", callback_data=f"next_{req}_{key}_{n_offset}")
                        ],
                    )
            else:
                if 0 < offset <= int(MAX_B_TN):
                    off_set = 0
                elif offset == 0:
                    off_set = None
                else:
                    off_set = offset - int(MAX_B_TN)
                if n_offset == 0:
                    btn.append(
                        [InlineKeyboardButton("⌫ 𝐁𝐀𝐂𝐊", callback_data=f"next_{req}_{key}_{off_set}"), InlineKeyboardButton(f"{math.ceil(int(offset)/int(MAX_B_TN))+1} / {math.ceil(total/int(MAX_B_TN))}", callback_data="pages")]
                    )
                elif off_set is None:
                    btn.append([InlineKeyboardButton("𝐏𝐀𝐆𝐄", callback_data="pages"), InlineKeyboardButton(f"{math.ceil(int(offset)/int(MAX_B_TN))+1} / {math.ceil(total/int(MAX_B_TN))}", callback_data="pages"), InlineKeyboardButton("𝐍𝐄𝐗𝐓 ➪", callback_data=f"next_{req}_{key}_{n_offset}")])
                else:
                    btn.append(
                        [
                            InlineKeyboardButton("⌫ 𝐁𝐀𝐂𝐊", callback_data=f"next_{req}_{key}_{off_set}"),
                            InlineKeyboardButton(f"{math.ceil(int(offset)/int(MAX_B_TN))+1} / {math.ceil(total/int(MAX_B_TN))}", callback_data="pages"),
                            InlineKeyboardButton("𝐍𝐄𝐗𝐓 ➪", callback_data=f"next_{req}_{key}_{n_offset}")
                        ],
                    )
        except KeyError:
            await save_group_settings(query.message.chat.id, 'max_btn', True)
            if 0 < offset <= 10:
                off_set = 0
            elif offset == 0:
                off_set = None
            else:
                off_set = offset - 10
            if n_offset == 0:
                btn.append(
                    [InlineKeyboardButton("⌫ 𝐁𝐀𝐂𝐊", callback_data=f"next_{req}_{key}_{off_set}"), InlineKeyboardButton(f"{math.ceil(int(offset)/10)+1} / {math.ceil(total/10)}", callback_data="pages")]
                )
            elif off_set is None:
                btn.append([InlineKeyboardButton("𝐏𝐀𝐆𝐄", callback_data="pages"), InlineKeyboardButton(f"{math.ceil(int(offset)/10)+1} / {math.ceil(total/10)}", callback_data="pages"), InlineKeyboardButton("𝐍𝐄𝐗𝐓 ➪", callback_data=f"next_{req}_{key}_{n_offset}")])
            else:
                btn.append(
                    [
                        InlineKeyboardButton("⌫ 𝐁𝐀𝐂𝐊", callback_data=f"next_{req}_{key}_{off_set}"),
                        InlineKeyboardButton(f"{math.ceil(int(offset)/10)+1} / {math.ceil(total/10)}", callback_data="pages"),
                        InlineKeyboardButton("𝐍𝐄𝐗𝐓 ➪", callback_data=f"next_{req}_{key}_{n_offset}")
                    ],
                )
        if settings.get("button", BUTTON_MODE):
            cur_time = datetime.now(pytz.timezone('Asia/Kolkata')).time()
            time_difference = timedelta(hours=cur_time.hour, minutes=cur_time.minute, seconds=(cur_time.second+(cur_time.microsecond/1000000))) - timedelta(hours=curr_time.hour, minutes=curr_time.minute, seconds=(curr_time.second+(curr_time.microsecond/1000000)))
            remaining_seconds = "{:.2f}".format(time_difference.total_seconds())
            cap = await get_text(settings, remaining_seconds, files, query, total, search)
            try:
                await query.message.edit_text(text=cap, reply_markup=InlineKeyboardMarkup(btn))
            except MessageNotModified:
                pass
        else:
            try:
                await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(btn))
            except MessageNotModified:
                pass
            await query.answer()
    except Exception as e:
        await query.answer(f"error found out\n\n{e}", show_alert=True)
        return
        
@Client.on_callback_query(filters.regex(r"^year"))
async def year_check(bot, query):
    try:
        curr_time = datetime.now(pytz.timezone('Asia/Kolkata')).time()
        _, userid, year = query.data.split("#")
        if int(userid) not in [query.from_user.id, 0]:
            return await query.answer(script.ALRT_TXT.format(query.from_user.first_name), show_alert=True)
        if year == "unknown":
            return await query.answer("Sᴇʟᴇᴄᴛ ᴀɴʏ ʟᴀɴɢᴜᴀɢᴇ ғʀᴏᴍ ᴛʜᴇ ʙᴇʟᴏᴡ ʙᴜᴛᴛᴏɴs !", show_alert=True)
        movie = temp.KEYWORD.get(query.from_user.id)
        if year != "home"
            movie = f"{movie} {year}"
        files, offset, total_results = await get_search_results(query.message.chat.id, movie, offset=0, filter=True)
        if files:
            settings = await get_settings(query.message.chat.id)
            key = f"{query.message.chat.id}-{query.message.id}"
            temp.GETALL[key] = files
            temp.CHAT[query.from_user.id] = query.message.chat.id
            if not settings['button']:
            btn = [
                    [
                        InlineKeyboardButton(
                            text=f"📁 [{get_size(file.file_size)}] ▷ {file.file_name}", callback_data=f'files#{file.file_id}'
                        ),
                    ]
                    for file in files
                ]
                btn.insert(0, [
                InlineKeyboardButton("♨️ ꜱᴇɴᴅ ᴀʟʟ ♨️", callback_data=f"sendfiles#{key}")
            ])
            btn.insert(0, [
                InlineKeyboardButton("sᴇᴀꜱᴏɴ", callback_data=f"seas#{req}"), 
                InlineKeyboardButton("ʏᴇᴀʀ", callback_data=f"select_year#{req}")
            ])
            btn.insert(0, [
                InlineKeyboardButton("ʟᴀɴɢᴜᴀɢᴇ", callback_data=f"select_lang#{req}"),
                InlineKeyboardButton("ǫᴜᴀʟɪᴛʏ", callback_data=f"quality#{req}")
            ])
            else:
                btn = []
                btn.insert(0, [
                InlineKeyboardButton("♨️ ꜱᴇɴᴅ ᴀʟʟ ♨️", callback_data=f"sendfiles#{key}")
            ])
            btn.insert(0, [
                InlineKeyboardButton("sᴇᴀꜱᴏɴ", callback_data=f"seas#{req}"), 
                InlineKeyboardButton("ʏᴇᴀʀ", callback_data=f"epi#{req}")
            ])
            btn.insert(0, [
                InlineKeyboardButton("ʟᴀɴɢᴜᴀɢᴇ", callback_data=f"select_lang#{req}"),
                InlineKeyboardButton("ǫᴜᴀʟɪᴛʏ", callback_data=f"quality#{req}")
            ])
    
            if offset != "":
                BUTTONS[key] = movie
                req = userid
                try:
                    if settings['max_btn']:
                        btn.append(
                            [InlineKeyboardButton("𝐏𝐀𝐆𝐄", callback_data="pages"), InlineKeyboardButton(text=f"1/{math.ceil(int(total_results)/10)}",callback_data="pages"), InlineKeyboardButton(text="𝐍𝐄𝐗𝐓 ➪",callback_data=f"next_{req}_{key}_{offset}")]
                        )
    
                    else:
                        btn.append(
                            [InlineKeyboardButton("𝐏𝐀𝐆𝐄", callback_data="pages"), InlineKeyboardButton(text=f"1/{math.ceil(int(total_results)/int(MAX_B_TN))}",callback_data="pages"), InlineKeyboardButton(text="𝐍𝐄𝐗𝐓 ➪",callback_data=f"next_{req}_{key}_{offset}")]
                        )
                except KeyError:
                    await save_group_settings(query.message.chat.id, 'max_btn', True)
                    btn.append(
                        [InlineKeyboardButton("𝐏𝐀𝐆𝐄", callback_data="pages"), InlineKeyboardButton(text=f"1/{math.ceil(int(total_results)/10)}",callback_data="pages"), InlineKeyboardButton(text="𝐍𝐄𝐗𝐓 ➪",callback_data=f"next_{req}_{key}_{offset}")]
                    )
            else:
                btn.append(
                    [InlineKeyboardButton(text="𝐍𝐎 𝐌𝐎𝐑𝐄 𝐏𝐀𝐆𝐄𝐒 𝐀𝐕𝐀𝐈𝐋𝐀𝐁𝐋𝐄",callback_data="pages")]
                )
            if settings.get("button", BUTTON_MODE):
                cur_time = datetime.now(pytz.timezone('Asia/Kolkata')).time()
                time_difference = timedelta(hours=cur_time.hour, minutes=cur_time.minute, seconds=(cur_time.second+(cur_time.microsecond/1000000))) - timedelta(hours=curr_time.hour, minutes=curr_time.minute, seconds=(curr_time.second+(curr_time.microsecond/1000000)))
                remaining_seconds = "{:.2f}".format(time_difference.total_seconds())
                cap = await get_text(settings, remaining_seconds, files, query, total_results, movie)
                try:
                    await query.message.edit_text(text=cap, reply_markup=InlineKeyboardMarkup(btn))
                except MessageNotModified:
                    pass
            else:
                try:
                    await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(btn))
                except MessageNotModified:
                    pass
                await query.answer()
        else:
            return await query.answer(f"Sᴏʀʀʏ, Nᴏ ғɪʟᴇs ғᴏᴜɴᴅ ғᴏʀ ʏᴏᴜʀ ᴏ̨ᴜᴇʀʏ {movie}.", show_alert=True)
    except Exception as e:
            await query.answer(f"error found out\n\n{e}", show_alert=True)
            return
    
@Client.on_callback_query(filters.regex(r"^select_year"))
async def select_year(bot, query):
    _, userid = query.data.split("#")
    curr_time = datetime.now(pytz.timezone('Asia/Kolkata')).time()
    if int(userid) not in [query.from_user.id, 0]:
        return await query.answer(script.ALRT_TXT.format(query.from_user.first_name), show_alert=True)
    btn = [[
        InlineKeyboardButton("Sᴇʟᴇᴄᴛ Yᴏᴜʀ Dᴇꜱɪʀᴇᴅ Lᴀɴɢᴜᴀɢᴇ ↓↓", callback_data=f"year#{userid}#unknown")
    ],[
        InlineKeyboardButton("𝟷𝟿𝟿𝟶", callback_data=f"year#{userid}#1990"),
        InlineKeyboardButton("𝟷𝟿𝟿𝟷", callback_data=f"year#{userid}#1991"),
        InlineKeyboardButton("𝟷𝟿𝟿𝟸", callback_data=f"year#{userid}#1992"),
        InlineKeyboardButton("𝟷𝟿𝟿𝟹", callback_data=f"year#{userid}#1993"),
        InlineKeyboardButton("𝟷𝟿𝟿𝟺", callback_data=f"year#{userid}#1994")
    ],[
        InlineKeyboardButton("𝟷𝟿𝟿𝟻", callback_data=f"year#{userid}#1995"),        
        InlineKeyboardButton("𝟷𝟿𝟿𝟼", callback_data=f"year#{userid}#1996"),
        InlineKeyboardButton("𝟷𝟿𝟿𝟽", callback_data=f"year#{userid}#1997"),
        InlineKeyboardButton("𝟷𝟿𝟿𝟾", callback_data=f"year#{userid}#1998"),
        InlineKeyboardButton("𝟷𝟿𝟿𝟿", callback_data=f"year#{userid}#1999")
    ],[
        InlineKeyboardButton("𝟸𝟶𝟶𝟶", callback_data=f"year#{userid}#2000"),
        InlineKeyboardButton("𝟸𝟶𝟶𝟷", callback_data=f"lang#{userid}#2001"),
        InlineKeyboardButton("𝟸𝟶𝟶𝟸", callback_data=f"year#{userid}#2002"),
        InlineKeyboardButton("𝟸𝟶𝟶𝟹", callback_data=f"year#{userid}#2003"),
        InlineKeyboardButton("𝟸𝟶𝟶𝟺", callback_data=f"year#{userid}#2004")
     ],[
        InlineKeyboardButton("𝟸𝟶𝟶𝟻", callback_data=f"year#{userid}#2005"),
        InlineKeyboardButton("𝟸𝟶𝟶𝟼", callback_data=f"year#{userid}#2006"),
        InlineKeyboardButton("𝟸𝟶𝟶𝟽", callback_data=f"year#{userid}#2007"),
        InlineKeyboardButton("𝟸𝟶𝟶𝟾", callback_data=f"year#{userid}#2008"),
        InlineKeyboardButton("𝟸𝟶𝟶𝟿", callback_data=f"year#{userid}#2009")
     ],[
        InlineKeyboardButton("𝟸𝟶𝟷𝟶", callback_data=f"year#{userid}#2010"),
        InlineKeyboardButton("𝟸𝟶𝟷𝟷", callback_data=f"year#{userid}#2011"),
        InlineKeyboardButton("𝟸𝟶𝟷𝟸", callback_data=f"year#{userid}#2012"),
        InlineKeyboardButton("𝟸𝟶𝟷𝟹", callback_data=f"year#{userid}#2013"),
        InlineKeyboardButton("𝟸𝟶𝟷𝟺", callback_data=f"year#{userid}#2014")
     ],[
        InlineKeyboardButton("𝟸𝟶𝟷𝟻", callback_data=f"year#{userid}#2015"),
        InlineKeyboardButton("𝟸𝟶𝟷𝟼", callback_data=f"year#{userid}#2016"),
        InlineKeyboardButton("𝟸𝟶𝟷𝟽", callback_data=f"year#{userid}#2017"),
        InlineKeyboardButton("𝟸𝟶𝟷𝟾", callback_data=f"year#{userid}#2018"),
        InlineKeyboardButton("𝟸𝟶𝟷𝟿", callback_data=f"year#{userid}#2019")
     ],[
        InlineKeyboardButton("𝟸𝟶𝟸𝟶", callback_data=f"year#{userid}#2020"),
        InlineKeyboardButton("𝟸𝟶𝟸𝟷", callback_data=f"year#{userid}#2021"),
        InlineKeyboardButton("𝟸𝟶𝟸𝟸", callback_data=f"year#{userid}#2022"),
        InlineKeyboardButton("𝟸𝟶𝟸𝟹", callback_data=f"year#{userid}#2023"),
        InlineKeyboardButton("𝟸𝟶𝟸𝟺", callback_data=f"year#{userid}#2024")
     ],[
        InlineKeyboardButton("𝟸𝟶𝟸𝟻", callback_data=f"year#{userid}#2025")
     ],[      
        InlineKeyboardButton("⋞ ʙᴀᴄᴋ", callback_data=f"year#{userid}#home")
    ]]
    try:
       await query.edit_message_reply_markup(
           reply_markup=InlineKeyboardMarkup(btn)
       )
    except MessageNotModified:
        pass
    await query.answer()
    
    
@Client.on_callback_query(filters.regex(r"^lang"))
async def language_check(bot, query):
    try:
        curr_time = datetime.now(pytz.timezone('Asia/Kolkata')).time()
        _, userid, language = query.data.split("#")
        if int(userid) not in [query.from_user.id, 0]:
            return await query.answer(script.ALRT_TXT.format(query.from_user.first_name), show_alert=True)
        if language == "unknown":
            return await query.answer("Sᴇʟᴇᴄᴛ ᴀɴʏ ʟᴀɴɢᴜᴀɢᴇ ғʀᴏᴍ ᴛʜᴇ ʙᴇʟᴏᴡ ʙᴜᴛᴛᴏɴs !", show_alert=True)
        movie = temp.KEYWORD.get(query.from_user.id)
        if language != "home":
            movie = f"{movie} {language}"
        files, offset, total_results = await get_search_results(query.message.chat.id, movie, offset=0, filter=True)
        if files:
            settings = await get_settings(query.message.chat.id)
            key = f"{query.message.chat.id}-{query.message.id}"
            temp.GETALL[key] = files
            temp.CHAT[query.from_user.id] = query.message.chat.id
            if not settings['button']:
                btn = [
                    [
                        InlineKeyboardButton(
                            text=f"📁 [{get_size(file.file_size)}] ▷ {file.file_name}", callback_data=f'files#{file.file_id}'
                        ),
                    ]
                    for file in files
                ]
                btn.insert(0, [
                InlineKeyboardButton("♨️ ꜱᴇɴᴅ ᴀʟʟ ♨️", callback_data=f"sendfiles#{key}")
            ])
            btn.insert(0, [
                InlineKeyboardButton("sᴇᴀꜱᴏɴ", callback_data=f"seas#{req}"), 
                InlineKeyboardButton("ʏᴇᴀʀ", callback_data=f"select_year#{req}")
            ])
            btn.insert(0, [
                InlineKeyboardButton("ʟᴀɴɢᴜᴀɢᴇ", callback_data=f"select_lang#{req}"),
                InlineKeyboardButton("ǫᴜᴀʟɪᴛʏ", callback_data=f"quality#{req}")
            ])
            else:
                btn = []
                btn.insert(0, [
                InlineKeyboardButton("♨️ ꜱᴇɴᴅ ᴀʟʟ ♨️", callback_data=f"sendfiles#{key}")
            ])
            btn.insert(0, [
                InlineKeyboardButton("sᴇᴀꜱᴏɴ", callback_data=f"seas#{req}"), 
                InlineKeyboardButton("ʏᴇᴀʀ", callback_data=f"select_year#{req}")
            ])
            btn.insert(0, [
                InlineKeyboardButton("ʟᴀɴɢᴜᴀɢᴇ", callback_data=f"select_lang#{req}"),
                InlineKeyboardButton("ǫᴜᴀʟɪᴛʏ", callback_data=f"quality#{req}")
            ])
    
            if offset != "":
                BUTTONS[key] = movie
                req = userid
                try:
                    if settings['max_btn']:
                        btn.append(
                            [InlineKeyboardButton("𝐏𝐀𝐆𝐄", callback_data="pages"), InlineKeyboardButton(text=f"1/{math.ceil(int(total_results)/10)}",callback_data="pages"), InlineKeyboardButton(text="𝐍𝐄𝐗𝐓 ➪",callback_data=f"next_{req}_{key}_{offset}")]
                        )
    
                    else:
                        btn.append(
                            [InlineKeyboardButton("𝐏𝐀𝐆𝐄", callback_data="pages"), InlineKeyboardButton(text=f"1/{math.ceil(int(total_results)/int(MAX_B_TN))}",callback_data="pages"), InlineKeyboardButton(text="𝐍𝐄𝐗𝐓 ➪",callback_data=f"next_{req}_{key}_{offset}")]
                        )
                except KeyError:
                    await save_group_settings(query.message.chat.id, 'max_btn', True)
                    btn.append(
                        [InlineKeyboardButton("𝐏𝐀𝐆𝐄", callback_data="pages"), InlineKeyboardButton(text=f"1/{math.ceil(int(total_results)/10)}",callback_data="pages"), InlineKeyboardButton(text="𝐍𝐄𝐗𝐓 ➪",callback_data=f"next_{req}_{key}_{offset}")]
                    )
            else:
                btn.append(
                    [InlineKeyboardButton(text="𝐍𝐎 𝐌𝐎𝐑𝐄 𝐏𝐀𝐆𝐄𝐒 𝐀𝐕𝐀𝐈𝐋𝐀𝐁𝐋𝐄",callback_data="pages")]
                )
            if settings.get("button", BUTTON_MODE):
                cur_time = datetime.now(pytz.timezone('Asia/Kolkata')).time()
                time_difference = timedelta(hours=cur_time.hour, minutes=cur_time.minute, seconds=(cur_time.second+(cur_time.microsecond/1000000))) - timedelta(hours=curr_time.hour, minutes=curr_time.minute, seconds=(curr_time.second+(curr_time.microsecond/1000000)))
                remaining_seconds = "{:.2f}".format(time_difference.total_seconds())
                cap = await get_text(settings, remaining_seconds, files, query, total_results, movie)
                try:
                    await query.message.edit_text(text=cap, reply_markup=InlineKeyboardMarkup(btn))
                except MessageNotModified:
                    pass
            else:
                try:
                    await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(btn))
                except MessageNotModified:
                    pass
                await query.answer()
        else:
            return await query.answer(f"Sᴏʀʀʏ, Nᴏ ғɪʟᴇs ғᴏᴜɴᴅ ғᴏʀ ʏᴏᴜʀ ᴏ̨ᴜᴇʀʏ {movie}.", show_alert=True)
    except Exception as e:
            await query.answer(f"error found out\n\n{e}", show_alert=True)
            return
    
@Client.on_callback_query(filters.regex(r"^select_lang"))
async def select_language(bot, query):
    _, userid = query.data.split("#")
    curr_time = datetime.now(pytz.timezone('Asia/Kolkata')).time()
    if int(userid) not in [query.from_user.id, 0]:
        return await query.answer(script.ALRT_TXT.format(query.from_user.first_name), show_alert=True)
    btn = [[
        InlineKeyboardButton("Sᴇʟᴇᴄᴛ Yᴏᴜʀ Dᴇꜱɪʀᴇᴅ Lᴀɴɢᴜᴀɢᴇ ↓↓", callback_data=f"lang#{userid}#unknown")
    ],[
        InlineKeyboardButton("Eɴɢʟɪꜱʜ", callback_data=f"lang#{userid}#eng"),
        InlineKeyboardButton("Tᴀᴍɪʟ", callback_data=f"lang#{userid}#tam")
    ],[
        InlineKeyboardButton("Hɪɴᴅɪ", callback_data=f"lang#{userid}#hin"),
        InlineKeyboardButton("Tᴇʟᴜɢᴜ", callback_data=f"lang#{userid}#tel")
    ],[
        InlineKeyboardButton("Kᴀɴɴᴀᴅᴀ", callback_data=f"lang#{userid}#kan"),
        InlineKeyboardButton("Mᴀʟᴀʏᴀʟᴀᴍ", callback_data=f"lang#{userid}#mal")        
    ],[
        InlineKeyboardButton("Gᴜᴊᴀʀᴀᴛɪ", callback_data=f"lang#{userid}#guj"),
        InlineKeyboardButton("Mᴀʀᴀᴛʜɪ", callback_data=f"lang#{userid}#mar"),
        InlineKeyboardButton("Pᴜɴᴊᴀʙɪ", callback_data=f"lang#{userid}#pun")
    ],[
        InlineKeyboardButton("Mᴜʟᴛɪ Aᴜᴅɪᴏ", callback_data=f"lang#{userid}#multi"),
        InlineKeyboardButton("Dᴜᴀʟ Aᴜᴅɪᴏ", callback_data=f"lang#{userid}#dual")
    ],[
        InlineKeyboardButton("⋞ ʙᴀᴄᴋ", callback_data=f"lang#{userid}#home")
    ]]
    try:
       await query.edit_message_reply_markup(
           reply_markup=InlineKeyboardMarkup(btn)
       )
    except MessageNotModified:
        pass
    await query.answer()

@Client.on_callback_query(filters.regex(r"^lusifilms"))
async def quality_check(bot, query):
    try:
        curr_time = datetime.now(pytz.timezone('Asia/Kolkata')).time()
        _, userid, quality = query.data.split("#")
        if int(userid) not in [query.from_user.id, 0]:
            return await query.answer(script.ALRT_TXT.format(query.from_user.first_name), show_alert=True)
        if quality == "unknown":
            return await query.answer("Sᴇʟᴇᴄᴛ ᴀɴʏ Qᴜᴀʟɪᴛʏꜱ ғʀᴏᴍ ᴛʜᴇ ʙᴇʟᴏᴡ ʙᴜᴛᴛᴏɴs !", show_alert=True)
        movie = temp.KEYWORD.get(query.from_user.id)
        if quality != "home":
            movie = f"{movie} {quality}"
        files, offset, total_results = await get_search_results(query.message.chat.id, movie, offset=0, filter=True)
        if files:
            settings = await get_settings(query.message.chat.id)
            key = f"{query.message.chat.id}-{query.message.id}"
            temp.GETALL[key] = files
            temp.CHAT[query.from_user.id] = query.message.chat.id
            if not settings['button']:
                btn = [
                    [
                        InlineKeyboardButton(
                            text=f"📁 [{get_size(file.file_size)}] ▷ {file.file_name}", callback_data=f'files#{file.file_id}'
                        ),
                    ]
                    for file in files
                ]
                btn.insert(0, [
                InlineKeyboardButton("♨️ ꜱᴇɴᴅ ᴀʟʟ ♨️", callback_data=f"sendfiles#{key}")
            ])
            btn.insert(0, [
                InlineKeyboardButton("sᴇᴀꜱᴏɴ", callback_data=f"seas#{req}"), 
                InlineKeyboardButton("ʏᴇᴀʀ", callback_data=f"select_year#{req}")
            ])
            btn.insert(0, [
                InlineKeyboardButton("ʟᴀɴɢᴜᴀɢᴇ", callback_data=f"select_lang#{req}"),
                InlineKeyboardButton("ǫᴜᴀʟɪᴛʏ", callback_data=f"quality#{req}")
            ])
            else:
                btn = []
                btn.insert(0, [
                InlineKeyboardButton("♨️ ꜱᴇɴᴅ ᴀʟʟ ♨️", callback_data=f"sendfiles#{key}")
            ])
            btn.insert(0, [
                InlineKeyboardButton("sᴇᴀꜱᴏɴ", callback_data=f"seas#{req}"), 
                InlineKeyboardButton("ʏᴇᴀʀ", callback_data=f"select_year#{req}")
            ])
            btn.insert(0, [
                InlineKeyboardButton("ʟᴀɴɢᴜᴀɢᴇ", callback_data=f"select_lang#{req}"),
                InlineKeyboardButton("ǫᴜᴀʟɪᴛʏ", callback_data=f"quality#{req}")
            ])
            if offset != "":
                BUTTONS[key] = movie
                req = userid
                try:
                    if settings['max_btn']:
                        btn.append(
                            [InlineKeyboardButton("𝐏𝐀𝐆𝐄", callback_data="pages"), InlineKeyboardButton(text=f"1/{math.ceil(int(total_results)/10)}",callback_data="pages"), InlineKeyboardButton(text="𝐍𝐄𝐗𝐓 ➪",callback_data=f"next_{req}_{key}_{offset}")]
                        )
    
                    else:
                        btn.append(
                            [InlineKeyboardButton("𝐏𝐀𝐆𝐄", callback_data="pages"), InlineKeyboardButton(text=f"1/{math.ceil(int(total_results)/int(MAX_B_TN))}",callback_data="pages"), InlineKeyboardButton(text="𝐍𝐄𝐗𝐓 ➪",callback_data=f"next_{req}_{key}_{offset}")]
                        )
                except KeyError:
                    await save_group_settings(query.message.chat.id, 'max_btn', True)
                    btn.append(
                        [InlineKeyboardButton("𝐏𝐀𝐆𝐄", callback_data="pages"), InlineKeyboardButton(text=f"1/{math.ceil(int(total_results)/10)}",callback_data="pages"), InlineKeyboardButton(text="𝐍𝐄𝐗𝐓 ➪",callback_data=f"next_{req}_{key}_{offset}")]
                    )
            else:
                btn.append(
                    [InlineKeyboardButton(text="𝐍𝐎 𝐌𝐎𝐑𝐄 𝐏𝐀𝐆𝐄𝐒 𝐀𝐕𝐀𝐈𝐋𝐀𝐁𝐋𝐄",callback_data="pages")]
                )
            if settings.get("button", BUTTON_MODE):
                cur_time = datetime.now(pytz.timezone('Asia/Kolkata')).time()
                time_difference = timedelta(hours=cur_time.hour, minutes=cur_time.minute, seconds=(cur_time.second+(cur_time.microsecond/1000000))) - timedelta(hours=curr_time.hour, minutes=curr_time.minute, seconds=(curr_time.second+(curr_time.microsecond/1000000)))
                remaining_seconds = "{:.2f}".format(time_difference.total_seconds())
                cap = await get_text(settings, remaining_seconds, files, query, total_results, movie)
                try:
                    await query.message.edit_text(text=cap, reply_markup=InlineKeyboardMarkup(btn))
                except MessageNotModified:
                    pass
            else:
                try:
                    await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(btn))
                except MessageNotModified:
                    pass
                await query.answer()
        else:
            return await query.answer(f"Sᴏʀʀʏ, Nᴏ ғɪʟᴇs ғᴏᴜɴᴅ ғᴏʀ ʏᴏᴜʀ ᴏ̨ᴜᴇʀʏ {movie}.", show_alert=True)
    except Exception as e:
            await query.answer(f"error found out\n\n{e}", show_alert=True)
            return

@Client.on_callback_query(filters.regex(r"^quality"))
async def select_quality(bot, query):
    _, userid = query.data.split("#")
    curr_time = datetime.now(pytz.timezone('Asia/Kolkata')).time()
    if int(userid) not in [query.from_user.id, 0]:
        return await query.answer(script.ALRT_TXT.format(query.from_user.first_name), show_alert=True)
    btn = [[
        InlineKeyboardButton("Sᴇʟᴇᴄᴛ Yᴏᴜʀ Dᴇꜱɪʀᴇᴅ Qᴜᴀʟɪᴛʏꜱ ↓↓", callback_data=f"lusifilms#{userid}#unknown")
    ],[
        InlineKeyboardButton("𝟺𝟾𝟶ᴘ", callback_data=f"lusifilms#{userid}#480p"),
        InlineKeyboardButton("𝟽𝟸𝟶ᴘ", callback_data=f"lusifilms#{userid}#720p")
    ],[
        InlineKeyboardButton("𝟷𝟶𝟾𝟶ᴘ", callback_data=f"lusifilms#{userid}#1080p"),
        InlineKeyboardButton("𝟷𝟶𝟾𝟶ᴘ ʜǫ", callback_data=f"lusifilms#{userid}#1080p HQ")
    ],[
        InlineKeyboardButton("𝟷𝟺𝟺𝟶ᴘ", callback_data=f"lusifilms#{userid}#1440p"),
        InlineKeyboardButton("𝟸𝟷𝟼𝟶ᴘ", callback_data=f"lusifilms#{userid}#2160p")
    ],[
        InlineKeyboardButton("⋞ ʙᴀᴄᴋ", callback_data=f"lusifilms#{userid}#home")
    ]]
    try:
       await query.edit_message_reply_markup(
           reply_markup=InlineKeyboardMarkup(btn)
       )
        except MessageNotModified:
        pass
    await query.answer()
    
@Client.on_callback_query(filters.regex(r"^seasons"))
async def seasons_check(bot, query):
    try:
        curr_time = datetime.now(pytz.timezone('Asia/Kolkata')).time()
        _, userid, seasons = query.data.split("#")
        if int(userid) not in [query.from_user.id, 0]:
            return await query.answer(script.ALRT_TXT.format(query.from_user.first_name), show_alert=True)
        if seasons == "unknown":
            return await query.answer("Sᴇʟᴇᴄᴛ ᴀɴʏ Sᴇᴀꜱᴏɴꜱ ғʀᴏᴍ ᴛʜᴇ ʙᴇʟᴏᴡ ʙᴜᴛᴛᴏɴs !", show_alert=True)
        movie = temp.KEYWORD.get(query.from_user.id)
        if seasons != "home":
            movie = f"{movie} {seasons}"
        files, offset, total_results = await get_search_results(query.message.chat.id, movie, offset=0, filter=True)
        if files:
            settings = await get_settings(query.message.chat.id)
            key = f"{query.message.chat.id}-{query.message.id}"
            temp.GETALL[key] = files
            temp.CHAT[query.from_user.id] = query.message.chat.id
            if not settings['button']:
                btn = [
                    [
                        InlineKeyboardButton(
                            text=f"[{get_size(file.file_size)}] {file.file_name}", callback_data=f'files#{file.file_id}'
                        ),
                    ]
                    for file in files
                ]
                btn.insert(0, [
                InlineKeyboardButton("♨️ ꜱᴇɴᴅ ᴀʟʟ ♨️", callback_data=f"sendfiles#{key}")
            ])
            btn.insert(0, [
                InlineKeyboardButton("sᴇᴀꜱᴏɴ", callback_data=f"seas#{req}"), 
                InlineKeyboardButton("ʏᴇᴀʀ", callback_data=f"select_year#{req}")
            ])
            btn.insert(0, [
                InlineKeyboardButton("ʟᴀɴɢᴜᴀɢᴇ", callback_data=f"select_lang#{req}"),
                InlineKeyboardButton("ǫᴜᴀʟɪᴛʏ", callback_data=f"quality#{req}")
            ])
            else:
                btn = []
                btn.insert(0, [
                InlineKeyboardButton("♨️ ꜱᴇɴᴅ ᴀʟʟ ♨️", callback_data=f"sendfiles#{key}")
            ])
            btn.insert(0, [
                InlineKeyboardButton("sᴇᴀꜱᴏɴ", callback_data=f"seas#{req}"), 
                InlineKeyboardButton("ʏᴇᴀʀ", callback_data=f"select_year#{req}")
            ])
            btn.insert(0, [
                InlineKeyboardButton("ʟᴀɴɢᴜᴀɢᴇ", callback_data=f"select_lang#{req}"),
                InlineKeyboardButton("ǫᴜᴀʟɪᴛʏ", callback_data=f"quality#{req}")
            ])
            if offset != "":
                BUTTONS[key] = movie
                req = userid
                try:
                    if settings['max_btn']:
                        btn.append(
                            [InlineKeyboardButton("𝐏𝐀𝐆𝐄", callback_data="pages"), InlineKeyboardButton(text=f"1/{math.ceil(int(total_results)/10)}",callback_data="pages"), InlineKeyboardButton(text="𝐍𝐄𝐗𝐓 ➪",callback_data=f"next_{req}_{key}_{offset}")]
                        )
    
                    else:
                        btn.append(
                            [InlineKeyboardButton("𝐏𝐀𝐆𝐄", callback_data="pages"), InlineKeyboardButton(text=f"1/{math.ceil(int(total_results)/int(MAX_B_TN))}",callback_data="pages"), InlineKeyboardButton(text="𝐍𝐄𝐗𝐓 ➪",callback_data=f"next_{req}_{key}_{offset}")]
                        )
                except KeyError:
                    await save_group_settings(query.message.chat.id, 'max_btn', True)
                    btn.append(
                        [InlineKeyboardButton("𝐏𝐀𝐆𝐄", callback_data="pages"), InlineKeyboardButton(text=f"1/{math.ceil(int(total_results)/10)}",callback_data="pages"), InlineKeyboardButton(text="𝐍𝐄𝐗𝐓 ➪",callback_data=f"next_{req}_{key}_{offset}")]
                    )
            else:
                btn.append(
                    [InlineKeyboardButton(text="𝐍𝐎 𝐌𝐎𝐑𝐄 𝐏𝐀𝐆𝐄𝐒 𝐀𝐕𝐀𝐈𝐋𝐀𝐁𝐋𝐄",callback_data="pages")]
                )
            if settings.get("button", BUTTON_MODE):
                cur_time = datetime.now(pytz.timezone('Asia/Kolkata')).time()
                time_difference = timedelta(hours=cur_time.hour, minutes=cur_time.minute, seconds=(cur_time.second+(cur_time.microsecond/1000000))) - timedelta(hours=curr_time.hour, minutes=curr_time.minute, seconds=(curr_time.second+(curr_time.microsecond/1000000)))
                remaining_seconds = "{:.2f}".format(time_difference.total_seconds())
                cap = await get_text(settings, remaining_seconds, files, query, total_results, movie)
                try:
                    await query.message.edit_text(text=cap, reply_markup=InlineKeyboardMarkup(btn))
                except MessageNotModified:
                    pass
            else:
                try:
                    await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(btn))
                except MessageNotModified:
                    pass
                await query.answer()
        else:
            return await query.answer(f"Sᴏʀʀʏ, Nᴏ ғɪʟᴇs ғᴏᴜɴᴅ ғᴏʀ ʏᴏᴜʀ ᴏ̨ᴜᴇʀʏ {movie}.", show_alert=True)
    except Exception as e:
            await query.answer(f"error found out\n\n{e}", show_alert=True)
            return

@Client.on_callback_query(filters.regex(r"^seas"))
async def select_seasons(bot, query):
    _, userid = query.data.split("#")
    curr_time = datetime.now(pytz.timezone('Asia/Kolkata')).time()
    if int(userid) not in [query.from_user.id, 0]:
        return await query.answer(script.ALRT_TXT.format(query.from_user.first_name), show_alert=True)
    btn = [[
        InlineKeyboardButton("Sᴇʟᴇᴄᴛ Yᴏᴜʀ Dᴇꜱɪʀᴇᴅ Sᴇᴀꜱᴏɴꜱ ↓", callback_data=f"seasons#{userid}#unknown")
    ],[
        InlineKeyboardButton("sᴇᴀꜱᴏɴ 𝟷", callback_data=f"seasons#{userid}#s01"),
        InlineKeyboardButton("sᴇᴀꜱᴏɴ 𝟸", callback_data=f"seasons#{userid}#s02"),
        InlineKeyboardButton("sᴇᴀꜱᴏɴ 𝟹", callback_data=f"seasons#{userid}#s03")
    ],[
        InlineKeyboardButton("sᴇᴀꜱᴏɴ 𝟺", callback_data=f"seasons#{userid}#s04"),
        InlineKeyboardButton("sᴇᴀꜱᴏɴ 𝟻", callback_data=f"seasons#{userid}#s05"),
        InlineKeyboardButton("sᴇᴀꜱᴏɴ 𝟼", callback_data=f"seasons#{userid}#s06")
    ],[
        InlineKeyboardButton("sᴇᴀꜱᴏɴ 𝟽", callback_data=f"seasons#{userid}#s07"),
        InlineKeyboardButton("sᴇᴀꜱᴏɴ 𝟾", callback_data=f"seasons#{userid}#s08"),
        InlineKeyboardButton("sᴇᴀꜱᴏɴ 𝟿", callback_data=f"seasons#{userid}#s09")
    ],[
        InlineKeyboardButton("sᴇᴀꜱᴏɴ 𝟷𝟶", callback_data=f"seasons#{userid}#s10"),
        InlineKeyboardButton("sᴇᴀꜱᴏɴ 𝟷𝟷", callback_data=f"seasons#{userid}#s11"),
        InlineKeyboardButton("sᴇᴀꜱᴏɴ 𝟷𝟸", callback_data=f"seasons#{userid}#s12")
    ],[
        InlineKeyboardButton("sᴇᴀꜱᴏɴ 𝟷𝟹", callback_data=f"seasons#{userid}#s13"),
        InlineKeyboardButton("sᴇᴀꜱᴏɴ 𝟷𝟺", callback_data=f"seasons#{userid}#s14"),
        InlineKeyboardButton("sᴇᴀꜱᴏɴ 𝟷𝟻", callback_data=f"seasons#{userid}#s15")
    ],[
        InlineKeyboardButton("⋞ ʙᴀᴄᴋ", callback_data=f"seasons#{userid}#home")
    ]]
    try:
       await query.edit_message_reply_markup(
           reply_markup=InlineKeyboardMarkup(btn)
       )
    except MessageNotModified:
        pass
    await query.answer()

@Client.on_callback_query(filters.regex(r"^spol"))
async def pm_spoll_choker(bot, query):
    _, id, user = query.data.split('#')
    if int(user) != 0 and query.from_user.id != int(user):
        return await query.answer(script.ALRT_TXT.format(query.from_user.first_name), show_alert=True)
    movie = await get_poster(id, id=True)
    search = movie.get('title')
    await query.answer('ᴄʜᴇᴄᴋɪɴɢ ɪɴ ᴍʏ ᴅᴀᴛᴀʙᴀꜱᴇ...')
    files, offset, total_results = await get_search_results(query.message.chat.id, search)
    if files:
        k = (search, files, offset, total_results)
        await auto_filter(bot, query, k)
    else:
        try:
            reqstr1 = query.from_user.id if query.from_user else 0
            reqstr = await bot.get_users(reqstr1)
            if NO_RESULTS_MSG:
                nishant = [[
                    InlineKeyboardButton('ɴᴏᴛ ʀᴇʟᴇᴀsᴇ 📅', callback_data=f"not_release:{reqstr1}:{search}"),
                    InlineKeyboardButton('ɴᴏᴛ ᴀᴠᴀɪʟᴀʙʟᴇ 🙅', callback_data=f"not_available:{reqstr1}:{search}")
                ],[
                    InlineKeyboardButton('ᴜᴘʟᴏᴀᴅᴇᴅ 📩', callback_data=f"uploaded:{reqstr1}:{search}")
                ],[
                    InlineKeyboardButton('ɪɴᴠᴀʟɪᴅ ғᴏʀᴍᴀᴛ 📃', callback_data=f"series:{reqstr1}:{search}"),
                    InlineKeyboardButton('sᴘᴇʟʟ ᴍɪsᴛᴇᴋ 📝', callback_data=f"spelling_error:{reqstr1}:{search}")
                ],[
                    InlineKeyboardButton('cʟosᴇ 🔐', callback_data=f"close_data")
                ]]
                reply_markup = InlineKeyboardMarkup(nishant)
                total=await bot.get_chat_members_count(query.message.chat.id)
                await bot.send_message(chat_id=LOG_CHANNEL, text=(script.NORSLTS.format(query.message.chat.title, query.message.chat.id, total, temp.B_NAME, reqstr.mention, search)), reply_markup=InlineKeyboardMarkup(safari))
            k = await query.message.edit(script.MVE_NT_FND)
            await asyncio.sleep(60)
            await k.delete()
            try:
                await query.message.reply_to_message.delete()
            except:
                pass
        except Exception as e:
            reqstr1 = query.from_user.id if query.from_user else 0
            reqstr = await bot.get_users(reqstr1)
            if NO_RESULTS_MSG:
                nishant = [[
                    InlineKeyboardButton('ɴᴏᴛ ʀᴇʟᴇᴀsᴇ 📅', callback_data=f"not_release:{reqstr1}:{search}"),
                    InlineKeyboardButton('ɴᴏᴛ ᴀᴠᴀɪʟᴀʙʟᴇ 🙅', callback_data=f"not_available:{reqstr1}:{search}")
                ],[
                    InlineKeyboardButton('ᴜᴘʟᴏᴀᴅᴇᴅ 📩', callback_data=f"uploaded:{reqstr1}:{search}")
                ],[
                    InlineKeyboardButton('ɪɴᴠᴀʟɪᴅ ғᴏʀᴍᴀᴛ 📃', callback_data=f"series:{reqstr1}:{search}"),
                    InlineKeyboardButton('sᴘᴇʟʟ ᴍɪsᴛᴇᴋ 📝', callback_data=f"spelling_error:{reqstr1}:{search}")
                ],[
                    InlineKeyboardButton('cʟosᴇ 🔐', callback_data=f"close_data")
                ]]
                reply_markup = InlineKeyboardMarkup(nishant)
                await bot.send_message(chat_id=LOG_CHANNEL, text=(script.PMNORSLTS.format(temp.B_NAME, reqstr.mention, search)), reply_markup=InlineKeyboardMarkup(safari))
            k = await query.message.edit(script.MVE_NT_FND)
            await asyncio.sleep(60)
            await k.delete()
            try:
                await query.message.reply_to_message.delete()
            except:
                pass

@Client.on_callback_query()
async def cb_handler(client: Client, query: CallbackQuery):
    data = query.data
    if query.data == "close_data":
        await query.message.delete()
    
    elif "groupcb" in query.data:
        await query.answer()

        group_id = query.data.split(":")[1]

        act = query.data.split(":")[2]
        hr = await client.get_chat(int(group_id))
        title = hr.title
        user_id = query.from_user.id

        if act == "":
            stat = "CONNECT"
            cb = "connectcb"
        else:
            stat = "DISCONNECT"
            cb = "disconnect"

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(f"{stat}", callback_data=f"{cb}:{group_id}"),
             InlineKeyboardButton("DELETE", callback_data=f"deletecb:{group_id}")],
            [InlineKeyboardButton("BACK", callback_data="backcb")]
        ])

        await query.message.edit_text(
            f"Gʀᴏᴜᴘ Nᴀᴍᴇ : **{title}**\nGʀᴏᴜᴘ ID : `{group_id}`",
            reply_markup=keyboard,
            parse_mode=enums.ParseMode.MARKDOWN
        )
        return await query.answer(MSG_ALRT)
    elif "connectcb" in query.data:
        await query.answer()

        group_id = query.data.split(":")[1]

        hr = await client.get_chat(int(group_id))

        title = hr.title

        user_id = query.from_user.id

        mkact = await make_active(str(user_id), str(group_id))

        if mkact:
            await query.message.edit_text(
                f"Cᴏɴɴᴇᴄᴛᴇᴅ ᴛᴏ **{title}**",
                parse_mode=enums.ParseMode.MARKDOWN
            )
        else:
            await query.message.edit_text('Sᴏᴍᴇ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ!!', parse_mode=enums.ParseMode.MARKDOWN)
        return await query.answer(MSG_ALRT)
    elif "disconnect" in query.data:
        await query.answer()

        group_id = query.data.split(":")[1]

        hr = await client.get_chat(int(group_id))

        title = hr.title
        user_id = query.from_user.id

        mkinact = await make_inactive(str(user_id))

        if mkinact:
            await query.message.edit_text(
                f"Dɪsᴄᴏɴɴᴇᴄᴛᴇᴅ ғʀᴏᴍ **{title}**",
                parse_mode=enums.ParseMode.MARKDOWN
            )
        else:
            await query.message.edit_text(
                f"Sᴏᴍᴇ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ!!",
                parse_mode=enums.ParseMode.MARKDOWN
            )
        return await query.answer(MSG_ALRT)
    elif "deletecb" in query.data:
        await query.answer()

        user_id = query.from_user.id
        group_id = query.data.split(":")[1]

        delcon = await delete_connection(str(user_id), str(group_id))

        if delcon:
            await query.message.edit_text(
                "Sᴜᴄᴄᴇssғᴜʟʟʏ ᴅᴇʟᴇᴛᴇᴅ ᴄᴏɴɴᴇᴄᴛɪᴏɴ !"
            )
        else:
            await query.message.edit_text(
                f"Sᴏᴍᴇ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ!!",
                parse_mode=enums.ParseMode.MARKDOWN
            )
        return await query.answer(MSG_ALRT)
    elif query.data == "backcb":
        await query.answer()

        userid = query.from_user.id

        groupids = await all_connections(str(userid))
        if groupids is None:
            await query.message.edit_text(
                "Tʜᴇʀᴇ ᴀʀᴇ ɴᴏ ᴀᴄᴛɪᴠᴇ ᴄᴏɴɴᴇᴄᴛɪᴏɴs!! Cᴏɴɴᴇᴄᴛ ᴛᴏ sᴏᴍᴇ ɢʀᴏᴜᴘs ғɪʀsᴛ.",
            )
            return await query.answer(MSG_ALRT)
        buttons = []
        for groupid in groupids:
            try:
                ttl = await client.get_chat(int(groupid))
                title = ttl.title
                active = await if_active(str(userid), str(groupid))
                act = " - ACTIVE" if active else ""
                buttons.append(
                    [
                        InlineKeyboardButton(
                            text=f"{title}{act}", callback_data=f"groupcb:{groupid}:{act}"
                        )
                    ]
                )
            except:
                pass
        if buttons:
            await query.message.edit_text(
                "Yᴏᴜʀ ᴄᴏɴɴᴇᴄᴛᴇᴅ ɢʀᴏᴜᴘ ᴅᴇᴛᴀɪʟs ;\n\n",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
    
    elif "alertmessage" in query.data:
        grp_id = query.message.chat.id
        i = query.data.split(":")[1]
        keyword = query.data.split(":")[2]
        reply_text, btn, alerts, fileid = await find_filter(grp_id, keyword)
        if alerts is not None:
            alerts = ast.literal_eval(alerts)
            alert = alerts[int(i)]
            alert = alert.replace("\\n", "\n").replace("\\t", "\t")
            await query.answer(alert, show_alert=True)
            
    elif query.data.startswith("files"):
        ident, file_id = query.data.split("#")
        user = query.message.reply_to_message.from_user.id
        if int(user) != 0 and query.from_user.id != int(user):
            return await query.answer(script.ALRT_TXT.format(query.from_user.first_name), show_alert=True)
        await query.answer(url=f"https://t.me/{temp.U_NAME}?start=files_{query.message.chat.id}_{file_id}")
                 
            
    elif query.data.startswith("sendfiles"):
        clicked = query.from_user.id
        ident, key = query.data.split("#") 
        settings = await get_settings(query.message.chat.id)
        try:
            await query.answer(url=f"https://telegram.me/{temp.U_NAME}?start=allfiles_{query.message.chat.id}_{key}")
            return
        except UserIsBlocked:
            await query.answer('Uɴʙʟᴏᴄᴋ ᴛʜᴇ ʙᴏᴛ ᴍᴀʜɴ !', show_alert=True)
        except PeerIdInvalid:
            await query.answer(url=f"https://telegram.me/{temp.U_NAME}?start=sendfiles3_{key}")
        except Exception as e:
            logger.exception(e)
            await query.answer(url=f"https://telegram.me/{temp.U_NAME}?start=sendfiles4_{key}")
            
    elif query.data.startswith("generate_stream_link"):
        _, file_id = query.data.split(":")
        try:
            user_id = query.from_user.id
            username =  query.from_user.mention 

            log_msg = await client.send_cached_media(
                chat_id=LOG_CHANNEL,
                file_id=file_id,
            )
            fileName = {quote_plus(get_name(log_msg))}
            stream = f"{URL}watch/{str(log_msg.id)}/{quote_plus(get_name(log_msg))}?hash={get_hash(log_msg)}"
            download = f"{URL}{str(log_msg.id)}/{quote_plus(get_name(log_msg))}?hash={get_hash(log_msg)}"

            xo = await query.message.reply_text(f'🔐')
            await asyncio.sleep(1)
            await xo.delete()

            await log_msg.reply_text(
                text=f"•• ʟɪɴᴋ ɢᴇɴᴇʀᴀᴛᴇᴅ ꜰᴏʀ ɪᴅ #{user_id} \n•• ᴜꜱᴇʀɴᴀᴍᴇ : {username} \n\n•• ᖴᎥᒪᗴ Nᗩᗰᗴ : {fileName}",
                quote=True,
                disable_web_page_preview=True,
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🚀 ғᴀsᴛ ᴅᴏᴡɴʟᴏᴀᴅ", url=download),  
                                                    InlineKeyboardButton('wᴀᴛᴄʜ ᴏɴʟɪɴᴇ 🧿', url=stream)]])  
            )
            button = [[
                InlineKeyboardButton("🚀 ғᴀsᴛ ᴅᴏᴡɴʟᴏᴀᴅ", url=download),
                InlineKeyboardButton(' wᴀᴛᴄʜ ᴏɴʟɪɴᴇ 🧿', url=stream)
            ],[
                InlineKeyboardButton("• ᴡᴀᴛᴄʜ ɪɴ ᴡᴇʙ ᴀᴘᴘ •", web_app=WebAppInfo(url=stream))
            ]]
            await query.message.reply_text(
                text="•• ʟɪɴᴋ ɢᴇɴᴇʀᴀᴛᴇᴅ ☠︎⚔",
                quote=True,
                disable_web_page_preview=True,
                reply_markup=InlineKeyboardMarkup(button)
            )
        except Exception as e:
            print(e)  
            await query.answer(f"☣Something Went Wrong Sweetheart\n\n{e}", show_alert=True)
            return            
            
    elif query.data == "pages":
        await query.answer()

    elif query.data.startswith("killfilesdq"):
        ident, keyword = query.data.split("#")
        await query.message.edit_text(f"<b>Fᴇᴛᴄʜɪɴɢ Fɪʟᴇs ғᴏʀ ʏᴏᴜʀ ᴏ̨ᴜᴇʀʏ {keyword} ᴏɴ DB... Pʟᴇᴀsᴇ ᴡᴀɪᴛ...</b>")
        files, total = await get_bad_files(keyword)
        await query.message.edit_text(f"<b>Fᴏᴜɴᴅ {total} Fɪʟᴇs ғᴏʀ ʏᴏᴜʀ ᴏ̨ᴜᴇʀʏ {keyword} !\n\nFɪʟᴇ ᴅᴇʟᴇᴛɪᴏɴ ᴘʀᴏᴄᴇss ᴡɪʟʟ sᴛᴀʀᴛ ɪɴ 5 sᴇᴄᴏɴᴅs!</b>")
        await asyncio.sleep(5)
        deleted = 0
        async with lock:
            try:
                for file in files:
                    file_ids = file.file_id
                    file_name = file.file_name
                    result = await Media.collection.delete_one({
                        '_id': file_ids,
                    })
                    if result.deleted_count:
                        logger.info(f'Fɪʟᴇ Fᴏᴜɴᴅ ғᴏʀ ʏᴏᴜʀ ᴏ̨ᴜᴇʀʏ {keyword}! Sᴜᴄᴄᴇssғᴜʟʟʏ ᴅᴇʟᴇᴛᴇᴅ {file_name} ғʀᴏᴍ ᴅᴀᴛᴀʙᴀsᴇ.')
                    deleted += 1
                    if deleted % 20 == 0:
                        await query.message.edit_text(f"<b>Pʀᴏᴄᴇss sᴛᴀʀᴛᴇᴅ ғᴏʀ ᴅᴇʟᴇᴛɪɴɢ ғɪʟᴇs ғʀᴏᴍ DB. Sᴜᴄᴄᴇssғᴜʟʟʏ ᴅᴇʟᴇᴛᴇᴅ {str(deleted)} ғɪʟᴇs ғʀᴏᴍ DB ғᴏʀ ʏᴏᴜʀ ᴏ̨ᴜᴇʀʏ {keyword} !\n\nPʟᴇᴀsᴇ ᴡᴀɪᴛ...</b>")
            except Exception as e:
                logger.exception(e)
                await query.message.edit_text(f'Eʀʀᴏʀ: {e}')
            else:
                await query.message.edit_text(f"<b>Pʀᴏᴄᴇss Cᴏᴍᴘʟᴇᴛᴇᴅ ғᴏʀ ғɪʟᴇ ᴅᴇʟᴇᴛɪᴏɴ !\n\nSᴜᴄᴄᴇssғᴜʟʟʏ ᴅᴇʟᴇᴛᴇᴅ {str(deleted)} ғɪʟᴇs ғʀᴏᴍ DB ғᴏʀ ʏᴏᴜʀ ᴏ̨ᴜᴇʀʏ {keyword}.</b>")
    
    elif query.data.startswith("reset_grp_data"):
        grp_id = query.message.chat.id
        btn = [[
            InlineKeyboardButton('✂️ ᴄʟᴏsᴇ ✂️️', callback_data='close_data')
        ]]
        reply_markup=InlineKeyboardMarkup(btn)
        await save_group_settings(grp_id, 'verify', VERIFY_URL)
        await save_group_settings(grp_id, 'verify_api', VERIFY_API)
        await save_group_settings(grp_id, 'verify_2', VERIFY_URL2)
        await save_group_settings(grp_id, 'verify_api2', VERIFY_API2)
        await save_group_settings(grp_id, 'verify_3',  VERIFY_URL3)
        await save_group_settings(grp_id, 'verify_api3', VERIFY_API3)
        await save_group_settings(grp_id, 'verify_time', TWO_VERIFY_GAP)
        await save_group_settings(grp_id, 'verify_time2', THIRD_VERIFY_GAP)
        await save_group_settings(grp_id, 'template', IMDB_TEMPLATE)
        await save_group_settings(grp_id, 'tutorial', TUTORIAL)
        await save_group_settings(grp_id, 'tutorial2', TUTORIAL2)
        await save_group_settings(grp_id, 'tutorial3', TUTORIAL3)
        await save_group_settings(grp_id, 'caption', CUSTOM_FILE_CAPTION)
        await save_group_settings(grp_id, 'fsub_id', AUTH_CHANNEL)
        await save_group_settings(grp_id, 'log', LOG_CHANNEL)
        await save_group_settings(grp_id, 'file_limit', FILE_LIMITE)
        await save_group_settings(grp_id, 'streamapi', STREAM_API)
        await save_group_settings(grp_id, 'streamsite', STREAM_SITE)
        await save_group_settings(grp_id, 'all_limit', SEND_ALL_LIMITE)

        await query.answer('ꜱᴜᴄᴄᴇꜱꜱғᴜʟʟʏ ʀᴇꜱᴇᴛ...')
        await query.message.edit_text("<b>ꜱᴜᴄᴄᴇꜱꜱғᴜʟʟʏ ʀᴇꜱᴇᴛ ɢʀᴏᴜᴘ ꜱᴇᴛᴛɪɴɢꜱ...\n\nɴᴏᴡ ꜱᴇɴᴅ /details ᴀɢᴀɪɴ</b>", reply_markup=reply_markup)

    elif query.data.startswith("opnsetgrp"):
        ident, grp_id = query.data.split("#")
        userid = query.from_user.id if query.from_user else None
        st = await client.get_chat_member(grp_id, userid)
        if (
                st.status != enums.ChatMemberStatus.ADMINISTRATOR
                and st.status != enums.ChatMemberStatus.OWNER
                and str(userid) not in ADMINS
        ):
            await query.answer("Yᴏᴜ Dᴏɴ'ᴛ Hᴀᴠᴇ Tʜᴇ Rɪɢʜᴛs Tᴏ Dᴏ Tʜɪs !", show_alert=True)
            return
        title = query.message.chat.title
        settings = await get_settings(grp_id)
        if settings is not None:
            buttons = [
                [
                    InlineKeyboardButton('Rᴇꜱᴜʟᴛ Pᴀɢᴇ',
                                         callback_data=f'setgs#button#{settings["button"]}#{str(grp_id)}'),
                    InlineKeyboardButton('Tᴇxᴛ' if settings["button"] else 'Bᴜᴛᴛᴏɴ',
                                         callback_data=f'setgs#button#{settings["button"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Iᴍᴅʙ', callback_data=f'setgs#imdb#{settings["imdb"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✔ Oɴ' if settings["imdb"] else '✘ Oғғ',
                                         callback_data=f'setgs#imdb#{settings["imdb"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Sᴘᴇʟʟ Cʜᴇᴄᴋ',
                                         callback_data=f'setgs#spell_check#{settings["spell_check"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✔ Oɴ' if settings["spell_check"] else '✘ Oғғ',
                                         callback_data=f'setgs#spell_check#{settings["spell_check"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Wᴇʟᴄᴏᴍᴇ Msɢ', callback_data=f'setgs#welcome#{settings["welcome"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✔ Oɴ' if settings["welcome"] else '✘ Oғғ',
                                         callback_data=f'setgs#welcome#{settings["welcome"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Aᴜᴛᴏ-Dᴇʟᴇᴛᴇ',
                                         callback_data=f'setgs#auto_delete#{settings["auto_delete"]}#{str(grp_id)}'),
                    InlineKeyboardButton('10 Mɪɴs' if settings["auto_delete"] else '✘ Oғғ',
                                         callback_data=f'setgs#auto_delete#{settings["auto_delete"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Aᴜᴛᴏ-Fɪʟᴛᴇʀ',
                                         callback_data=f'setgs#auto_ffilter#{settings["auto_ffilter"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✔ Oɴ' if settings["auto_ffilter"] else '✘ Oғғ',
                                         callback_data=f'setgs#auto_ffilter#{settings["auto_ffilter"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Mᴀx Bᴜᴛᴛᴏɴs',
                                         callback_data=f'setgs#max_btn#{settings["max_btn"]}#{str(grp_id)}'),
                    InlineKeyboardButton('10' if settings["max_btn"] else f'{MAX_B_TN}',
                                         callback_data=f'setgs#max_btn#{settings["max_btn"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Fɪʟᴇ Lɪᴍɪᴛ', 
                                        callback_data=f'setgs#filelock#{settings.get("filelock", LIMIT_MODE)}#{grp_id}'),
                    InlineKeyboardButton('ᴏɴ ✔️' if settings.get("filelock", LIMIT_MODE) else 'ᴏғғ ✗', 
                                        callback_data=f'setgs#filelock#{settings.get("filelock", LIMIT_MODE)}#{grp_id}')
                ],
                [  
                     InlineKeyboardButton('Sᴛʀᴇᴀᴍ Sʜᴏʀᴛ', 
                                        callback_data=f'setgs#stream_mode#{settings.get("stream_mode", STREAM_MODE)}#{grp_id}'),
                    InlineKeyboardButton('✔ Oɴ' if settings.get("stream_mode", STREAM_MODE) else '✘ Oғғ', 
                                        callback_data=f'setgs#stream_mode#{settings.get("stream_mode", STREAM_MODE)}#{grp_id}')
                ], 
                [
                    InlineKeyboardButton('Vᴇʀɪғʏ', 
                                        callback_data=f'setgs#is_verify#{settings.get("is_verify", IS_VERIFY)}#{grp_id}'), 
                    InlineKeyboardButton('✔ Oɴ' if settings.get("is_verify", IS_VERIFY) else '✘ Oғғ', 
                                        callback_data=f'setgs#is_verify#{settings.get("is_verify", IS_VERIFY)}#{grp_id}')
                ]
            ]
            reply_markup = InlineKeyboardMarkup(buttons)
            await query.message.edit_text(
                text=f"<b>Cʜᴀɴɢᴇ Yᴏᴜʀ Sᴇᴛᴛɪɴɢs Fᴏʀ {title} As Yᴏᴜʀ Wɪsʜ ⚙</b>",
                disable_web_page_preview=True,
                parse_mode=enums.ParseMode.HTML
            )
            await query.message.edit_reply_markup(reply_markup)
        
    elif query.data.startswith("opnsetpm"):
        ident, grp_id = query.data.split("#")
        userid = query.from_user.id if query.from_user else None
        st = await client.get_chat_member(grp_id, userid)
        if (
                st.status != enums.ChatMemberStatus.ADMINISTRATOR
                and st.status != enums.ChatMemberStatus.OWNER
                and str(userid) not in ADMINS
        ):
            await query.answer("Yᴏᴜ Dᴏɴ'ᴛ Hᴀᴠᴇ Tʜᴇ Rɪɢʜᴛs Tᴏ Dᴏ Tʜɪs !", show_alert=True)
            return
        title = query.message.chat.title
        settings = await get_settings(grp_id)
        btn2 = [[
                 InlineKeyboardButton("Cʜᴇᴄᴋ PM", url=f"t.me/{temp.U_NAME}")
               ]]
        reply_markup = InlineKeyboardMarkup(btn2)
        await query.message.edit_text(f"<b>Yᴏᴜʀ sᴇᴛᴛɪɴɢs ᴍᴇɴᴜ ғᴏʀ {title} ʜᴀs ʙᴇᴇɴ sᴇɴᴛ ᴛᴏ ʏᴏᴜʀ PM</b>")
        await query.message.edit_reply_markup(reply_markup)
        if settings is not None:
            buttons = [
                [
                    InlineKeyboardButton('Rᴇꜱᴜʟᴛ Pᴀɢᴇ',
                                         callback_data=f'setgs#button#{settings["button"]}#{str(grp_id)}'),
                    InlineKeyboardButton('Tᴇxᴛ' if settings["button"] else 'Bᴜᴛᴛᴏɴ',
                                         callback_data=f'setgs#button#{settings["button"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Iᴍᴅʙ', callback_data=f'setgs#imdb#{settings["imdb"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✔ Oɴ' if settings["imdb"] else '✘ Oғғ',
                                         callback_data=f'setgs#imdb#{settings["imdb"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Sᴘᴇʟʟ Cʜᴇᴄᴋ',
                                         callback_data=f'setgs#spell_check#{settings["spell_check"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✔ Oɴ' if settings["spell_check"] else '✘ Oғғ',
                                         callback_data=f'setgs#spell_check#{settings["spell_check"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Wᴇʟᴄᴏᴍᴇ Msɢ', callback_data=f'setgs#welcome#{settings["welcome"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✔ Oɴ' if settings["welcome"] else '✘ Oғғ',
                                         callback_data=f'setgs#welcome#{settings["welcome"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Aᴜᴛᴏ-Dᴇʟᴇᴛᴇ',
                                         callback_data=f'setgs#auto_delete#{settings["auto_delete"]}#{str(grp_id)}'),
                    InlineKeyboardButton('10 Mɪɴs' if settings["auto_delete"] else '✘ Oғғ',
                                         callback_data=f'setgs#auto_delete#{settings["auto_delete"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Aᴜᴛᴏ-Fɪʟᴛᴇʀ',
                                         callback_data=f'setgs#auto_ffilter#{settings["auto_ffilter"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✔ Oɴ' if settings["auto_ffilter"] else '✘ Oғғ',
                                         callback_data=f'setgs#auto_ffilter#{settings["auto_ffilter"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Mᴀx Bᴜᴛᴛᴏɴs',
                                         callback_data=f'setgs#max_btn#{settings["max_btn"]}#{str(grp_id)}'),
                    InlineKeyboardButton('10' if settings["max_btn"] else f'{MAX_B_TN}',
                                         callback_data=f'setgs#max_btn#{settings["max_btn"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Fɪʟᴇ Lɪᴍɪᴛ', 
                                        callback_data=f'setgs#filelock#{settings.get("filelock", LIMIT_MODE)}#{grp_id}'),
                    InlineKeyboardButton('ᴏɴ ✔️' if settings.get("filelock", LIMIT_MODE) else 'ᴏғғ ✗', 
                                        callback_data=f'setgs#filelock#{settings.get("filelock", LIMIT_MODE)}#{grp_id}')
                ],
                [  
                     InlineKeyboardButton('Sᴛʀᴇᴀᴍ Sʜᴏʀᴛ', 
                                        callback_data=f'setgs#stream_mode#{settings.get("stream_mode", STREAM_MODE)}#{grp_id}'),
                    InlineKeyboardButton('✔ Oɴ' if settings.get("stream_mode", STREAM_MODE) else '✘ Oғғ', 
                                        callback_data=f'setgs#stream_mode#{settings.get("stream_mode", STREAM_MODE)}#{grp_id}')
                ], 
                [
                    InlineKeyboardButton('Vᴇʀɪғʏ', 
                                        callback_data=f'setgs#is_verify#{settings.get("is_verify", IS_VERIFY)}#{grp_id}'), 
                    InlineKeyboardButton('✔ Oɴ' if settings.get("is_verify", IS_VERIFY) else '✘ Oғғ', 
                                        callback_data=f'setgs#is_verify#{settings.get("is_verify", IS_VERIFY)}#{grp_id}')
                ]
            ]
            reply_markup = InlineKeyboardMarkup(buttons)
            await client.send_message(
                chat_id=userid,
                text=f"<b>Cʜᴀɴɢᴇ Yᴏᴜʀ Sᴇᴛᴛɪɴɢs Fᴏʀ {title} As Yᴏᴜʀ Wɪsʜ ⚙</b>",
                reply_markup=reply_markup,
                disable_web_page_preview=True,
                parse_mode=enums.ParseMode.HTML,
                reply_to_message_id=query.message.id
            )
    elif query.data == "start":
        buttons = [[
                    InlineKeyboardButton('⁠☆ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ ☆', url=f'http://t.me/{temp.U_NAME}?startgroup=true')
                ],[
                    InlineKeyboardButton('ᴘʀᴇᴍɪᴜᴍ 💳', callback_data='premium_info'),
                    InlineKeyboardButton('ʀᴇғᴇʀ ⚜️', callback_data="pm_reff")
                ],[
                    InlineKeyboardButton('ʜᴇʟᴘ 🔧', callback_data='help'),
                    InlineKeyboardButton('ᴇᴀʀɴ ᴍᴏɴᴇʏ 💰', callback_data='shortlink_info')
                ],[
                    InlineKeyboardButton('ᴛʀᴇɴᴅɪɴɢ ⚡', callback_data='trending'),
                    InlineKeyboardButton('ᴀʙᴏᴜᴛ 🦋', callback_data='about')
                ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS), has_spoiler=True)
        )
        await query.message.edit_text(
            text=script.START_TXT.format(message.from_user.mention, get_status(), message.from_user.id),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
        await query.answer(MSG_ALRT)
        
    elif query.data == 'features':
        buttons = [[
            InlineKeyboardButton('⋞ ʙᴀᴄᴋ', callback_data='start')
        ]] 
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(                     
            text=script.FEATURES,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "show_pm":
        user_id = query.from_user.id
        total_referrals = sdb.get_refer_points(user_id)
        await query.answer(text=f'You Have: {total_referrals} Refferal Points', show_alert=True)
        
    elif query.data == "pm_reff":
        try:
            user_id = query.from_user.id
            total_referrals = sdb.get_refer_points(user_id)
            buttons = [[
                InlineKeyboardButton('Invite 🔗', url=f'https://t.me/share/url?url=%E0%A4%AF%E0%A5%87%20Bot%20%E0%A4%9F%E0%A5%87%E0%A4%B2%E0%A5%80%E0%A4%97%E0%A5%8D%E0%A4%B0%E0%A4%BE%E0%A4%AE%20%E0%A4%AA%E0%A4%B0%20%20%E0%A4%B8%E0%A4%AC%E0%A4%B8%E0%A5%87%20%E0%A4%AA%E0%A4%B9%E0%A4%B2%E0%A5%87%20%E0%A4%AE%E0%A5%82%E0%A4%B5%E0%A5%80%20%E0%A4%94%E0%A4%B0%20%E0%A4%B8%E0%A5%80%E0%A4%B0%E0%A5%80%E0%A4%9C%20%E0%A4%85%E0%A4%AA%E0%A4%B2%E0%A5%8B%E0%A4%A1%20%E0%A4%95%E0%A4%B0%20%E0%A4%A6%E0%A5%87%E0%A4%A4%E0%A4%BE%20%E0%A4%B9%E0%A5%88%20%0A%0A%E0%A4%85%E0%A4%97%E0%A4%B0%20%E0%A4%86%E0%A4%AA%20%E0%A4%AD%E0%A5%80%20%E0%A4%AE%E0%A5%82%E0%A4%B5%E0%A5%80%20%E0%A4%94%E0%A4%B0%20%E0%A4%B8%E0%A5%80%E0%A4%B0%E0%A5%80%E0%A4%9C%20%E0%A4%A6%E0%A5%87%E0%A4%96%E0%A4%A8%E0%A5%87%20%E0%A4%95%E0%A4%BE%20%E0%A4%B6%E0%A5%8C%E0%A4%95%20%E0%A4%B0%E0%A4%96%E0%A4%A4%E0%A5%87%20%E0%A4%B9%E0%A5%88%20%E0%A4%A4%E0%A5%8B%20%E0%A4%87%E0%A4%B8%20Bot%20%E0%A4%95%E0%A5%8B%20%E0%A4%B8%E0%A5%8D%E0%A4%9F%E0%A4%BE%E0%A4%B0%E0%A5%8D%E0%A4%9F%20%E0%A4%95%E0%A4%B0%E0%A5%87%E0%A4%82%0A%0ALink%3Dhttps://t.me/{temp.U_NAME}?start=reff_{user_id}'), 
                InlineKeyboardButton(text=f'⏳{total_referrals}', callback_data=f"show_pm"), 
                InlineKeyboardButton('⋞ ʙᴀᴄᴋ', callback_data='start')
            ]]
            reply_markup = InlineKeyboardMarkup(buttons)
            await client.edit_message_media(
                query.message.chat.id, 
                query.message.id, 
                InputMediaPhoto(REFFER_PIC)
            )
            await query.message.edit_text(
                text=script.REFFER_TXT.format(temp.U_NAME, user_id),
                reply_markup=reply_markup,
                parse_mode=enums.ParseMode.HTML
            )
        except Exception as e:
            await query.answer(f"{e}", show_alert=True)
                    
    elif query.data.startswith("not_available"):
        _, user_id, movie = data.split(":")
        try:
            btns = [[
                    InlineKeyboardButton(text=f"🗑 Delete Log ", callback_data = "close_data")
                    ]]
            reply_markup = InlineKeyboardMarkup(btns)
            await client.send_message(int(user_id), script.NOT_AVAILABLE_TXT.format(movie),parse_mode=enums.ParseMode.HTML)
            msg=await query.edit_message_text(text=f"Mᴇꜱꜱᴀɢᴇ Sᴇɴᴅ Sᴜᴄᴄᴇꜱꜱғᴜʟʟʏ ✅\n\n⏳ꜱᴛᴀᴛᴜꜱ : Nᴏᴛ Aᴠᴀɪʟᴀʙʟᴇ 😒.\n🪪ᴜꜱᴇʀɪᴅ : `{user_id}`\n🎞ᴄᴏɴᴛᴇɴᴛ : `{movie}`", reply_markup=InlineKeyboardMarkup(safari))
        except Exception as e:
            print(e)
            await query.answer(f"{e}", show_alert=True)
            return
    elif data.startswith("uploaded"):
        _, user_id, movie = data.split(":")
        try:
            btns = [[
                    InlineKeyboardButton(text=f"🗑 Delete Log", callback_data = "close_data")
                    ]]
            reply_markup = InlineKeyboardMarkup(btns)
            await client.send_message(int(user_id), script.UPLOADED_TXT.format(movie),parse_mode=enums.ParseMode.HTML)
            msg=await query.edit_message_text(text=f"Mᴇꜱꜱᴀɢᴇ Sᴇɴᴅ Sᴜᴄᴄᴇꜱꜱғᴜʟʟʏ ✅\n\n⏳ꜱᴛᴀᴛᴜꜱ : Uᴘʟᴏᴀᴅᴇᴅ 🎊.\n🪪ᴜꜱᴇʀɪᴅ : `{user_id}`\n🎞ᴄᴏɴᴛᴇɴᴛ : `{movie}`", reply_markup=InlineKeyboardMarkup(safari))
        except Exception as e:
            print(e)
            await query.answer(f"{e}", show_alert=True)
            return
    elif data.startswith("not_release"):
        _, user_id, movie = data.split(":")
        try:
            btns = [[
                    InlineKeyboardButton(text=f"🗑 Delete Log", callback_data = "close_data")
                    ]]
            reply_markup = InlineKeyboardMarkup(btns)
            await client.send_message(int(user_id), script.NOT_RELEASE_TXT.format(movie),parse_mode=enums.ParseMode.HTML)
            msg=await query.edit_message_text(text=f"Mᴇꜱꜱᴀɢᴇ Sᴇɴᴅ Sᴜᴄᴄᴇꜱꜱғᴜʟʟʏ ✅\n\n⏳ꜱᴛᴀᴛᴜꜱ : ɴᴏᴛ ʀᴇʟᴇᴀsᴇ 🙅.\n🪪ᴜꜱᴇʀɪᴅ : `{user_id}`\n🎞ᴄᴏɴᴛᴇɴᴛ : `{movie}`", reply_markup=InlineKeyboardMarkup(safari))
        except Exception as e:
            print(e)
            await query.answer(f"{e}", show_alert=True)
            return
    elif data.startswith("spelling_error"):
        _, user_id, movie = data.split(":")
        try:
            btns = [[
                    InlineKeyboardButton(text=f"🗑 Delete Log", callback_data = "close_data")
                    ]]
            reply_markup = InlineKeyboardMarkup(btns)
            await client.send_message(int(user_id), script.SPELL_TXT.format(movie),parse_mode=enums.ParseMode.HTML)
            msg=await query.edit_message_text(text=f"Mᴇꜱꜱᴀɢᴇ Sᴇɴᴅ Sᴜᴄᴄᴇꜱꜱғᴜʟʟʏ ✅\n\n⏳ꜱᴛᴀᴛᴜꜱ : Sᴘᴇʟʟɪɴɢ Eʀʀᴏʀ 🕵️.\n🪪ᴜꜱᴇʀɪᴅ : `{user_id}`\n🎞ᴄᴏɴᴛᴇɴᴛ : `{movie}`", reply_markup=InlineKeyboardMarkup(safari))
        except Exception as e:
            print(e)
            await query.answer(f"{e}", show_alert=True)
            return
    elif data.startswith("series"):
        _, user_id, movie = data.split(":")
        try:
            buttons = [[
                    InlineKeyboardButton(text=f"🗑 Delete Log ❌", callback_data = "close_data")
                    ]]
            reply_markup = InlineKeyboardMarkup(buttons)
            await client.send_message(int(user_id), script.SERIES_FORMAT_TXT.format(movie),parse_mode=enums.ParseMode.HTML)
            msg=await query.edit_message_text(text=f"Mᴇꜱꜱᴀɢᴇ Sᴇɴᴅ Sᴜᴄᴄᴇꜱꜱғᴜʟʟʏ ✅\n\n⏳ꜱᴛᴀᴛᴜꜱ : Sᴇʀɪᴇs Eʀʀᴏʀ 🕵️.\n🪪ᴜꜱᴇʀɪᴅ : `{user_id}`\n🎞ᴄᴏɴᴛᴇɴᴛ : `{movie}`", reply_markup=InlineKeyboardMarkup(safari))
        except Exception as e:
            print(e) 
            await query.answer(f"{e}", show_alert=True)
            return
        
    elif query.data == "premium_info":
        buttons = [[
            InlineKeyboardButton('ʙʀᴏɴᴢᴇ 🥉', callback_data='bronze'),
            InlineKeyboardButton('ꜱɪʟᴠᴇʀ 🥈', callback_data='silver')
        ],[
            InlineKeyboardButton('ɢᴏʟᴅ 🥇', callback_data='gold'),
            InlineKeyboardButton('ᴘʟᴀᴛɪɴᴜᴍ 🏅', callback_data='platinum')
        ],[
            InlineKeyboardButton('ᴅɪᴀᴍᴏɴᴅ 💎', callback_data='diamond')
        ],[            
            InlineKeyboardButton('⇋ ʙᴀᴄᴋ ᴛᴏ ʜᴏᴍᴇ ⇋', callback_data='start')
        ]]
        
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.PREMIUM_CMD.format(query.from_user.mention),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    
    elif query.data == "bronze":
        buttons = [[
            InlineKeyboardButton('🔐 ᴄʟɪᴄᴋ ʜᴇʀᴇ ᴛᴏ ʙᴜʏ ᴘʀᴇᴍɪᴜᴍ', callback_data='purchase')
        ],[
            InlineKeyboardButton('𝟷 / 𝟻', callback_data='pagesn1'),
            InlineKeyboardButton('ɴᴇxᴛ ⋟', callback_data='silver')
        ],[
            InlineKeyboardButton('⇋ ʙᴀᴄᴋ ᴛᴏ ʜᴏᴍᴇ ⇋', callback_data='premium_info')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.BRONZE_TXT.format(query.from_user.mention),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )

    elif query.data == "silver":
        buttons = [[
            InlineKeyboardButton('🔐 ᴄʟɪᴄᴋ ʜᴇʀᴇ ᴛᴏ ʙᴜʏ ᴘʀᴇᴍɪᴜᴍ', callback_data='purchase')
        ],[
            InlineKeyboardButton('⋞ ʙᴀᴄᴋ', callback_data='bronze'),
            InlineKeyboardButton('𝟸 / 𝟻', callback_data='pagesn1'),
            InlineKeyboardButton('ɴᴇxᴛ ⋟', callback_data='gold')
        ],[
            InlineKeyboardButton('⇋ ʙᴀᴄᴋ ᴛᴏ ʜᴏᴍᴇ ⇋', callback_data='premium_info')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.SILVER_TXT.format(query.from_user.mention),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )

    elif query.data == "gold":
        buttons = [[
            InlineKeyboardButton('🔐 ᴄʟɪᴄᴋ ʜᴇʀᴇ ᴛᴏ ʙᴜʏ ᴘʀᴇᴍɪᴜᴍ', callback_data='purchase')
        ],[
            InlineKeyboardButton('⋞ ʙᴀᴄᴋ', callback_data='silver'),
            InlineKeyboardButton('𝟹 / 𝟻', callback_data='pagesn1'),
            InlineKeyboardButton('ɴᴇxᴛ ⋟', callback_data='platinum')
        ],[
            InlineKeyboardButton('⇋ ʙᴀᴄᴋ ᴛᴏ ʜᴏᴍᴇ ⇋', callback_data='premium_info')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.GOLD_TXT.format(query.from_user.mention),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )

    elif query.data == "platinum":
        buttons = [[
            InlineKeyboardButton('🔐 ᴄʟɪᴄᴋ ʜᴇʀᴇ ᴛᴏ ʙᴜʏ ᴘʀᴇᴍɪᴜᴍ', callback_data='purchase')
        ],[
            InlineKeyboardButton('⋞ ʙᴀᴄᴋ', callback_data='gold'),
            InlineKeyboardButton('𝟺 / 𝟻', callback_data='pagesn1'),
            InlineKeyboardButton('ɴᴇxᴛ ⋟', callback_data='diamond')
        ],[
            InlineKeyboardButton('⇋ ʙᴀᴄᴋ ᴛᴏ ʜᴏᴍᴇ ⇋', callback_data='premium_info')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.PLATINUM_TXT.format(query.from_user.mention),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )

    
    elif query.data == "diamond":
        buttons = [[
            InlineKeyboardButton('🔐 ᴄʟɪᴄᴋ ʜᴇʀᴇ ᴛᴏ ʙᴜʏ ᴘʀᴇᴍɪᴜᴍ', callback_data='purchase')
        ],[
            InlineKeyboardButton('⋞ ʙᴀᴄᴋ', callback_data='platinum'),
            InlineKeyboardButton('𝟻 / 𝟻', callback_data='pagesn1'),
            InlineKeyboardButton('ɴᴇxᴛ ⋟', callback_data='other')
        ],[
            InlineKeyboardButton('⇋ ʙᴀᴄᴋ ᴛᴏ ʜᴏᴍᴇ ⇋', callback_data='premium_info')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.DIAMOND_TXT.format(query.from_user.mention),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
        
    elif query.data == "qr_info":
        buttons = [[
            InlineKeyboardButton('📸 sᴇɴᴅ ᴘᴀʏᴍᴇɴᴛ sᴄʀᴇᴇɴsʜᴏᴛ 📸', url=f'https://t.me/{OWNER_USER_NAME}')
        ], [
            InlineKeyboardButton('🚫 ᴄʟᴏꜱᴇ 🚫', callback_data='close_data')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.reply_photo(QR_CODE, caption=script.QR_TXT, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)

    elif query.data == "upi_info":
        buttons = [[
            InlineKeyboardButton('📸 sᴇɴᴅ ᴘᴀʏᴍᴇɴᴛ sᴄʀᴇᴇɴsʜᴏᴛ 📸', url=f'https://t.me/{OWNER_USER_NAME}')
        ], [
            InlineKeyboardButton('🚫 ᴄʟᴏꜱᴇ 🚫', callback_data='close_data')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.reply_text(script.UPI_TXT, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)
        
    elif query.data == "give_trial":
        user_id = query.from_user.id        
        await db.give_free_trial(user_id)
        await query.message.reply_text(
            text="ʏᴏᴜ ʜᴀᴠᴇ ʙᴇᴇɴ ᴀᴅᴅᴇᴅ ᴛᴏ ᴘʀᴇᴍɪᴜᴍ ᴜsᴇʀ ✨ ғᴏʀ 5 ᴍɪɴᴜᴛᴇs\n\nɴᴏᴡ ʏᴏᴜ ᴄᴀɴ ᴅᴏᴡɴʟᴏᴀᴅ ғɪʟᴇs ᴡɪᴛʜᴏᴜᴛ ᴠᴇʀɪғɪᴄᴀᴛɪᴏɴ\n\nsᴇᴇ ʏᴏᴜʀ ᴘʟᴀɴ /myplan",
            disable_web_page_preview=True
        )
        await query.message.delete()
        return    

  
    elif query.data == "channels":
        buttons = [[
            InlineKeyboardButton('Uᴘᴅᴀᴛᴇꜱ Cʜᴀɴɴᴇʟ', url=CHNL_LNK)
        ],[
            InlineKeyboardButton('⇇ ʙᴀᴄᴋ', callback_data='start')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.CHANNELS.format(query.from_user.mention),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )

    elif query.data == "users":
        buttons = [[
            InlineKeyboardButton('⇋ ʙᴀᴄᴋ ⇋', callback_data='help')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.USERS_TXT,
            reply_markup=reply_markup, 
            parse_mode=enums.ParseMode.HTML
        )

    elif query.data == "group":
        buttons = [[
            InlineKeyboardButton('⇋ ʙᴀᴄᴋ ⇋', callback_data='help')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.GROUP_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )

    elif query.data == "admincmd":
        if query.from_user.id not in ADMINS:
            return await query.answer("⚠️ ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀ ʙᴏᴛ ᴀᴅᴍɪɴ ! ⚠️", show_alert=True)        
        buttons = [[
            InlineKeyboardButton('⬅︎ ʙᴀᴄᴋ', callback_data='help'), 
            InlineKeyboardButton('ɴᴇxᴛ ➡︎', callback_data='admic2')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS), has_spoiler=True)
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.ADMIC_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
        
    elif query.data == "admincmd2":
        buttons = [[
            InlineKeyboardButton('⬅︎ ʙᴀᴄᴋ', callback_data='admic')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS), has_spoiler=True)
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.ADMIC_TEX2T,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )

    elif query.data == "help":
        buttons = [[
            InlineKeyboardButton('ᴀᴅᴍɪɴ - ᴄᴏᴍᴍᴀɴᴅꜱ', callback_data='admic')
        ], [
            InlineKeyboardButton('ᴜꜱᴇʀ - ᴄᴏᴍᴍᴀɴᴅꜱ', callback_data='users'),
            InlineKeyboardButton('ɢʀᴏᴜᴘ - ᴄᴏᴍᴍᴀɴᴅꜱ', callback_data='group')
        ], [
            InlineKeyboardButton('⇋ ʙᴀᴄᴋ ᴛᴏ ʜᴏᴍᴇ ⇋', callback_data='start')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS), has_spoiler=True)
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.HELP_TXT.format(query.from_user.mention),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
            elif query.data == "about":
        buttons = [[
            InlineKeyboardButton('‼️ ᴅɪꜱᴄʟᴀɪᴍᴇʀ ‼️', callback_data='disclaimer')
        ], [
            InlineKeyboardButton('ᴏᴡɴᴇʀ ɪɴꜰᴏ 🦋', callback_data='owner_info')
        ], [
            InlineKeyboardButton('sᴛᴀᴛᴜs 📈', callback_data='stats'),
            InlineKeyboardButton('🛰️ ʀᴇɴᴅᴇʀɪɴɢ ꜱᴛᴀᴛᴜꜱ ', callback_data='rendr')
        ], [
            InlineKeyboardButton('⋞ ʙᴀᴄᴋ ᴛᴏ ʜᴏᴍᴇ', callback_data='start')
        ]]
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text="ᴡᴀɪᴛ..."
        )
        await query.message.edit_text(
            text="ᴘʀᴏᴄᴇssɪɴɢ... "
        )
        await query.message.edit_text(
            text="ᴄᴏᴍᴘʟᴇᴛᴇ !"
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.ABOUT_TXT.format(temp.B_NAME),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "rendr":
        await query.answer("⚡️ ʟɪᴠᴇ sʏsᴛᴇᴍ sᴛᴀᴛᴜs ⚡️\n\n❂ ʀᴀᴍ ●●●●●●◌◌◌\n✇ ᴄᴘᴜ ●●●●●●◌◌◌◌◌◌\n✪ ᴅᴀᴛᴀ ᴛʀᴀꜰɪᴄs ●●●●◌◌◌◌◌◌ 🛰\n\nsᴛᴀᴛᴜs : ᴠ𝟽.𝟷 [ᴀᴅᴠᴀɴᴄᴇ] """, show_alert=True)

        elif query.data == "owner_info":
        buttons = [[
            InlineKeyboardButton('⋞ ʙᴀᴄᴋ', callback_data='about')
        ]]
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.OWNER_INFO,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    
    elif query.data == "disclaimer":
            btn = [[
                    InlineKeyboardButton("⇋ ʙᴀᴄᴋ ⇋", callback_data="about")
                  ]]
            reply_markup = InlineKeyboardMarkup(btn)
            await query.message.edit_text(
                text=(script.DISCLAIMER_TXT),
                reply_markup=reply_markup,
                parse_mode=enums.ParseMode.HTML 
            )
    elif query.data == "stats":
        if query.from_user.id not in ADMINS:
            return await query.answer("⚠️ ʏᴏᴜ'ʀᴇ ɴᴏᴛ ᴀ ʙᴏᴛ ᴀᴅᴍɪɴ !", show_alert=True) 
        buttons = [[
            InlineKeyboardButton('⟸ Bᴀᴄᴋ', callback_data='start'),
            InlineKeyboardButton('⟲ Rᴇғʀᴇsʜ', callback_data='rfrsh')
        ]]
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS), has_spoiler=True)
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        total = await Media.count_documents()
        users = await db.total_users_count()
        chats = await db.total_chat_count()
        monsize = await db.get_db_size()
        free = 536870912 - monsize
        monsize = get_size(monsize)
        free = get_size(free)
        await query.message.edit_text(
            text=script.STATUS_TXT.format(total, users, chats, monsize, free),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "rfrsh":
        await query.answer("Fetching MongoDb DataBase")
        buttons = [[
            InlineKeyboardButton('⟸ Bᴀᴄᴋ', callback_data='help'),
            InlineKeyboardButton('⟲ Rᴇғʀᴇsʜ', callback_data='rfrsh')
        ]]
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS), has_spoiler=True)
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        total = await Media.count_documents()
        users = await db.total_users_count()
        chats = await db.total_chat_count()
        monsize = await db.get_db_size()
        free = 536870912 - monsize
        monsize = get_size(monsize)
        free = get_size(free)
        await query.message.edit_text(
            text=script.STATUS_TXT.format(total, users, chats, monsize, free),
            reply_markup=reply_markup,
            
            parse_mode=enums.ParseMode.HTML
        )
    

    elif query.data.startswith("setgs"):
        ident, set_type, status, grp_id = query.data.split("#")
        grpid = await active_connection(str(query.from_user.id))

        if str(grp_id) != str(grpid) and query.from_user.id not in ADMINS:
            await query.message.edit("Yᴏᴜʀ Aᴄᴛɪᴠᴇ Cᴏɴɴᴇᴄᴛɪᴏɴ Hᴀs Bᴇᴇɴ Cʜᴀɴɢᴇᴅ. Gᴏ Tᴏ /connections ᴀɴᴅ ᴄʜᴀɴɢᴇ ʏᴏᴜʀ ᴀᴄᴛɪᴠᴇ ᴄᴏɴɴᴇᴄᴛɪᴏɴ.")
            return await query.answer(MSG_ALRT)

        if status == "True":
            await save_group_settings(grpid, set_type, False)
        else:
            await save_group_settings(grpid, set_type, True)

        settings = await get_settings(grpid)

        if settings is not None:
            buttons = [
                [
                    InlineKeyboardButton('Rᴇꜱᴜʟᴛ Pᴀɢᴇ',
                                         callback_data=f'setgs#button#{settings["button"]}#{str(grp_id)}'),
                    InlineKeyboardButton('Tᴇxᴛ' if settings["button"] else 'Bᴜᴛᴛᴏɴ',
                                         callback_data=f'setgs#button#{settings["button"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Iᴍᴅʙ', callback_data=f'setgs#imdb#{settings["imdb"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✔ Oɴ' if settings["imdb"] else '✘ Oғғ',
                                         callback_data=f'setgs#imdb#{settings["imdb"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Sᴘᴇʟʟ Cʜᴇᴄᴋ',
                                         callback_data=f'setgs#spell_check#{settings["spell_check"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✔ Oɴ' if settings["spell_check"] else '✘ Oғғ',
                                         callback_data=f'setgs#spell_check#{settings["spell_check"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Wᴇʟᴄᴏᴍᴇ Msɢ', callback_data=f'setgs#welcome#{settings["welcome"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✔ Oɴ' if settings["welcome"] else '✘ Oғғ',
                                         callback_data=f'setgs#welcome#{settings["welcome"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Aᴜᴛᴏ-Dᴇʟᴇᴛᴇ',
                                         callback_data=f'setgs#auto_delete#{settings["auto_delete"]}#{str(grp_id)}'),
                    InlineKeyboardButton('10 Mɪɴs' if settings["auto_delete"] else '✘ Oғғ',
                                         callback_data=f'setgs#auto_delete#{settings["auto_delete"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Aᴜᴛᴏ-Fɪʟᴛᴇʀ',
                                         callback_data=f'setgs#auto_ffilter#{settings["auto_ffilter"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✔ Oɴ' if settings["auto_ffilter"] else '✘ Oғғ',
                                         callback_data=f'setgs#auto_ffilter#{settings["auto_ffilter"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Mᴀx Bᴜᴛᴛᴏɴs',
                                         callback_data=f'setgs#max_btn#{settings["max_btn"]}#{str(grp_id)}'),
                    InlineKeyboardButton('10' if settings["max_btn"] else f'{MAX_B_TN}',
                                         callback_data=f'setgs#max_btn#{settings["max_btn"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Fɪʟᴇ Lɪᴍɪᴛ', 
                                        callback_data=f'setgs#filelock#{settings.get("filelock", LIMIT_MODE)}#{grp_id}'),
                    InlineKeyboardButton('ᴏɴ ✔️' if settings.get("filelock", LIMIT_MODE) else 'ᴏғғ ✗', 
                                        callback_data=f'setgs#filelock#{settings.get("filelock", LIMIT_MODE)}#{grp_id}')
                ], 
                [
                    InlineKeyboardButton('Sᴛʀᴇᴀᴍ Sʜᴏʀᴛ', 
                                        callback_data=f'setgs#stream_mode#{settings.get("stream_mode", STREAM_MODE)}#{grp_id}'),
                    InlineKeyboardButton('✔ Oɴ' if settings.get("stream_mode", STREAM_MODE) else '✘ Oғғ', 
                                        callback_data=f'setgs#stream_mode#{settings.get("stream_mode", STREAM_MODE)}#{grp_id}')
                ], 
                [
                    InlineKeyboardButton('Vᴇʀɪғʏ', 
                                        callback_data=f'setgs#is_verify#{settings.get("is_verify", IS_VERIFY)}#{grp_id}'), 
                    InlineKeyboardButton('✔ Oɴ' if settings.get("is_verify", IS_VERIFY) else '✘ Oғғ', 
                                        callback_data=f'setgs#is_verify#{settings.get("is_verify", IS_VERIFY)}#{grp_id}')
                ]
            ]
            reply_markup = InlineKeyboardMarkup(buttons)
            await query.message.edit_reply_markup(reply_markup)
    await query.answer(MSG_ALRT)

async def ai_spell_check(chat_id, wrong_name):
    try:  
        async def search_movie(wrong_name):
            search_results = imdb.search_movie(wrong_name)
            movie_list = [movie['title'] for movie in search_results]
            return movie_list
        movie_list = await search_movie(wrong_name)
        if not movie_list:
            return
        for _ in range(5):
            closest_match = process.extractOne(wrong_name, movie_list)
            if not closest_match or closest_match[1] <= 80:
                return 
            movie = closest_match[0]
            files, offset, total_results = await get_search_results(chat_id=chat_id, query=movie)
            if files:
                return movie
            movie_list.remove(movie)
        return
    except Exception as e:
        print('Got error while searching movie in ai_spell_check', e)
        
async def auto_filter(client, msg, spoll=False):
    try:
        curr_time = datetime.now(pytz.timezone('Asia/Kolkata')).time()
        if not spoll:
            message = msg
            if message.text.startswith("/"): return  # ignore commands
            if re.findall("((^\/|^,|^!|^\.|^[\U0001F600-\U000E007F]).*)", message.text):
                return
            if len(message.text) < 100:
                search = message.text
                m=await message.reply_sticker(sticker="CAACAgIAAxkBAAEVugJljpdfkszexOUZu8hPjuPKty8ZmAACdxgAAqPjKEmMVSFmXGLogR4E",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🅿︎🅻︎🅴︎🅰︎🆂︎🅴︎  🆆︎🅰︎🅸︎🆃︎", url=CHNL_LNK)]]))
                search = search.lower()
                find = search.split(" ")
                search = ""
                removes = ["in","upload", "series", "full", "horror", "thriller", "mystery", "print", "file", "send", "chahiye", "chiye", "movi", "movie", "bhejo", "dijiye", "jaldi", "hd", "bollywood", "hollywood", "south", "karo"]
                for x in find:
                    if x in removes:
                        continue
                    else:
                        search = search + x + " "
                search = re.sub(r"\b(pl(i|e)*?(s|z+|ease|se|ese|(e+)s(e)?)|((send|snd|giv(e)?|gib)(\sme)?)|movie(s)?|new|latest|bro|bruh|broh|helo|that|find|dubbed|link|venum|iruka|pannunga|pannungga|anuppunga|anupunga|anuppungga|anupungga|film|undo|kitti|kitty|tharu|kittumo|kittum|movie|any(one)|with\ssubtitle(s)?)", "", search, flags=re.IGNORECASE)
                search = re.sub(r"\s+", " ", search).strip()
                search = search.replace("-", " ")
                search = search.replace(":","")
                files, offset, total_results = await get_search_results(message.chat.id ,search, offset=0, filter=True)
                settings = await get_settings(message.chat.id)
                if not files:
                    await m.delete()
                    if settings["spell_check"]:
                        ai_sts = await message.reply_sticker(sticker=f"CAACAgQAAxkBAAEq2R9mipkiW9ACyj7oQXznwKTPHqNCXQACkBUAA3mRUZGx4GwLX9XCHgQ")
                        st=await message.reply('<b>Ai is Cheking For Your Spelling. Please Wait.</b>') 
                        is_misspelled = await ai_spell_check(chat_id = message.chat.id,wrong_name=search)
                        if is_misspelled:
                            await st.edit(f'<b>Ai Suggested <code>{is_misspelled}</code> name\nSo Im Searching for <code>{is_misspelled}</code></b>')
                            await asyncio.sleep(2)
                            msg.text = is_misspelled
                            await ai_sts.delete()
                            await st.delete()
                            return await auto_filter(client, msg)
                        await ai_sts.delete()
                        await st.delete()
                        return await advantage_spell_chok(client, msg)
                    else:
                        return
            else:
                return
        else:
            message = msg.message.reply_to_message  # msg will be callback query
            search, files, offset, total_results = spoll
            m=await message.reply_sticker(sticker="CAACAgIAAxkBAAEVugJljpdfkszexOUZu8hPjuPKty8ZmAACdxgAAqPjKEmMVSFmXGLogR4E",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🅿︎🅻︎🅴︎🅰︎🆂︎🅴︎  🆆︎🅰︎🅸︎🆃︎", url=CHNL_LNK)]]))
            settings = await get_settings(message.chat.id)
        key = f"{message.chat.id}-{message.id}"
        temp.GETALL[key] = files
        temp.CHAT[message.from_user.id] = message.chat.id
        temp.KEYWORD[message.from_user.id] = search
        if not settings.get("button", BUTTON_MODE):
            btn = [
                [
                    InlineKeyboardButton(
                        text=f"📁 [{get_size(file.file_size)}] ▷ {file.file_name}", callback_data=f'files#{file.file_id}'
                    ),
                ]
                for file in files
            ]
            
            btn.insert(0, [
                InlineKeyboardButton("♨️ ꜱᴇɴᴅ ᴀʟʟ ♨️", callback_data=f"sendfiles#{key}")
            ])
            btn.insert(0, [
                InlineKeyboardButton("sᴇᴀꜱᴏɴ", callback_data=f"seas#{req}"), 
                InlineKeyboardButton("ʏᴇᴀʀ", callback_data=f"select_year#{req}")
            ])
            btn.insert(0, [
                InlineKeyboardButton("ʟᴀɴɢᴜᴀɢᴇ", callback_data=f"select_lang#{req}"),
                InlineKeyboardButton("ǫᴜᴀʟɪᴛʏ", callback_data=f"quality#{req}")
            ])
        else:
            btn = []
            btn.insert(0, [
                InlineKeyboardButton("♨️ ꜱᴇɴᴅ ᴀʟʟ ♨️", callback_data=f"sendfiles#{key}")
            ])
            btn.insert(0, [
                InlineKeyboardButton("sᴇᴀꜱᴏɴ", callback_data=f"seas#{req}"), 
                InlineKeyboardButton("ʏᴇᴀʀ", callback_data=f"select_year#{req}")
            ])
            btn.insert(0, [
                InlineKeyboardButton("ʟᴀɴɢᴜᴀɢᴇ", callback_data=f"select_lang#{req}"),
                InlineKeyboardButton("ǫᴜᴀʟɪᴛʏ", callback_data=f"quality#{req}")
            ])
    
        if offset != "":
            key = f"{message.chat.id}-{message.id}"
            BUTTONS[key] = search
            req = message.from_user.id if message.from_user else 0
            try:
                if settings['max_btn']:
                    btn.append(
                        [InlineKeyboardButton("𝐏𝐀𝐆𝐄", callback_data="pages"), InlineKeyboardButton(text=f"1/{math.ceil(int(total_results)/10)}",callback_data="pages"), InlineKeyboardButton(text="𝐍𝐄𝐗𝐓 ➪",callback_data=f"next_{req}_{key}_{offset}")]
                    )
                else:
                    btn.append(
                        [InlineKeyboardButton("𝐏𝐀𝐆𝐄", callback_data="pages"), InlineKeyboardButton(text=f"1/{math.ceil(int(total_results)/int(MAX_B_TN))}",callback_data="pages"), InlineKeyboardButton(text="𝐍𝐄𝐗𝐓 ➪",callback_data=f"next_{req}_{key}_{offset}")]
                    )
            except KeyError:
                await save_group_settings(message.chat.id, 'max_btn', True)
                btn.append(
                    [InlineKeyboardButton("𝐏𝐀𝐆𝐄", callback_data="pages"), InlineKeyboardButton(text=f"1/{math.ceil(int(total_results)/10)}",callback_data="pages"), InlineKeyboardButton(text="𝐍𝐄𝐗𝐓 ➪",callback_data=f"next_{req}_{key}_{offset}")]
                )
        else:
            btn.append(
                [InlineKeyboardButton(text="𝐍𝐎 𝐌𝐎𝐑𝐄 𝐏𝐀𝐆𝐄𝐒 𝐀𝐕𝐀𝐈𝐋𝐀𝐁𝐋𝐄",callback_data="pages")]
            )
        imdb = await get_poster(search, file=(files[0]).file_name) if settings["imdb"] else None
        cur_time = datetime.now(pytz.timezone('Asia/Kolkata')).time()
        time_difference = timedelta(hours=cur_time.hour, minutes=cur_time.minute, seconds=(cur_time.second+(cur_time.microsecond/1000000))) - timedelta(hours=curr_time.hour, minutes=curr_time.minute, seconds=(curr_time.second+(curr_time.microsecond/1000000)))
        remaining_seconds = "{:.2f}".format(time_difference.total_seconds())
        TEMPLATE = settings['template']
        if imdb:
            cap = TEMPLATE.format(
                query=search,
                title=imdb['title'],
                votes=imdb['votes'],
                aka=imdb["aka"],
                seasons=imdb["seasons"],
                box_office=imdb['box_office'],
                localized_title=imdb['localized_title'],
                kind=imdb['kind'],
                imdb_id=imdb["imdb_id"],
                cast=imdb["cast"],
                runtime=imdb["runtime"],
                countries=imdb["countries"],
                certificates=imdb["certificates"],
                languages=imdb["languages"],
                director=imdb["director"],
                writer=imdb["writer"],
                producer=imdb["producer"],
                composer=imdb["composer"],
                cinematographer=imdb["cinematographer"],
                music_team=imdb["music_team"],
                distributors=imdb["distributors"],
                release_date=imdb['release_date'],
                year=imdb['year'],
                genres=imdb['genres'],
                poster=imdb['poster'],
                plot=imdb['plot'],
                rating=imdb['rating'],
                url=imdb['url'],
                **locals()
            )
            temp.IMDB_CAP[message.from_user.id] = cap
            if settings.get("button", BUTTON_MODE):
                for file in files:
                    cap += f"<b>\n\n<a href='https://telegram.me/{temp.U_NAME}?start=files_{message.chat.id}_{file.file_id}'> 📁 {get_size(file.file_size)} ▷ {file.file_name}</a></b>"
        else:
            CAPTION = f"<b>☠️ ᴛɪᴛʟᴇ : <code>{search}</code>\n📂 ᴛᴏᴛᴀʟ ꜰɪʟᴇꜱ : <code>{total_results}</code>\n📝 ʀᴇǫᴜᴇsᴛᴇᴅ ʙʏ : {message.from_user.first_name}\n⏰ ʀᴇsᴜʟᴛ ɪɴ : <code>{remaining_seconds} Sᴇᴄᴏɴᴅs</code>\n\n📚 Your Requested Files 👇\n\n</b>"
            if not settings.get("button", BUTTON_MODE):
                cap = f"{CAPTION}"
            else:
                cap = f"{CAPTION}"
                for file in files:
                    cap += f"<b><a href='https://telegram.me/{temp.U_NAME}?start=files_{message.chat.id}_{file.file_id}'> 📁 {get_size(file.file_size)} ▷ {file.file_name}\n\n</a></b>"

        if imdb and imdb.get('poster'):  
            try:
                hehe = await message.reply_photo(photo=imdb.get('poster'), caption=cap, reply_markup=InlineKeyboardMarkup(btn))
                await m.delete()
                try:
                    if settings['auto_delete']:
                        await asyncio.sleep(600)
                        await hehe.delete()
                        await message.delete()
                except KeyError:
                    await save_group_settings(message.chat.id, 'auto_delete', True)
                    await asyncio.sleep(600)
                    await hehe.delete()
                    await message.delete()
            except (MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty):
                pic = imdb.get('poster')
                poster = pic.replace('.jpg', "._V1_UX360.jpg")
                hmm = await message.reply_photo(photo=poster, caption=cap, reply_markup=InlineKeyboardMarkup(btn))
                try:
                    if settings['auto_delete']:
                        await asyncio.sleep(600)
                        await hmm.delete()
                        await message.delete()
                except KeyError:
                    await save_group_settings(message.chat.id, 'auto_delete', True)
                    await asyncio.sleep(600)
                    await hmm.delete()
                    await message.delete()
            except Exception as e:
                logger.exception(e)
                fek = await message.reply_text(text=cap, reply_markup=InlineKeyboardMarkup(btn))
                try:
                    if settings['auto_delete']:
                        await asyncio.sleep(600)
                        await fek.delete()
                        await message.delete()
                except KeyError:
                    await save_group_settings(message.chat.id, 'auto_delete', True)
                    await asyncio.sleep(600)
                    await fek.delete()
                    await message.delete()
        else:
            fuk = await message.reply_text(text=cap, reply_markup=InlineKeyboardMarkup(btn))
            await message.delete()
            await m.delete()
            try:
                if settings['auto_delete']:
                    await asyncio.sleep(600)
                    await fuk.delete()
                    await message.delete()
            except KeyError:
                await save_group_settings(message.chat.id, 'auto_delete', True)
                await asyncio.sleep(600)
                await fuk.delete()
                await message.delete()
        if spoll:
            await msg.message.delete()
    except Exception as e:
            await message.reply(f"{e}")
            return

async def advantage_spell_chok(client, message):
    mv_id = message.id
    search = message.text
    chat_id = message.chat.id
    user = message.from_user.id
    settings = await get_settings(chat_id)
    find = search.split(" ")
    query = ""
    removes = ["in","upload", "series", "full", "horror", "thriller", "mystery", "print", "file", "send", "chahiye", "chiye", "movi", "movie", "bhejo", "dijiye", "jaldi", "hd", "bollywood", "hollywood", "south", "karo"]
    for x in find:
        if x in removes:
            continue
        else:
            query = query + x + " "
    query = re.sub(
        r"\b(pl(i|e)*?(s|z+|ease|se|ese|(e+)s(e)?)|((send|snd|giv(e)?|gib)(\sme)?)|movie(s)?|new|latest|br((o|u)h?)*|^h(e|a)?(l)*(o)*|mal(ayalam)?|t(h)?amil|file|that|find|und(o)*|kit(t(i|y)?)?o(w)?|thar(u)?(o)*w?|kittum(o)*|aya(k)*(um(o)*)?|full\smovie|any(one)|with\ssubtitle(s)?)",
        "", message.text, flags=re.IGNORECASE)
    query = query.strip() + " movie"
    try:
        movies = await get_poster(search, bulk=True)
    except:
        k = await message.reply(script.I_CUDNT.format(search))
        await asyncio.sleep(60)
        await k.delete()
        try:
            await message.delete()
        except:
            pass
        return
    if not movies:
        google = search.replace(" ", "+")
        button = [[
            InlineKeyboardButton("🔍 ᴄʜᴇᴄᴋ sᴘᴇʟʟɪɴɢ ᴏɴ ɢᴏᴏɢʟᴇ 🔍", url=f"https://www.google.com/search?q={google}")
        ]]
        k = await message.reply_text(text=script.I_CUDNT.format(search), reply_markup=InlineKeyboardMarkup(button))
        await asyncio.sleep(120)
        await k.delete()
        try:
            await message.delete()
        except:
            pass
        return
    user = message.from_user.id if message.from_user else 0
    buttons = [[
        InlineKeyboardButton(text=movie.get('title'), callback_data=f"spol#{movie.movieID}#{user}")
    ]
        for movie in movies
    ]
    buttons.append(
        [InlineKeyboardButton(text="🚫 ᴄʟᴏsᴇ 🚫", callback_data='close_data')]
    )
    d = await message.reply_text(text=script.CUDNT_FND.format(search), reply_markup=InlineKeyboardMarkup(buttons), reply_to_message_id=message.id)
    await asyncio.sleep(120)
    await d.delete()
    try:
        await message.delete()
    except:
        pass
                                     


# THANKS TO NISHANT
# CREDIT @IM_NISHANTT
# PLZ.. DON'T REMOVE THIS CREDIT
# CONTACT FOR DOUBTS ON TG - @IM_NISHANT
#--------------------------------------------------------------------------👻👻👻👻👻👻--------------------------------------------------------------------------