import os
import sys

from django.core.management.base import BaseCommand

from django_nomad.git.exceptions import GitHookAlreadyExists
from django_nomad.git.utils import find_git_directory


class Command(BaseCommand):
    help = """
        Creates a post-checkout executable file inside git hooks folder that checks migration
        files.
    """

    git_path = find_git_directory()
    hooks_path = os.path.join(git_path, 'hooks')
    post_checkout_path = os.path.abspath(os.path.join(hooks_path, 'post-checkout'))

    def add_arguments(self, *args):
        pass

    def should_update_existing_hook(self):
        response = input('Update existing hook? [y|N] ')
        return 'y' in response.lower()

    def handle(self, *args, **kwargs):
        append = False
        if self.has_post_checkout_file():
            if self.should_update_existing_hook():
                append = True
            else:
                raise GitHookAlreadyExists()

        self.copy_hook_to_post_checkout_folder(append=append)
        print('post-checkout file was created...')

    def has_post_checkout_file(self):
        """
        Verify if there is a file called post-checkout inside the git hooks folder

        Returns:
        bool: True, if the file is exists.
        """
        return os.path.exists(self.post_checkout_path)

    def copy_hook_to_post_checkout_folder(self, append=False):
        """
        Create a post-checkout file and add content from `post-checkout.py` to it, adding the a
        shebang based on user environment to top of file.
        """
        with open(self.post_checkout_path, 'w+') as f:
            if not append:
                f.write('#!/bin/sh')
            f.write(HOOK_SCRIPT)
        os.chmod(self.post_checkout_path, 0o555)


HOOK_SCRIPT = """


CURRENT=$1
TARGET=$2
IS_BRANCH=$3

if [[ "$IS_BRANCH" == 1 ]]; then
    python manage.py check_nomad_migrations $CURRENT $TARGET || echo "An error occurred while checking migrations."
fi
"""
