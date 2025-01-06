import os
import asyncio
import typer
from zcfg import ConfigFactory


async def main():
    conf = ConfigFactory.parse_file('./conf/base.conf')
    print(conf)
    path_workspace = conf.get_string("atk.path_workspace")
    print(path_workspace)
    job_tasks = conf.get_list("defaults.flink.job_tasks")
    print(job_tasks)


if __name__ == "__main__":
    asyncio.run(main())


