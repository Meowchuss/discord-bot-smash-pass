import discord
from discord.ext import commands
from discord import app_commands


class VerificationRole(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="verification-role",
        description="Liste les membres qui ne possèdent pas un rôle donné"
    )
    @app_commands.describe(
        role="Rôle à vérifier"
    )
    async def verification_role(
        self,
        interaction: discord.Interaction,
        role: discord.Role
    ):

        membres_sans_role = [
            membre
            for membre in interaction.guild.members
            if role not in membre.roles
            and not membre.bot
        ]

        if not membres_sans_role:
            await interaction.response.send_message(
                f"Tous les membres possèdent le rôle {role.mention}."
            )
            return

        mentions = "\n".join(
            membre.mention
            for membre in membres_sans_role
        )

        embed = discord.Embed(
            title="Vérification des rôles"
        )

        embed.add_field(
            name="Rôle vérifié",
            value=role.mention,
            inline=False
        )

        embed.add_field(
            name="Nombre de membres concernés",
            value=len(membres_sans_role),
            inline=False
        )

        embed.add_field(
            name="Membres",
            value=mentions[:1024],
            inline=False
        )

        await interaction.response.send_message(
            embed=embed
        )


async def setup(bot):
    await bot.add_cog(
        VerificationRole(bot)
    )