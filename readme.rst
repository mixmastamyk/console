
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
and setting title bars.
A bit more comprehensive than most,
however.


:reverse:`␛`\ [1;3m\ :bi:`Hello World` :reverse:`␛`\ [0m
--------------------------------------------------------------

Coding with console styles might look like this::

    >>> from console import fg, bg, fx

    >>> fg.green + 'Hello World!' + fg.default
    '\x1b[32mHello World!\x1b[39m'

The "escaped" string ``'\x1b'`` represents the ASCII Escape character
(27 in decimal, ``1b`` hex).
Command ``32`` turns the text green
and 39 back to the default color,
but you don't need to know all of that.

Printing to a supporting terminal from Python might look like this:

.. raw:: html

    <pre>
    &gt;&gt;&gt; print(fg.red, fx.italic,
              'Heart', fx.end, 'of Glass…')
    <span style="color:red; font-style: italic">Heart</span> of Glass…
    </pre>

.. ~ &gt;&gt;&gt; print(fg.purple, fx.italic,
          .. ~ '⛈ PURPLE RAIN ⛈', fx.end)
.. ~ <span style="color:purple; font-style: italic">⛈ PURPLE&nbsp;RAIN ⛈</span>
.. ~ </pre>
.. ~ 🔔


``fx.end`` is an convenient object to note---\
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

Console is cross-platform,
however
`colorama <https://pypi.python.org/pypi/colorama>`_
will need to be installed to view these examples under lame versions of
Windows.


Overview
------------------

``console.utils`` also has a number of nifty functions::

    >>> from console.utils import cls, set_title

    >>> cls()  # whammo!  clear screen and scrollback
    >>> set_title('Console FTW! 🤣')
    '\x1b]2;Console FTW! 🤣\x07'

- You can move the cursor around in ``console.screen``.
- Detect the environment with ``console.detection`` :

    - Tty or redirected?
    - Query palette support
    - Check environment variables, such as ``NO_COLOR``, ``CLICOLOR``.
    - Is background light or dark?
    - and more.

Console does its best to figure out what your terminal supports on startup.
It will also deactivate itself when output is redirected into a pipe for
example.
Detection can be bypassed and handled manually when needed.
Simply create your own objects from the classes in the ``style`` and ``screen``
modules.


Palettes
~~~~~~~~~~~~~~~

While the standard palette of 16 colors is accessed by name,
the others have a prefix letter and a number of digits or name to specify the
color.
Shortcut access to the various palettes may be accomplished like so:

.. code-block:: sh

    # Examples      Format  Palette

.. code-block:: text

    fg.red          NAME    8-color
    fg.lightred     NAME    16-color w/o bold

    fg.i22          iDDD    256-color indexed/extended
    fg.nf0f         nHHH    Nearest to indexed
    fg.tff00bb      tHHH    Truecolor, 3 | 6 digits
    fg.x_navyblue   x_NM    X11 color name
    fg.w_bisque     w_NM    Webcolors, if installed

Background works the same of course.

X11 colors only available where its ``rgb.txt`` file is,
however if demand were high enough they could be copied into the package.

I'm still deciding on the format of these attributes,
let me know in the bug section if you'd prefer underscores or not.

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


