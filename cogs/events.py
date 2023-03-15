from __future__ import annotations

import random
import pathlib

from typing import TYPE_CHECKING

import discord

from discord.ext import commands, tasks

if TYPE_CHECKING:
	from playground import Bot

from data.__init__ import config

class Events(commands.Cog):
	def __init__(self, bot: Bot):
		self.bot = bot
		self.tree = bot.tree
		self.blocked = ['cogs..old.fun', 'cogs..old.mod', 'cogs..old.utility', "cogs.events", "cogs.fun.youtube_search", "cogs.others.antispam"]
		self.cogs_path = pathlib.Path("cogs")
		self.extensions = [self.format_cog(str(item)) for item in self.cogs_path.glob('**/*.py') if self.format_cog(str(item)) not in self.blocked]

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

		print(
			f"🟩 Logged in as {self.bot.user} with a {round(self.bot.latency * 1000)}ms delay")

	@commands.Cog.listener()
	async def on_message(self, message):
		if 'oh' in message.content and message.author.bot is False:
			await message.channel.send('oh')


async def setup(ce):
	await ce.add_cog(Events(ce))
