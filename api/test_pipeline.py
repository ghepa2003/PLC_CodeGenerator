import asyncio
import json
import sys
import logging

logging.basicConfig(level=logging.DEBUG)

sys.path.append('.')
from layers.orchestration import Orchestrator

async def main():
    o = Orchestrator()
    r = await o.execute_workflow('se premo start, il motore parte e si accende la luce verde. se premo stop il motore si ferma e si accende la luce rossa.', 'siemens', 'media')
    print(json.dumps(r, indent=2))

asyncio.run(main())
