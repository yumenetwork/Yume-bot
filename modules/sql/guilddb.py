#  Copyright (c) 2019.
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
import psycopg2
from psycopg2 import extras

from modules.sql.guild import Guild

try:
    con = psycopg2.connect("host=localhost dbname=yumebot user=postgres")
    cur = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
except psycopg2.DatabaseError as e:
    print('Error %s' % e)


class GuildDB:
    @staticmethod
    def guild_from_row(rows):
        return Guild(rows['guild_id'], rows['blacklist'], rows['color'], rows['greet'], rows['greet_chan'],
                     rows['log_chan'], rows['logging'], rows['setup'], rows['stats_category'], rows['stats_channels'],
                     rows['vip'])

    @staticmethod
    def guilds_from_row(rows):
        guilds = []
        for row in rows:
            guilds.append(GuildDB.guild_from_row(row))
        return guilds

    @staticmethod
    def get_one(guild_id: int):
        cur.execute("SELECT * FROM public.guild WHERE guild_id = {};".format(guild_id))
        rows = cur.fetchone()
        if rows:
            return GuildDB.guild_from_row(rows)
        return "Error : Guild not found"

    @staticmethod
    def get_guild(guild: Guild):
        cur.execute("SELECT * FROM public.guild WHERE guild_id = {};".format(guild.guild_id))
        rows = cur.fetchone()
        if rows:
            return GuildDB.guild_from_row(rows)

        return "Error : Guild not found"

    @staticmethod
    def get_all():
        cur.execute("SELECT * FROM public.guild;")
        rows = cur.fetchall()
        if rows:
            return GuildDB.guilds_from_row(rows)
        return "Error: No Guild"

    """
    Checks methods
    """

    @staticmethod
    def is_vip(guild: Guild) -> bool:
        cur.execute('SELECT vip FROM public.guild WHERE guild_id = {};'.format(guild.guild_id))
        rows = cur.fetchone()
        if rows:
            return rows[0]
        return False

    @staticmethod
    def is_setup(guild: Guild) -> bool:
        cur.execute('SELECT setup FROM public.guild WHERE guild_id = {};'.format(guild.guild_id))
        rows = cur.fetchone()
        if rows:
            return rows[0]
        return False

    @staticmethod
    def has_blacklist(guild: Guild) -> bool:
        cur.execute('SELECT blacklist FROM public.guild WHERE guild_id = {};'.format(guild.guild_id))
        rows = cur.fetchone()
        if rows:
            return rows[0]
        return False

    @staticmethod
    def has_logging(guild: Guild) -> bool:
        cur.execute('SELECT logging FROM public.guild WHERE guild_id = {};'.format(guild.guild_id))
        rows = cur.fetchone()
        if rows:
            return rows[0]
        return False

    @staticmethod
    def guild_exists(guild: Guild) -> bool:
        cur.execute("SELECT count(*) FROM public.guild WHERE user_id = {};".format(guild.guild_id))
        rows = cur.fetchone()
        if rows[0] > 0:
            return True
        return False

    """
    Create & delete methods
    """


