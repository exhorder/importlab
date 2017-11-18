# Copyright 2017 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Tests for parsepy.py."""

import textwrap
import unittest

import google3

from importlab import parsepy


class TestParsePy(unittest.TestCase):
  """Tests for parsepy.py."""

  def parse(self, src):
    return parsepy.scan_string(textwrap.dedent(src))

  def test_simple(self):
    self.assertItemsEqual(self.parse("""
      import a
    """), [parsepy.ImportStatement(name="a")])

  def test_dotted(self):
    self.assertItemsEqual(self.parse("""
      import a.b
    """), [parsepy.ImportStatement(name="a.b")])

  def test_as(self):
    self.assertItemsEqual(self.parse("""
      import a as b
    """), [parsepy.ImportStatement(name="a", new_name="b")])

  def test_dotted_as(self):
    self.assertItemsEqual(self.parse("""
      import a.b as c
    """), [parsepy.ImportStatement(name="a.b", new_name="c")])

  def test_dotted_comma(self):
    self.assertItemsEqual(self.parse("""
      import a.b, c
    """), [parsepy.ImportStatement(name="a.b"),
           parsepy.ImportStatement(name="c")])

  def test_multiple_1(self):
    self.assertItemsEqual(self.parse("""
      import a, b, c, d
    """), [parsepy.ImportStatement(name="a"),
           parsepy.ImportStatement(name="b"),
           parsepy.ImportStatement(name="c"),
           parsepy.ImportStatement(name="d")])

  def test_multiple_2(self):
    self.assertItemsEqual(self.parse("""
      import a, b as bb
    """), [parsepy.ImportStatement(name="a"),
           parsepy.ImportStatement(name="b", new_name="bb")])

  def test_multiple_3(self):
    self.assertItemsEqual(self.parse("""
      import a, b as bb, a.x, a.x.y as a_x_y
    """), [parsepy.ImportStatement(name="a"),
           parsepy.ImportStatement(name="b", new_name="bb"),
           parsepy.ImportStatement(name="a.x", new_name="a.x"),
           parsepy.ImportStatement(name="a.x.y", new_name="a_x_y"),
          ])

  def test_multiple_4(self):
    self.assertItemsEqual(self.parse("""
      import a
      import b
      import c
      import d
    """), [parsepy.ImportStatement(name="a"),
           parsepy.ImportStatement(name="b"),
           parsepy.ImportStatement(name="c"),
           parsepy.ImportStatement(name="d")])

  def test_from(self):
    self.assertItemsEqual(self.parse("""
      from a import b
    """), [parsepy.ImportStatement(name="a.b", new_name="b", is_from=True)])

  def test_from_with_rename(self):
    self.assertItemsEqual(self.parse("""
      from a import b as c
    """), [parsepy.ImportStatement(name="a.b", new_name="c", is_from=True)])

  def test_dotted_from(self):
    self.assertItemsEqual(self.parse("""
      from a.b.c import d as e
    """), [parsepy.ImportStatement(name="a.b.c.d", new_name="e", is_from=True)])

  def test_from_multiple(self):
    self.assertItemsEqual(self.parse("""
      from a import b, c, d as dd
    """), [parsepy.ImportStatement(name="a.b", new_name="b", is_from=True),
           parsepy.ImportStatement(name="a.c", new_name="c", is_from=True),
           parsepy.ImportStatement(name="a.d", new_name="dd", is_from=True)])

  def test_from_parentheses(self):
    self.assertItemsEqual(self.parse("""
      from a import (b, c, d as dd)
    """), [parsepy.ImportStatement(name="a.b", new_name="b", is_from=True),
           parsepy.ImportStatement(name="a.c", new_name="c", is_from=True),
           parsepy.ImportStatement(name="a.d", new_name="dd", is_from=True)])

  def test_asterisk(self):
    self.assertItemsEqual(self.parse("""
      from a import *
      from a.b import *
      from a . b . c import *
    """), [parsepy.ImportStatement(name="a", everything=True),
           parsepy.ImportStatement(name="a.b", everything=True),
           parsepy.ImportStatement(name="a.b.c", everything=True)])

  def test_dot(self):
    self.assertItemsEqual(self.parse("""
      from . import a
      from .a import b
      from .a.b import c
      from .a.b.c import *
    """), [parsepy.ImportStatement(name=".a", new_name="a", is_from=True),
           parsepy.ImportStatement(name=".a.b", new_name="b", is_from=True),
           parsepy.ImportStatement(name=".a.b.c", new_name="c", is_from=True),
           parsepy.ImportStatement(name=".a.b.c", everything=True)])

  def test_dotdot(self):
    self.assertItemsEqual(self.parse("""
      from .. import a
      from ..a import b
      from ..a.b import c
      from ..a.b.c import *
    """), [parsepy.ImportStatement(name="..a", new_name="a", is_from=True),
           parsepy.ImportStatement(name="..a.b", new_name="b", is_from=True),
           parsepy.ImportStatement(name="..a.b.c", new_name="c", is_from=True),
           parsepy.ImportStatement(name="..a.b.c", everything=True)])

  def test_dotdotdot_asterisk(self):
    self.assertItemsEqual(self.parse("""
      from ... import *
    """), [parsepy.ImportStatement(name="...", everything=True)])

  def test_dot_multiple(self):
    self.assertItemsEqual(self.parse("""
      from . import a, b, c as cc
    """), [parsepy.ImportStatement(name=".a", new_name="a", is_from=True),
           parsepy.ImportStatement(name=".b", new_name="b", is_from=True),
           parsepy.ImportStatement(name=".c", new_name="cc", is_from=True)])

  def test_encoding_utf8(self):
    self.assertItemsEqual(self.parse("""
      # -*- coding: utf-8 -*-
      # Author: Lo\x6f\xc3\xafc Fooman
      import a
    """), [parsepy.ImportStatement(name="a")])

  def test_encoding_latin1(self):
    self.assertItemsEqual(self.parse("""
      # -*- coding: iso-8859-1 -*-
      # Author: Thomas Sch\xf6n
      import a
    """), [parsepy.ImportStatement(name="a")])

  def test_print_statement(self):
    self.assertItemsEqual(self.parse("""
      print "hello", "world", "!"
    """), [])

  def test_print_function(self):
    self.assertItemsEqual(self.parse("""
      from __future__ import print_function
      import sys
      print("hello world", file=sys.stdout)
    """), [parsepy.ImportStatement(name="__future__.print_function",
                                   new_name="print_function", is_from=True),
           parsepy.ImportStatement(name="sys")])


if __name__ == "__main__":
  unittest.main()
