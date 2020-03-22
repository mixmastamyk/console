
::

    ┌───────────────────────────┐
    │   ┏━╸┏━┓┏┓╻┏━┓┏━┓╻  ┏━╸   │
    │   ┃  ┃ ┃┃┗┫┗━┓┃ ┃┃  ┣╸    │
    │   ┗━╸┗━┛╹ ╹┗━┛┗━┛┗━╸┗━╸   │
    └───────────────────────────┘

*Tonight we're gonna party like it's 1979…*

╰─(˙𝀓˙)─╮  ╭─(＾0＾)─╯



Console
============

.. sidebar:: **Testimonials**

    - *"👍 Ayyyyyy… 👍"—The Fonz*
    - *"DYN-O-MITE!!" — J.J. from Good Times*
    - *“Better… Stronger… Faster”—Oscar Goldman*
    - *"There is nothing we won't try…" —Laverne and Shirley*
    - *"Nothin' can stand in our way…" —Olivia Newton-John*
    - *"Fightin' the system like a true modern day Robin Hood" —Waylon Jennings*

|
..    - *"So hot, totally hot…"—Olivia Newton-John*
..    - *"Suddenly, the wheels are in motion…"—Olivia Newton-John*


Yet another package that makes it easy to generate the inline codes used to
display colors and character styles in ANSI-compatible terminals and emulators,
as well as other functionality such clearing screens,
moving cursors,
setting title bars,
and detecting capabilities.

How is this one different?
Well,
it's highly composable and more comprehensive than most.
How does it work?
It's a piece of cake.

    *"Piece of cake?
    Oh, I wish somebody would tell me what that means." —Dr. Huer*


