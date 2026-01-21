import discord
from discord.ext import commands
import asyncio
import random
import logging
import os
import datetime
from dotenv import load_dotenv
#import webserver

#pinged by uptimerobot

#from flask import Flask
#from threading import Thread

load_dotenv()
loc = 'DISCORD_TOKEN'
pub = 'discordkey'
TOKEN = os.getenv(pub)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("bot")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

# ---------- Session state ----------
class SessionState:
    def __init__(self):
        self.hp = 2
        self.max_hp = 3
        self.loot_id = None
        self.current_channel = None  # always a discord.TextChannel
        self.user_loot = {}
        self.last_gold_response = {}  # per-channel throttle
        self.minTime = 1500
        self.maxTime = 70000
        self.respawnDaysMax = 3
        self.nextRandMsg = None

session = SessionState()
LOOT_FILE = "membersData.txt"

roleReactMsgId = [
    1463294603250634857,
    1463294624272613490
]


# app = Flask('')
# @app.route('/')
# def home():
#     return "Discord bot ok"

# def run():
#     app.run(host="0.0.0.0", port=8080)

# def keep_alive():
#     t = Thread(target=run)
#     t.start()



# ---------- Helper functions ----------
async def load_loot():
    def _load():
        loot = {}
        try:
            with open(LOOT_FILE, "r") as f:
                for line in f:
                    user_id, amount = line.split()
                    loot[int(user_id)] = int(amount)
        except FileNotFoundError:
            pass
        return loot
    session.user_loot = await asyncio.to_thread(_load)

async def save_loot():
    def _save():
        with open(LOOT_FILE, "w") as f:
            for user_id, amount in session.user_loot.items():
                f.write(f"{user_id} {amount}\n")
    await asyncio.to_thread(_save)

# ---------- Responses ----------
gold_responses = [
    'gold you say', 
    'did I hear gold', 
    'gold mentioned', 
    'gold?',
    'yooo', 
    'what was that', 
    'can you repeat that', 
    'hey', 
    'hiii', 
    ':eyes:'
]

random_messages = [
    '(walks past)', 
    '(coughs)', 
    '(cough cough)',
    'urgh',
    'hrm',
    'huff',
    'has anybody seen my inhaler',
    '(grinds axe)',
    '(buries hatchet)',
    'you know which part of a joke is the most important? the execution- har har har',
    'is that gold over there',
    '(achoo)',
    '(stands menacingly)',
    '(looks for a fight)',
    'i sure hope no one takes my loot today',
    'yarr',
    '(cough)',
    '(draped in shadow)',
    'ugg',
    'trans rights',
    'what\'s up my goat :goat:',
    'my boss is gonna kill me if he finds out how few people i executed this week',
    'you\'re gonna need a rescue party after i\'m done with you',
    '(walks by)',
    'har har har',
    'what\'s that over there',
    'huff',
    'arr',
    'phew',
    'argh',
    '(grunt)',
    '(grunts)',
    'grr',
    'grrrr',
    'boo!',
    'ha ha ha',
    ':3',
    ':/',
    ':)',
    ':0',
    'i\'m too old for this crap',
    'where is my axe',
    'where is my wife',
    'has anybody seen my scary robe and hood',
    'hey can you watch my kid for me for a sec <:greed_babane:1463223765453508679>',
    'hey'

    ]

hit_responses = [
    'oof',
    'ouch',
    'aj',
    'ourgh',
    'ouh',
    'ouuuhh',
    'arrrgghh',
    'ough',
    'aurh',
    'oaruh',
    'uoh',
    'ahhh',
    'ahhh...'
]

random_channels = [
    1339606740626444330, 
    1339607410851053599,
    1339628444757262461,
    1340384199340986388,
    1417802113022693397,

    1463315121555243009,
    1463315121555243009,
    1463315121555243009,
    1463315121555243009,
    1463315121555243009,
    ]

botNotificationChannel = 1463315121555243009

