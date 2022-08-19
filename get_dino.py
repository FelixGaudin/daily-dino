import requests
from bs4 import BeautifulSoup
from html2text import html2text
from discord import Embed
from discord.ext import commands
from datetime import datetime, time, timedelta
import asyncio

from private import TOKEN, CHANNEL_ID

URL = "https://dinosaurpictures.org/random"

def get_dino_infos():
    resp = requests.get(URL)
    soup = BeautifulSoup(resp.content, "html.parser")
    div = soup.find("div", {"class" : "intro"})
    return {
        "url" : resp.url,
        "name": soup.find("meta", property="og:title")["content"],
        "content": "\n".join([html2text(str(p)) if "<ul>" in str(p) else p.get_text().strip() for p in div.find_all("p")[:-1]]),
        "img": div.find_next('img')['src']
    }

bot = commands.Bot(command_prefix="GRAOU")
WHEN = time(16, 0, 0)


async def called_once_a_day():  # Fired every day
    # Make sure your guild cache is ready so the channel can be found via get_channel
    await bot.wait_until_ready()

    infos = get_dino_infos()
    # Note: It's more efficient to do bot.get_guild(guild_id).get_channel(channel_id) as there's less looping involved, but just get_channel still works fine
    channel = bot.get_channel(CHANNEL_ID)

    embed=Embed(title=infos["name"], url=infos["url"], description=infos["content"])
    embed.set_thumbnail(url=infos["img"])
    await channel.send(embed=embed)


async def background_task():
    now = datetime.now()
    print(now)
    # Make sure loop doesn't start after {WHEN} as then it will send immediately the first time as negative seconds will make the sleep yield instantly
    if now.time() > WHEN:
        tomorrow = datetime.combine(now.date() + timedelta(days=1), time(0))
        # Seconds until tomorrow (midnight)
        seconds = (tomorrow - now).total_seconds()
        # Sleep until tomorrow and then the loop will start
        await asyncio.sleep(seconds)
    while True:
        # You can do now() or a specific timezone if that matters, but I'll leave it with utcnow
        now = datetime.now()
        target_time = datetime.combine(
            now.date(), WHEN)  # 6:00 PM today (In UTC)
        seconds_until_target = (target_time - now).total_seconds()
        # Sleep until we hit the target time
        await asyncio.sleep(seconds_until_target)
        await called_once_a_day()  # Call the helper function that sends the message
        tomorrow = datetime.combine(now.date() + timedelta(days=1), time(0))
        # Seconds until tomorrow (midnight)
        seconds = (tomorrow - now).total_seconds()
        # Sleep until tomorrow and then the loop will start a new iteration
        await asyncio.sleep(seconds)

if __name__ == "__main__":
    bot.loop.create_task(background_task())
    bot.run(TOKEN)
