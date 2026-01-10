import discord
from discord.ext import commands
import sqlite3
from config import token

# 1. Intents və Bot obyektini yaradın
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# =========================
# Select Menu və Modal Sinifləri
# =========================
class SoruSelect(discord.ui.Select):
    def __init__(self, departman_id: int):
        self.departman_id = departman_id

        conn = sqlite3.connect("qa.db")
        cursor = conn.cursor()
        cursor.execute(
            "SELECT question FROM qa WHERE departman_id=?",
            (departman_id,)
        )
        questions = cursor.fetchall()
        conn.close()

        if not questions:
            options = [
                discord.SelectOption(
                    label="Bu departmanda sual yoxdur",
                    value="no_data"
                )
            ]
        else:
            options = [
                discord.SelectOption(label=q[0], value=q[0])
                for q in questions[:25]
            ]

        super().__init__(
            placeholder="▶ Soru seç",
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        question = self.values[0]

        if question == "no_data":
            await interaction.response.send_message(
                "Bu departmanda sual yoxdur.",
                ephemeral=True
            )
            return

        conn = sqlite3.connect("qa.db")
        cursor = conn.cursor()
        cursor.execute(
            "SELECT answer FROM qa WHERE question=?",
            (question,)
        )
        answer = cursor.fetchone()
        conn.close()

        await interaction.response.send_message(
            f"**Soru:** {question}\n**Cevap:** {answer[0]}",
            ephemeral=True
        )

class DepartmanSelect(discord.ui.Select):
    def __init__(self):
        conn = sqlite3.connect("qa.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, departman_adi FROM departman")
        data = cursor.fetchall()
        conn.close()

        options = [
            discord.SelectOption(
                label=adi,
                value=str(id)
            )
            for id, adi in data
        ]

        super().__init__(
            placeholder="▶ Departman seç",
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        departman_id = int(self.values[0])

        # Yeni view yaradılır
        view = discord.ui.View()
        view.add_item(DepartmanSelect())
        view.add_item(SoruSelect(departman_id))

        await interaction.response.edit_message(
            content="Departman seçildi. İndi sual seç:",
            view=view
        )

class CategoryView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(DepartmanSelect())

class CtgModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="Soru Sistemi")

    name = discord.ui.TextInput(label="İsmini yaz", placeholder="Mes: Ali")

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"Selam **{self.name.value}** 👋\nSoru seç:", view=CategoryView(), ephemeral=True)

class OpenModalView(discord.ui.View):
    @discord.ui.button(label="▶ Devam et", style=discord.ButtonStyle.primary)
    async def open_modal(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(CtgModal())

# =========================
# Slash Command və Sync (Sinxronizasiya)
# =========================

@bot.event
async def on_ready():
    # Bot açılan kimi slash commandları qlobal olaraq sinxronizasiya edir
    try:
        synced = await bot.tree.sync()
        print(f"{len(synced)}")
    except Exception as e:
        print(f"Sinxronizasiya xətası: {e}")
    
    print(f"Bot aktifdir: {bot.user}")

# /ctg komandası
@bot.tree.command(name="ctg", description="Soru sistemini açar")
async def ctg(interaction: discord.Interaction):
    await interaction.response.send_message("Soru sormak için düğmeye bas:", view=OpenModalView())

@bot.tree.command(name="info", description="info")
async def info(interaction: discord.Interaction):
    await interaction.response.send_message(
        """
ℹ️ **Bilgi Sistemi**

Bu bot, departmanlara görə hazırlanmış soru–cevap sistemidir.

📂 **Nasıl Kullanılır?**
1️⃣ /ctg yaz  
2️⃣ Departman seç  
3️⃣ Sorunu seç ve cavabın karşına çıksın

🛠️ **Mevcut Departmanlar**
• Programcılar  
• Personel  

Cevabını bulamazsan yetkiliyle iletişime geç.
        """
    )


bot.run(token)
