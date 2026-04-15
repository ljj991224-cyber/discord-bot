import discord
from discord.ext import commands
import json
import os

# ===== TOKEN (Render에서 주입) =====
TOKEN = os.getenv("TOKEN")

# ===== Intents =====
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

DATA_FILE = "scores.json"

# ===== 데이터 =====
def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

SCORE_TABLE = {
    1: 25, 2: 18, 3: 12, 4: 6,
    5: -6, 6: -12, 7: -18, 8: -25
}

# ===== 등록 =====
@bot.command()
async def 등록(ctx):
    data = load_data()
    uid = str(ctx.author.id)

    if uid not in data:
        data[uid] = {"score": 0, "streak": 0, "team": None}
        save_data(data)

    await ctx.send("등록 완료")

# ===== 팀 설정 =====
@bot.command()
async def 팀(ctx, user: discord.Member, team: str):
    data = load_data()
    uid = str(user.id)

    if uid not in data:
        await ctx.send("먼저 등록해야 함")
        return

    if team not in ["A", "B"]:
        await ctx.send("A 또는 B만 가능")
        return

    data[uid]["team"] = team
    save_data(data)

    await ctx.send(f"{user.name} → {team}팀")

# ===== 결과 =====
@bot.command()
async def 결과(ctx, user: discord.Member, place: int):
    data = load_data()
    uid = str(user.id)

    if uid not in data:
        await ctx.send("먼저 등록 필요")
        return

    if place not in SCORE_TABLE:
        await ctx.send("1~8등만 가능")
        return

    base = SCORE_TABLE[place]
    streak = data[uid]["streak"]

    if place <= 4:
        streak = streak + 1 if streak >= 0 else 1
    else:
        streak = streak - 1 if streak <= 0 else -1

    bonus = 0

    if streak >= 2:
        if streak == 2: bonus = 3
        elif streak == 3: bonus = 5
        elif streak == 4: bonus = 7
        else: bonus = 10

    if streak <= -3:
        if streak == -3: bonus = -3
        elif streak == -4: bonus = -5
        else: bonus = -8

    total = base + bonus

    data[uid]["score"] += total
    data[uid]["streak"] = streak

    save_data(data)

    await ctx.send(f"{user.name} {place}등 → {total}점 (총 {data[uid]['score']})")

# ===== 팀 점수 =====
@bot.command()
async def 팀점수(ctx):
    data = load_data()

    team_scores = {"A": 0, "B": 0}

    for u in data.values():
        if u["team"] in team_scores:
            team_scores[u["team"]] += u["score"]

    await ctx.send(f"A팀: {team_scores['A']} / B팀: {team_scores['B']}")

# ===== 실행 =====
bot.run(TOKEN)
