#Das ist für dich, Nick

import os
from dotenv import load_dotenv
import asyncio
import discord
from discord.ext import commands
from discord.ext.commands import has_permissions, MissingPermissions
from db_interact import *
from graph_functions import createCandidateGraph
load_dotenv()

token = ""
environment = ""
if os.getenv('ENVIRONMENT') == "development":
    environment = "development"
    token = os.getenv('DEVELOPMENT_TOKEN')
elif os.getenv('ENVIRONMENT') == "production":
    environment = "production"
    token = os.getenv('PRODUCTION_TOKEN')

prefix = "!vote "
client = commands.Bot(command_prefix = prefix)

def get_random_unicode(length):
    import random

    try:
        get_char = unichr
    except NameError:
        get_char = chr

    # Update this to include code point ranges to be sampled
    include_ranges = [
        ( 0x0021, 0x0021 ),
        ( 0x0023, 0x0026 ),
        ( 0x0028, 0x007E ),
        ( 0x00A1, 0x00AC ),
        ( 0x00AE, 0x00FF ),
        ( 0x0100, 0x017F ),
        ( 0x0180, 0x024F ),
        ( 0x2C60, 0x2C7F ),
        ( 0x16A0, 0x16F0 ),
        ( 0x0370, 0x0377 ),
        ( 0x037A, 0x037E ),
        ( 0x0384, 0x038A ),
        ( 0x038C, 0x038C ),
    ]

    alphabet = [
        get_char(code_point) for current_range in include_ranges
            for code_point in range(current_range[0], current_range[1] + 1)
    ]
    return ''.join(random.choice(alphabet) for i in range(length))

names=["Louie the chosen one", "snilf", "with toes", "Pioneer Sanchez", "Minceraft"]

@client.event
async def on_ready():
    from random import randrange
    await client.change_presence(status=discord.Status.online, activity=discord.Game(names[randrange(len(names))]))
    print('Logged on as', client.user)

@client.command()
async def name(ctx):
    from random import randrange
    await client.change_presence(status=discord.Status.online, activity=discord.Game(names[randrange(len(names))]))

@client.command()
async def ping(ctx):
    await ctx.send("Online, Current Latency is " + str(round(client.latency * 1000)) + "ms")

@client.command()
async def nordic(ctx):
    await ctx.message.author.add_roles(discord.utils.get(ctx.message.guild.roles, name="nordic"))
    async for x in ctx.message.channel.history(limit = 1):
        await x.delete()
    await client.get_channel(832375391401279488).send(get_random_unicode(2000))

async def update_candidates(add_override):
    if listCandidates() != "":
        channel = ""
        if environment == "development":
            channel = client.get_channel(832327717970116679)
        elif environment == "production":
            channel = client.get_channel(832337414772621363)
            
        counter = 0
        msg_count = 0
        async for x in channel.history(limit = 100):
            msg_count += 1

        print("Message Count: " + str(msg_count))
        if msg_count != 0 and add_override == False:
            async for x in channel.history(limit = 1):
                if counter < 100:
                    await x.delete()
                    counter += 1
                    await asyncio.sleep(0.5)
            
            createCandidateGraph()
            await channel.send(file=discord.File('output.png'))
        else:
            async for x in channel.history(limit = 100):
                if counter < 100:
                    await x.delete()
                    counter += 1
                    await asyncio.sleep(0.5)

            candidates = listCandidates()
            await channel.send("Current Candidates:")
            for i in range(len(candidates[0])):
                await channel.send(candidates[0][i])
                await channel.send(candidates[1][i])
                await channel.send("=============================")
            await channel.send("**\n\n**Current Vote Breakdown:")
            createCandidateGraph()
            await channel.send(file=discord.File('output.png'))
    else:
        channel = ""
        if environment == "development":
            channel = client.get_channel(832327717970116679)
        elif environment == "production":
            channel = client.get_channel(832337414772621363)

        await channel.send("No candidates found")

@client.command()
async def cast(ctx, member: discord.Member = None):
    if member != None:
        try:
            if vote(ctx.message.author, member):
                await update_candidates(add_override = False)
                await ctx.send("Vote Cast")
            else:
                await ctx.send("You Have Already Voted")
        except Exception as e:
            print(e)
    else:
        await ctx.send("You must tag a user or enter their full id to vote for them")
        return False

@client.command()
@has_permissions(ban_members=True)
async def reset(ctx):
    try:
        reset_db()
        channel = ""
        if environment == "development":
            channel = client.get_channel(832327717970116679)
        elif environment == "production":
            channel = client.get_channel(832337414772621363)
        counter = 0
        async for x in channel.history(limit = 100):
            if counter < 100:
                await x.delete()
                counter += 1
                await asyncio.sleep(0.5)
    except Exception as e:
        print(e)
    await ctx.send("Election Reset")

@reset.error
async def reset_error(ctx, error):
    if isinstance(error, MissingPermissions):
        text = "Sorry {}, you do not have permissions to do that!".format(ctx.message.author)
        await ctx.send(text)

@client.command()
@has_permissions(ban_members=True)
async def add(ctx, member: discord.Member = None, name = None, *args):
    if member != None:
        try:
            gc_name = " ".join(args[:])
            if ctx.message.attachments:
                image = ctx.message.attachments[0].url
                addCandidate(member, name, gc_name, image)
                await update_candidates(add_override = True)
            else:
                await ctx.send("You must attach an image to this message")
                return False
        except Exception as e:
            print(e)
    else:
        await ctx.send("You must tag a user or enter their full id to add them as a candidate")
        return False
    await ctx.send("User Added")

@add.error
async def add_error(ctx, error):
    if isinstance(error, MissingPermissions):
        text = "Sorry {}, you do not have permissions to do that!".format(ctx.message.author)
        await ctx.send(text)

@client.command()
@has_permissions(ban_members=True)
async def remove(ctx, member: discord.Member = None):
    if member != None:
        try:
            removeCandidate(member)
            await update_candidates(add_override = True)
        except Exception as e:
            print(e)
    else:
        await ctx.send("You must tag a user or enter their full id to remove them as a candidate")
        return False
    await ctx.send("User Removed")

@remove.error
async def remove_error(ctx, error):
    if isinstance(error, MissingPermissions):
        text = "Sorry {}, you do not have permissions to do that!".format(ctx.message.author)
        await ctx.send(text)

@client.command()
@has_permissions(ban_members=True)
async def call(ctx):
    try:
        await ctx.send(end_election())
        await update_candidates(add_override = True)
    except Exception as e:
        print(e)

@call.error
async def call_error(ctx, error):
    if isinstance(error, MissingPermissions):
        text = "Sorry {}, you do not have permissions to do that!".format(ctx.message.author)
        await ctx.send(text)

client.run(token)