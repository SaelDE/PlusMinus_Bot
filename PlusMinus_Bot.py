import os
import configparser
import sys
import time
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

# declare vars
plus = 0
minus = 0
neutral = 0
vote_first = 0
vote_last = 0
votes = {}

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


@bot.event
async def event_message(ctx):
    """Runs every time a message is sent in chat."""
    global votes, vote_first, vote_last

    # make sure the bot ignores itself and nightbot
    # if ctx.author.name.lower() == config['Default']['BOT_NICK'].lower():
    #    return
    if ctx.author.name.lower() == 'nightbot':
        return

    # check if message is a vote
    msg = ctx.content
    if msg[:2] == '+-' or msg[:2] == '-+' or msg[:9] == 'haugeNeut':
        vote(ctx, 'neutral')
    elif msg[:1] == '+' or msg[:9] == 'haugePlus':
        vote(ctx, 'plus')
    elif msg[:1] == '-' or msg[:9] == 'haugeMinu':
        vote(ctx, 'minus')

    # have X seconds passed since last vote? -> post end result
    if time.time() >= vote_last + 5 and vote_first != 0:
        # not enough votes?
        if len(votes) < 5:
            print('Nicht genug votes: {}'.format(len(votes)))
        else:
            get_votes()
            output = 'Endergebnis nach 5 Sekunden ohne Vote: ' \
                     'Plus: {} +++ Neutral: {} --- Minus: {} '.format(
                         plus, neutral, minus)
            await ctx.channel.send(output)
            print(output)

        vote_first = 0
        vote_last = 0
        votes.clear()

    # have X seconds passed since first vote? -> post interim result
    if time.time() >= vote_first + 10 and vote_first != 0:
        vote_first = time.time()
        get_votes()
        output = 'Zwischenergebnis: ' \
                 'Plus: {} +++ Neutral: {} --- Minus: {} '.format(
                     plus, neutral, minus)
        await ctx.channel.send(output)
        print(output)


def vote(ctx, votetype):
    global votes, vote_first, vote_last

    # is this the first vote?
    if vote_first == 0:
        vote_first = time.time()

    # set time of last vote
    vote_last = time.time()

    # add vote to dict
    votes[ctx.author.name] = votetype
    print('Vote Added: {} - {}'.format(ctx.author.name, votetype))


def get_votes():
    global plus, minus, neutral

    # reset global vars
    plus = 0
    minus = 0
    neutral = 0

    # count values in dict
    for x in votes.values():
        if x == 'neutral':
            neutral += 1
        elif x == 'plus':
            plus += 1
        elif x == 'minus':
            minus += 1


if __name__ == "__main__":
    bot.run()