␛\ [1;3m *Hello World* ␛\ [0m
----------------------------------------------------------

There are many flexible ways to use console's styling functionality.
Most simply, adding a little color with console might look like this.
First, import the styling palettes and go to town.
The palette entries (aka attributes) can be used in place of strings and handle
everything a string might:

.. code-block:: python

    >>> from console import fg, bg, fx

    >>> fg.green + 'Hello World!' + fg.default
    '\x1b[32mHello World!\x1b[39m'

    >>> f'{fx.dim}Lo-key text:{fx.end}'
    '\x1b[2mLo-key text:\x1b[0m'

    >>> print(fg.red, fx.italic, '♥ Heart', fx.end,
    ...       ' of Glass…', sep='')

    ♥ Heart of Glass…  # ← not styled due to readme limits 😉



FYI, the string  ``'\x1b'`` represents the ASCII Escape character
(``27`` in decimal, ``1b`` hex).
Command ``[32m`` turns the text green
and ``[39m`` back to the default color.
But, there's no need to worry about any of that.
That's why you're here, right?


.. note::

    *Apologies, text output can't be styled due to PyPI/github readme
    limitations.
    Try the*
    `Sphinx docs <https://mixmastamyk.bitbucket.io/console/>`_
    *instead.
    When you see "😉" in a comment, that's a reminder you're not getting
    the full monty.*


Above, ``fx.end`` is a convenient object to note---\
it ends all styles and fore/background colors at once,
where as ``fg.default`` or ``bg.default`` for example,
resets only the fore or background to its default color.
To avoid that responsibility,
one may also use the call form instead,
where
`it's automatic <https://youtu.be/y5ybok6ZGXk>`_:

.. code-block:: python

    >>> fg.yellow('Far Out!')
    '\x1b[33mFar Out!\x1b[39m'


There's also a rich-text printer that handles basic HTML
(and even hyperlinks if your terminal supports it):

.. code-block:: python

    >>> from console.printers import print
    >>> print('<i>Hello <b>World!</b> ;-)</i>')

    *Hello World! ;-)*  # 😉


But there's a shitload,^H^H^H^H^H, crap-ton,^H^H^H^H^H
err…
*lot more!*  Kindly read on.


.. _compose:

Composability++
~~~~~~~~~~~~~~~~

    | *"East bound and down, loaded up and truckin'…*
    | *We gonna do what they say can't be done"—Smokey and the Bandit*

Console's palette entry objects are meant to be highly composable and useful in
multiple ways.
For example,
you might like to create your own compound styles to use over and over again.
How to? 
Just add 'em up:

.. ~ They can also be called (remember?) as functions if desired and have "mixin"
.. ~ styles added in as well.
.. ~ The callable form also automatically resets styles to their defaults at the end
.. ~ of each line in the string (to avoid breaking pagers),
.. ~ so those tasks no longer need to be managed manually:

.. code-block:: python

    >>> muy_importante = fg.white + fx.bold + bg.red
    >>> print(muy_importante('¡AHORITA!', fx.underline))  # ← mixin

    ¡AHORITA!  # ← not styled due to readme limits 😉

One nice feature---\
when palette objects are combined together as done above,
the list of codes to be rendered is kept on ice until final output as a string.
Meaning, there won't be redundant styling (Select Graphic Rendition) sequences
in the output,
no matter how many you add:

.. code-block:: python

    '\x1b[37;1;41;4m¡AHORITA!\x1b[0m'
    # ⇤-----------⇥  One compound sequence, not four 😎

Styles can be built on the fly as well, if need-be:

.. code-block:: python

    >>> print(
    ...   f'{fg.i208 + fx.reverse}Tangerine Dream{fx.end}',  # or
    ...     (fg.i208 + fx.reverse)('Tangerine Dream'),
    ... )
    Tangerine Dream  # 😉

.. rubric:: **Templating**

To build templates,
call a palette entry with placeholder strings,
with (or instead of) text:

.. code-block:: python

    >>> sam_template = bg.i22('{}')  # dark green
    >>> print(sam_template.format(' GREEN Eggs… '))

.. code-block:: python

     GREEN Eggs…   # No, I do not like… 😉

Other template formats are no problem either,
try ``%s`` or ``${}``.


.. rubric:: **Performance**

*Outta Sight!*

Console is lightweight,
but perhaps you'd like a pre-rendered string to be used in a tight loop for
performance reasons.
Simply use ``str()`` to finalize the output then use it in the loop.

.. code-block:: python

    >>> msg = str(muy_importante('¡AHORITA!'))

    >>> for i in range(100000000):
    ...     print(msg)  # rapidinho, por favor


.. rubric:: **Managers**

Palette entries work as context-managers as well:

.. code-block:: python

    with bg.dodgerblue:
        print('Infield: Garvey, Lopes, Russel, Cey, Yeager')
        print('Outfield: Baker, Monday, Smith')
        print('Coach: Lasorda')


::

                                ⚾
    ¸¸.·´¯`·.¸¸.·´¯`·.¸¸.·´¯`·.⫽⫽¸¸.·´¯`·.¸¸¸.·´¯`·.¸¸¸
                              ⫻⫻    Tok!


Color Palettes
~~~~~~~~~~~~~~~

    *"Looo-king Gooood!"—Chico and the Man*

The color palettes entries may be further broken down into three main
categories of available colors.
Unleash your inner
`Britto <https://www.art.com/gallery/id--a266/romero-britto-posters.htm>`_
below:

    - Basic, the original 8/16 ANSI named colors
    - Extended, a set of 256 indexed colors
    - "True", a.k.a. 16 million colors, consisting of either:

      - RGB specified colors
      - X11-named colors (now built-in), or
      - Webcolors-named colors

As mentioned,
the original palette,
X11,
and Webcolor palettes
may be accessed directly from a palette object by name.
For example:

.. code-block:: python

    # Basic                Comment
    fg.red                # One of the original 8 colors
    fg.lightred           # Another 8 brighter colors w/o bold

    # Truecolor variants
    fg.bisque             # Webcolors or X11 color name
    fg.navyblue           # Webcolors takes precedence, if installed


.. rubric:: Advanced Color Selection

*Specific* palettes/colors may be chosen via a prefix letter and number of digits
(or name) to specify the color.
For example:

.. code-block:: python

    # Extended     Format  Comment
    bg.i_123       iDDD   # Extended/indexed 256-color palette
    bg.n_f0f       nHHH   # Hex to *nearest* indexed color

    # Truecolor
    bg.t_ff00bb    tHHH   # Truecolor, 3 or 6 digits
    bg.x_navyblue  x_NM   # Force an X11 color name (built-in)
    bg.w_bisque    w_NM   # Force Webcolors, if installed

(The underscores in the attribute names that are numbers are optional.
Choose depending whether brevity or readability are more important to you.)

The assorted truecolor forms are used to specify a color explicitly without
ambiguity—\
X11 and Webcolors
`differ <https://en.wikipedia.org/wiki/X11_color_names#Clashes_between_web_and_X11_colors_in_the_CSS_color_scheme>`_
on a few obscure colors.
Though nothing beats "þe olde" hexdigits for certainty.

.. note::

    Be aware,
    an unrecognized color name or index will result in an ``AttributeError``.


Installen-Sie, Bitte
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: shell

    ⏵ pip3 install --user console

Suggested additional support packages,
some of which may be installed automatically if needed:

.. code-block:: shell

    webcolors             # Moar! color names
    future_fstrings       # Needed for: Python Version < 3.6

    colorama              # Needed for: Windows Version < 10
    win_unicode_console   # Useful: for Win Python < 3.6


Jah!
While console is cross-platform,
`colorama <https://pypi.python.org/pypi/colorama>`_
will need to be installed and .init() run beforehand to view these examples
under the lame (no-ANSI support) versions of Windows < 10

.. note::

    ``console`` supports Python 3.6 and over by default.
    However!  It is trying out
    `"future-fstrings" <https://github.com/asottile/future-fstrings>`_
    for experimental support under Python versions 3.5 and 3.4,
    perhaps earlier.
    Keep an eye peeled for oddities under older Pythons.
    Sorry, neither 2.X or 1.X is supported.  ``:-P``


Der ``console`` package has recently been tested on:

- Ubuntu 19.10 - Python 3.7

  - xterm, mate-terminal, linux console, fbterm
  - Very occasionally on kitty, guake

- FreeBSD 11 - Python 3.7
- MacOS 10.13 - Python 3.6

  - Terminal.app, iTerm2

- Windows XP - Python 3.4 - 32 bit + colorama, ansicon
- Windows 7 - Python 3.6 - 32 bit + colorama
- Windows 10 - Python 3.7 - 64bit

  - Conhost, WSL, Windows Terminal


::

    ¸¸.·´¯`·.¸¸.·´¯`·.¸¸.·´¯`·.¸¸.·´¯`·.¸¸¸.·´¯`·.¸¸¸


Package Overview
~~~~~~~~~~~~~~~~~~

    *"Hey, Mr. Kot-tair!"—Freddie "Boom Boom" Washington*

As mentioned,
console handles lots more than color and styles.

.. rubric:: **Utils Module**

`console.utils`
includes a number of nifty functions:

.. code-block:: python

    >>> from console.utils import cls, set_title

    >>> cls()  # whammo! a.k.a. reset terminal
    >>> set_title('Le Freak')  # c'est chic
    '\x1b]2;Le Freak\x07'

It can also ``strip_ansi`` from strings,
wait for keypresses,
clear a line or the screen (with or without scrollback),
make hyperlinks,
or easily ``pause`` a script like the old ``DOS`` commands of yesteryear.

There are also modules to print stylish progress bars:
`console.progress`,
or beep up a storm with
`console.beep`.


.. rubric:: **Screen Module**

With `console.screen` you can
save, create a new, or restore a screen.
Move the cursor around,
get its position,
and enable
`bracketed paste <https://cirw.in/blog/bracketed-paste>`_
if any of that floats your boat. 
`Blessings <https://pypi.org/project/blessings/>`_-\
compatible context managers are available for full-screen fun.

.. code-block:: python

    >>> from console.screen import sc

    >>> with sc.location(40, 20):
    ...     print('Hello, Woild.')


.. rubric:: **Detection Module**

Detect the terminal environment with
`console.detection`:

    - Determine palette support
    - Redirection---is this an interactive "``tty``" or not?
    - Check relevant user preferences through environment variables,
      such as
      `NO_COLOR <http://no-color.org/>`_,
      `COLORFGBG <https://unix.stackexchange.com/q/245378/159110>`_,
      and
      `CLICOLOR <https://bixense.com/clicolors/>`_,
      and even
      `TERM <https://www.gnu.org/software/gettext/manual/html_node/The-TERM-variable.html>`_.
    - Query terminal colors and themes—light or dark?
    - Get titles, cursor position, and more.
    - Legacy Windows routines are in `console.windows`

Console does its best to figure out what your terminal supports on startup
and will configure its convenience objects
(we imported above)
to do the right thing.
They will *deactivate themselves automatically* at startup when output is
redirected into a pipe,
for example.

Detection can be bypassed and handled manually when needed however.
Simply use the detection functions in the module or write your own as desired,
then create your own objects from the classes in the
`console.style` and
`console.screen`
modules.
(See the Environment Variables section for full deactivation.)

There's also logging done—\
enable the debug level before loading the console package and you'll see the
results of the queries from the detection module.

.. rubric:: **Constants**

A number of useful constants are provided in
`console.constants`,
such as
`CSI <https://en.wikipedia.org/wiki/ANSI_escape_code#Escape_sequences>`_
and
`OSC <https://en.wikipedia.org/wiki/ANSI_escape_code#Escape_sequences>`_
for building your own apps.
You can:

.. code-block:: python

    from console.constants import BEL
    print(f'Ring my {BEL}… Ring my {BEL}')  # ring-a-ling-a-ling…


.. rubric:: **ASCII Table**

A four-column ASCII table in fruity flavors is provided for your convenience
and teaching opportunities.
This format is great for spotting Control key correspondence with letters,
e.g.: Ctrl+M=Enter, Ctrl+H=Backspace, etc:

.. code-block:: shell

    ⏵ python3 -m console.ascii4 [-h]

    00111   7 07  BEL         39 27  '           71 47  G          103 67  g
    …  # 😉


.. rubric:: **The Rest**

See the Advanced page for more detail.


Demos and Tests
~~~~~~~~~~~~~~~~

    *"I got chills, they're multiplyin'…"—Danny Zuko*

A series of positively jaw-dropping demos (haha, ok maybe not) may be run at
the command-line with::

    ⏵ python3 -m console.demos

If you have pytest installed,
tests can be run from the install folder.

.. code-block:: shell

    ⏵ pytest -s

The Makefile in the repo at github has more details on such topics.


Contributions
~~~~~~~~~~~~~~~~

    *"Use the Source, Luke!"—'Ben' Kenobi*

Could use some help testing on Windows and MacOS as my daily driver is a 🐧 Tux
racer.
Can you help?


Legalese
~~~~~~~~~~~~~~~~

*"Stickin' it to the Man"*

- Copyright 2018-2020, Mike Miller
- Released under the LGPL, version 3+.
- Enterprise Pricing:

  | 6 MEEllion dollars…  *Bwah-haha-ha!*
  | (only have to sell *one* copy!)
