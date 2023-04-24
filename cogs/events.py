from __future__ import annotations

import random
import pathlib
import aiosqlite
import datetime

from typing import TYPE_CHECKING

import discord

from data import Data, config, DATABASE_FILE
from discord.ext import commands, tasks

if TYPE_CHECKING:
    from playground import Bot


class Events(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.tree = bot.tree
        self.blocked = ['cogs..old.fun', 'cogs..old.mod', 'cogs..old.utility',
                        "cogs.events", "cogs.fun.youtube_search", "cogs.others.antispam"]
        self.cogs_path = pathlib.Path("cogs")
        self.extensions = [self.format_cog(str(item)) for item in self.cogs_path.glob(
            '**/*.py') if self.format_cog(str(item)) not in self.blocked]

    def format_cog(self, string: str):
        return string.replace("\\", ".")[:-3]

    async def setup_hook(self):
        # note from razy: hi
        await self.tree.sync(guild=discord.Object(id=904460336118267954))

    @tasks.loop(seconds=20.0)
    async def presences(self):

        await self.bot.change_presence(status=discord.Status.online, activity=discord.Activity(
            type=discord.ActivityType.watching, name=random.choice(config["catchphrases"])))

    @commands.Cog.listener()
    async def on_ready(self):

        await Data.create_tables()

        await self.bot.change_presence(status=discord.Status.idle, activity=discord.Activity(
            type=discord.ActivityType.watching, name='loading up...'))

        for extension in self.extensions:
            try:
                await self.bot.load_extension(extension)
                print(f'🟨 {extension} was loaded')
            except Exception as e:
                print(f'🟥 {extension} was not loaded: {e}')

        print('🟪 all extensions loaded!!')

        try:
            synced = await self.bot.tree.sync()
            print(f"🔁 synced {len(synced)} slash commands")
        except Exception as e:
            print(e)

        if not self.presences.is_running():
            self.presences.start()

        if not self.cakeloop.is_running():
            await self.cakeloop.start()
            print("cake loop has begun")

        print(
            f"🟩 Logged in as {self.bot.user} with a {round(self.bot.latency * 1000)}ms delay")

    @commands.Cog.listener()
    async def on_message(self, message):
        if 'oh' in message.content and message.author.bot is False:
            await message.channel.send('oh')

    async def format_date(self, date: str):
        date, consd = date.split(":")
        day, month, year = date.split("/")
        if consd.lower() == "true":
            consd = True
        else:
            consd = False
        return {
            "day": day,
            "month": month,
            "year": year,
            "consd": consd
        }

    @tasks.loop(hours=12)
    async def cakeloop(self):
        print("started")
        date = datetime.datetime.today().strftime('%d/%m/%Y')
        print(f"date = {date}")
        day, month, year = date.split("/")
        print(f"{day}, {month}, {year}")
        async with aiosqlite.connect(DATABASE_FILE) as conn:
            async with conn.execute("SELECT user_id, cake, follow_list FROM profiles") as cursor:
                rows = await cursor.fetchall()
            for row in rows:
                print(row)
                user_id = row[0]
                cake_str = row[1]
                if cake_str is None:
                    continue
                cake_date = await self.format_date(cake_str)
                print(f"cake_date = {cake_date}")
                if cake_date["day"] == day and cake_date["month"] == month:
                    cake_user = await self.bot.fetch_user(user_id)
                    if row[2] is None:
                        continue
                    for i in eval(row[2]):
                        notif_user = await self.bot.fetch_user(i)
                        embed = discord.Embed(title=str(cake_user))
                        embed.set_thumbnail(url=cake_user.avatar.url)
                        c = [
                            "🎉 Happy Birthday, {user}! Let's party!",
                            "🎂 It's {user}'s birthday, Wish them a wonderful day!",
                            "🎉 It's {user}'s special day! Celebrate!",
                            "🎁 Cheers to another year! Happy Birthday, {user}!",
                            "🎉 Let's celebrate {user}'s birthday! Enjoy the day!"
                        ]
                        embed.description = random.choice(
                            c).replace("{user}", cake_user.mention)
                        embed.set_footer(text="You can unsubscribe in your settings (not yet)")
                        if cake_date["consd"]:
                            embed.description = f"{embed.description}\nThey are turning `{int(year) - int(cake_date['year'])}`"
                            await notif_user.send(embed=embed)
                        else:
                            await notif_user.send(embed=embed)


async def setup(ce):
    await ce.add_cog(Events(ce))
