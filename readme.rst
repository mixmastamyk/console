
.. raw:: html

    <pre id='logo' class='center'>
    ┌───────────────────────────┐
    │   ┏━╸┏━┓┏┓╻┏━┓┏━┓╻  ┏━╸   │
    │   ┃  ┃ ┃┃┗┫┗━┓┃ ┃┃  ┣╸    │
    │   ┗━╸┗━┛╹ ╹┗━┛┗━┛┗━╸┗━╸   │
    └───────────────────────────┘
    </pre>

    <p class='center'><i>Tonight we're gonna party like it's 1979…</i></p>
    <p class='center'>╰─(˙𝀓˙)─╮  ╭─(＾0＾)─╯</p>


Console
============

*Yet another easy-to-use console helper and ANSI-sequence library.
More comprehensive than most.*

This package makes it easy to generate the inline codes used to display colors
and character styles in ANSI-compatible terminals and emulators,
as well as other functionality such clearing screens,
moving cursors,
and setting title bars.
What's that, you say?
See the links below for background information:

    - `Terminal Emulator <https://en.wikipedia.org/wiki/Terminal_emulator>`_
    - `ANSI Escape Codes <http://en.wikipedia.org/wiki/ANSI_escape_code>`_
    - `XTerm Control Sequences
      <http://invisible-island.net/xterm/ctlseqs/ctlseqs.html>`_
      (`PDF <https://www.x.org/docs/xterm/ctlseqs.pdf>`_)

In short, the characters seen below are translated into commands for the
terminal to execute,
in this case to render the text "Hello World" with the attributes of italic and
bold.

␛[1;3m \ *Hello World* ␛[0m
--------------------------------------

Coding with console looks like this::

    >>> from console import fg, bg, fx

    >>> fg.green + 'Hello World!' + fg.default
    '\x1b[32mHello World!\x1b[39m'

The "escaped" string ``'\x1b'`` represents the ASCII Escape character,
number 27 in decimal, or ``1b`` in hexadecimal,
while command ``32`` turns the text green…
but you don't need to know all of that.

Printing to a supporting terminal from Python might look like this:


.. raw:: html

    <pre>
    &gt;&gt;&gt; print(fg.purple, fx.italic,
              '⛈ PURPLE RAIN ⛈', fx.end)
    <span style="color:purple; font-style: italic">⛈ PURPLE&nbsp;RAIN ⛈</span>
    </pre>


``fx.end`` is an convenient object to note---\
it ends all styles and fore/background colors,
where as ``bg.default`` for example,
resets only the background to its default color.


.. raw:: html

    <p>But wait!&nbsp;  There's a
    <s><span style="opacity: .9">shitload,</span></s>
    <s><span style="opacity: .9">crapton,</span></s>
    err…
    <i>lot</i> more!</p>


Installen-Sie, Bitte
~~~~~~~~~~~~~~~~~~~~~
::

    ⏵ pip3 install --user console

    # console[webcolors]  # for webcolor support

Console is cross-platform however
`colorama <https://pypi.python.org/pypi/colorama>`_
will also need to be installed to view these examples under lame versions of
Windows.


Overview
------------------

``console.utils`` has a number of nifty functions::

    >>> from console.utils import cls, set_title

    >>> cls()  # whammo!  clear screen and scrollback
    >>> set_title('Console FTW! 🤣')
    '\x1b]2;Console FTW! 🤣\x07'

- You can move the cursor around in ``console.screen``.
- Detect the environment with ``console.detection``.

    - Is it a tty or redirected?
    - Detect palettes
    - Check ``NO_COLOR``, ``CLICOLOR`` environment variables
    - Light or dark background?
    - and more.

Console does its best to figure out if your terminal supports ANSI sequences
and various color palettes on startup.
It will also deactivate itself when output is redirected into a pipe for
example.
Detection can be bypassed and handled manually if performance is a concern.
Just create your own objects from the classes in the style and screen modules.


Palettes
~~~~~~~~~~~~~~~

The standard palette is accessed by name,
but the others typically have a prefix letter and digits to specify the color.
Shortcut access to the various palettes may be accomplished like so::

    # Examples    Format    Palette
    fg.red        NAME      8-color
    fg.lightred   NAME      16-color w/o bold

    fg.i22        iDDD      256-color indexed/extended
    fg.nf0f       nHHH      Nearest to indexed
    fg.tff00bb    tHHH      Truecolor, 3 or 6 digits
    fg.x_navyblue x_N       X11 color name
    fg.w_bisque   w_N       Webcolors, if installed

Background works the same.

I'm still deciding on these, let me know in the bug section if you'd prefer
underscores or not.

Composability
~~~~~~~~~~~~~~~

Console's convenience objects are meant to be highly composable and can be used
in many ways.
For example,
you might like to create your own styles to use over and over and over.
You can call them and add "mixins" as well:

.. raw:: html

    <pre>
    &gt;&gt;&gt; muy_importante = fg.white + fx.bold + bg.red

    &gt;&gt;&gt; print(muy_importante('AHORITA!', fx.underline))
    <div style="display: inline-block; background: #d00; color: white; font-weight: bold; text-decoration: underline">AHORITA!</div>
    </pre>

When console objects are combined together as we did above,
a list of codes to be rendered to is kept on ice until final output as a
string.
Meaning, there won't be redundant escape sequences in the output.

Perhaps you'd prefer a pre-rendered template for performance reasons.
Call the object with a placeholder string::

    >>> template = bg.i22('{}') # dark green

    >>> template.format('No I do not like…')
    '\x1b[48;5;22mNo I do not like…\x1b[49m'

.. raw:: html

    <pre>
    &gt;&gt;&gt; print(template.format(' GREEN Eggs… '))
    <div style="display: inline-block; background: #040;"> GREEN Eggs… </div>
    </pre>


Other formats work also, e.g. ``%s``.

As a context-manager::

    with bg.blue:
        print('\tThis text here,\n'
              '\twill be on a blue background.')


Demos and Tests
------------------

A series of positively *jaw-dropping* demos (haha, ok maybe not) may be run at
the command-line with::

    ⏵ python3 -m console.demos


If you have pytest installed, tests can be run in the install folder?

::

    ⏵ pytest -s




TODOs
-----------

- detect colorama



Legalese
----------------

    - © 2018, Mike Miller
    - Released under the LGPL, version 3+.
    - Enterprise Pricing:

      - 1 MEEllion dollars!
        (only have to sell *one* copy!)
        *Bwah-haha-ha!*


