import random

import discord
from discord.ext import commands

from modules.utils import lists
from modules.utils.db import Settings


class Event(commands.Cog):
    conf = {}

    def __init__(self, bot):
        self.bot = bot
        self.config = bot.config

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        """

        :param member: The member who joined the guild
        """

        guild = member.guild
        server = await Settings().get_server_settings(str(guild.id))

        # glob = await Settings().get_glob_settings()
        if 'Greet' in server and server['Greet'] is True and 'GreetChannel' in server:
            channel = self.bot.get_channel(int(server['GreetChannel']))
            greet = random.choice(lists.greet)

            em = discord.Embed(timestamp=member.joined_at)
            em.set_author(name="Welcome", icon_url=member.avatar_url)
            em.set_footer(text=f'{member.name}')
            em.description = f"{greet}"
            await channel.send(embed=em)

        if 'Display' in server and server['Display'] is True:
            category = discord.utils.get(
                member.guild.categories, id=int(server['category']))
            for channel in category.channels:
                try:
                    await channel.delete()
                except discord.Forbidden:
                    return
                except discord.HTTPException:
                    return

            overwrite = {
                member.guild.default_role: discord.PermissionOverwrite(connect=False),
            }

            await member.guild.create_voice_channel(f'Users : {len(member.guild.members)}', overwrites=overwrite,
                                                    category=category)
            bots = []
            for user in member.guild.members:
                if user.bot is True:
                    bots.append(user)
            await member.guild.create_voice_channel(f'Bots : {len(bots)}', overwrites=overwrite, category=category)
            await member.guild.create_voice_channel(f'Members : {len(member.guild.members) - len(bots)}',
                                                    overwrites=overwrite, category=category)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        """

        :param member: The member who has left
        """

        guild = member.guild
        server = await Settings().get_server_settings(str(guild.id))

        if 'Display' in server and server['Display'] is True:
            category = discord.utils.get(
                member.guild.categories, id=int(server['category']))
            for channel in category.channels:
                try:
                    await channel.delete()
                except discord.Forbidden:
                    return
                except discord.HTTPException:
                    return

            overwrite = {
                member.guild.default_role: discord.PermissionOverwrite(connect=False),
            }

            await member.guild.create_voice_channel(f'Users : {len(member.guild.members)}', overwrites=overwrite,
                                                    category=category)
            bots = []
            for user in member.guild.members:
                if user.bot is True:
                    bots.append(user)
            await member.guild.create_voice_channel(f'Bots : {len(bots)}', overwrites=overwrite, category=category)
            await member.guild.create_voice_channel(f'Members : {len(member.guild.members) - len(bots)}',
                                                    overwrites=overwrite, category=category)

        if 'Greet' in server and server['Greet'] is True and 'GreetChannel' in server:
            channel = self.bot.get_channel(int(server['GreetChannel']))
            leave = random.choice(lists.leave)

            em = discord.Embed(timestamp=member.joined_at)
            em.set_author(name="Left", icon_url=member.avatar_url)
            em.set_footer(text=f'{member.name}')
            em.description = f"{leave}"
            await channel.send(embed=em)

    @commands.Cog.listener()
    async def on_message(self, message):
        author = message.author
        glob = await Settings().get_glob_settings()
        if 'AFK' in glob:
            if author.id in glob['AFK']:
                if message.content is '--afk':
                    return
                glob['AFK'].remove(author.id)
                await Settings().set_glob_settings(glob)
                await message.channel.send("{}, welcome back !".format(author.mention), delete_after=10)
            else:
                for user in message.mentions:
                    if user.id in glob['AFK']:
                        await message.channel.send("{}#{} is AFK".format(user.name, user.discriminator),
                                                   delete_after=10)
                        # await user.send(f"{author} has mentionned you in {message.guild} : \n`{message.content}`")


def setup(bot):
    bot.add_cog(Event(bot))
