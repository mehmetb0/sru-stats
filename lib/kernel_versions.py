
import os
import subprocess
import traceback
import ruamel.yaml


KERNEL_VERSIONS_REPO_PATH: str = "/home/memoks//canonical/kernel-versions"

class KernelAssignment:

    def __init__(self, series: str, codename: str, source: str, owner: str, peer_reviewer: str) -> None:
        self.series: str = series
        self.codename: str = codename
        self.source: str = source
        self.owner: str = owner
        self.peer_reviewer: str = peer_reviewer

    def __str__(self) -> str:
        return "{0}:{1} ({2}) -> {3},{4}".format(
            self.series,
            self.codename,
            self.source,
            self.owner,
            self.peer_reviewer)

    @staticmethod
    def read_kernel_versions(cycle: str) -> ruamel.yaml:
        yaml = ruamel.yaml.YAML()
        path: str = os.path.join(KERNEL_VERSIONS_REPO_PATH, cycle, "info", "kernel-series.yaml")
        with open(path, "r") as f:
            return yaml.load(f)

    @staticmethod
    def update_kernel_versions_repo():
        wd = os.getcwd()
        try:
            os.chdir(KERNEL_VERSIONS_REPO_PATH)
            subprocess.run(["git", "pull"])
        except Exception as e:
            print("{}\n{}\n\n".format(str(e), traceback.format_exc()))

        os.chdir(wd)


assignments: dict[str, dict[str, KernelAssignment]] = dict()

def read_uptodate_kernel_assignment(cycle: str) -> dict[str, dict[str, KernelAssignment]]:
    if len(assignments) > 0:
        return assignments

    # KernelAssignment.update_kernel_versions_repo()
    yaml = KernelAssignment.read_kernel_versions(cycle)

    for series, series_data in yaml.items():
        if "codename" not in series_data:
            continue
        if "sources" not in series_data:
            continue

        codename = series_data["codename"]
        if codename not in assignments:
            assignments[codename] = dict()

        for source, source_data in series_data["sources"].items():
            if "owner" not in source_data:
                continue

            owner = source_data["owner"]
            peer_reviewer = ""
            if "peer-reviewer" in source_data:
                peer_reviewer = source_data["peer-reviewer"]

            assignments[codename][source] = KernelAssignment(
                series, codename, source, owner, peer_reviewer)

    return assignments
