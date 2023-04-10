"""Module that processes all received messages"""
import re
import time
import random
import emoji
import discord
from discord.ext import commands
from modules.wordle_loser import play_wordle
from config import WORDLE_GLOBAL_BAN, WORDLE_BAN_LIST, OFFICIAL_WORDLE_CHANNEL, PRIVATE_CHANNEL

# Save the Wordle day on startup to be used to check for daily reset
WORDLE_DAY = int(play_wordle()['wordle_num'])

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
    "Wordle": "(Wordle \\d{1,} \\d/\\d)",                             # Wordle 298 3/6
    "Letterle": "(Letterle \\d{1,}/26)",                              # Letterle 7/26
    "Heardle": "(#Heardle #)\\d{1,}",                                 # #Heardle #47
    "Dordle": "(Daily Dordle #\\d{4} )((0-9|X)&(0-9|X)/7)",           # Daily Dordle #0078 X&X/7
    "Tridle": "(TRIDLE - \\d{1,}/3 words, (\\d{1,}/8 tries|failed))", # TRIDLE- 3/3 words, 7/8 tries
    "Quordle": "(Daily Quordle \\d{2,})",                             # Daily Quordle 78
    "Duotrigordle": "(Daily Duotrigordle #\\d{2,})",                  # Daily Duotrigordle #42
    "Lewdle": "(Lewdle 🍆💦 \\d{2,})( (\\d{1}|X)(/6))",              # Lewdle 🍆💦 83 5/6
    }

class OnMessage(commands.Cog):
    """Class handling all viewable messages"""
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, context):
        """Actions upon seeing any message in viewable channel"""
        global WORDLE_DAY
        message = str(context.content.lower())

        if context.author == self.bot.user:
            return

        # Relays received DM to specified channel (based on ID)
        if context.channel.type is discord.ChannelType.private:
            # Destination server can be customized in config.py
            return await send_dms_to_server(context, self.bot.get_channel(PRIVATE_CHANNEL))

        if context.channel.id in OFFICIAL_WORDLE_CHANNEL:
            if re.search(rdleverse_dict["Wordle"].lower(), message):
                # Assure that Wordle is only played once per day. wordle_day will x+1 so that it
                # won't play again until the next reset. Plays well with Eu**pe.
                message_day = int(message.split()[1])
                if WORDLE_DAY == int(play_wordle()['wordle_num']) and WORDLE_DAY == message_day:
                    await context.channel.send('alright i can beat that')
                    time.sleep(random.randint(2, 8))

                    wrdl = play_wordle(starting_word='crane',
                                       custom_list='data/wordlists/sorted-valid-wordle-words.txt',
                                       print_output=True)

                    # For some reason the number is a few days behind, even though the word is correct
                    wrdl_output = f"Wordle {int(wrdl['wordle_num'])+3} {wrdl['guess_count']}/6*\n{wrdl['emoji_block']}"
                    WORDLE_DAY = int(WORDLE_DAY) + 1
                    await context.channel.send(wrdl_output)
                    time.sleep(random.randint(1, 4))

                    # Friendly banter if whoever triggers the script does worse than dogdog
                    user_guess_count = int(message.partition('\n')[0][11])
                    if user_guess_count > int(wrdl['guess_count']):
                        await context.channel.send(
                            f"<@{context.author.id}> you suck lol. nice {user_guess_count}/6")
                    elif user_guess_count == int(wrdl['guess_count']):
                        await context.channel.send(
                            'close tbh')
                    else:
                        await context.channel.send(
                            'nvm lol')
                    return

                # Encourage easy mode Wordlers to try out hard mode
                elif not message.partition('\n')[0].endswith('*'):
                    return await context.channel.send(
                        "Consider not playing on baby mode next time, bozo")

                elif random.randint(1, 5) == 1:
                    return await context.channel.send(
                        "i wish i could wordle rn :(")

        # if 'Global Wordle Ban' is ON, or the message is in the channel or server banlist, do this:
        if (WORDLE_GLOBAL_BAN) or (context.channel.id in WORDLE_BAN_LIST) or (context.guild.id in WORDLE_BAN_LIST):
            banned_message = banned_server(message, context)
            return await context.channel.send(banned_message) if banned_message else None

        await self.bot.process_commands(context)

def setup(bot):
    """Adds the cog (module) to startup. See main/load_extensions"""
    bot.add_cog(OnMessage(bot))
