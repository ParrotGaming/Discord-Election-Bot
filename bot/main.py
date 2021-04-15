#Das ist für dich, Nick

import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
from discord.ext.commands import has_permissions, MissingPermissions
from db_interact import *
from graph_functions import createCandidateGraph
load_dotenv()

token = ""
if os.getenv('ENVIRONMENT') == "development":
    token = os.getenv('DEVELOPMENT_TOKEN')
elif os.getenv('ENVIRONMENT') == "production":
    token = os.getenv('PRODUCTION_TOKEN')

prefix = "!vote "
client = commands.Bot(command_prefix = prefix)

@client.event
async def on_ready():
    print('Logged on as', client.user)

@client.command()
async def ping(ctx):
    await ctx.send("Online, Current Latency is " + str(round(client.latency * 1000)) + "ms")

@client.command()
async def candidates(ctx):
    createCandidateGraph()
    if listCandidates() != "":
        await ctx.message.author.send(listCandidates())
        await ctx.message.author.send(file=discord.File('output.png'))
    else:
        await ctx.message.author.send("No candidates found")

@client.command()
async def cast(ctx, member: discord.Member = None):
    if member != None:
        try:
            if vote(ctx.message.author, member):
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
            addCandidate(member, name, gc_name)
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
    except Exception as e:
        print(e)

@call.error
async def call_error(ctx, error):
    if isinstance(error, MissingPermissions):
        text = "Sorry {}, you do not have permissions to do that!".format(ctx.message.author)
        await ctx.send(text)

client.run(token)