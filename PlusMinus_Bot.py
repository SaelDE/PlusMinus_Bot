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

# check delays to prevent excessive spamming or prematurely ending votes
if int(config['Vote']['DELAY_END']) < 5:
    config['Vote']['DELAY_END'] = '5'
    print('DELAY_END too low. Setting DELAY_END to 5 seconds')
if int(config['Vote']['DELAY_INTERIM']) < 15:
    config['Vote']['DELAY_INTERIM'] = '15'
    print('DELAY_INTERIM too low. Setting DELAY_INTERIM to 15 seconds')
if int(config['Vote']['DELAY_END']) > int(config['Vote']['DELAY_INTERIM']):
    config['Vote']['DELAY_END'] = config['Vote']['DELAY_INTERIM']
    print('DELAY_END too high. Setting DELAY_END to {}'.format(config['Vote']['DELAY_INTERIM']))

# declare global vars
plus = 0
minus = 0
neutral = 0
vote_first = 0
vote_last = 0
votes = {}
spammer = {}

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
    global votes, vote_first, vote_last, spammer

    # make sure the bot ignores itself and nightbot
    if ctx.author.name.lower() == config['Default']['BOT_NICK'].lower():
        return
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
    if time.time() >= vote_last + int(config['Vote']['DELAY_END']) and vote_first != 0:
        # not enough votes?
        if len(votes) < int(config['Vote']['VOTES_MIN']):
            print('Not enough votes: {}'.format(len(votes)))
        else:
            get_votes()
            output = '/me Plus: {} ({}%) + Neutral: {} ({}%) - Minus: {} ({}%) ' \
                     'Endergebnis nach {} Sekunden ohne neuen Vote.' \
                     ' '.format(plus,
                                int(plus / len(votes) * 100),
                                neutral,
                                int(neutral / len(votes) * 100),
                                minus,
                                100-int(plus / len(votes) * 100)-int(neutral / len(votes) * 100),
                                config['Vote']['DELAY_END'])

            # spammer_top = max(spammer, key=spammer.get)
            # if spammer[spammer_top] >= 10:
            #     output = output + '@{} ({}) hör auf zu spammen!'.format(spammer_top,
            #                                                        spammer[spammer_top])
            await ctx.channel.send(output)
            print('Sending: {}'.format(output))

        vote_first = 0
        vote_last = 0
        votes.clear()
        spammer.clear()

    # have X seconds passed since first vote? -> post interim result
    if time.time() >= vote_first + int(config['Vote']['DELAY_INTERIM']) and vote_first != 0:
        # not enough votes?
        if len(votes) < int(config['Vote']['VOTES_MIN']):
            print('Not enough votes: {}'.format(len(votes)))
            vote_first = 0
            vote_last = 0
            votes.clear()
            spammer.clear()
        else:
            vote_first = time.time()
            get_votes()
            output = '/me Plus: {} ({}%) + Neutral: {} ({}%) - Minus: {} ({}%) ' \
                     'Zwischenergebnis nach {} Sekunden durchgängige Votes.' \
                     ' '.format(plus,
                                int(plus / len(votes) * 100),
                                neutral,
                                int(neutral / len(votes) * 100),
                                minus,
                                100-int(plus / len(votes) * 100)-int(neutral / len(votes) * 100),
                                config['Vote']['DELAY_INTERIM'])

            await ctx.channel.send(output)
            print('Sending: {}'.format(output))


def vote(ctx, votetype):
    """adds votes to the votes-dict and sets timestamps"""
    global votes, vote_first, vote_last, spammer

    # is this the first vote?
    if vote_first == 0:
        vote_first = time.time()

    # new, changed or spam?
    if ctx.author.name in votes:
        if votes[ctx.author.name] == votetype:
            print('Vote spam: {} - {} -> {}'.format(ctx.author.name, votes[ctx.author.name], votetype))
            if ctx.author.name in spammer:
                spammer[ctx.author.name] = spammer[ctx.author.name] + 1
            else:
                spammer[ctx.author.name] = 1
                # spammers dont' set vote_last, so they cannot extend the time a vote lasts.
        else:
            print('Vote changed: {} - {} -> {}'.format(ctx.author.name, votes[ctx.author.name], votetype))
            # set time of last vote in case vote changed
            vote_last = time.time()
    else:
        print('Vote added: {} - {}'.format(ctx.author.name, votetype))
        # set time of last vote in case it is a new vote
        vote_last = time.time()

    # add vote to dict
    votes[ctx.author.name] = votetype


def get_votes():
    """analyzes the votes-dict and counts the votes"""
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
