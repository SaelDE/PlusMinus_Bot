import os
import configparser
import sys
from twitchio.ext import commands

# Check platform
if sys.platform == "linux" or sys.platform == "linux2":
    configfile = '/config.ini'
elif sys.platform == "win32":
    configfile = '\\config.ini'
else:
    print('Platform unsupported: {}'.format(sys.platform))
    sys.exit()

# get current folder
dir_path = os.path.dirname(os.path.realpath(__file__))

# init config
config = configparser.ConfigParser()
config.read(dir_path + configfile)

# declare messages list
messages = [], []


bot = commands.Bot(
    # set up the bot
    irc_token=config['Default']['TMI_TOKEN'],
    client_id=config['Default']['CLIENT_ID'],
    nick=config['Default']['BOT_NICK'],
    prefix=config['Default']['BOT_PREFIX'],
    initial_channels=[config['Default']['CHANNEL']]
)


@bot.event
async def event_ready():
    """Called once when the bot goes online."""
    print('Logged in as {}. Listening to channel {}.'.format(config['Default']['BOT_NICK'],
                                                             config['Default']['CHANNEL']))



@bot.command(name='plusminus')
async def plusminus(ctx):
    """command !plusminus for a special voting method"""
    if ctx.message.tags['mod'] == 1:
        pass
    elif ctx.author.name.lower() == 'derhauge':
        pass
    elif ctx.author.name.lower() == 'sael_de':
        pass
    else:
        print('Invalid User: {}'.format(ctx.author.name))
        return

    plus = 0
    minus = 0
    neutral = 0
    voters = []

    for i in range(len(messages[0])):
        msg = messages[0][i]
        user = messages[1][i]

        if user not in voters:
            if msg[:2] == ['+-'] or msg[:2] == ['-+'] or msg[:9] == ['haugeNeut']:
                neutral += 1
                voters.append(user)
            elif msg[:1] == ['+'] or msg[:9] == ['haugePlus']:
                plus += 1
                voters.append(user)
            elif msg[:1] == ['-'] or msg[:9] == ['haugeMinu']:
                minus += 1
                voters.append(user)

    if (neutral + plus + minus) == 0:
        await ctx.send('Keine gültigen Votes in den letzten {} Nachrichten gefunden.'.format(len(messages[0])))
    else:
        # Nightbot does not like visualizations:
        # bar = '||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||'
        # scale = 3
        # plus_len = int(round((plus / (neutral + plus + minus) * 100) / scale, 0))
        # neutral_len = int(round((neutral / (neutral + plus + minus) * 100) / scale, 0))
        # minus_len = int(round((minus / (neutral + plus + minus) * 100) / scale, 0))
        # output = 'Ergebnis der letzten {} MSGs: ' \
        #         'Plus: {} --- Neutral: {} --- Minus: {} ' \
        #         '+|{}|_|{}|_|{}|-'.format(
        #            len(messages[0]), plus, neutral, minus, bar[:plus_len], bar[:neutral_len], bar[:minus_len])
        
        output = 'Ergebnis der letzten {} MSGs: ' \
                 'Plus: {} --- Neutral: {} --- Minus: {} '.format(
                     len(messages[0]), plus, neutral, minus)
        await ctx.send(output)
        print(output)


@bot.event
async def event_message(ctx):
    """Runs every time a message is sent in chat."""

    # make sure the bot ignores itself and nightbot
    if ctx.author.name.lower() == config['Default']['BOT_NICK'].lower():
        return
    if ctx.author.name.lower() == 'nightbot':
        return

    # log every message
    # print('{}: {}'.format(ctx.author.name, ctx.content))
    messages[0].append([ctx.content])
    messages[1].append([ctx.author.name])

    # remove the last message over 150
    if len(messages[0]) > 150:
        messages[0].pop(0)
        messages[1].pop(0)

    # hook for commands
    await bot.handle_commands(ctx)

if __name__ == "__main__":
    bot.run()
