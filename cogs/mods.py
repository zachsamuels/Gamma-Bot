from discord.ext import commands
from datetime import datetime
import discord
import asyncio


class Mods:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        aliases=['bl', 'toggle'],
        description="Blacklist a certain user from using any of my commands.",
        brief="Blacklist a user from my commands."
    )
    @commands.has_permissions(manage_guild=True)
    async def blacklist(self, ctx, *, user: discord.Member):
        if ctx.guild.id not in self.bot.user_blacklist:
            self.bot.user_blacklist.setdefault(ctx.guild.id, list())
        if user.id in self.bot.user_blacklist.get(ctx.guild.id):
            self.bot.user_blacklist[ctx.guild.id].remove(user.id)
            d = f"<:nano_check:484247886461403144> {user} is no longer blacklisted."
            b = "white"
        else:
            self.bot.user_blacklist[ctx.guild.id].append(user.id)
            d = f"<:nano_check:484247886461403144> {user} is now blacklisted."
            b = "black"
        await ctx.send(
            embed=discord.Embed(
                color=discord.Color.blurple(),
                description=d
            )
        )
        logging = await self.bot.get_logging_channel(ctx.guild)
        if not logging:
            return
        embed = discord.Embed(
            color=discord.Color.blurple(),
            title=f"{user}",
            timestamp=datetime.utcnow(),
            description=f"**Responsible Moderator**\n{ctx.author}"
        )
        embed.set_author(
            name=f"User was {b}listed",
            icon_url=user.avatar_url_as(format="png")
        )
        await logging.send(embed=embed)

    @commands.command(
        aliases=['vbl', 'viewblacklist'],
        description="View a list of people who are blacklisted from using my commands.",
        brief="View the current guilds blacklist."
    )
    @commands.has_permissions(manage_guild=True)
    async def view_blacklist(self, ctx):
        try:
            data = self.bot.user_blacklist.get(ctx.guild.id)
        except KeyError:
            raise discord.errors.CommandError("Guild does not have a blacklist.")
        mems = [str(ctx.guild.get_member(d)) for d in data]
        await ctx.send(
            embed=discord.Embed(
                color=discord.Color.blurple(),
                description="\n".join(mems),
                title=f"{ctx.guild} blacklist"
            ).set_footer(text="Note: Ignores Xua#9307 and anyone with Administrator permissions")
        )

    @commands.command(
        aliases=['prune', 'clear'],
        description="Purge a set number of messages from a channel.",
        brief="Purge some messages."
    )
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True)
    async def purge(self, ctx, amount: int, user: discord.Member=None):
        try:
            self.bot.is_purging[ctx.channel.id] = True
        except KeyError:
            self.bot.is_purging.setdefault(ctx.channel.id, True)
        if user:
            def check(message):
                return message.author == user
            m = await ctx.channel.purge(limit=amount, check=check)
            await ctx.send(
                embed=discord.Embed(
                    color=discord.Color.blurple(),
                    description=f"<:nano_check:484247886461403144> Deleted {len(m)} messages."
                ),
                delete_after=3
            )
        else:
            m = await ctx.channel.purge(limit=amount)
            await ctx.send(
                embed=discord.Embed(
                    color=discord.Color.blurple(),
                    description=f"<:nano_check:484247886461403144> Deleted {len(m)} messages."
                ),
                delete_after=3
            )
        logging = await self.bot.get_logging_channel(ctx.guild)
        if logging:
            amount = len(m)
            embed = discord.Embed(
                color=discord.Color.blurple(),
                timestamp=datetime.utcnow(),
                description=f"{ctx.channel.mention}"
            )
            embed.set_author(
                name="Chat was purged",
                icon_url=ctx.author.avatar_url_as(format="png")
            )
            embed.add_field(
                name="Total messages deleted",
                value=f"{amount}"
            )
            if user:
                embed.add_field(
                    name="Affected user",
                    value=f"{user}"
                )
            embed.add_field(
                name="Responsible Moderator",
                value=f"{ctx.author}"
            )
            await logging.send(embed=embed)
        await asyncio.sleep(2)
        self.bot.is_purging[ctx.channel.id] = False


def setup(bot):
    bot.add_cog(Mods(bot))
