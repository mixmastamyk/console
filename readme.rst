
.. role:: reverse
   :class: reverse

.. role:: bi
   :class: bi

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

Yet another package that makes it easy to generate the inline codes used to
display colors and character styles in ANSI-compatible terminals and emulators,
as well as other functionality such clearing screens,
moving cursors,
setting title bars,
and detecting capabilities.
A bit more comprehensive than most.
How does it work?


:reverse:`␛`\ [1;3m\ :bi:`Hello World` :reverse:`␛`\ [0m
--------------------------------------------------------------

*"Piece of cake? Oh, I wish somebody would tell me what that means." — Dr. Huer*

Coding with console styles might look like this::

    >>> from console import fg, bg, fx

    >>> fg.green + 'Hello World!' + fg.default
    '\x1b[32mHello World!\x1b[39m'

The string  ``'\x1b'`` represents the ASCII Escape character
(27 in decimal, ``1b`` hex).
Command 32 turns the text green
and 39 back to the default color,
but you don't need to care about all of that.
Printing to a supporting terminal from Python might look like this:

.. raw:: html

    <pre>
    &gt;&gt;&gt; print(fg.red, fx.italic, '♥ Heart', fx.end,
              ' of Glass…', sep='')
    <span style="color:red; font-style: italic">♥ Heart</span> of Glass…
    </pre>


Above, ``fx.end`` is a convenient object to note---\
it ends all styles and fore/background colors at once,
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

.. code-block:: shell

    ⏵ pip3 install --user console

    # console[colorama]   # for colorama support
    # console[webcolors]  # for webcolor support

Jah!
While console is cross-platform,
`colorama <https://pypi.python.org/pypi/colorama>`_
will need to be installed to view these examples under lame versions of Windows
< 10.

::

    ¸.·´¯`·.¸¸.·´¯`·.¸¸.·´¯`·.¸¸.·´¯`·.¸¸¸.·´¯`·.¸¸


Overview
------------------

As mentioned,
console handles more than color and styles.

.. rubric:: Utils

:mod:`console.utils`
includes a number of nifty functions::

    >>> from console.utils import cls, set_title

    >>> cls()  # whammo! a.k.a. reset terminal
    >>> set_title('Le Freak')
    '\x1b]2;Le Freak\x07'

It can also ``strip_ansi`` from strings,
wait for keypresses,
clear a line or the screen (with or without scrollback),
and easily ``pause`` a script like the old DOS command.

.. rubric:: Screen

With :mod:`console.screen` you can
save or restore it,
move the cursor around,
get its position,
and enable
`bracketed paste <https://cirw.in/blog/bracketed-paste>`_
if any of that floats your boat.


.. rubric:: Detection

Detect the terminal environment with :mod:`console.detection`:

    - Determine palette support
    - Check relevant environment variables, such as
      `NO_COLOR <http://no-color.org/>`_,
      `CLICOLOR <https://bixense.com/clicolors/>`_,
      etc.
    - Query terminal colors and themes---light or dark?
    - Redirection---is this an interactive "``tty``" or not?
    - and more.

Console does its best to figure out what your terminal supports on startup
and will configure its convenience objects
(we imported above)
to do the right thing.
They will deactivate themselves at startup when output is redirected into a
pipe, for example.

Detection can be bypassed and handled manually when needed however.
Simply use the detection functions in the module or write your own as desired,
then create your own objects from the classes in the
:mod:`console.style` and :mod:`console.screen`
modules.

There's also logging done---\
enable the debug level and you'll see the results of the queries from the
detection module.

.. rubric:: Constants

A number of useful constants are provided in
:mod:`console.constants`,
such as
`CSI <https://en.wikipedia.org/wiki/ANSI_escape_code#Escape_sequences>`_
and
`OSC <https://en.wikipedia.org/wiki/ANSI_escape_code#Escape_sequences>`_
for building your own apps.
You can::

    from console.constants import BEL
    print('Ring my ', BEL)  # ring-a-ling-a-ling…


Extended Color
~~~~~~~~~~~~~~~

While the original palette of 8/16 colors is accessed directly by name,
others have a prefix letter and a name or digits to specify the color.
Unleash your inner
`Britto <https://www.art.com/gallery/id--a266/romero-britto-posters.htm>`_
below:

.. code-block:: sh


    # Basic        Format  Comment
    fg.red         NAME   # 8 colors
    fg.lightred    NAME   # Another 8 colors w/o bold

    # Extended
    fg.i_123       iDDD   # Extended/indexed 256-color
    fg.n_f0f       nHHH   # Hex to nearest indexed

    # True
    fg.t_ff00bb    tHHH   # Truecolor, 3 or 6 digits
    fg.x_navyblue  x_NM   # X11 color name, if avail
    fg.w_bisque    w_NM   # Webcolors, if avail

The underscores are optional,
choose depending whether brevity or readability are more important to you.
Backgrounds have the same access.


Composability++
~~~~~~~~~~~~~~~~

*Dy-no-mite!! — J.J.*

Console's palette entry objects are meant to be highly composable and useful in
multiple ways.
For example,
you might like to create your own compound styles to use over and over again.
They can be called like functions if desired and have "mixins" added in as well.
The callable form resets styles to their defaults at the end of the string,
so that no longer needs to be managed:

.. raw:: html

    <pre>
    &gt;&gt;&gt; muy_importante = fg.white + fx.bold + bg.red

    &gt;&gt;&gt; print(muy_importante('AHORITA!', fx.underline))
    <div style="display: inline-block; background: #d00; color: white; font-weight: bold; text-decoration: underline">AHORITA!</div>
    </pre>

When palette objects are combined together as we did above,
a list of codes to be rendered to is kept on ice until final output as a
string.
Meaning, there won't be redundant escape sequences in the output::

    '\x1b[37;1;41;4mAHORITA!\x1b[0m'

Styles can be built on the fly as well:

.. raw:: html

    <pre>
    &gt;&gt;&gt; print(
        f'{fg.i208 + fx.reverse}Tangerine Dream{fx.end}'
    )
    <span style="color: #222; background-color:#ff8700">Tangerine Dream</span>
    </pre>


.. rubric:: Templating

To build templates,
call the entry object with a placeholder string,
with or instead of text::

    >>> template = bg.i22('{}')  # dark green

.. raw:: html

    <pre>
    &gt;&gt;&gt; print(template.format(' GREEN Eggs… '))
    <div style="display: inline-block; background: #040;"> GREEN Eggs… </div>
    </pre>

Other template formats are not a problem either, e.g. ``%s`` and ``${}``.

Perhaps you'd like a pre-rendered string in a tight loop for performance
reasons.
Simply use ``str()`` on the final output and use it in the loop.


Palette entries work as context-managers as well::

    with bg.w_dodgerblue:  # or .x_…
        print('Infield: Garvey, Lopes, Russel, Cey, Yeager')
        print('Outfield: Baker, Monday, Smith')
        print('Coach: Lasorda')


Demos and Tests
------------------

*Outta Sight!*

A series of positively *jaw-dropping* demos (haha, ok maybe not) may be run at
the command-line with::

    ⏵ python3 -m console.demos

If you have pytest installed,
tests can be run from the install folder.

::

    ⏵ pytest -s



Legalese
----------------

*"Stickin' it to the Man"*

- Copyright 2018, Mike Miller
- Released under the LGPL, version 3+.
- Enterprise Pricing:

  | 1 MEEllion dollars!
  | *Bwah-haha-ha!*
  | (only have to sell *one* copy!)
