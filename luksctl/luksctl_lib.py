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
import os, sys
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
    self.header_path = configParser.get('luks', 'header_path')

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
  def get_header_path(self): return self.header_path

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
  def set_header_path(self, header_path): self.header_path = header_path

  #______________________________________
  def exec_command(self, command):
    proc = subprocess.Popen( args=command, shell=True,  stdout=subprocess.PIPE, stderr=subprocess.PIPE )
    communicateRes = proc.communicate()
    stdOutValue, stdErrValue = communicateRes
    status = proc.wait()
    return stdOutValue, stdErrValue, status

  #____________________________________
  # dmsetup info
  def dmsetup_info(self):
    command = 'dmsetup info /dev/mapper/%s' % self.cryptdev
    stdOutValue, stdErrValue, status = self.exec_command(command)
    return status
  
  #____________________________________
  # Display dmsetup info
  def display_dmsetup_info(self):
    command = 'dmsetup info /dev/mapper/%s' % self.cryptdev
    stdOutValue, stdErrValue, status = self.exec_command(command)
  
    if str(status) == '0':
      print stdOutValue
      print 'Encrypted volume: [ OK ]'
      sys.exit(0)
    else:
      logs.error('[luksctl] %s' % stdErrValue)
      print 'Encrypted volume: [ FAIL ]'
      sys.exit(1)
  
  #______________________________________
  # luksOpen device
  def luksopen_device(self):
    cmd_open = 'cryptsetup luksOpen /dev/disk/by-uuid/%s %s' % (self.uuid, self.cryptdev)
    self.exec_command(cmd_open)
  
    cmd_mount = 'mount /dev/mapper/%s %s' % (self.cryptdev, self.mountpoint)
    stdout, stderr, status = self.exec_command(cmd_mount)
  
    if str(status) == '0':
      cmd_ownership = 'chown galaxy:galaxy %s' % self.mountpoint
      os.system(cmd_ownership)
      self.display_dmsetup_info()
    else:
      print 'Encrypted volume mount: [ FAIL ]'
      sys.exit(1)
  
  #______________________________________
  # luksClose device
  def luksclose_device(self):
    cmd_umount = 'umount %s' % self.mountpoint
    self.exec_command(cmd_umount)
  
    cmd_close = 'cryptsetup close %s' % self.cryptdev
    self.exec_command(cmd_close)
  
    # if dmsetup_setup fails (status 1) the volume has been correctly closed
    if str(self.dmsetup_info()) == '0':
      print 'Encrypted volume umount: [ FAIL ]'
      sys.exit(1)
    else:
      print 'Encrypted volume umount: [ OK ]' 
      sys.exit(0)


  #______________________________________
  # LUKS header test open
  def luksheader_test_open(self):

    self.display_dmsetup_info()
    if str(self.dmsetup_info()) != '0':

      if not os.path.ismount(self.mountpoint):

        self.set_cryptdev('test')
  
        cmd_test_open = 'cryptsetup -v --header ' + self.header_path + ' open ' + self.device + ' ' + self.cryptdev
        self.exec_command(cmd_test_open)
  
        cmd_header_mount = 'mount /dev/mapper/' + self.cryptdev + ' ' + self.mountpoint
        stdout, stderr, status = self.exec_command(cmd_header_mount)
  
        if str(status) == '0':
          self.display_dmsetup_info()
        else:
          print('Mounting encrypted volume with header: [ FAIL ]')
          sys.exit(1)

      else:
        print(self.mountpoint + ' is already a mountpoint: [ FAIL ]')
        sys.exit(1)
    
    else:
      print('Encrypted volume already mounted: [ FAIL ]')
      sys.exit(1)

  #______________________________________
  # LUKS header test close
  def luksheader_test_close(self):
    self.set_cryptdev('test')
    self.luksclose_device()

  #______________________________________
  # LUKS header restore
  def luksheader_restore(self):

    if str(self.dmsetup_info()) != '0':

      if not os.path.ismount(self.mountpoint):

        cmd_restore = 'cryptsetup luksHeaderRestore ' + self.device + ' --header-backup-file ' + self.header_path
        proc = subprocess.Popen( args=cmd_restore, shell=True, stderr=subprocess.PIPE )
        communicateRes = proc.communicate()

      else:
        print(self.mountpoint + ' is already a mountpoint: [ FAIL ]')
        sys.exit(1)

    else:
      print('Encrypted volume already mounted: [ FAIL ]')
      sys.exit(1)
