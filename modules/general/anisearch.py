#  Copyright (c) 2020.
#  MIT License
#
#  Copyright (c) 2019 YumeNetwork
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.

import datetime
import json
import re

import aiohttp
import discord
from discord.ext import commands

# SOURCES : https://github.com/Jintaku/Jintaku-Cogs-V3

SEARCH_ANIME_MANGA_QUERY = """
query ($id: Int, $page: Int, $search: String, $type: MediaType) {
    Page (page: $page, perPage: 10) {
        media (id: $id, search: $search, type: $type) {
            id
            idMal
            description(asHtml: false)
            title {
                english
                romaji
            }
            coverImage {
            		medium
            }
            bannerImage
            averageScore
            meanScore
            status
            episodes
            chapters
            externalLinks {
                url
                site
            }
            nextAiringEpisode {
                timeUntilAiring
            }
        }
    }
}
"""

SEARCH_CHARACTER_QUERY = """
query ($id: Int, $page: Int, $search: String) {
  Page(page: $page, perPage: 10) {
    characters(id: $id, search: $search) {
      id
      description (asHtml: true),
      name {
        first
        last
        native
      }
      image {
        large
      }
      media {
        nodes {
          id
          type
          title {
            romaji
            english
            native
            userPreferred
          }
        }
      }
    }
  }
}
"""

SEARCH_USER_QUERY = """
query ($id: Int, $page: Int, $search: String) {
    Page (page: $page, perPage: 10) {
        users (id: $id, search: $search) {
            id
            name
            siteUrl
            avatar {
                    large
            }
            about (asHtml: true),
            stats {
                watchedTime
                chaptersRead
            }
            favourites {
            manga {
              nodes {
                id
                title {
                  romaji
                  english
                  native
                  userPreferred
                }
              }
            }
            characters {
              nodes {
                id
                name {
                  first
                  last
                  native
                }
              }
            }
            anime {
              nodes {
                id
                title {
                  romaji
                  english
                  native
                  userPreferred
                }
              }
            }
            }
        }
    }
}
"""


