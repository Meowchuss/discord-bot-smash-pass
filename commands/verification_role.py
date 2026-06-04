import discord
from discord.ext import commands
from discord import app_commands
from discord.app_commands import AppCommandError
import io

class PaginationView(discord.ui.View):
    def __init__(self, pages):
        super().__init__(timeout=120)
        self.pages = pages
        self.index = 0

    def get_embed(self):
        embed = discord.Embed(
            title="Vérification des rôles",
            description=self.pages[self.index],
            color=discord.Color.purple()
        )
        embed.set_footer(text=f"Page {self.index + 1}/{len(self.pages)}")
        return embed

    @discord.ui.button(label="◀", style=discord.ButtonStyle.secondary)
    async def previous(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.index > 0:
            self.index -= 1
        await interaction.response.edit_message(embed=self.get_embed(), view=self)

    @discord.ui.button(label="▶", style=discord.ButtonStyle.secondary)
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.index < len(self.pages) - 1:
            self.index += 1
        await interaction.response.edit_message(embed=self.get_embed(), view=self)

class VerificationRole(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="verification-role",
        description="Liste les membres qui ne possèdent pas un rôle donné"
    )
    @app_commands.describe(
        role="Rôle à vérifier",
        fichier="Envoyer aussi un fichier .txt"
    )

    @app_commands.checks.has_permissions(manage_roles=True)
    async def verification_role(
        self,
        interaction: discord.Interaction,
        role: discord.Role,
        fichier: bool = False
    ):

        await interaction.response.defer()

        guild = interaction.guild

        members = [m async for m in guild.fetch_members(limit=None)]

        membres_sans_role = [
            m for m in members
            if role not in m.roles and not m.bot
        ]

        if not membres_sans_role:
            return await interaction.followup.send(
                f"Tous les membres possèdent {role.mention}"
            )

        mentions = [m.mention for m in membres_sans_role]

        # 🔹 pagination (25 par page pour rester lisible)
        chunk_size = 25
        pages = [
            "\n".join(mentions[i:i + chunk_size])
            for i in range(0, len(mentions), chunk_size)
        ]

        view = PaginationView(pages)

        await interaction.followup.send(
            embed=view.get_embed(),
            view=view
        )

        # 📁 option fichier
        if fichier:
            content = "\n".join(m.mention for m in membres_sans_role)

            file = discord.File(
                io.StringIO(content),
                filename="membres_sans_role.txt"
            )

            await interaction.followup.send(file=file)
            
    @verification_role.error
    async def verification_role_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.errors.MissingPermissions):
            await interaction.response.send_message(
                "❌ Tu n'as pas la permission d'utiliser cette commande.",
                ephemeral=True
            )

async def setup(bot):
    await bot.add_cog(
        VerificationRole(bot)
    )