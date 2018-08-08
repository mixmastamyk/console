

.. raw:: html

    <div style="font-family: monospace, fixed; font-weight: bold; background: inherit; padding: 1rem; text-align: center; border-radius: .3em">
    <span style=";color:#729fcf">&#9484;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;</span><span style=";color:#3465a4">&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9488;</span><br />
    <span style=";color:#729fcf">&#9474;</span><span style="">&#160;&#160;&#160;</span><span style=";color:#729fcf">&#9487;&#9473;&#9592;&#9487;</span><span style=";color:#3465a4">&#9473;&#9491;&#9487;&#9491;&#9595;&#9487;&#9473;&#9491;&#9487;&#9473;&#9491;&#9595;</span><span style="">&#160;&#160;</span><span style=";color:#3465a4">&#9487;&#9473;</span><span style=";color:#b4b8b0">&#9592;</span><span style="">&#160;&#160;&#160;</span><span style=";color:#b4b8b0">&#9474;</span><br />
    <span style=";color:#3465a4">&#9474;</span><span style="">&#160;&#160;&#160;</span><span style=";color:#3465a4">&#9475;</span><span style="">&#160;&#160;</span><span style=";color:#3465a4">&#9475;</span><span style="">&#160;</span><span style=";color:#3465a4">&#9475;&#9475;&#9495;&#9515;&#9495;&#9473;&#9491;</span><span style=";color:#b4b8b0">&#9475;</span><span style="">&#160;</span><span style=";color:#b4b8b0">&#9475;&#9475;</span><span style="">&#160;&#160;</span><span style=";color:#b4b8b0">&#9507;&#9592;</span><span style="">&#160;&#160;&#160;&#160;</span><span style=";color:#b4b8b0">&#9474;</span><br />
    <span style=";color:#3465a4">&#9474;</span><span style="">&#160;&#160;&#160;</span><span style=";color:#3465a4">&#9495;&#9473;&#9592;&#9495;</span><span style=";color:#b4b8b0">&#9473;&#9499;&#9593;</span><span style="">&#160;</span><span style=";color:#b4b8b0">&#9593;&#9495;&#9473;&#9499;&#9495;&#9473;&#9499;&#9495;&#9473;&#9592;&#9495;&#9473;</span><span style=";color:#555">&#9592;</span><span style="">&#160;&#160;&#160;</span><span style=";color:#555">&#9474;</span><br />
    <span style=";color:#b4b8b0">&#9492;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;</span><span style=";color:#555">&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9496;</span><br />
    </div>

    <div style="text-align: center; padding: .6em">
        <i>Tonight we're gonna party like it's 1979…</i><br><br>
        ╰─(˙𝀓˙)─╮  ╭─(＾0＾)─╯
    </div>
    <br>


Console
============

*Yet another ANSI-sequence library.  Easy, comprehensive*

This module makes it easy to generate inline codes used to display colors and
character styles in ANSI-compatible terminals and emulators,
as well as other functionality such clearing screens,
moving cursors,
and setting title bars.
It looks a little something like this::

    >>> from console import fg, bg, fx

    >>> fg.green + 'Hello World' + fg.default
    '\x1b[32mHello World\x1b[39m'

    >>> print(bg.purple, fx.italic, '⛈ PURPLE RAIN ⛈', fx.end)
      ⛈ PURPLE RAIN ⛈

.. raw:: html

    <p>But wait!  There's a <s><span style="opacity: .9">shitload</span></s>
    Giant-Robot-sized portion more!</p>


␛[1;3m \ *Introduction* ␛[0m
--------------------------------------

Lost?  What are terminals and ANSI escape codes?
See the links below for background information:

    - `Terminal Emulator <https://en.wikipedia.org/wiki/Terminal_emulator>`_
    - `ANSI Escape Codes <http://en.wikipedia.org/wiki/ANSI_escape_code>`_
    - `XTerm control sequences <http://invisible-island.net/xterm/ctlseqs/ctlseqs.html>`_,
      and more readable `PDF <https://www.x.org/docs/xterm/ctlseqs.pdf>`_.


Installen-Sie, Bitte
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
::

    ⏵ pip3 install --user console


Another One, eh 🤔?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Well, ANSI escape codes have been standard on UNIX
with the belt-and-suspenders crowd for several decades,
and even saw use on DOS and BBSs back in the day.
With the advent of macOS (X),
a whole new generation of bearded-hipsters was exposed to the command-line and
terminal environment.

Finally with Windows 10──\
the Ballmer "I'm a PC" lame-o-barrier has finally been breached,
allowing *multi-decade-late*
`improvements
<http://www.nivot.org/blog/post/2016/02/04/Windows-10-TH2-(v1511)-Console-Host-Enhancements>`_
to be made to its until-now pathetic "console,"
analogous to a virtual terminal,
as a Yugo to a BMW.

So, the three major platforms now support ANSI escape sequences.
Again!
What's old is new again.


Python and the Cheeseshop
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In the Python world,
there has never been much direct support for terminal sequences in the standard
library,
beyond curses and termios
(which overlap somewhat in functionality with this of course).
They are low-level interfaces however
focused on "full screen" terminal apps and tty control respectively.
Perhaps styling a text snippet here and there was thought too… trivial.
Not exactly rocket surgery.

And so, now there are ad-hoc ANSI codes being generated in every command-line
app and eleventy million micro-libs on the PyPI Cheeseshop doing the same.
Looks to be a fun exercise and somewhat of a rite of passage to create one---\
and good luck finding an appropriate name on PyPi.

While most of the modules have plenty going for them in their areas of focus,
they generally aren't very comprehensive──\
providing 8 colors, and a few styles/effects like bold and underline.
One or more items that are often missing:

    - Python3 support
    - Styles, cursor movements, clearing the screen,
      setting titles, etc.
    - Palette auto-detection, support and deactivation:

      - 16 color palette
      - 256 extended color palette - rare
      - 16M color palette - rarer

    - Maintained
    - Has tests
    - Standard color names support - TODO

Most have an easy to use design, but may sill miss one of these nice to haves:

    - Composable objects
    - Short names
    - No capital, mixed, camel-case names on instances.

Looked over these and picked a few design cues from several:

    - ansi
    - colorama.ansi
    - click.style
    - ansicolors
    - kolors                - terminfo?
    - style  - check out
    - blessings / blessed   - terminfo?
    - pycolor?
    - colorize
    - fabric.colors
    - escape

.. ~ Outside of colorama for Ballmer/Windows support I don't use m'


Getting Started
------------------

blah



Demos and Tests
------------------

A series of positively *jaw-dropping* demos (hehe) may be run at the
command-line with::

    ⏵ python3 -m console.demos


If you have pytest installed, tests can be run in the install folder?

::

    ⏵ pytest -s



Legalese
----------------

    - © 2018, Mike Miller
    - Released under the LGPL, version 3+.
    - Enterprise Pricing:
      1 MEEllion dollars!  (only have to sell *one* copy!)