# ---------- Events ----------
@bot.event
async def on_ready():
    if not hasattr(bot, "tasks_started"):
        bot.tasks_started = True
        logger.info(f"Bot ready: {bot.user}")
        await load_loot()
        bot.loop.create_task(background_loop())
        bot.loop.create_task(daily_respawn())

@bot.event
async def on_raw_reaction_add(payload):
    if payload.message_id == roleReactMsgId[0] or payload.message_id == roleReactMsgId[1]:
        member = payload.member
        guild = member.guild

        emoji = payload.emoji.id
        if emoji == 1463197948992032966:
            role = discord.utils.get(guild.roles, name='Community Events')
        elif emoji == 1463199521663356928:
            role = discord.utils.get(guild.roles, name='Public Playtesting')
        elif emoji == 1463198073445552395:
            role = discord.utils.get(guild.roles, name='Executioner Hunter')
        elif emoji == 1463223765453508679:
            role = discord.utils.get(guild.roles, name='Game Developer')
        elif emoji == 1463221838674002104:
            role = discord.utils.get(guild.roles, name='Player')
        elif emoji == 1463242519050588160:
            role = discord.utils.get(guild.roles, name='Public Playtesting')
        else: 
            print(f"test, no role found - {emoji}")
            return

        await member.add_roles(role)
    

@bot.event
async def on_raw_reaction_remove(payload):
    if payload.message_id == roleReactMsgId[0] or payload.message_id == roleReactMsgId[1]:
        guild = await(bot.fetch_guild(payload.guild_id))
        
        emoji = payload.emoji.id
        if emoji == 1463197948992032966:
            role = discord.utils.get(guild.roles, name='Community Events')
        elif emoji == 1463199521663356928:
            role = discord.utils.get(guild.roles, name='Public Playtesting')
        elif emoji == 1463198073445552395:
            role = discord.utils.get(guild.roles, name='Executioner Hunter')
        elif emoji == 1463223765453508679:
            role = discord.utils.get(guild.roles, name='Game Developer')
        elif emoji == 1463221838674002104:
            role = discord.utils.get(guild.roles, name='Player')
        elif emoji == 1463242519050588160:
            role = discord.utils.get(guild.roles, name='Public Playtesting')
        else: 
            print(f"test, no role found - {emoji}")
            return

        member = await(guild.fetch_member(payload.user_id))
        if member is not None:
            await member.remove_roles(role)
        else:
            print("Member not found")


@bot.event
async def on_message(message):

    # Gold response throttled per-channel
    now = asyncio.get_event_loop().time()
    last_time = session.last_gold_response.get(message.channel.id, 0)
    if "gold" in message.content.lower() and "!checkgold" not in message.content.lower():
        if now - last_time >= 1:  # 5s throttle per channel
            session.last_gold_response[message.channel.id] = now
            if(session.hp > 0) : asyncio.create_task(handle_gold_response(message))

    await bot.process_commands(message)

async def handle_gold_response(message):
    try:
        if message.author == bot.user: 
            return
        
        await asyncio.sleep(2,5)
        async with message.channel.typing():
            await asyncio.sleep(random.randint(2,5))
            await message.channel.send(random.choice(gold_responses))
            session.current_channel = message.channel
    except Exception:
        logger.exception("Error handling gold response")
    
# ---------- Background loop ----------
async def background_loop():
    while True:
        try:
            if session.hp > 0:
                now = datetime.datetime.now()

                delay_seconds = random.randint(session.minTime, session.maxTime)
                nextTime = now + datetime.timedelta(seconds=delay_seconds)

                session.nextRandMsg = nextTime  # ✅ this is saved correctly

                await asyncio.sleep(delay_seconds)
                channel_id = random.choice(random_channels)
                channel = bot.get_channel(channel_id)

                if not isinstance(channel, discord.TextChannel):
                    logger.warning(f"Channel {channel_id} invalid, skipping")
                    continue

                if session.hp > 0: #just to be sure, sometimes the wait already is going before it dies
                    session.current_channel = channel
                    await channel.send(random.choice(random_messages))
            else:
                # If HP <= 0, slow down loop to avoid CPU spin
                await asyncio.sleep(120) #FIX sätt till typ 120
        except Exception:
            logger.exception("Error in background loop")
            await asyncio.sleep(5)  # slow down after exception

