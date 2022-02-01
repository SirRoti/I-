import discord
from discord.ext import commands
from discord.ext.commands import has_permissions

from configparser import ConfigParser

from colorama import Fore
import datetime

# OTM3NDExNjY4NDk1OTcwMzM0.YfbWpg.c40G-kIMkpcfdaLRUve_ZVDFi7s
token = "NzU3MTEwNjI3NjkyMDUyNDkw.X2boOA.GDy1QY1WGDIgPahFLj7Fu4LGiUE"
prefix = '>'

client = commands.Bot(command_prefix=prefix)
client.remove_command('help')

@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game(">help"))
    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {Fore.MAGENTA}Bot Started...{Fore.RESET}")

@client.event
async def on_message(ctx):
    data_file = "data.ini"
    data = ConfigParser()
    data.read(data_file)

    if ctx.author.bot:
        return

    guild_id = str(ctx.guild.id)

    if ctx.content.startswith(prefix):
        print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Command : {Fore.LIGHTCYAN_EX}{ctx.content}{Fore.RESET} on {ctx.guild} ({ctx.guild.id})")
        await client.process_commands(ctx)

    if ctx.content.isdigit() and str(ctx.channel.id) == data[guild_id]["channel"]:
        guild_steps = data[guild_id]["steps"]
        next_number = int(data[guild_id]["number"])+int(guild_steps)
        if ctx.content == str(next_number):
            if str(ctx.author.id) != data[guild_id]["user"]:
                data[guild_id]["number"] = str(next_number)
                data[guild_id]["message"] = str(ctx.id)
                data[guild_id]["user"] = str(ctx.author.id)
                if next_number == 100:
                    await ctx.add_reaction('💯')
                else:
                    await ctx.add_reaction('✅')
            else:
                data[guild_id]["number"] = "0"
                data[guild_id]["message"] = "none"
                data[guild_id]["user"] = "none"
                await ctx.add_reaction('❌')
                await ctx.reply(f"```Counting was interrupted by {ctx.author}\nReason: You can't count twice in a row\nCount restarts at {guild_steps}```")
        else:
            data[guild_id]["number"] = "0"
            data[guild_id]["message"] = "none"
            data[guild_id]["user"] = "none"
            await ctx.add_reaction('❌')
            if guild_steps > "1":
                extra_info = f"\nInfo: Server Counting Steps are set to {guild_steps}"
            else:
                extra_info = ""
            await ctx.reply(f"```Counting was interrupted by {ctx.author}\nReason: Wrong Number{extra_info}\nCount restarts at {guild_steps}```")
        with open(data_file, "w") as data_dump:
            data.write(data_dump)

@client.event
async def on_message_delete(ctx):
    data_file = "data.ini"
    data = ConfigParser()
    data.read(data_file)

    if ctx.author.bot:
        return

    guild_id = str(ctx.guild.id)

    if str(ctx.id) == data[guild_id]["message"]:
        channel = client.get_channel(int(data[guild_id]["channel"]))
        guild_steps = data[guild_id]["steps"]
        next_number = int(data[guild_id]["number"])+int(guild_steps)
        await channel.send(f"```The last counting message by {ctx.author} was deleted\nThe next counting number would be {next_number}```")
    

@client.command()
async def help(ctx):
    await ctx.message.reply("```\nCommand List:\n - help >> shows this list\n - setchannel [channel] >> sets a count channel\n - setsteps [steps] >> sets the steps in witch the users have to count\n - deletedata >> deletes any data i got about the server```")

@client.command()
async def setchannel(ctx, message_channel=None):
    if ctx.author.guild_permissions.administrator:
        data_file = "data.ini"
        data = ConfigParser()
        data.read(data_file)

        guild_id = str(ctx.guild.id)

        if message_channel == None:
            await ctx.message.reply("```Please provide a channel```")
            return 

        try:
            channel = discord.utils.get(client.get_all_channels(), id=int(message_channel[2:20]))
        except:
            await ctx.message.reply("```Please ping the channel```")
            return

        try:
            if data[guild_id]["channel"] == str(channel.id):
                await ctx.message.reply(f"```Counting Channel is already set to {channel}```")
                return
            data[guild_id]["channel"] = str(channel.id)
        except:
            data.add_section(guild_id)
            data.set(guild_id, "channel", str(channel.id))
            data.set(guild_id, "number", "0")
            data.set(guild_id, "message", "none")
            data.set(guild_id, "user", "none")
            data.set(guild_id, "steps", "1")
        with open(data_file, "w") as data_dump:
            data.write(data_dump)
        await ctx.message.reply(f"```Counting Channel was set to {channel}```")
    else:
        await ctx.message.reply("```You don't have Permission to do that```")

@client.command()
async def setsteps(ctx, steps=None):
    if ctx.author.guild_permissions.administrator:
        data_file = "data.ini"
        data = ConfigParser()
        data.read(data_file)

        guild_id = str(ctx.guild.id)

        if steps == None:
            await ctx.message.reply("```Please provide a steps number```")
            return
        if not steps.isdigit():
            await ctx.message.reply("```Pleas provide a valid number```")
            return
        elif int(steps) > 100 or int(steps) < 1:
            await ctx.message.reply("```You're steps value can be between 1 and 100```")
            return
        else:
            try:
                data[guild_id]["steps"] = steps
            except:
                data.add_section(guild_id)
                data.set(guild_id, "channel", "none")
                data.set(guild_id, "number", "0")
                data.set(guild_id, "message", "none")
                data.set(guild_id, "user", "none")
                data.set(guild_id, "steps", steps)
            with open(data_file, "w") as data_dump:
                data.write(data_dump)
            await ctx.message.reply(f"```Steps value was set to {steps}```")


    else:
        await ctx.message.reply("```You don't have Permission to do that```")

@client.command()
async def deletedata(ctx):
    if ctx.author.guild_permissions.administrator:
        data_file = "data.ini"
        data = ConfigParser()
        data.read(data_file)

        guild_id = str(ctx.guild.id)

        try:
            data.remove_section(guild_id)
        except:
            await ctx.message.reply("```Your Server has no Data```")
            return
        with open(data_file, "w") as data_dump:
            data.write(data_dump)
        await ctx.message.reply("```Your Server Data was deleted```")
    else:
        await ctx.message.reply("```You don't have Permission to do that```")

client.run(token)