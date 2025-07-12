# plugins/userbot/sysinfo.py — نسخه بازنویسی شده با Telethon

import os
import psutil
from time import time
from datetime import datetime
from config import Config
from telethon import events
from telethon.tl.types import Message
from psutil._common import bytes2human
from user import USER

START_TIME = datetime.utcnow()
START_TIME_ISO = START_TIME.replace(microsecond=0).isoformat()

async def _human_time_duration(seconds):
    if seconds == 0:
        return 'inf'
    units = [
        ('week', 60 * 60 * 24 * 7),
        ('day', 60 * 60 * 24),
        ('hour', 60 * 60),
        ('min', 60),
        ('sec', 1)
    ]
    parts = []
    for unit, div in units:
        amount, seconds = divmod(int(seconds), div)
        if amount > 0:
            parts.append(f"{amount} {unit}{'s' if amount != 1 else ''}")
    return ', '.join(parts)

async def generate_sysinfo(workdir):
    info = {
        'boot': datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S")
    }

    cpu_freq = psutil.cpu_freq().current
    cpu_freq = f"{round(cpu_freq / 1000, 2)}GHz" if cpu_freq >= 1000 else f"{round(cpu_freq, 2)}MHz"
    info['cpu'] = f"{psutil.cpu_percent(interval=1)}% ({psutil.cpu_count()}) {cpu_freq}"

    vm = psutil.virtual_memory()
    sm = psutil.swap_memory()
    info['ram'] = f"{bytes2human(vm.total)}, {bytes2human(vm.available)} available"
    info['swap'] = f"{bytes2human(sm.total)}, {sm.percent}%"

    du = psutil.disk_usage(workdir)
    dio = psutil.disk_io_counters()
    info['disk'] = f"{bytes2human(du.used)} / {bytes2human(du.total)} ({du.percent}%)"
    if dio:
        info['disk io'] = f"R {bytes2human(dio.read_bytes)} | W {bytes2human(dio.write_bytes)}"

    nio = psutil.net_io_counters()
    info['net io'] = f"TX {bytes2human(nio.bytes_sent)} | RX {bytes2human(nio.bytes_recv)}"

    try:
        sensors = psutil.sensors_temperatures()
        if sensors and 'coretemp' in sensors:
            temps = [sensor.current for sensor in sensors['coretemp']]
            info['temp'] = f"{sum(temps) / len(temps):.1f}°C"
    except Exception:
        pass

    info = {f"{key}:": value for key, value in info.items()}
    max_len = max(len(k) for k in info)
    return "```" + "\n".join(f"{k:<{max_len}} {v}" for k, v in info.items()) + "```"

@USER.on(events.NewMessage(pattern=r"\.ping"))
async def ping_pong(event):
    start = time()
    m_reply = await event.reply("Pong!")
    delta_ping = time() - start
    await m_reply.edit(f"🤖 **Ping**: `{delta_ping * 1000:.3f} ms`")

@USER.on(events.NewMessage(pattern=r"\.uptime"))
async def get_uptime(event):
    uptime_sec = (datetime.utcnow() - START_TIME).total_seconds()
    uptime = await _human_time_duration(int(uptime_sec))
    await event.reply(
        f"🤖 **Radio Player V3.0**\n"
        f"- **Uptime:** `{uptime}`\n"
        f"- **Restarted:** `{START_TIME_ISO}`"
    )

@USER.on(events.NewMessage(pattern=r"\.sysinfo"))
async def get_sysinfo(event):
    workdir = os.getcwd()
    response = "**System Information:**\n"
    m_reply = await event.reply(response + "`...`")
    response += await generate_sysinfo(workdir)
    await m_reply.edit(response)
