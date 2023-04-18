"""Module that processes all received messages"""
import re
import time
import random
import emoji
import discord
from discord.ext import commands
from modules.wordle import play_wordle
from config import WORDLE_GLOBAL_BAN, WORDLE_BAN_LIST, OFFICIAL_WORDLE_CHANNEL
from config import PRIVATE_CHANNEL, MODULE_SUBDIR, TIME


def daily_wordle(message, context):
    """Play Wordle and return the output along with a response to who set it off"""
    wrdl = play_wordle(custom_list='data/wordlists/sorted-valid-wordle-words.txt',
                       print_output=False)

    wrdl_output = f"Wordle {int(wrdl['wordle_num'])+3} {wrdl['guess_count']}/6*\n{wrdl['emoji_block']}"
    # For some reason the number is a few days behind, even though the word is correct
    # wrdl_day = int(wrdl['wordle_num']) + 3      # Current Wordle day

    print(f"{TIME}: Wordle {int(wrdl['wordle_num'])+3} path: {wrdl['guess_path']}")

    # Friendly banter if whoever triggers the script does worse than dogdog
    user_guess_count = message.split('/', 1)[0].rsplit(' ', 1)[1]
    # Split message by first '/' and then last ' ' to find the # of guesses required by user
    if int(user_guess_count) > int(wrdl['guess_count']):
        response = f'<@{context.author.id}> bozo. nice {user_guess_count}/6'
    elif user_guess_count == int(wrdl['guess_count']):
        response = 'ill win next time'
    else:
        response = 'sadge'
    return wrdl_output, response

def hardmode_check(message):
    """Check if user is playing Wordle in hardmode"""
    if not message.partition('\n')[0].endswith('*'):
        return "Consider not playing on baby mode next time, bozo"

def banned_server(message, context):
    """Caught playing an -rdle in an unapproved server or channel"""
    square_count = len(re.findall("(_square:)", emoji.demojize(message)))

    for key, value in rdleverse_dict.items():
        if re.search(value.lower(), message):
            print(f'Put a {key}r in their place ({context.author})')
            return f"Get lost, {key}r"
    # Catch the possibility of something rlding without the -rdle prefix
    return "Not even close to avoiding my wrath" if square_count > 9 else None

def send_dms_to_server(context, priv):
    """Send dms sent to the bot to a private server"""
    private_message = [context.content]

    if len(context.attachments) > 0:    # Length check required to avoid IndexError
        for pic in context.attachments:
            private_message.append(pic.url)

    private_joined = "\n".join(private_message)
    return priv.send(f'From {context.author}: {private_joined}')

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

class OnMessage(commands.Cog):
    """Class handling all viewable messages"""
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, context):
        """Actions upon seeing any message in viewable channel"""
        message = str(context.content.lower())

        if context.author == self.bot.user:
            return

        # Relays received DM to specified channel (based on ID)
        if context.channel.type is discord.ChannelType.private:
            # Destination server can be customized in config.py
            return await send_dms_to_server(context, self.bot.get_channel(PRIVATE_CHANNEL))

        if context.channel.id in OFFICIAL_WORDLE_CHANNEL:
            if re.search(rdleverse_dict["Wordle"].lower(), message):
                roll_check = random.randint(1, 5)

                if "⬜" in message:
                    await context.channel.send(f"Remember to change to dark theme next time <@{context.author.id}>")

                if message.split('/', 1)[0].rsplit(' ', 1)[1] == 'x':
                    return await context.channel.send("LMAO")

                elif roll_check % 2 == 0:     # If even
                    print(f"{TIME}: Playing Wordle against {context.author}")
                    time.sleep(random.randint(1, 6))
                    results, response = daily_wordle(message, context)
                    await context.channel.send(results)
                    time.sleep(random.randint(1, 4))
                    self.bot.reload_extension(f'{MODULE_SUBDIR}.wordle')
                    print(f'{TIME}: Reloaded Wordle module (on_message)')
                    return await context.channel.send(response)

                elif roll_check == 1:
                    return await context.channel.send("i wish i could wordle rn :(")

                else:
                    hardmode = hardmode_check(message)
                    return await context.channel.send(hardmode) if hardmode else None
            return

        # if 'Global Wordle Ban' is ON, or the message is in the channel or server banlist, do this:
        if (WORDLE_GLOBAL_BAN) or (context.channel.id in WORDLE_BAN_LIST) or (context.guild.id in WORDLE_BAN_LIST):
            banned_message = banned_server(message, context)
            await context.channel.send(banned_message) if banned_message else None

        await self.bot.process_commands(context)

def setup(bot):
    """Adds the cog (module) to startup. See main/load_extensions"""
    bot.add_cog(OnMessage(bot))
