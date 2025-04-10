import asyncio import os from datetime import datetime, timedelta from typing import Union

from pyrogram import Client from pyrogram.types import InlineKeyboardMarkup from pytgcalls import PyTgCalls from pytgcalls.types.stream import StreamType from pytgcalls.exceptions import ( AlreadyJoinedError, NoActiveGroupCall, TelegramServerError, ) from pytgcalls.types import Update from pytgcalls.types.input_stream import AudioPiped, AudioVideoPiped from pytgcalls.types.input_stream.quality import HighQualityAudio, MediumQualityVideo from pytgcalls.types.stream import StreamAudioEnded

import config from Clonify import LOGGER, YouTube, app from Clonify.misc import db from Clonify.utils.database import ( add_active_chat, add_active_video_chat, get_lang, get_loop, group_assistant, is_autoend, music_on, remove_active_chat, remove_active_video_chat, set_loop, ) from Clonify.utils.exceptions import AssistantErr from Clonify.utils.formatters import check_duration, seconds_to_min, speed_converter from Clonify.utils.inline.play import stream_markup, telegram_markup from Clonify.utils.stream.autoclear import auto_clean from strings import get_string from Clonify.utils.thumbnails import get_thumb

class Call(PyTgCalls): def init(self): self.userbot1 = Client( name="RAUSHANAss1", api_id=config.API_ID, api_hash=config.API_HASH, session_string=str(config.STRING1), ) self.one = PyTgCalls( self.userbot1, cache_duration=150, ) self.autoend = {} self.counter = {}

async def _clear_(self, chat_id):
    db[chat_id] = []
    await remove_active_video_chat(chat_id)
    await remove_active_chat(chat_id)

async def pause_stream(self, chat_id: int):
    assistant = await group_assistant(self, chat_id)
    await assistant.pause_stream(chat_id)

async def resume_stream(self, chat_id: int):
    assistant = await group_assistant(self, chat_id)
    await assistant.resume_stream(chat_id)

async def stop_stream(self, chat_id: int):
    assistant = await group_assistant(self, chat_id)
    try:
        await self._clear_(chat_id)
        await assistant.leave_group_call(chat_id)
    except Exception:
        pass

async def stop_stream_force(self, chat_id: int):
    try:
        if config.STRING1:
            await self.one.leave_group_call(chat_id)
    except Exception:
        pass
    try:
        await self._clear_(chat_id)
    except Exception:
        pass

async def force_stop_stream(self, chat_id: int):
    assistant = await group_assistant(self, chat_id)
    try:
        db.get(chat_id).pop(0)
    except Exception:
        pass
    await remove_active_video_chat(chat_id)
    await remove_active_chat(chat_id)
    try:
        await assistant.leave_group_call(chat_id)
    except Exception:
        pass

async def start(self):
    LOGGER(__name__).info("Starting PyTgCalls Client...\n")
    if config.STRING1:
        await self.one.start()

async def ping(self):
    pings = []
    if config.STRING1:
        pings.append(await self.one.ping)
    return str(round(sum(pings) / len(pings), 3))

async def decorators(self):
    @self.one.on_kicked()
    @self.one.on_closed_voice_chat()
    @self.one.on_left()
    async def stream_services_handler(_, chat_id: int):
        await self.stop_stream(chat_id)

    @self.one.on_stream_end()
    async def stream_end_handler(client, update: Update):
        if not isinstance(update, StreamAudioEnded):
            return
        await self.change_stream(client, update.chat_id)

PRO = Call()

