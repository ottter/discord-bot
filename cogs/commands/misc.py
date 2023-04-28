from discord.ext import commands
from random import randint
from config import timestamp as TIME


def dice_roll(dice, user_id):
    try:
        rolls, sides = map(int, dice[1].split('d'))
        result = ', '.join(str(randint(1, sides)) for r in range(rolls))
        output = f'🎲 <@{user_id}> rolled {rolls} d{sides} dice and the results are: 🎲 \n '
        return(output + result)

    except IndexError:
        result = str(randint(1, 100))
        return(f'🎲 <@{user_id}> rolled 1-100 and got: {result}🎲')

    except Exception as err:
        print(err)
        return('Format has to be in NdN! Example: 4d6')

class MiscCmd(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, context):
        """Test latency to server"""
        server_ping = round(self.bot.latency * 1000)
        print(f"{TIME()}: {context.author} pinged the server: {server_ping}ms")
        await context.send(f"Ping: {server_ping}ms")

    @commands.cooldown(1, 2, commands.BucketType.user)
    @commands.command(name='roll', aliases=['dice'], pass_context=True)
    async def dice_roll(self, context):
        """Use RNG to roll NdN dice
            .roll  ==== RNG 1-100 result
            .roll 2d6 = RNG 2 6-sided dice rolls"""
        user_id = context.message.author.id
        user_input = str(context.message.content)
        dice = user_input.split(' ', 1)

        output = dice_roll(dice, user_id)
        await context.send(output)

async def setup(bot):
    """Adds the cog (module) to startup. See main/load_extensions"""
    await bot.add_cog(MiscCmd(bot))