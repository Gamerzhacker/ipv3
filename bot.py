import discord
from discord.ext import commands
import random
import string
import subprocess
import json

TOKEN = 'BOT_TOKEN'
ADMIN_ID =  1258646055860568094 # Replace with your Discord user ID

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='/', intents=intents)

vps_db = {}

def generate_random_ip():
    return f"192.168.{random.randint(0, 255)}.{random.randint(1, 254)}"

def generate_user_pass():
    user = ''.join(random.choices(string.ascii_lowercase, k=6))
    pwd = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
    return user, pwd

@bot.event
async def on_ready():
    print(f'Bot online: {bot.user}')

@bot.command()
async def ping(ctx):
    latency = round(bot.latency * 1000)
    await ctx.send(f'Pong! `{latency}ms`')

@bot.command()
async def deployipv4(ctx, userid: str):
    ip = generate_random_ip()
    user, password = generate_user_pass()
    container_name = f"vps_{userid}_{random.randint(1000,9999)}"
    
    subprocess.run([
        "docker", "run", "-d",
        "--name", container_name,
        "-p", f"{random.choice([22, 80, 443, 8080, 2022, 5080, 3001])}:22",
        "ubuntu_vps"
    ])

    entry = {'ip': ip, 'user': user, 'pass': password, 'container': container_name}
    vps_db.setdefault(userid, []).append(entry)
    await ctx.send(f"VPS deployed for `{userid}`:\n`IP: {ip}`, `User: {user}`, `Pass: {password}`")

@bot.command()
async def list(ctx):
    userid = str(ctx.author.id)
    vps_list = vps_db.get(userid, [])
    if not vps_list:
        return await ctx.send("You have no VPS.")
    
    msg = '\n'.join([f"- IP: {v['ip']}, User: {v['user']}, Pass: {v['pass']}" for v in vps_list])
    await ctx.send(f"**Your VPS List:**\n{msg}")

@bot.command()
async def ipv4(ctx, userid: str, ip: str, user: str, password: str):
    vps_db.setdefault(userid, []).append({'ip': ip, 'user': user, 'pass': password, 'container': 'manual'})
    await ctx.send(f"Manually added VPS for `{userid}`: `{ip}`, `{user}`, `{password}`")

@bot.command()
async def nodeadmin(ctx):
    if ctx.author.id != ADMIN_ID:
        return await ctx.send("Unauthorized.")
    await ctx.send(f"**All VPS Data:**\n```json\n{json.dumps(vps_db, indent=2)}```")

@bot.command()
async def delvps(ctx, userid: str):
    if ctx.author.id != ADMIN_ID:
        return await ctx.send("Unauthorized.")
    
    for vps in vps_db.get(userid, []):
        if vps["container"] != 'manual':
            subprocess.run(["docker", "rm", "-f", vps["container"]])
    vps_db.pop(userid, None)
    await ctx.send(f"Deleted VPS for `{userid}`")

@bot.command()
async def removeall(ctx):
    if ctx.author.id != ADMIN_ID:
        return await ctx.send("Unauthorized.")
    
    for user, vps_list in vps_db.items():
        for vps in vps_list:
            if vps["container"] != 'manual':
                subprocess.run(["docker", "rm", "-f", vps["container"]])
    vps_db.clear()
    await ctx.send("All VPS removed for all users.")

@bot.command()
async def start(ctx, arg=None):
    if arg != "list":
        return await ctx.send("Usage: `/start list`")
    
    userid = str(ctx.author.id)
    for vps in vps_db.get(userid, []):
        if vps["container"] != 'manual':
            subprocess.run(["docker", "start", vps["container"]])
    await ctx.send("Started all your VPS containers.")

@bot.command()
async def stop(ctx, arg=None):
    if arg != "list":
        return await ctx.send("Usage: `/stop list`")
    
    userid = str(ctx.author.id)
    for vps in vps_db.get(userid, []):
        if vps["container"] != 'manual':
            subprocess.run(["docker", "stop", vps["container"]])
    await ctx.send("Stopped all your VPS containers.")

@bot.command()
async def restart(ctx, arg=None):
    if arg != "list":
        return await ctx.send("Usage: `/restart list`")
    
    userid = str(ctx.author.id)
    for vps in vps_db.get(userid, []):
        if vps["container"] != 'manual':
            subprocess.run(["docker", "restart", vps["container"]])
    await ctx.send("Restarted all your VPS containers.")

# run the bot
bot.run(TOKEN)
