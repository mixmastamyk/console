
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

How do they work?

:reverse:`␛`\ [1;3m\ :bi:`Hello World` :reverse:`␛`\ [0m
--------------------------------------------------------------

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
    &gt;&gt;&gt; print(fg.red, fx.italic, 'Heart', fx.end,
              'of Glass…')
    <span style="color:red; font-style: italic">Heart</span> of Glass…
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

    # console[colorama]   # for colorama support
    # console[webcolors]  # for webcolor support

Jah!
While console is cross-platform,
`colorama <https://pypi.python.org/pypi/colorama>`_
will need to be installed to view these examples under the many lame versions of
Windows < 10.


Overview
------------------

As mentioned,
console handles more than color and styles.
A number of useful constants are provided in
:mod:`console.constants`,
such as
`CSI <https://en.wikipedia.org/wiki/ANSI_escape_code#Escape_sequences>`_
and
`OSC <https://en.wikipedia.org/wiki/ANSI_escape_code#Escape_sequences>`_
for building your own apps.


Utils, Screen
~~~~~~~~~~~~~~~~

:mod:`console.utils`
has a number of nifty functions::

    >>> from console.utils import cls, set_title

    >>> cls()  # whammo! a.k.a. reset terminal
    >>> set_title('Le Freak')
    '\x1b]2;Le Freak\x07'

It can also ``strip_ansi`` from strings,
wait for keypresses,
clear the screen with or without scrollback,
and easily pause a script,
like the old DOS commands.

You can move the cursor around with :mod:`console.screen`,
get its position,
save/restore the screen,
and enable
`bracketed paste <https://cirw.in/blog/bracketed-paste>`_
in your app,
among other things.


Detection
~~~~~~~~~~~

Detect the terminal environment with :mod:`console.detection`:

    - Redirection---is this an interactive "``tty``" or not?
    - Determine palette support
    - Check relevant environment variables, such as
      `NO_COLOR <http://no-color.org/>`_,
      `CLICOLOR <https://bixense.com/clicolors/>`_,
      etc.
    - Query terminal colors and themes---light or dark?
    - and more.

Console does its best to figure out what your terminal supports on startup
and will configure the convenience objects we imported above to do typically
the right thing.
They will deactivate themselves at startup when output is redirected into a
pipe, for example.

Detection can be bypassed and handled manually when needed.
Simply use the detection functions in the module or write your own as desired,
then create your own objects from the classes in the
:mod:`console.style` and :mod:`console.screen`
modules.

There's also logging done---\
enable debug level and you'll see the results of the queries from the module.


Color Palettes
~~~~~~~~~~~~~~~

While the original palette of 8/16 colors is accessed by name,
the others have a prefix letter then a name or number of digits to specify the
color.
Access to the color entries of various palettes are accomplished like so.
Unleash your inner
`Britto <https://www.art.com/gallery/id--a266/romero-britto-posters.htm>`_.

.. code-block:: sh

    # Examples      Format  Palette

.. code-block:: text

    fg.red          NAME    8 colors
    fg.lightred     NAME    Another 8 colors w/o bold

    fg.i_22         iDDD    extended/indexed 256-color
    fg.n_f0f        nHHH    Nearest hex to indexed

    fg.t_ff00bb     tHHH    Truecolor, 3 or 6 digits
    fg.x_navyblue   x_NM    X11 color name, if avail
    fg.w_bisque     w_NM    Webcolors, if installed

The underscores are optional,
choose depending whether brevity or readability are more important to you.
Background palettes work the same of course.

Composability++
~~~~~~~~~~~~~~~~

Console's convenience objects are meant to be highly composable and can be used
in many ways.
For example,
you might like to create your own styles to use over and over and over.
They can be called and have "mixins" added in as well:

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
It can be done on the fly as well:

.. raw:: html

    <pre>
    &gt;&gt;&gt; print(f'{fg.i202 + fx.reverse}Tangerine Dream{fx.end}')
    <span style="color: #222; background-color:#ff5f00">Tangerine Dream</span>
    </pre>


Perhaps you'd prefer a pre-rendered template for performance reasons.
Call the entry object with a placeholder string,
with or instead of text::

    >>> template = bg.i22('{}') # dark green

    >>> template.format('No, I do not like…')
    '\x1b[48;5;22mNo, I do not like…\x1b[49m'

.. raw:: html

    <pre>
    &gt;&gt;&gt; print(template.format(' GREEN Eggs… '))
    <div style="display: inline-block; background: #040;"> GREEN Eggs… </div>
    </pre>


Other template formats work also, e.g. ``%s`` and ``${}``.

Palette entries work as context-managers as well::

    with bg.blue:
        print('The following text,'
              'shall be on a blue background.')



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

- Copyright 2018, Mike Miller
- Released under the LGPL, version 3+.
- Enterprise Pricing:

  | 1 MEEllion dollars!
  | *Bwah-haha-ha!*
  | (only have to sell *one* copy!)


