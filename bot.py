# Прототип интеграции ИИ нейросетей (Groq API) в Discord бота
import discord
from discord.ext import commands
from discord import app_commands
import aiohttp
import io
import os

DISCORD_TOKEN = "YOUR_DISCORD_TOKEN_HERE"
GROQ_API_KEY = "YOUR_GROQ_API_KEY_HERE"

SYSTEM_PROMPT = """
You are a helpful and intelligent AI assistant working in a Discord server.
Provide clear, concise, and friendly answers to the users.
"""

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print("======================")
    print(f"Logged in as {bot.user.name} ({bot.user.id})")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"Failed to sync commands: {e}")
    print("======================")

@bot.tree.command(name="ask", description="Задать вопрос ИИ нейросети")
@app_commands.describe(question="Ваш вопрос")
async def ask(interaction: discord.Interaction, question: str):
    await interaction.response.defer(thinking=True)

    try:
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }

        data = {
            "model": "openai/gpt-oss-20b",
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": question}
            ],
            "temperature": 0.7,
            "max_tokens": 1024
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                response.raise_for_status()
                response_data = await response.json()
                reply = response_data["choices"][0]["message"]["content"]

        if len(reply) <= 2000:
            await interaction.followup.send(reply)
        else:
            file = discord.File(
                io.BytesIO(reply.encode("utf-8")),
                filename="response.txt"
            )
            await interaction.followup.send(
                "Ответ слишком большой, отправляю файлом:",
                file=file
            )

    except aiohttp.ClientError as e:
        await interaction.followup.send(f"❌ API Error: {str(e)}")
    except Exception as e:
        await interaction.followup.send(f"❌ Ошибка: {str(e)}")

if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)


