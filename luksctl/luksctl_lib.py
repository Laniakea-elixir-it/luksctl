#!/usr/bin/env python
# ELIXIR-ITALY
# IBIOM-CNR
#
# Contributors:
# author: Tangaro Marco
# email: ma.tangaro@ibiom.cnr.it
#
# Dependencies:

# Imports
import socket
import errno
import json
import os
import signal
import time
import subprocess
import platform

try:
  import ConfigParser
except ImportError:
  import configparser

#______________________________________
# Log config
from .common_logging import set_log
logs = set_log('/tmp/luksctl.log', 'DEBUG')

#______________________________________
class LUKSCtl:
  def __init__(self, fname):

    self.fname = fname

    configParser = ConfigParser.RawConfigParser()
    configParser.readfp(open(fname))
    configParser.read(fname)

    self.cipher_algorithm = configParser.get('luks', 'cipher_algorithm')
    self.hash_algorithm = configParser.get('luks', 'hash_algorithm')
    self.keysize = configParser.get('luks', 'keysize')
    self.device = configParser.get('luks', 'device')
    self.uuid = configParser.get('luks', 'uuid')
    self.cryptdev = configParser.get('luks', 'cryptdev')
    self.mapper = configParser.get('luks', 'mapper')
    self.mountpoint = configParser.get('luks', 'mountpoint')
    self.filesystem = configParser.get('luks', 'filesystem')

  #______________________________________
  # getter
  def get_cipher_algorithm(self): return self.cipher_algorithm
  def get_hash_algorithm(self): return self.hash_algorithm
  def get_keysize(self): return self.keysize
  def get_device(self): return self.device
  def get_uuid(self): return self.uuid
  def get_cryptdev(self): return self.cryptdev
  def get_mapper(self): return self.mapper
  def get_mountpoint(self): return self.mountpoint
  def get_filesystem(self): return self.filesystem

  #______________________________________
  # setter
  def set_cipher_algorithm(self, cipher_algorithm): self.cipher_algorithm = cipher_algorithm
  def set_hash_algorithm(self, hash_algorithm): self.hash_algorithm = hash_algorithm
  def set_keysize(self, keysize): keysize = keysize
  def set_device(self, device): self.device = device
  def set_uuid(self, uuid): self.uuid = uuid
  def set_cryptdev(self, cryptdev): self.cryptdev = cryptdev
  def set_mapper(self, mapper): self.mapper = mapper
  def set_mountpoint(self, mountpoint): self.mountpoint = mountpoint
  def set_filesystem(self, filesystem): self.filesystem = filesystem
