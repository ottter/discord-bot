from discord.ext import commands
from random import choice, randint
import config


def fbi_pasta_text(name, version):
    pasta_1 = f"I, {name} , DECLARE THAT EVERY POST I HAVE EVER MADE ON THIS DISCORD IS SATIRE. I DO NOT CONDONE NOR " \
              f"SUPPORT ANY OF THE OPINIONS EXPRESSED ON THIS CHATROOM."
    pasta_2 = f"\n\nAny post associated with this IP is satire " \
              f"and should be treated as such. At no point has anyone associated with this IP ever condoned, encouraged, " \
              f"committed or abated acts of violence or threats of violence against any persons, regardless of racial, " \
              f"ethnic, religious or cultural background.\n\nIn case of an investigation by any federal entity or similar, " \
              f"I do not have any involvement with this group or with the people in it, I do not know how I am here, " \
              f"probably added by a third party, I do not support any actions by the members of this group."
    # spam_prev = "\n\n*React with `✔`️ for full pasta and `❌` for abbreviated version*"
    if version == 'long':
        return pasta_1 + pasta_2
    elif version == 'short':
        return pasta_1


class Misc(commands.Cog):
    """Miscellaneous commands that did not fit in anywhere else"""
    def __init__(self, bot):
        self.bot = bot

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name='8ball', pass_context=True)
    async def eight_ball(self, context):
        """Ask the magic 8 ball any question"""
        possible_responses = [
            'It is certain', 'It is decidedly so', 'Without a doubt', 'Yes definitely', 'You may rely on it',
            'As I see it, yes', 'Most likely', 'Outlook good', 'Yes', 'Signs point to yes', 'Reply hazy try again',
            'Ask again later', 'Better not tell you now', 'Cannot predict now', 'Concentrate and ask again',
            'Don\'t count on it', 'My reply is no', 'My sources say no', 'Outlook not so good', 'Very doubtful']
        await context.send(f"🎱 {choice(possible_responses)}, {context.message.author.mention} 🎱")

    @commands.cooldown(1, 2, commands.BucketType.user)
    @commands.command(name='roll', aliases=['dice'], pass_context=True)
    async def dice_roll(self, context):
        """Use RNG to roll NdN dice
            .roll  ==== RNG 1-100 result
            .roll 2d6 = RNG 2 6-sided dice rolls"""
        user_id = context.message.author.id
        user_input = str(context.message.content)
        dice = user_input.split(' ', 1)

        try:
            rolls, sides = map(int, dice[1].split('d'))
            result = ', '.join(str(randint(1, sides)) for r in range(rolls))
            await context.send(f'🎲 <@{user_id}> rolled {rolls} d{sides} dice and the results are: 🎲 \n ' + result)

        except IndexError:    # More elegant ways? sure. Easier ways? no.
            result = str(randint(1, 100))
            await context.send(f'🎲 <@{user_id}> rolled 1-100 and got: {result}🎲')

        except Exception as err:
            print(err)
            await context.send('Format has to be in NdN! Example: 4d6')

    @commands.cooldown(1, 2, commands.BucketType.user)
    @commands.command(name='fbi', aliases=['cia', 'nsa'], pass_context=True)
    async def fbi_pasta(self, context):
        user = context.message.author.mention
        pasta = fbi_pasta_text(user, 'short')
        response = await context.send(pasta)

        if not config.FBI_PASTA_BOOL:
            return

        await response.add_reaction(emoji='✔️')
        await response.add_reaction(emoji='❌')


    # TODO: word-association-metagame https://wordassociations.net/en random response


def setup(bot):
    bot.add_cog(Misc(bot))
