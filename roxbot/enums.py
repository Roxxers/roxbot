# -*- coding: utf-8 -*-

# MIT License
#
# Copyright (c) 2017-2018 Roxanne Gibson
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


from enum import IntEnum


class EmbedColours(IntEnum):
	pink       = 0xDEADBF  # Roxbot Pink
	yellow     = 0xFDDF86  # Roxbot Yellow
	blue       = 0x6F90F5  # Roxbot Blue
	orange     = 0xdd8d16  # Used for warnings (not the admin cog command)
	red        = 0xe74c3c  # Used for errors
	dark_red   = 0x992d22  # Used for on_command_error
	frog_green = 0x4C943D  # Used for FROGTIPS
	triv_green = 0x1fb600  # Used for the correct answer in trivia
	gold       = 0xd4af3a  # Used for displaying the winner in trivia