async def daily_respawn():
    role = None
    channel = bot.get_channel(botNotificationChannel)
    while True:
        if(session.hp < 1):
            now = datetime.datetime.now()
            next_respawn = datetime.datetime.combine(now.date(), datetime.time(hour=6, minute=0)) + datetime.timedelta(days=random.randrange(1, session.respawnDaysMax))
            wait_seconds = (next_respawn - now).total_seconds()
            await asyncio.sleep(wait_seconds-600)
            if channel:
                if role is None:
                    guild = channel.guild
                    role = guild.get_role(1463297281322127587)

                if role:
                    await channel.send(f"{role.mention} The Executioner is about to respawn soon...")

            #mention role here, roleid: 1463297281322127587
            await asyncio.sleep(random.randrange(60, 600))
            session.hp = random.randrange(1, session.max_hp)
        else:
            await asyncio.sleep(600)

# ---------- Commands ----------
@bot.command()
async def hit(ctx):
    if session.hp <= 0:
        #await ctx.reply("Nothing happens, the bot is dead.")
        return

    if ctx.channel != session.current_channel:
        #await ctx.reply("You can't hit here!")
        return

    session.hp = max(0, session.hp - 1)
    session.current_channel = ctx.channel  # ensure it's consistent

    try:
        if session.hp > 0:
            if random.randint(1,7) != 1:
                await ctx.reply(random.choice(hit_responses))
            else:
                await ctx.reply("*dodges*")
        else:
            await ctx.reply("*dies* <:greed_dead:1463198222091682018>")
            await asyncio.sleep(0.5)
            msg = await ctx.send("*drops loot <:greed_gold:1463188620205756508>*")
            session.loot_id = msg.id
    except Exception:
        logger.exception("Error in hit command")

@bot.command()
async def loot(ctx):
    if session.loot_id is None:
        await ctx.send("No loot available.")
        return

    try:
        msg = await ctx.channel.fetch_message(session.loot_id)
        user_id = ctx.author.id
        session.user_loot[user_id] = session.user_loot.get(user_id,0) + 1
        await ctx.send(f"{ctx.author.mention} looted 1 gold!")
        await msg.delete()
        session.loot_id = None
        await save_loot()
    except discord.NotFound:
        await ctx.send("Loot message not found.")
    except Exception:
        logger.exception("Error in loot command")

@bot.command()
async def checkgold(ctx):
    amount = session.user_loot.get(ctx.author.id,0)
    await ctx.reply(f"{ctx.author.mention} You have {amount} gold <:greed_gold:1463188620205756508>")

@bot.command()
@commands.is_owner()
async def spawn(ctx):
    session.hp = random.randrange(1, session.max_hp)
    await ctx.send("Respawned <:greed_executioner:1463198073445552395>")

@bot.command()
@commands.is_owner()
async def status(ctx):
    channel_name = session.current_channel.name if isinstance(session.current_channel, discord.TextChannel) else "None"
    await ctx.send(f"Status: HP={session.hp}, current channel={channel_name}, next random message time: {session.nextRandMsg}")

@bot.command()
@commands.is_owner()
async def shutdown(ctx):
    await ctx.send("Shutting down bot… 👋")
    await bot.close()

# ---------- Run ----------
#webserver.keep_alive()
#bot.run(TOKEN)
if __name__ == "__main__":
    bot.run(os.getenv(TOKEN))

# import discord
# from discord.ext import commands
# import asyncio
# import random
# import logging
# import os
# from dotenv import load_dotenv

# load_dotenv()
# TOKEN = os.getenv("DISCORD_TOKEN")

# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger("bot")

# intents = discord.Intents.default()
# intents.message_content = True
# intents.members = True

# bot = commands.Bot(command_prefix="!", intents=intents)

# # ---------- Session state ----------
# class SessionState:
#     def __init__(self):
#         self.hp = 1
#         self.max_hp = 2
#         self.loot_id = None
#         self.current_channel = None
#         self.user_loot = {}
#         self.last_gold_response = {}  # per-channel throttle

# session = SessionState()
# LOOT_FILE = "membersData.txt"

# # ---------- Helper functions ----------
# async def load_loot():
#     def _load():
#         loot = {}
#         try:
#             with open(LOOT_FILE, "r") as f:
#                 for line in f:
#                     user_id, amount = line.split()
#                     loot[int(user_id)] = int(amount)
#         except FileNotFoundError:
#             pass
#         return loot
#     session.user_loot = await asyncio.to_thread(_load)

# async def save_loot():
#     def _save():
#         with open(LOOT_FILE, "w") as f:
#             for user_id, amount in session.user_loot.items():
#                 f.write(f"{user_id} {amount}\n")
#     await asyncio.to_thread(_save)

# # ---------- Messages ----------
# gold_responses = [
#     'gold you say', 'did I hear gold', 'gold mentioned', 'gold?',
#     'yooo', 'what was that', 'can you repeat that', 'hey', 'hiii', ':eyes:'
# ]
# random_messages = ['(walks past)', '(coughs)', '(cough cough)']
# hit_responses = [
#     'oof','ouch','aj','ourgh','ouh','ouuuhh','arrrgghh','ough','aurh','oaruh','uoh','ahhh','ahhh...'
# ]
# random_channels = [1462817378747547752, 1463159978960486515]

# # ---------- Events ----------
# @bot.event
# async def on_ready():
#     logger.info(f"Bot ready: {bot.user}")
#     await load_loot()
#     bot.loop.create_task(background_loop())

# @bot.event
# async def on_message(message):
#     if message.author.bot or session.hp < 1:
#         return
    
#     # Gold response throttled per-channel
#     now = asyncio.get_event_loop().time()
#     last_time = session.last_gold_response.get(message.channel.id, 0)
#     if "gold" in message.content.lower() and "!checkgold" not in message.content.lower():
#         if now - last_time >= 5:  # 5 seconds throttle per channel
#             session.last_gold_response[message.channel.id] = now
#             asyncio.create_task(handle_gold_response(message))
    
#     await bot.process_commands(message)

# async def handle_gold_response(message):
#     try:
#         async with message.channel.typing():
#             await asyncio.sleep(random.randint(2,5))
#             await message.channel.send(random.choice(gold_responses))
#             session.current_channel = message.channel
#     except Exception:
#         logger.exception("Error handling gold response")

# # ---------- Background loop ----------
# async def background_loop():
#     while True:
#         try:
#             if session.hp > 0:
#                 await asyncio.sleep(random.randint(10,30))
#                 channel_id = random.choice(random_channels)
#                 channel = bot.get_channel(channel_id)
#                 if channel is None:
#                     logger.warning(f"Channel {channel_id} not found, skipping")
#                     continue
#                 session.current_channel = channel
#                 await channel.send(random.choice(random_messages))
#         except Exception:
#             logger.exception("Error in background loop")
#             await asyncio.sleep(5)  # prevent tight loop on error

# # ---------- Commands ----------
# @bot.command()
# async def hit(ctx):
#     if session.hp < 1 or ctx.channel != session.current_channel:
#         return
    
#     session.hp -= 1
#     try:
#         if session.hp > 0:
#             if random.randint(1,7) != 1:
#                 await ctx.reply(random.choice(hit_responses))
#             else:
#                 await ctx.reply("*dodges*")
#         else:
#             await ctx.reply("*dies*")
#             await asyncio.sleep(0.5)
#             msg = await ctx.send("*drops loot :coin:*")
#             session.loot_id = msg.id
#     except Exception:
#         logger.exception("Error in hit command")

