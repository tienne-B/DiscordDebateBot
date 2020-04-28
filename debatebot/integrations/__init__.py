from .mittab import MITTabIntegration
from .tabbycat import TabbycatIntegration


async def get_integration(tournament, ctx=ctx, db=db):
	return {
		"MIT-Tab": MITTabIntegration,
		"Tabbycat": TabbycatIntegration,
	}[tournament['tabsite_type']](tournament, ctx, db)
