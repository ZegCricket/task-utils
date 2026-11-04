import datetime
from pathlib import Path

import yaml


def _format_timedelta(td: datetime.timedelta) -> str:
    total_seconds = int(td.total_seconds())
    days, rem = divmod(total_seconds, 86400)
    hours, rem = divmod(rem, 3600)
    minutes, seconds = divmod(rem, 60)

    parts = []
    if days:
        parts.append(f"{days}d")
    parts.append(f"{hours:02}:{minutes:02}:{seconds:02}")
    return " ".join(parts)


def _timedelta_representer(
    dumper: yaml.SafeDumper, td: datetime.timedelta
) -> yaml.Node:
    return dumper.represent_scalar("tag:yaml.org,2002:str", _format_timedelta(td))


def _path_representer(dumper: yaml.SafeDumper, td: Path) -> yaml.Node:
    return dumper.represent_scalar("tag:yaml.org,2002:str", str(td))