# @bot.command()
# async def loot(ctx):
#     if session.loot_id is None:
#         await ctx.send("No loot available")
#         return
#     try:
#         msg = await ctx.channel.fetch_message(session.loot_id)
#         user_id = ctx.author.id
#         session.user_loot[user_id] = session.user_loot.get(user_id,0) + 1
#         await ctx.send(f"{ctx.author.mention} looted 1 gold!")
#         await msg.delete()
#         session.loot_id = None
#         await save_loot()
#     except discord.NotFound:
#         await ctx.send("Loot message not found")
#     except Exception:
#         logger.exception("Error in loot command")

# @bot.command()
# async def checkgold(ctx):
#     amount = session.user_loot.get(ctx.author.id,0)
#     await ctx.reply(f"{ctx.author.mention} You have {amount} gold")

# @bot.command()
# @commands.is_owner()
# async def spawn(ctx):
#     session.hp = session.max_hp
#     await ctx.send("Respawned")

# @bot.command()
# @commands.is_owner()
# async def status(ctx):
#     channel_name = session.current_channel.name if isinstance(session.current_channel, discord.TextChannel) else "None"
#     await ctx.send(f"Status: HP={session.hp}, current channel={channel_name}")

# # ---------- Run ----------
# bot.run(TOKEN)



# import discord
# from discord.ext import commands
# import logging
# from dotenv import load_dotenv
# import os
# import random
# import asyncio
# import traceback

# load_dotenv()
# token = os.getenv('DISCORD_TOKEN')

# handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
# intents = discord.Intents.default()
# intents.message_content = True
# intents.members = True

# GUILD_ID = discord.Object(id="683435204647452767")
# #guild = 683435204647452767
# bot = commands.Bot(command_prefix='!', intents=intents)
# #client = discord.Client()

# bot.session_state = {
#     "hp": 1,
#     "maxHp": 2,
#     "lootId": 123,
#     "currentChannel": 123
# }

# randomnessChannels = [
#     1462817378747547752, 
#     1463159978960486515
#     ]

# goldResponses = [
#     'gold you say', 
#     'did I hear gold', 
#     'gold mentioned', 
#     'gold?', 
#     'yooo', 
#     'what was that',
#     'can you repeat that',
#     'hey',
#     'hiii', 
#     ':eyes:'
#     ]

# randomMessages = [
#     '(walks past)',
#     '(coughs)',
#     '(cough cough)'
# ]

# hitResponses = [
#     'oof',
#     'ouch',
#     'aj',
#     'ourgh',
#     'ouh',
#     'ouuuhh',
#     'arrrgghh',
#     'ough',
#     'aurh',
#     'oaruh',
#     'uoh',
#     'ahhh',
#     'ahhh...'
# ]


# moneyResponses = ['tell me more about this money']


# @bot.event
# async def on_ready():
#     print(f"Ready to go {bot.user.name}")
#     #bot.loop.create_task(background_loop()) FIX
    
    

# @bot.event
# async def on_member_join(member):
#     await member.send(f"Welcome to the server, {member.name}!")

# @bot.event
# async def on_message(message):
#     if message.author == bot.user or bot.session_state["hp"] < 1:
#         return
        
#     if "gold" in message.content.lower() and not "!checkgold" in message.content.lower() and message.author != bot.user:    
#         await bot.loop.create_task(respondGold())
        

#     await bot.process_commands(message) 


# roleReactMsgId = 1463127449293422615

# @bot.event
# async def on_raw_reaction_add(payload):
#     if roleReactMsgId == payload.message_id:
#         member = payload.member
#         guild = member.guild

#         emoji = payload.emoji.name
#         if emoji == '🔥':
#             role = discord.utils.get(guild.roles, name='testRole')

#         await member.add_roles(role)
    

