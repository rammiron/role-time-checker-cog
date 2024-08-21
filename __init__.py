from .role_time_checker_cog import RoleTimeCheckerCog


def setup(bot):
    bot.add_cog(RoleTimeCheckerCog(bot))

