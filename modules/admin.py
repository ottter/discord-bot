from discord.ext import commands
from discord import Game
import discord
import config
import json

bot_admins = [
    '150125122408153088',   # me
    '205144077144948737',   # liam
]
accepted_servers = [
    '563549980439347201',   # lightscord
    '436327337928294421',   # testing ground
]
banned_users = [
    '178563304321581056',   # jebbers
]
common_users = {
    "elena": 209385907101368322,
    "twilie": 209385907101368322,
    "morgan": 273532188803203072,
    "saj": 328043851891605506,
    "swims": 193427271992868864,
    "miles": 149187078981287936,
    "zin": 240046314321084417,
}

MODULE_SUBDIR = 'modules'
FILES_SUBDIR = 'data'


class Admin(commands.Cog):
    """Basic bot admin-level controls"""

    def __init__(self, bot):
        self.bot = bot

        # for role in context.guild.roles:
        #     if role.name in ['Philosopher', 'OG', 'Current WORST poster', 'Current BEST Pogrammer', 'Big Stonker',
        #                      'Preppy muslim', 'SUPER TAXPAYER (100K+)']:
        #         try:
        #             await member.add_roles(role)
        #         except:
        #             continue

    @commands.command()
    async def unban(self, context, member: discord.Member = None):
        if member is None:
            unban_user_id = context.message.author.id
        elif member in common_users:
            unban_user_id = common_users[context]
        else:
            unban_user_id = context.message.author.id

        unban_user = await self.bot.fetch_user(unban_user_id)

        # Users I don't want unbanned for whatever particular reason
        if (str(context.author.id) in banned_users) or (str(unban_user_id) in banned_users):
            await context.send(f'I can\'t do that, {context.author.mention}')
            return print(f'{config.time}: {context.author} failed to unban {unban_user}. Reason: Perm Banned')

        # Only users specified above are able to use this command
        if not str(context.author.id) in bot_admins:
            return print(f'{config.time}: {context.author} failed to unban {unban_user}. Reason: Invalid Admin')

        # This command is only usable in accepted servers above
        if not str(context.guild.id) in accepted_servers:
            return print(f'{config.time}: {context.author} failed to unban {unban_user}. Reason: Invalid Server')

        try:
            # Logic for banned user to unban themself, can call via DM (only works on Lightscord)
            if member is None:
                unban_server = await self.bot.fetch_guild(guild_id=436327337928294421)

            # "Logic" "for users to unban another user. Unbans in the channel it is activated in.
            else:
                unban_server = context.guild

            # Actual unban section using vars and filters from above.
            await unban_server.unban(unban_user)
            invite_link = await unban_server.create_invite(max_age=1000)
            invite_channel = await unban_user.create_dm()
            await invite_channel.send(invite_link)

            print(f'{config.time}: {context.author} unbanned {unban_user} from {context.guild}.')

        except Exception as err:
            await context.send(f'Error. Try `.unban [user ID]` or just `.unban`')
            return print(f'{config.time}: Could not unban {unban_user}. Reason: {err}')

    @commands.command()
    async def nick(self, context, nick):
        if not str(context.guild.id) in accepted_servers:
            return print(f'{config.time}: {context.author} failed to change name. Reason: Invalid Server')
        try:
            await context.author.edit(nick=nick)
        except Exception as err:
            return print(f'{config.time}: {context.author} failed to change name. Reason: {err}')

    @commands.command(pass_context=True)
    async def invite(self, context, member: discord.Member = None):
        """Send an invite link to self or user. Leave context blank or include user discord ID"""
        invite_server = context.channel
        if member is None:
            invited_user = context.message.author.id
        elif member in common_users:
            invited_user = common_users[context]
        else:
            invited_user = context.message.author.id
        try:
            invite_user = await self.bot.fetch_user(invited_user)
            invite_link = await invite_server.create_invite(max_age=1000)
            dm_channel = await invite_user.create_dm()
            await dm_channel.send(invite_link)
        except Exception as err:
            print(err)
            await context.send(f'I can\'t do that, {context.author.mention}')

    # @commands.command()
    # async def clear_role(self, context):
    #     if str(context.author.id) in bot_admins:
    #         return
    #     lightscord = await self.bot.fetch_guild(guild_id=563549980439347201)
    #     default_role = lightscord.get_role(731911251721977897)
    #     unrole_user = await self.bot.fetch_user(context.author.id)  # returns discord.Member aka James#0000
    #     print(f'cleared role {unrole_user} with {default_role}')
    #     await context.author.edit(roles=[default_role])

    @commands.command()
    async def change_prefix(self, context, prefix):
        """Custom prefixes on a per-server basis in order to prevent command overlap"""
        # TODO: Change prefix quantifier (right word?) to utilize RegEx for non-alphanumeric keyboard characters
        if str(context.message.author.id) in bot_admins:
            if len(prefix) == 1:
                with open(f'./{FILES_SUBDIR}/prefixes.json', 'r') as file:
                    prefixes = json.load(file)
                prefixes[str(context.guild.id)] = prefix
                with open(f'./{FILES_SUBDIR}/prefixes.json', 'w') as file:
                    json.dump(prefixes, file, indent=4)
                await context.send(f'Prefix changed to: {prefix}')
            else:
                await context.send(f'Entry is not a valid prefix')

    @commands.command(pass_context=True)
    async def reload(self, context, module: str):
        """Reload the specified cog [off then on]"""
        if str(context.message.author.id) in bot_admins:
            try:
                self.bot.reload_extension(f'{MODULE_SUBDIR}.{module}')
                await context.send(f'Reloaded: {module}')
            except Exception as err:
                print('{}: {}'.format(type(err).__name__, err))
                await context.send(err)
        else:
            await context.send('You don\'t have permission to do that')

    @commands.command(pass_context=True)
    async def load(self, context, module: str):
        """Loads the specified cog [on]"""
        if str(context.message.author.id) in bot_admins:
            try:
                self.bot.load_extension(f'{MODULE_SUBDIR}.{module}')
                await context.send(f'Reloaded: {module}')
            except Exception as err:
                print('{}: {}'.format(type(err).__name__, err))
                await context.send(err)
        else:
            await context.send('You don\'t have permission to do that')

    @commands.command(pass_context=True)
    async def unload(self, context, module: str):
        """Unloads the specified cog [off]"""
        if str(context.message.author.id) in bot_admins:
            try:
                self.bot.unload_extension(f'{MODULE_SUBDIR}.{module}')
                await context.send(f'Unloaded: {module}')
            except Exception as err:
                print('{}: {}'.format(type(err).__name__, err))
                await context.send('Error unloading cog')
        else:
            await context.send('You don\'t have permission to do that')

    @commands.command(pass_context=True)
    async def game(self, context):
        """Changes the 'game played' status message"""
        if str(context.message.author.id) in bot_admins:
            user_input = context.message.content.split(' ', 1)
            if user_input[1] == 'default'.lower():
                return await self.bot.change_presence(activity=Game(name=config.discord_game_played))
            await self.bot.change_presence(activity=Game(name=user_input[1]))

    @commands.command(pass_context=True)
    async def admin(self, context):
        """Lists the possible admin controls"""
        if str(context.message.author.id) in bot_admins:
            cog = ('Admin',)
            variable = ((x, y) for x in self.bot.cogs for y in cog if x == y)

            for x, y in variable:
                helper = discord.Embed(title='Admin Commands')
                for cmd in self.bot.get_cog(y).get_commands():
                    if not cmd.hidden:
                        helper.add_field(name=cmd.name, value=cmd.help, inline=False)

            await context.message.author.send('', embed=helper)
        else:
            await context.send('Bot Admin Only')

    @commands.command(hidden=True)
    async def shutdown(self, context):
        if str(context.message.author.id) in bot_admins:
            print('Shutting down...')
            await self.bot.logout()


def setup(bot):
    bot.add_cog(Admin(bot))
