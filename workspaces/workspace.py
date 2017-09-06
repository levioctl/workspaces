import os
import subprocess

import printwarning
import configuration
import workspacetomainrepo


class Workspace(object):
    def __init__(self, name):
        self.path = os.path.join(configuration.root_dir, name)
        self.main_repo = workspacetomainrepo.get_main_repo(self.path)
        self.name = name
        self.untracked_files_modified = None
        self.tracked_files_modified = None
        self.branch = None
        self.head_description = None
        self._read()

    def is_branch_checked_out(self):
        return not self.branch.startswith("(HEAD detached ")

    def _read(self):
        status = self._git_command("status", "--porcelain")
        status = status.splitlines()
        self.untracked_files_modified = any(line for line in status if line.startswith("??"))
        self.tracked_files_modified = any(line for line in status if not line.startswith("??"))
        self.branch = self._read_branch()
        self.head_description = self._git_command("show", "--quiet", "--oneline")

    def _read_branch(self):
        branch = self._git_command("branch")
        branchLine = [line.strip("\t *") for line in branch.splitlines() if line.startswith("* ")]
        return branchLine[0] if branchLine else "No branch"

    def _git_command(self, *args):
        repo_path = os.path.join(self.path, self.main_repo)
        git_dir = os.path.join(repo_path, ".git")
        args = ["git", "--work-tree", repo_path, "--git-dir", git_dir] + list(args)
        try:
            result = subprocess.check_output(args)
        except subprocess.CalledProcessError:
            printwarning.printwarning("%s is not a git repository" % (repo_path))
            result = None
        return result


def list_workspaces_dirs():
    return [dirname for dirname in os.listdir(configuration.root_dir) if
            os.path.isdir(os.path.join(configuration.root_dir, dirname)) and
            dirname not in configuration.dirs_to_ignore]