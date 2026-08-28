"""VIGÍA local web UI — read-only bundle browser + Mode 1 investigation launcher.

This package is strictly downstream of the sealed verdict path: it renders
what the bundles say, verbatim, and never computes, restates, or reconciles
a verdict. Verifiers are invoked as stdlib-only subprocesses, never imported.
"""
