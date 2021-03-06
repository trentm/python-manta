#!/usr/bin/env python
# Copyright (c) 2012 Joyent, Inc.  All rights reserved.
"""Shared code for test case files."""

from __future__ import absolute_import

__all__ = ["stor", "MantaTestCase"]

import sys
import os
from posixpath import join as ujoin
import unittest
import subprocess
from subprocess import PIPE

import manta

#---- exports


def stor(*subpaths):
    MANTA_USER = os.environ['MANTA_USER']
    if not subpaths:
        return '/%s/stor' % MANTA_USER
    subpath = ujoin(*subpaths)
    if subpath.startswith("/"):
        subpath = subpath[1:]
    return "/%s/stor/%s" % (MANTA_USER, subpath)


class MantaTestCase(unittest.TestCase):
    def __init__(self, *args):
        self.account = os.environ["MANTA_USER"]
        self.subuser = os.environ.get("MANTA_SUBUSER", None)
        self.role = os.environ.get("MANTA_ROLE", None)
        unittest.TestCase.__init__(self, *args)

    _client = None

    def get_client(self):
        MANTA_URL = os.environ['MANTA_URL']
        MANTA_KEY_ID = os.environ['MANTA_KEY_ID']
        MANTA_TLS_INSECURE = bool(os.environ.get('MANTA_TLS_INSECURE', False))
        if not self._client:
            signer = manta.CLISigner(key_id=MANTA_KEY_ID)
            self._client = manta.MantaClient(
                url=MANTA_URL,
                account=self.account,
                subuser=self.subuser,
                role=self.role,
                signer=signer,
                # Uncomment this for verbose client output for test run.
                #verbose=True,
                disable_ssl_certificate_validation=MANTA_TLS_INSECURE)
        return self._client

    def mantash(self, args):
        mantash = os.path.realpath(os.path.join(
            os.path.dirname(__file__), "..", "bin", "mantash"))
        argv = [sys.executable, mantash]
        MANTA_INSECURE = bool(os.environ.get('MANTA_INSECURE', False))
        if MANTA_INSECURE:
            argv.append('-k')
        argv += args
        p = subprocess.Popen(argv,
                             shell=False,
                             stdout=PIPE,
                             stderr=PIPE,
                             close_fds=True)
        p.wait()
        stdout = p.stdout.read()
        stderr = p.stderr.read()
        code = p.returncode
        return code, stdout, stderr