class AniSearch(commands.Cog):
    """Search for anime, manga, characters and users using Anilist"""

    def __init__(self, bot):
        self.url = "https://graphql.anilist.co"
        self.bot = bot
        self.config = bot.config

    @staticmethod
    def format_name(first_name, last_name):  # Combines first_name and last_name and/or shows either of the two
        if first_name and last_name:
            return first_name + " " + last_name
        elif first_name:
            return first_name
        elif last_name:
            return last_name
        else:
            return "No name"

    @staticmethod
    def clean_html(description):  # Removes html tags
        if not description:
            return ""
        cleanr = re.compile("<.*?>")
        cleantext = re.sub(cleanr, "", description)
        return cleantext

    @staticmethod
    def clean_spoilers(description):  # Removes spoilers using the html tag given by AniList
        if not description:
            return ""
        cleanr = re.compile("/<span[^>]*>.*</span>/g")
        cleantext = re.sub(cleanr, "", description)
        return cleantext

    def description_parser(self, description):  # Limits text to 400characters and 5 lines and adds "..." at the end
        description = self.clean_spoilers(description)
        description = self.clean_html(description)
        description = "\n".join(description.split("\n")[:5])
        if len(description) > 400:
            return description[:400] + "..."
        else:
            return description

    @staticmethod
    def list_maximum(items):  # Limits to 5 strings than adds "+X more"
        if len(items) > 5:
            return items[:5] + ["+ " + str(len(items) - 5) + " more"]
        else:
            return items

    async def _request(self, query, variables=None):

        if variables is None:
            variables = {}

        request_json = {"query": query, "variables": variables}

        headers = {"content-type": "application/json"}

        async with aiohttp.ClientSession() as session:
            async with session.post(self.url, data=json.dumps(request_json), headers=headers) as response:
                return await response.json()

    async def _search_anime_manga(self, ctx, cmd, entered_title):

        # Outputs MediaStatuses to strings
        MediaStatusToString = {
            # Has completed and is no longer being released
            "FINISHED": "Finished",
            # Currently releasing
            "RELEASING": "Releasing",
            # To be released at a later date
            "NOT_YET_RELEASED": "Not yet released",
            # Ended before the work could be finished
            "CANCELLED": "Cancelled",
        }

        variables = {"search": entered_title, "page": 1, "type": cmd}

        data = (await self._request(SEARCH_ANIME_MANGA_QUERY, variables))["data"]["Page"]["media"]

        if data is not None and len(data) > 0:

            # a list of embeds
            embeds = []

            for anime_manga in data:
                # Sets up various variables for Embed
                link = f"https://anilist.co/{cmd.lower()}/{anime_manga['id']}"
                description = anime_manga["description"]
                title = anime_manga["title"]["english"] or anime_manga["title"]["romaji"]
                if anime_manga.get("nextAiringEpisode"):
                    seconds = anime_manga["nextAiringEpisode"]["timeUntilAiring"]
                    time_left = str(datetime.timedelta(seconds=seconds))
                else:
                    time_left = "Never"

                external_links = ""
                for i in range(0, len(anime_manga["externalLinks"])):
                    ext_link = anime_manga["externalLinks"][i]
                    external_links += f"[{ext_link['site']}]({ext_link['url']}), "
                    if i + 1 == len(anime_manga["externalLinks"]):
                        external_links = external_links[:-2]

                embed = discord.Embed(title=title, colour=3447003)
                embed.url = link
                embed.description = self.description_parser(description)
                embed.set_thumbnail(url=anime_manga["coverImage"]["medium"])
                embed.add_field(name="Score", value=anime_manga.get("averageScore", "N/A"))
                if cmd == "ANIME":
                    embed.add_field(name="Episodes", value=anime_manga.get("episodes", "N/A"))
                    embed.set_footer(text="Status : " + MediaStatusToString[
                        anime_manga["status"]] + ", Next episode : " + time_left + ", Powered by Anilist")
                else:
                    embed.add_field(name="Chapters", value=anime_manga.get("chapters", "N/A"))
                    embed.set_footer(text="Status : " + MediaStatusToString.get(anime_manga.get("status"),
                                                                                "N/A") + ", Powered by Anilist")
                if external_links:
                    embed.add_field(name="Streaming and/or Info sites", value=external_links)
                if anime_manga["bannerImage"]:
                    embed.set_image(url=anime_manga["bannerImage"])
                embed.add_field(name="You can find out more",
                                value=f"[Anilist]({link}), [MAL](https://myanimelist.net/{cmd.lower()}/{anime_manga['idMal']}), Kitsu (Soon™)")
                embeds.append(embed)

            return embeds, data

        else:
            return None

    async def _search_character(self, ctx, entered_title):

        variables = {"search": entered_title, "page": 1}

        data = (await self._request(SEARCH_CHARACTER_QUERY, variables))["data"]["Page"]["characters"]

        if data is not None and len(data) > 0:

            # a list of embeds
            embeds = []

            for character in data:
                # Sets up various variables for Embed
                link = f"https://anilist.co/character/{character['id']}"
                character_anime = [
                    f'[{anime["title"]["userPreferred"]}]({"https://anilist.co/anime/" + str(anime["id"])})' for anime
                    in character["media"]["nodes"] if anime["type"] == "ANIME"]
                character_manga = [
                    f'[{manga["title"]["userPreferred"]}]({"https://anilist.co/manga/" + str(manga["id"])})' for manga
                    in character["media"]["nodes"] if manga["type"] == "MANGA"]
                embed = discord.Embed(title=self.format_name(character["name"]["first"], character["name"]["last"]),
                                      colour=3447003)
                embed.url = link
                embed.description = self.description_parser(character["description"])
                embed.set_thumbnail(url=character["image"]["large"])
                if len(character_anime) > 0:
                    embed.add_field(name="Anime", value="\n".join(self.list_maximum(character_anime)))
                if len(character_manga) > 0:
                    embed.add_field(name="Manga", value="\n".join(self.list_maximum(character_manga)))
                embed.set_footer(text="Powered by Anilist")
                embeds.append(embed)

            return embeds, data

        else:
            return None

    async def _search_user(self, ctx, entered_title):

        variables = {"search": entered_title, "page": 1}

        data = (await self._request(SEARCH_USER_QUERY, variables))["data"]["Page"]["users"]

        if data is not None and len(data) > 0:

            # a list of embeds
            embeds = []

            for user in data:
                # Sets up various variables for Embed
                link = f"https://anilist.co/user/{user['id']}"
                title = f"[{user['name']}]({link})"
                title = user["name"]

                embed = discord.Embed(title=title, colour=3447003)
                embed.url = link
                embed.description = self.description_parser(user["about"])
                embed.set_thumbnail(url=user["avatar"]["large"])
                embed.add_field(name="Watched time",
                                value=datetime.timedelta(minutes=int(user["stats"]["watchedTime"])))
                embed.add_field(name="Chapters read", value=user["stats"].get("chaptersRead", "N/A"))
                for category in "anime", "manga", "characters":
                    fav = []
                    for node in user["favourites"][category]["nodes"]:
                        url_path = category
                        if category == "characters":
                            name = node["name"]
                            title = self.format_name(name["first"], name["last"])
                            url_path = "character"  # without the s
                        else:
                            title = node["title"]["userPreferred"]

                        fav.append(f'[{title}](https://anilist.co/{url_path}/{node["id"]})')

                    if fav:
                        embed.add_field(name=f"Favorite {category}", value="\n".join(self.list_maximum(fav)))
                embed.set_footer(text="Powered by Anilist")
                embeds.append(embed)

            return embeds, data

        else:
            return None

    @commands.command()
    @commands.guild_only()
    @commands.bot_has_permissions(embed_links=True, add_reactions=True)
    async def anime(self, ctx, *, entered_title):
        """Searches for anime using Anilist"""

        try:
            cmd = "ANIME"
            embeds, data = await self._search_anime_manga(ctx, cmd, entered_title)

            if embeds is not None:
                await ctx.send(embed=embeds[0])
            else:
                await ctx.send("No anime was found or there was an error in the process")

        except TypeError:
            await ctx.send("No anime was found or there was an error in the process")

    @commands.command()
    @commands.guild_only()
    @commands.bot_has_permissions(embed_links=True, add_reactions=True)
    async def manga(self, ctx, *, entered_title):
        """Searches for manga using Anilist"""

        try:
            cmd = "MANGA"
            embeds, data = await self._search_anime_manga(ctx, cmd, entered_title)

            if embeds is not None:
                await ctx.send(embed=embeds[0])
            else:
                await ctx.send("No mangas were found or there was an error in the process")
        except TypeError:
            await ctx.send("No mangas were found or there was an error in the process")

    @manga.error
    async def manga_error(self, ctx, error):
        if isinstance(error, commands.UserInputError):
            help = self.bot.get_cog('Help')
            await ctx.invoke(help.manga)

    @commands.command()
    @commands.guild_only()
    async def character(self, ctx, *, entered_title):
        """Searches for characters using Anilist"""

        try:
            embeds, data = await self._search_character(ctx, entered_title)

            if embeds is not None:
                await ctx.send(embed=embeds[0])
            else:
                await ctx.send("No characters were found or there was an error in the process")

        except TypeError:
            await ctx.send("No characters were found or there was an error in the process")

    @commands.command()
    @commands.guild_only()
    @commands.bot_has_permissions(embed_links=True, add_reactions=True)
    async def anilist(self, ctx, *, entered_title):
        """Searches users using Anilist"""

        try:
            embeds, data = await self._search_user(ctx, entered_title)

            if embeds is not None:
                await ctx.send(embed=embeds[0])
            else:
                await ctx.send("No users were found or there was an error in the process")

        except TypeError:
            await ctx.send("No users were found or there was an error in the process")

    # TODO: Faire plusieurs fichiers + ajouter un système de "menu" pour gérer des flèches etc (voir REDBot)


def setup(bot):
    bot.add_cog(AniSearch(bot))
