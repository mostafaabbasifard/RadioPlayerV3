"""
RadioPlayerV3, Telegram Voice Chat Bot
Copyright (c) 2021  Asm Safone <https://github.com/AsmSafone>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>
"""

import os
import psutil
from time import time
from datetime import datetime
from config import Config
from pyrogram import Client, filters, emoji
from pyrogram.types import Message
from psutil._common import bytes2human

START_TIME = datetime.utcnow()
START_TIME_ISO = START_TIME.replace(microsecond=0).isoformat()

TIME_DURATION_UNITS = (
    ('week', 60 * 60 * 24 * 7),
    ('day', 60 * 60 * 24),
    ('hour', 60 * 60),
    ('min', 60),
    ('sec', 1)
)

self_or_contact_filter = filters.create(
    lambda _, __, message:
    (message.from_user and message.from_user.is_contact) or message.outgoing
)

async def _human_time_duration(seconds):
    if seconds == 0:
        return 'inf'
    parts = []
    for unit, div in TIME_DURATION_UNITS:
        amount, seconds = divmod(int(seconds), div)
        if amount > 0:
            parts.append(f"{amount} {unit}{'s' if amount != 1 else ''}")
    return ', '.join(parts)

async def generate_sysinfo(workdir):
    info = {
        'boot': datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S")
    }

    # CPU
    cpu_freq = psutil.cpu_freq().current
    cpu_freq = f"{round(cpu_freq / 1000, 2)}GHz" if cpu_freq >= 1000 else f"{round(cpu_freq, 2)}MHz"
    info['cpu'] = f"{psutil.cpu_percent(interval=1)}% ({psutil.cpu_count()}) {cpu_freq}"

    # Memory
    vm = psutil.virtual_memory()
    sm = psutil.swap_memory()
    info['ram'] = f"{bytes2human(vm.total)}, {bytes2human(vm.available)} available"
    info['swap'] = f"{bytes2human(sm.total)}, {sm.percent}%"

    # Disk
    du = psutil.disk_usage(workdir)
    dio = psutil.disk_io_counters()
    info['disk'] = f"{bytes2human(du.used)} / {bytes2human(du.total)} ({du.percent}%)"
    if dio:
        info['disk io'] = f"R {bytes2human(dio.read_bytes)} | W {bytes2human(dio.write_bytes)}"

    # Network
    nio = psutil.net_io_counters()
    info['net io'] = f"TX {bytes2human(nio.bytes_sent)} | RX {bytes2human(nio.bytes_recv)}"

    # Temperature (if available)
    try:
        sensors = psutil.sensors_temperatures()
        if sensors and 'coretemp' in sensors:
            temps = [sensor.current for sensor in sensors['coretemp']]
            info['temp'] = f"{sum(temps) / len(temps):.1f}°C"
    except Exception:
        pass

    # Format output
    info = {f"{key}:": value for key, value in info.items()}
    max_len = max(len(k) for k in info)
    return "```\n" + "\n".join(f"{k:<{max_len}} {v}" for k, v in info.items()) + "\n```"


@Client.on_message(
    filters.command("ping", prefixes=".") &
    (filters.group | filters.private) &
    self_or_contact_filter &
    ~filters.bot &
    ~filters.via_bot
)
async def ping_pong(_, m: Message):
    start = time()
    m_reply = await m.reply_text("Pong!")
    delta_ping = time() - start
    await m_reply.edit_text(f"{emoji.ROBOT} **Ping** : `{delta_ping * 1000:.3f} ms`")


@Client.on_message(
    filters.command("uptime", prefixes=".") &
    (filters.group | filters.private) &
    self_or_contact_filter &
    ~filters.bot &
    ~filters.via_bot
)
async def get_uptime(_, m: Message):
    uptime_sec = (datetime.utcnow() - START_TIME).total_seconds()
    uptime = await _human_time_duration(int(uptime_sec))
    await m.reply_text(
        f"{emoji.ROBOT} **Radio Player V3.0**\n"
        f"- **Uptime:** `{uptime}`\n"
        f"- **Restarted:** `{START_TIME_ISO}`"
    )


@Client.on_message(
    filters.command("sysinfo", prefixes=".") &
    (filters.group | filters.private) &
    self_or_contact_filter &
    ~filters.bot &
    ~filters.via_bot
)
async def get_sysinfo(client, m: Message):
    response = "**System Information**:\n"
    m_reply = await m.reply_text(f"{response}`...`")
    response += await generate_sysinfo(client.workdir)
    await m_reply.edit_text(response)


