import os
import discord
from discord import app_commands
from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

ai_client = AsyncOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

MODEL = "deepseek/deepseek-v3.2"

intents = discord.Intents.default()
intents.members = True
intents.message_content = True


class DiscordBot(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()


client = DiscordBot()


# ── Shared helpers ─────────────────────────────────────────────────────────────

async def ask_ai(prompt: str, system: str, max_tokens: int = 120) -> str:
    """Call DeepSeek V3.2 via OpenRouter and return the text response."""
    response = await ai_client.chat.completions.create(
        model=MODEL,
        max_tokens=max_tokens,
        messages=[
            {"role": "system", "content": system},
            {"role": "user",   "content": prompt},
        ],
    )
    return response.choices[0].message.content.strip()


async def fetch_channel_context(
    channel: discord.TextChannel,
    subject: discord.Member,
    limit: int = 35,
    subject_label: str = "THE ACCUSED",
) -> list[str]:
    """Pull recent non-bot messages and tag the subject with a label."""
    lines: list[str] = []
    async for msg in channel.history(limit=limit):
        if msg.content.strip() and not msg.author.bot:
            if msg.author.id == subject.id:
                label = f"[{msg.author.display_name} ({subject_label})]"
            else:
                label = f"[{msg.author.display_name}]"
            lines.append(f"{label}: {msg.content.strip()}")
    lines.reverse()
    return lines


def extract_tagged_line(raw: str, tag: str) -> str:
    """Return the first line containing `tag` (case-insensitive), else line 1."""
    for line in raw.splitlines():
        if tag.upper() in line.upper():
            return line.strip()
    return raw.splitlines()[0].strip()


def truncate(text: str, limit: int = 250) -> str:
    return text[:limit - 3] + "..." if len(text) > limit else text


# ── /obituary ──────────────────────────────────────────────────────────────────

@client.tree.command(name="obituary", description="Write a dramatic fake obituary for a user")
@app_commands.describe(user="The user to eulogize")
async def obituary(interaction: discord.Interaction, user: discord.Member):
    await interaction.response.defer()

    if interaction.guild is None:
        await interaction.followup.send("This command can only be used in a server.")
        return

    if not isinstance(interaction.channel, discord.TextChannel):
        await interaction.followup.send("This command can only be used in a text channel.")
        return

    context_lines = await fetch_channel_context(
        interaction.channel, user, limit=35, subject_label="THE DECEASED"
    )

    if context_lines:
        context_block = "\n".join(context_lines)
        context_note = (
            f"Here is the recent conversation in this channel "
            f"(the deceased is labelled THE DECEASED):\n{context_block}\n\n"
        )
    else:
        context_note = "No messages could be collected — invent something suitably absurd.\n\n"

    prompt = (
        f"You are a dramatic obituary writer. {user.display_name} has just died.\n\n"
        f"{context_note}"
        f"Based on the conversation (especially what THE DECEASED said), invent a completely absurd, "
        f"made-up cause of death that connects to the chat in a ridiculous, creative way.\n\n"
        f"Respond with ONLY ONE sentence, formatted EXACTLY like this:\n"
        f"**OBITUARY:** [one sentence describing the ridiculous death]\n\n"
        f"Be funny and absurd. No sensitive topics."
    )

    system = (
        "You write comedy obituaries for a Discord bot. "
        "Output ONLY a single bolded obituary line — nothing else. "
        "One sentence. No extra commentary."
    )

    try:
        raw = await ask_ai(prompt, system, max_tokens=100)
    except Exception as e:
        await interaction.followup.send(
            f"The Grim Reaper's Wi-Fi is down. Try again later. (`{e}`)"
        )
        return

    text = truncate(extract_tagged_line(raw, "OBITUARY"))

    embed = discord.Embed(
        title=f"🪦 In Loving (and Chaotic) Memory of {user.display_name}",
        description=text,
        color=discord.Color.dark_grey(),
    )
    embed.set_thumbnail(url=user.display_avatar.url)
    footer = (
        f"Evidence gathered from the last {len(context_lines)} messages in this channel."
        if context_lines else "No messages found — the coroner improvised."
    )
    embed.set_footer(text=footer)

    await interaction.followup.send(embed=embed)


# ── /trial ─────────────────────────────────────────────────────────────────────

@client.tree.command(name="trial", description="Put a user on trial for an absurd crime")
@app_commands.describe(user="The user to put on trial")
async def trial(interaction: discord.Interaction, user: discord.Member):
    await interaction.response.defer()

    if interaction.guild is None:
        await interaction.followup.send("This command can only be used in a server.")
        return

    if not isinstance(interaction.channel, discord.TextChannel):
        await interaction.followup.send("This command can only be used in a text channel.")
        return

    context_lines = await fetch_channel_context(
        interaction.channel, user, limit=35, subject_label="THE ACCUSED"
    )

    if context_lines:
        evidence_block = "\n".join(context_lines)
        evidence_note = (
            f"Here is the recent conversation in this channel "
            f"(the accused is labelled THE ACCUSED):\n{evidence_block}\n\n"
        )
    else:
        evidence_note = "No messages could be collected — invent something suitably absurd.\n\n"

    prompt = (
        f"You are a dramatic courtroom narrator. {user.display_name} is being put on trial.\n\n"
        f"{evidence_note}"
        f"Based on the conversation (especially what THE ACCUSED said), invent a completely made-up, "
        f"utterly absurd crime that connects to the chat in a ridiculous, creative way.\n\n"
        f"Respond with ONLY ONE sentence, formatted EXACTLY like this:\n"
        f"**THE CRIME:** [one sentence describing the ridiculous charge]\n\n"
        f"Be funny and absurd. No real crimes or sensitive topics."
    )

    system = (
        "You are a courtroom narrator for a comedy Discord bot. "
        "Output ONLY a single bolded crime charge — nothing else. "
        "One sentence. No verdict, jury, or extra content."
    )

    try:
        raw = await ask_ai(prompt, system, max_tokens=100)
    except Exception as e:
        await interaction.followup.send(
            f"The court is in recess due to a technical malfunction. (`{e}`)"
        )
        return

    crime = truncate(extract_tagged_line(raw, "THE CRIME"))

    embed = discord.Embed(
        title=f"⚖️ THE PEOPLE vs. {user.display_name.upper()}",
        description=crime,
        color=discord.Color.gold(),
    )
    embed.set_thumbnail(url=user.display_avatar.url)
    footer = (
        f"Evidence gathered from the last {len(context_lines)} messages in this channel."
        if context_lines else "No messages found — the prosecution improvised."
    )
    embed.set_footer(text=footer)

    await interaction.followup.send(embed=embed)


# ── Startup ────────────────────────────────────────────────────────────────────

@client.event
async def on_ready():
    print(f"Logged in as {client.user} (ID: {client.user.id})")
    print(f"Model: {MODEL}")
    print("Slash commands synced. Bot is ready!")


if __name__ == "__main__":
    if not DISCORD_TOKEN:
        raise ValueError("DISCORD_TOKEN is not set in .env")
    if not OPENROUTER_API_KEY:
        raise ValueError("OPENROUTER_API_KEY is not set in .env")
    client.run(DISCORD_TOKEN)