# @bot.event
# async def on_raw_reaction_remove(payload):
#     if roleReactMsgId == payload.message_id:
#         guild = await(bot.fetch_guild(payload.guild_id))
#         emoji = payload.emoji.name
        
#         if emoji == '🔥':
#             role = discord.utils.get(guild.roles, name='testRole')

#         member = await(guild.fetch_member(payload.user_id))
#         if member is not None:
#             await member.remove_roles(role)
#         else:
#             print("Member not found")

# async def background_loop():

#     try:
#         while True:
#             if bot.session_state["hp"] > 0:

#                 channel = bot.get_channel(response)
#                 if channel is None:
#                     print(f"Channel {response} not found")
#                     continue

#                 await asyncio.sleep(random.randrange(10,30))
#                 response = random.choice(randomnessChannels)
                
#                 bot.session_state["currentChannel"] = channel
                
#                 strin = bot.session_state["currentChannel"].name
#                 print(f"{response} in {strin}")

#                 await channel.send(random.choice(randomMessages))

#     except Exception:
#         import traceback
#         traceback.print_exc()

    

# @bot.command()
# async def hit(ctx):

#     if bot.session_state["hp"] < 1 or ctx.channel != bot.session_state["currentChannel"]: 
#         return
    
#     bot.session_state["hp"] -= 1

#     if bot.session_state["hp"] > 0:
#         if random.randrange(1, 8) != 1:
#             await ctx.reply(random.choice(hitResponses))
#         else:
#             await ctx.reply("*dodges*")
#     else:
#         await ctx.reply("*dies*")
#         try:
#             await asyncio.sleep(0.5)
            
#             msg = await ctx.send("*drops loot :coin:")

#             bot.session_state["lootId"] = msg.id
#         except Exception:
#             traceback.print_exc()
        

# @bot.command()
# async def loot(ctx):
#     if bot.session_state["lootId"] != 123:
#         try:
#             loot = await load_loot()
#             user_id = ctx.author.id

#             loot[user_id] = loot.get(user_id, 0) + 1
#             await save_loot(loot)

#             msg = await ctx.channel.fetch_message(bot.session_state["lootId"])

#             await ctx.send(f"{ctx.author.mention} looted 1 gold")
#             await msg.delete()

#             bot.session_state["lootId"] = 123

#         except discord.NotFound:
#             await ctx.send("Message not found.")
    
# @bot.command()
# async def checkgold(ctx):
#     loot = await load_loot()
#     amount = loot.get(ctx.author.id, 0)

#     await ctx.reply(f"{ctx.author.mention} You have {amount} gold")

# @bot.command()
# @commands.is_owner()
# async def spawn(ctx):
#     bot.session_state["hp"] = bot.session_state["maxHp"]
#     await ctx.send("Respawned")


# @bot.command()
# @commands.is_owner()
# async def status(ctx):
#     strin = bot.session_state["hp"]
#     strin2 = bot.session_state["currentChannel"].name
#     await ctx.send(f"status: hp: {strin}, current channel: {strin2}")

# LOOT_FILE = "membersData.txt"

# async def respondGold(message):
#     try:
#         await asyncio.sleep(random.randrange(2,5))
#         async with message.channel.typing():
#             await asyncio.sleep(random.randrange(2,5))
#             await message.channel.send(f"{random.choice(goldResponses)}") 
            
#             bot.session_state["currentChannel"] = message.channel
#     except Exception:
#         traceback.print_exc()
#     return

# async def load_loot():
#     loot = {}
#     try:
#         with open(LOOT_FILE, "r") as f:
#             for line in f:
#                 user_id, amount = line.split()
#                 loot[int(user_id)] = int(amount)
#     except FileNotFoundError:
#         pass
#     return loot


# async def save_loot(loot: dict):
#     with open(LOOT_FILE, "w") as f:
#         for user_id, amount in loot.items():
#             f.write(f"{user_id} {amount}\n")



# bot.run(token, log_handler=handler, log_level=logging.DEBUG)