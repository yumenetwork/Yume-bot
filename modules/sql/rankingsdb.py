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

#
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#
import numpy as np
import pandas
import psycopg2
from psycopg2 import extras

from modules.sql.guild import Guild
from modules.sql.user import User

try:
    con = psycopg2.connect("host=localhost dbname=yumebot user=postgres")
    cur = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
except psycopg2.DatabaseError as e:
    print('Error %s' % e)


class RankingsDB:

    @staticmethod
    def rows_to_dict(rows) -> dict:
        rankings = {"level": rows['level'], "xp": rows['xp'], "total": rows['total'], "guild_id": rows['guild_id'],
                    "reach": rows['reach'], "user_id": rows['user_id']}
        return rankings

    """
    Get methods
    """

    @staticmethod
    def get_one(user_id: int, guild_id: int) -> dict:
        cur.execute("SELECT * FROM public.rankings WHERE user_id = {} and guild_id = {};".format(user_id, guild_id))
        rows = cur.fetchone()
        if rows:
            rankings = RankingsDB.rows_to_dict(rows)
            return rankings
        return "Error : User not found"

    @staticmethod
    def get_user(user: User, guild: Guild) -> dict:
        cur.execute(
            "SELECT * FROM public.rankings WHERE user_id = {} and guild_id = {};".format(user.user_id, guild.guild_id))
        rows = cur.fetchone()
        if rows:
            rankings = RankingsDB.rows_to_dict(rows)
            return rankings

        return "Error : User not found"

    @staticmethod
    def ranking_exists(user: User, guild: Guild) -> bool:
        cur.execute("SELECT count(*) FROM public.rankings WHERE user_id = {} AND guild_id = {};".format(user.user_id, guild.guild_id))
        rows = cur.fetchone()
        if rows[0] > 0:
            return True
        return False

    """
    Create methods
    """

    @staticmethod
    def create_ranking(user: User, guild: Guild):
        cur.execute(
            "INSERT INTO public.rankings ( guild_id, level, reach, total, user_id, xp)  VALUES ( {}, 0, 20, 0, {}, 0 );".format(
                guild.guild_id, user.user_id))
        con.commit()

    @staticmethod
    def reset_user(user: User, guild: Guild):
        cur.execute(
            "UPDATE public.rankings SET level = 0 reach = 20, total = 0, xp = 0 WHERE guild_id = {} AND user_id = {};".format(
                guild.guild_id, user.user_id))
        con.commit()

    """
    Level methods
    """

    @staticmethod
    def update_user(user: User, guild: Guild, ranking: dict):
        cur.execute(
            "UPDATE public.rankings SET level = {}, reach = {}, total = {}, xp = {} WHERE guild_id = {} AND user_id = {};".format(
                ranking['level'], ranking['reach'], ranking['total'], ranking['xp'],
                guild.guild_id, user.user_id))
        con.commit()

    @staticmethod
    def get_rank(user: User, guild: Guild) -> int:
        cur.execute(
            "SELECT user_id FROM public.rankings WHERE guild_id = {} GROUP BY user_id, total ORDER BY total DESC ".format(
                guild.guild_id))
        rows = cur.fetchall()
        if rows:
            df = pandas.DataFrame(np.array(rows), columns=["ID"])
            return df.ID[df.ID == user.user_id].index.tolist()[0] + 1
        return 0