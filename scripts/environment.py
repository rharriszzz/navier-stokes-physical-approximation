"""Print the same environment information stored with each profile run."""

import json

from nsblowup.io import environment_info


if __name__ == "__main__":
    print(json.dumps(environment_info(), indent=2))