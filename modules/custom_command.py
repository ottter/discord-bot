from discord.ext import commands


def cc_add():
    print('1 add')


def cc_list():
    print('2 list')


def cc_delete():
    print('3 delete')


def cc_help():  # syntax help for creating a custom command
    print('4 help')


class CustomCommand(commands.Cog):
    """Gives users the ability to add simple custom commands"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['cc'])
    async def _cc(self, context):
        args = context.message.content.lower().split(" ", 1)
        if args[1] in ['add', 'a']:
            cc_add()
        elif args[1] in ['list', 'ls', 'l']:
            cc_list()
        elif args[1] in ['del', 'delete', 'rm', 'd']:
            cc_delete()
        elif args[1] in ['help', 'h']:
            cc_help()
        else:
            print('invalid entry')


def setup(bot):
    bot.add_cog(CustomCommand(bot))
