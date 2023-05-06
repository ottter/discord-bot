"""Module that processes all received messages"""
import re
import time
import emoji
import random
import discord
from discord.ext import commands
from discord.ext import commands

from config import WORDLE_GLOBAL_BAN, WORDLE_BAN_LIST, OFFICIAL_WORDLE_CHANNEL
from config import PRIVATE_CHANNEL, MODULE_SUBDIR
from config import timestamp as TIME
from scripts.wordle import play_wordle


def daily_wordle(message):
    """Play Wordle and return the output along with a response to who set it off"""
    wrdl = play_wordle(custom_list='data/wordlists/sorted-valid-wordle-words.txt',
                       print_output=False, starting_word='stole')

    wrdl_output = f"Wordle {int(wrdl['wordle_num'])+3} {wrdl['guess_count']}/6*\n{wrdl['emoji_block']}"
    # For some reason the number is a few days behind, even though the word is correct
    # wrdl_day = int(wrdl['wordle_num']) + 3      # Current Wordle day

    # Friendly banter if whoever triggers the script does worse than dogdog
    user_guess_count = message.content.split('/', 1)[0].rsplit(' ', 1)[1]
    # Split message by first '/' and then last ' ' to find the # of guesses required by user
    if int(user_guess_count) > int(wrdl['guess_count']):
        response = f'{message.author.mention} nice one bozo. only a {user_guess_count}/6?'
    elif int(user_guess_count) == int(wrdl['guess_count']):
        response = f'{message.author.mention} youre just as dumb as me'
    else:
        response = 'sadge'
    return wrdl_output, response

def hardmode_check(message):
    """Check if user is playing Wordle in hardmode"""
    if not message.partition('\n')[0].endswith('*'):
        return "Consider not playing on baby mode next time, bozo"

def banned_server(message):
    """Caught playing an -rdle in an unapproved server or channel"""
    square_count = len(re.findall("(_square:)", emoji.demojize(message.content)))

    for key, value in rdleverse_dict.items():
        if re.search(value, message.content):
            print(f'Put a {key}r in their place ({message.author})')
            return f"Get lost, {key}r"
    # Catch the possibility of something rlding without the -rdle prefix
    return "Not even close to avoiding my wrath" if square_count > 9 else None

def send_dms_to_server(message, priv):
    """Send dms sent to the bot to a private server"""
    private_message = [message.content]

    if len(message.attachments) > 0:    # Length check required to avoid IndexError
        for pic in message.attachments:
            private_message.append(pic.url)

    private_joined = "\n".join(private_message)
    return priv.send(f'From {message.author}: {private_joined}')

rdleverse_dict = {
    "Letterle": "(Letterle \\d{1,}/26)",                              # Letterle 7/26
    "Heardle": "(#Heardle #)\\d{1,}",                                 # #Heardle #47
    "Dordle": "(Daily Dordle #\\d{4} )((0-9|X)&(0-9|X)/7)",           # Daily Dordle #0078 X&X/7
    "Tridle": "(TRIDLE - \\d{1,}/3 words, (\\d{1,}/8 tries|failed))", # TRIDLE- 3/3 words, 7/8 tries
    "Quordle": "(Daily Quordle \\d{2,})",                             # Daily Quordle 78
    "Duotrigordle": "(Daily Duotrigordle #\\d{2,})",                  # Daily Duotrigordle #42
    "Lewdle": "(Lewdle 🍆💦 \\d{2,})( (\\d{1}|X)(/6))",              # Lewdle 🍆💦 83 5/6
    "Wordle": "(Wordle \\d{1,} (\\d|X)/\\d)",                         # Wordle 298 3/6
    }

class OnMessageListen(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        """This requires Intents.messages to be enabled."""
        if message.author == self.bot.user:
            return

        # # dogdog is tired of being bullied for user error
        dumb_bot = r'(dumb|(?:ass)|idiot|stupid)(?:\s+\w+)?\s+((ro)?bot|(dog)?dog)'
        if re.search(dumb_bot, message.content):
            dumb_response = re.sub(r'\b(bot|(dog)?dog)\b', 'human', message.content)
            return await message.channel.send(dumb_response)

        # Relays received DM to specified channel (based on ID)
        if message.channel.type is discord.ChannelType.private:
            # Destination server can be customized in config.py
            return await send_dms_to_server(message, self.bot.get_channel(PRIVATE_CHANNEL))

        if message.channel.id in OFFICIAL_WORDLE_CHANNEL:
            if re.search(rdleverse_dict["Wordle"], message.content):
                roll_check = random.randint(1, 5)

                await self.bot.reload_extension(f'{MODULE_SUBDIR}.commands.wordle')
                print(f'{TIME()}: Reloaded Wordle module (on_message)')

                if "⬜" in message.content:
                    await message.channel.send(f"Remember to change to dark theme next time {message.author.mention}")

                if message.content.split('/', 1)[0].rsplit(' ', 1)[1] in ['x', '6']:
                    return await message.channel.send("Loooooooool")

                elif roll_check % 2 == 0:     # If even
                    print(f"{TIME()}: Playing Wordle against {message.author}")
                    time.sleep(random.randint(1, 4))
                    results, reaction = daily_wordle(message)
                    await message.channel.send(results)
                    time.sleep(random.randint(0, 2))
                    return await message.channel.send(reaction)

                elif roll_check == 1:
                    return await message.channel.send("i wish i could wordle rn :(")

                is_hardmode = hardmode_check(message.content)
                return await message.channel.send(is_hardmode) if is_hardmode else None

        # if 'Global Wordle Ban' is ON, or the message is in the channel or server banlist, do this:
        if (WORDLE_GLOBAL_BAN) or (message.channel.id in WORDLE_BAN_LIST) or (message.guild.id in WORDLE_BAN_LIST):
            banned_message = banned_server(message)
            await message.channel.send(banned_message) if banned_message else None

        await self.bot.process_commands(message)


async def setup(bot):
    await bot.add_cog(OnMessageListen(bot))