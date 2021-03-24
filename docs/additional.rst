
.. role:: reverse
   :class: reverse

.. raw:: html

    <pre id='logo' class='center'>
    <span style="color:#729fcf">&#9484;───────────────</span><span style="color:#3465a4">────────────&#9488;</span>
    <span style="color:#729fcf">│</span>   <span style="color:#729fcf">&#9487;&#9473;&#9592;&#9487;</span><span style="color:#3465a4">&#9473;&#9491;&#9487;&#9491;&#9595;&#9487;&#9473;&#9491;&#9487;&#9473;&#9491;&#9595;</span>  </span><span style="color:#3465a4">&#9487;&#9473;</span><span style="color:#b4b8b0">&#9592;</span>   <span style="color:#b4b8b0">│</span>
    <span style="color:#3465a4">│</span>   <span style="color:#3465a4">&#9475;</span>  </span><span style="color:#3465a4">&#9475;</span> </span><span style="color:#3465a4">&#9475;&#9475;&#9495;&#9515;&#9495;&#9473;&#9491;</span><span style="color:#b4b8b0">&#9475;</span> </span><span style="color:#b4b8b0">&#9475;&#9475;</span>  <span style="color:#b4b8b0">&#9507;&#9592;</span>    </span><span style="color:#b4b8b0">│</span>
    <span style="color:#3465a4">│</span>   <span style="color:#3465a4">&#9495;&#9473;&#9592;&#9495;</span><span style="color:#b4b8b0">&#9473;&#9499;&#9593;</span> </span><span style="color:#b4b8b0">&#9593;&#9495;&#9473;&#9499;&#9495;&#9473;&#9499;&#9495;&#9473;&#9592;&#9495;&#9473;</span><span style="color:#555">&#9592;</span>   <span style="color:#555">│</span>
    <span style="color:#b4b8b0">&#9492;───────────────</span><span style="color:#555">────────────&#9496;</span>
    </pre>

.. container:: center

    *Gimme! Gimme! Gimme! (A Man After Midnight)*

.. raw:: html

    <style>
        .backb { display: inline-block; transform: rotateY(180deg) }
        #wrapper {
            text-align: center;
            margin-top: -13px;
        }
        #cen {
            display: inline-block;
        }
    </style>

    <div id="wrapper">
        <div id="cen">
            —A<div class="backb">B</div>BA &nbsp; &nbsp;
        </div>
    </div>

|

Additional Topics
=======================

    *"Can You Dig It?"*

.. rubric:: How do the styles work?

Behind the scenes in
:mod:`console.core`
you've been working with the two main parent classes of those in
:mod:`console.style`:

.. rubric:: Palette Collections:

A Palette is a collection object holding a large number of associated Entries,
available as attributes, e.g.:

    - ``fg``, ``bg``, ``fx``
    - ``defx`` (for deactivating specific styles)

While the simplest palette entries
(original and effects, such as ``fg.blue`` or ``fx.bold``)
are created up front,
the rest, such as indexed or truecolor,
are built up on demand.
Like a traffic cop,
palettes objects direct attribute access to the appropriate code to initialize
each palette entry.

Once created,
palette Entry attributes are cached and available for future use.
This namespace cache may also be cleared in uncommon scenarios using huge
palettes,
with the ``clear()`` method.

.. rubric:: Palette Entries:

Entry objects are what actually produce the escape sequences and other
functionality.
They are accessed as attributes of a palette collection, e.g.:

    - ``.red``
    - ``.i22``
    - ``.cornflowerblue``

Entries:

    - Keep track of their ANSI codes and others they've been added to.
    - Can be called and "mixed in" with other attributes to render
      themselves, then end the style when finished.
    - Can be used as a context-manager.
    - Last but not least,
      can be rendered as an escape sequence string on any form of output.

Similar functionality is available from
:mod:`console.screen`'s screen object.


.. rubric:: Automatic Detection

When automatic detection is used and palettes are found not to be supported,
palette entries are replaced instead with "dummy" blank objects that render to
nothing.
Well, more specifically empty strings.


.. raw:: html

    <div class="center rounded dark p1">
        <div class=pacman>
            <span class=pline>╭───────────────────────────╮&nbsp;&nbsp;<br>
            │
            </span>
            <span class=dots>·····•·····</span>
            <span id=pac>ᗤ</span>&nbsp;
            <span id=sha>ᗣ</span><span id=spe>ᗣ</span>
            <span id=bas>ᗣ</span><span id=pok>ᗣ</span>
            <span class=pline>│&nbsp;&nbsp;<br>
            </span>
            <i style="opacity: .7">…waka waka waka…</i>&nbsp;&nbsp;
        </div>
    </div>


Custom Initialization
------------------------

    *"I hope you know this violates my warranty!"—Twiki*


On terminals advertising xterm compatibility (though incomplete) color
detection may hang and need to be disabled.
Recent versions of console implement a blacklist and timeout to
alleviate/mitigate this.
If you notice that console startup stutters briefly at import time,
you might be affected.
See troubleshooting below to enable DEBUG logging.

To disable automatic detection of terminal capabilities at import time the
environment variable
``PY_CONSOLE_AUTODETECT`` may be set to ``0``.
Writing a bug at the
`console repo <https://github.com/mixmastamyk/console/issues/>`_
would help also.

Forcing the support of all palettes ON can also be done externally with an
environment variable,
such as ``CLICOLOR_FORCE``,
if desired.


.. rubric:: Initializing Your Own

*"I love the smell of napalm in the morning."—Lt. Col. Kilgore*

To configure auto-detection, palette support,
or detect other output streams besides stdout,
one may build palette objects yourself:

.. code-block:: shell

    ⏵ env PY_CONSOLE_AUTODETECT='0' script.py

.. code-block:: python

    from console.constants import TermLevel
    from console.style import BackgroundPalette

    # e.g. force all palettes on:
    fullbg = BackgroundPalette(level=TermLevel.THE_FULL_MONTY)



Palette Downgrade
----------------------

    *"Get down, boogie oogie oogie…"—A Taste of Honey*

When using true or extended colors on a terminal that is not configured to
support it,
console will "downgrade" the colors to their nearest neighbors in the available
palette.

Neat, huh?
It does this using a "Euclidian 3D" distance method which is quite fast but
only somewhat accurate,
due to the fact that the RGB color space is not uniform.

That lead to some experimentation with
`CIEDE2000 <https://en.wikipedia.org/wiki/Color_difference#CIEDE2000>`_
libraries like colormath and colorzero.
Unfortunately they were both quite heavy and slow as molasses,
even with numpy loaded,
which is also slow to import.

Fast and inaccurate it is!
Unless someone would like to write a highly optimized implementation in
C or Assembler for kicks,
it doesn't seem worth the trouble for this library.

::

    ¸¸¸¸,ø¤º°`°º¤ø,¸¸,ø¤º°`°º¤ø,¸,ø¤°º¤ø,¸¸,ø¤º°`°º¤ø,¸¸¸¸


Environment Variables
-----------------------

    | *"But I took them away from all that, and now they work for me.*
    | *My name is Charlie."*

The following standard variables are noted by ``console`` and affect its
behavior:

Operating System:

    - ``TERM`` - basic category of terminal, more info is often needed due to
      most terminals lying that they are an xterm.
    - ``TERM_PROGRAM`` - for hints on what it supports
    - ``SSH_CLIENT`` - when remote, downgrade to terminfo detection potentially
      simpler support.
    - ``LANG`` - is Unicode available?

Color-specific:

    - ``CLICOLOR``, 1/0 - Enable or disable ANSI sequences if on a tty
    - ``CLICOLOR_FORCE`` - Force it on anyway
    - ``COLORTERM`` - "truecolor" or "24bit" support
    - ``NO_COLOR`` - None, dammit!
    - ``COLORFGBG`` - Light or dark background?

Windows:

    - ``ANSICON`` - a shim to render ANSI on older Windows is recognized.

MacOS:

    - ``TERM_PROGRAM_*`` - is looked at for more specific program information.

Console itself:

    - ``PY_CONSOLE_AUTODETECT`` - Disables automatic detection routines.

    .. ~ - ``PY_CONSOLE_COLOR_SEP`` - inner separator char for extended color
      .. ~ sequences.
      .. ~ Typically ``:``, but may need to be changed to ``;`` under legacy terms.

    - ``PY_CONSOLE_USE_TERMINFO`` - Enables terminfo lookup for many
      capabilities.


Screen Stuff
-------------------

    | *Wilma: I confess I thought the Princess had you beguiled.*
    | *Buck: Well, she did have the nicest set of horns at the ball!*
    | *Dr. Theopolis: Yes—it was an attractive hat.*

The :mod:`console.screen` module is the one you're looking for,
although there is a preconfigured convenience instance in the root of the
package as well:

.. code-block:: python

    >>> from console import sc

    >>> sc.clear_line(1)  # mode 1, clear to left
    '\x1b[1K'

    >>> print('already deleted!', sc.clear_line(1))

    >>>  # this space intentionally left blank ;-)

There are several blessings-inspired context managers as well:

- ``sc.bracketed_paste()``
- ``sc.fullscreen()``
- ``sc.hidden_cursor()``
- ``sc.location(x, y)``
- ``sc.rare_mode()  # aka "cbreak mode"``
- ``sc.raw_mode()``


Progress Bars
-------------------

    | *"What's Happening, 'Raj' !?!"*
    | *"What's Happening, Duh-wayne!?"*

A progress bar implementation is located in :mod:`console.progress` and may be
demoed thusly:

.. code-block:: shell

    ⏵ python3 -m console.progress -l


Hello world looks like this:

.. code-block:: python

    >>> from console.progress import ProgressBar

    >>> bar = ProgressBar()  # "Hey HEY, hey!"
    >>> print(bar(50))       # out of 100

.. raw:: html

    <style>
        .b { color: #005f87 }
        .g { color: #5faf00 }
        .o { opacity: .8 }
    </style>
    <pre style="margin-top: -13px; padding-top: .1em">
    <span class=g>
    ▮▮▮▮▮▮▮▮▮▮▮▮▮▮▮</span><span class=b>▯▯▯▯▯▯▯▯▯▯▯▯▯▯▯</span>  <span class=o>50%</span>

    </pre>


"Icon" sets and color schemes can be set independently,
or combined into a full theme.
There is also a ``HiDefProgressBar`` class that can render itself with sub-cell
Unicode block characters for "more resolution" in environments with constrained
width.
Some examples:

.. code-block:: python

    ProgressBar(theme='basic')          # ASCII
    ProgressBar(theme='basic_color')    # default for Windows
    ProgressBar(theme='shaded')         # Unicode ← ↓
    ProgressBar(theme='warm_shaded')
    ProgressBar(theme='shaded', icons='faces')
    ProgressBar(theme='heavy_metal')
    ProgressBar(icons='segmented')
    ProgressBar(theme='shaded', icons='triangles')
    ProgressBar(theme='solid')
    ProgressBar(theme='solid', styles='amber_mono')

    # To use partial characters:
    HiDefProgressBar(styles='greyen')
    HiDefProgressBar(theme='dies', partial_chars='⚀⚁⚂⚃⚄⚅',
                                   partial_char_extra_style=None)

(Windows console has very limited Unicode font support unfortunately,
though Lucida Console is a bit more comprehensive than Consolas.
ProgressBar defaults to an ASCII representation in that environment.)

A more robust use of the modules is illustrated below::

    from time import sleep  # demo purposes only
    from console.screen import sc
    from console.progress import ProgressBar

    with sc.hidden_cursor():  # "Ooooohh, I'm tellin' Mama!"

        items = range(256)      # example tasks, set total
        bar = ProgressBar(total=len(items)-1)

        # simple loop
        for i in items:
            print(bar(i), end='', flush=True)
            sleep(.02)         # "Uh-Uhn"
        print()

        # how to use with a trailing caption:
        for i in items:
            print(bar(i), f' copying: /path/to/img_{i:>04}.jpg',
                  end='', flush=True)
            sleep(.05)
        print()

        # or use as a simple tqdm-style iterable wrapper, sans print
        for i in ProgressBar(range(100)):
            sleep(.05)



Not all of this code is required, of course.
For example, you may not want to hide the cursor or clear the line each time,
but often will.
To expand to the full line,
``expand=True`` is available as well.
See the docs (:mod:`console.progress`) and source for more details.


Experimental Stuff
-------------------

    *“Well, kiss my grits!”—Flo*


Hyperlinks
~~~~~~~~~~~~~~~~~~~

Real hyperlinks in the terminal, eh?
Sounds cool.
This feature is experimental and more information can be
`found here. <https://gist.github.com/egmontkob/eb114294efbcd5adb1944c9f3cb5feda>`_

.. code-block:: python

    >>> from console.utils import make_hyperlink

    >>> make_hyperlink('ftp://netscape.com/', 'Blast from the FUTURE!')
    '\x1b]8;;ftp://netscape.com/\x1b\\Blast from the FUTURE!\x1b]8;;\x1b\\'

    >>> print(_)

.. raw:: html

    <pre style="margin-top: -13px; border-radius: 0 0 1em 1em;">
    <a style="border-bottom: 1px dashed" href="ftp://netscape.com/">Blast from the FUTURE!</a>
    </pre>


Underline Hijinks
~~~~~~~~~~~~~~~~~~~

Curly, dunder, and/or colored underlines are supported in a few terminals now,
in addition to the standard ``fx.u(…)``:

.. code-block:: python

    >>> from console import fx, ul

    >>> bad_grammar = fx.curly_underline + ul.i2
    >>> bad_spelling = fx.curly_underline + ul.i1

    >>> print('I', bad_grammar('not'), bad_spelling('mizpelled.'))

.. raw:: html

    <pre style="margin-top: -13px; border-radius: 0 0 1em 1em;">
    I <span style="text-decoration: underline wavy green">not</span> <span style="text-decoration: underline wavy red">mizpelled.</span>
    </pre>

.. code-block:: python

    >>> print(fx.dunder, ul.goldenrod('WOOT!'), sep='')  # X, Webcolors

.. raw:: html

    <pre style="margin-top: -13px; border-radius: 0 0 1em 1em;">
    <span style="border-bottom: 3px double goldenrod">WOOT!</span>
    </pre>


HTML Viewers
~~~~~~~~~~~~~~~~~~~

Would you like to print some rich text to the terminal,
but would rather put styles inline and not have to fiddle with objects?
Maybe you have some existing HTML laying around?

.. code-block:: python

    >>> from console.viewers import hprint as print
    >>> print(html_doc)


The HTML Printer function takes the same parameters as the standard ``print``
function.
For example,
output can be saved to a file by passing a ``file=`` parameter.
It implements a small subset of tags that makes sense in the terminal,
but has quite a few features,
collapses whitespace,
and converts entities:

- a *(see above)*
- br *(+newline)*
- b, strong
- blockquote
- hr *(+newlines)*
- h1, h2, h3 *(+newlines)*
- i, em
- p *(+newlines)*
- q "fancy quotes"
- span
- s, strike
- u
- ul, ol, li

It handles a few inline style attributes as well:

.. code-block:: html

    <span style="color: red">text</span>
    <span style=background:green>text</span>
    <span style="font-style:italic; font-weight:bold">text</span>
    <span style="text-decoration:overline; text-decoration:underline">…

As you can see,
setting text color is *very* verbose,
so you guessed it,
I unfortunately broke down and implemented a concise ``c`` tag for color.
Like the inline-CSS above,
it handles X11 or Webcolors (if installed) color names, hex digits,
and the word "dim":

.. code-block:: plain

    <c orange>l'orange</c>
    <c black on bisque3>bisque3</c>
    <c #b0b>deadbeefcafe</c>
    <c dim>text</c>


.. rubric:: Viewing a file

Viewing an html file on the terminal is also available with the
``viewers.view(filename)`` function
or via command-line (see below).


Context Managers
~~~~~~~~~~~~~~~~~~~

.. rubric:: Configuring Output

Console's Palette Entry objects can be used as context managers as well.
We saw this in the readme previously.
An output file may also be set if it needs to be changed from stdout and not
able to be redirected outside the process:

.. code-block:: python

    Dodgers = bg.dodgerblue + fx.bold
    Dodgers.set_output(sys.stderr)

    with Dodgers:
        print('Infield: Garvey, Lopes, Russel, Cey, Yeager')
        print('Outfield: Baker, Monday, Smith')

(This feature is experimental for now. ;-)


.. rubric:: Fullscreen Apps, a la Blessings

Here's a short script to show off console's full-screen abilities:

.. code-block:: python

    from console import fg, fx, defx
    from console.screen import Screen
    from console.utils import wait_key, set_title
    from console.constants import ESC

    exit_keys = (ESC, 'q', 'Q')

    with Screen() as screen:  # or screen.fullscreen():

        set_title(' 🤓 Hi, from console!')
        with screen.location(5, 4):
            print(
                fg.lightgreen('** Hi from a '
                              f'{fx.i}fullscreen{defx.i} app! **'),
                screen.move_x(5),  # back up, then down
                screen.move_down(5),
                fg.yellow(f'(Hit the {fx.reverse("ESC")} key to exit): '),
                end='', flush=True,  # optional
            )

        with screen.hidden_cursor():
            wait_key(exit_keys)

The text below should appear.
Check the title too!
After hitting the ESC key your terminal shall be restored:

.. raw:: html

    <pre>

    <div style="color: green; ">
     * Hi, from a <i>fullscreen</i> app! **
    </div>



    <div style="color: #ba0; ">
      (Hit the <span style="background: #ba0; color: black">ESC</span> key to exit):
    </div>
    </pre>


.. rubric:: TermStack

TermStack is a content-manager for making temporary modifications to the
terminal via termios,
that copies the original settings and restores them when finished.

It's in the detection module because that's where it's used often,
but also aliased to the package namespace.
For example:

.. code-block:: python

    import tty, termios
    from console import TermStack
    from console.constants import CSI

    with TermStack() as fd:
        tty.setcbreak(fd, termios.TCSANOW)  # echo off
        sys.stdout.write(f'{CSI}6n')  # do something
        sys.stdout.flush()

    # Back to normal

And off you go.


Command-line
-------------------

There is now a console command-line script for use interactively and
shell-scripts,
all sub-commands support help ``-h`` and verbose ``-v``:

.. code-block:: shell

    ⏵ console  # help and show all available sub-command actions
    …

    ⏵ console line  # print a nifty full-width line, such as:
    ──────────────────────────────────────────────────────

    # make a ctrl-clickable link in supporting terminals
    ⏵ console link http://example.com/ "Klicken-Sie hier!"
    Klicken-Sie hier!

    ⏵ console ascii         # A four-column chart, -l for links!
    ⏵ console beep          # bidi-bidi-bidi…
    ⏵ console detect [-v]   # prints term level and environ. info
    ⏵ console flash         # Bam!
    ⏵ console pause         # Press any key to continue…
    ⏵ console progress      # show a progress bar
    ⏵ console view [file]   # view a file, e.g.: foo.html

And more.
You can also run several console modules for information and other
functionality:

.. code-block:: shell

    ⏵ python3 -m console.constants  # ANSI constants available

    # demos
    ⏵ python3 -m console.demos [-d]
    ⏵ python3 -m console.viewers  # more demos

    ⏵ python3 -m console.progress -l  # demo with labels

    # ANSI constants in Python syntax can be printed via:
    ⏵ python3 -m console.constants
    CSI = '\x1b['
    ESC = '\x1b'
    LF = '\n'
    OSC = '\x1b]'
    ST = '\x1b\\'
    VT = '\x0b'
    # etc…


``-d`` often enables ``DEBUG`` logging.
The ``3`` at the end of ``python3`` may not be necessary,
e.g. on Windows or Arch Linux.


Tips
------------

    | *"Easy Miss, I’ve got you."*
    | *"You’ve got ME? Who’s got YOU?"—Superman*

- The styles bold, italic, underline, and strike have one-letter shortcuts as
  they do in HTML,
  if you're into that sort of thing::

    # COWABUNGA, DUDE !
    XTREME_STYLING = fx.b + fx.i + fx.u + fx.s

- When using the extended or truecolor palettes,
  keep in mind that some folks will have dark backgrounds and some light---\
  which could make your fancy colors unreadable.

  Make two themes preferably and check the background via
  ``detection.get_theme()``.
  This is one strategy,
  though not available on every terminal.
  An application argument to change the theme may also be in order.
  (Console does recognize several environment variables like ``COLORFGBG``
  as well.)

- X11 color names may be searched with this command:

  .. code-block:: shell

        ⏵ python3 -m console.color_tables_x11 darkorange
        darkorange (255, 140, 0)
        darkorange1 (255, 127, 0)
        darkorange2 (238, 118, 0)
        darkorange3 (205, 102, 0)
        darkorange4 (139, 69, 0)

- ANSI support may be enabled on Windows 10 legacy console via the following
  incantation:

  .. code-block:: python

    >>> import console.windows as cw

    >>> cw.enable_vt_processing()  # status for (stdout, stderr)
    (0, 0)


Troubleshooting
------------------

    *"Goddammit, I'd piss on a spark plug if I thought it'd do any good!"—General Beringer*

- Console performs auto-detection of the environment at startup to determine
  terminal capabilities.

  - If you'd like to see, check the results with this command:

    .. code-block:: shell

            ⏵ python -m console.detection

  - Note: This could *momentarily* hang obscure terminals that advertise xterm
    on posix compatibility without a full implementation.
    To disable this,
    set the environment variable:
    ``PY_CONSOLE_AUTODETECT='0'``.
    Unfortunately,
    you'll now have to create the palette and screen objects
    (and possibly configure them)
    yourself.

- Another way to do the same thing in your own program.

  If console isn't working as you'd expect,
  turn on DEBUG logging before loading it to see what it finds.
  A sample script is below::

    # load logging first to see all messages:
    import logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='  %(levelname)-7.7s %(module)s/'
               '%(funcName)s:%(lineno)s %(message)s',
    )

    # now logs autodetection messages:
    from console import fg, bg, fx

    # After an accidental overdose of gamma radiation…
    dr_banner = fg.green + fx.bold + fx.italic

    print('\n\t',
          dr_banner("Mr. McGee, don't make me angry…"),
    )


- Try to avoid this type of ambiguous addition operation:

  .. code-block:: python

    fg.white + bg.red('Hello\nWorld')

  Why is it ambiguous?
  Well, the left operand is a palette entry object,
  while the second reduces to an ANSI escaped string.
  Did you mean to add a sequence just to the beginning of the string,
  or every line of it?
  Remember paging?
  Also, what about the ending sequence?
  Should it reset the foreground, background, styles, or everything?
  Hard to know because there's not enough information here to decide.

  Console warns you about this.
  It also does its best to divvy up the second object (string),
  add the first operand to every line,
  and fix the reset-to-default sequence at the end.
  So it *might* work as expected,
  possibly not.
  It's not very efficient either.
  Best to use one of these explicit forms instead:

  .. code-block:: python

    # create a new anonymous style, apply it:
    (pal.style1 + pal.style2)(msg)

    # or add it in via a "mixin" style
    pal.style2(msg, pal.style1)

You could also wrap it around,
in call form,
but these will be more efficient.

Deeper Dive
------------

    *"I'm so confused."—‘Vinnie' Barbarino*

Still interested?
More than you wanted to know on the subject of terminals and escape codes can
be found below:

    - `Terminal Emulator <https://en.wikipedia.org/wiki/Terminal_emulator>`_
    - `ANSI Escape Codes <http://en.wikipedia.org/wiki/ANSI_escape_code>`_
    - `XTerm Control Sequences
      <http://invisible-island.net/xterm/ctlseqs/ctlseqs.html>`_
      (`PDF <https://www.x.org/docs/xterm/ctlseqs.pdf>`_)
    - `ANSI Terminal Animations
      <http://artscene.textfiles.com/vt100/>`_ - Get busy!
    - :mod:`console` source code

.. rubric:: Aside - Warm Colors

Did you know that thirty+ years before
`f.lux <https://en.wikipedia.org/wiki/F.lux>`_
and
`redshift <https://en.wikipedia.org/wiki/Redshift_(software)>`_
debuted that
`Amber Monochrome monitors <https://www.google.com/search?q=amber+monochrome+monitor&tbm=isch>`_
with a dark background were known as the
*"ergonomic choice?"*  ``;-)``

Easier on the eyes for extended periods (i.e. late nights) they said.
Interesting knowledge rediscovered perhaps.

.. container:: center mfull italic flright

    "Believe it…

    or not!"

    .. ~ ---Jack Palance, on `Ripley's <https://youtu.be/o4ELw6kCEDs>`_
        .. ~ allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture"

    ---Jack Palance, on `Ripley's <https://youtu.be/HVT3kOxqStA>`_

.. raw:: html

    <iframe width="50%" height="auto" frameborder="0" class="mt mb"
        src="https://www.youtube.com/embed/HVT3kOxqStA"
        allowfullscreen>
    </iframe>

|

10-7, Signing Off…
--------------------

.. raw:: html

    <pre class=center>
       ♫♪ .ılılıll |̲̅̅●̲̅̅|̲̅̅=̲̅̅|̲̅̅●̲̅̅| llılılı. ♫♪&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
    </pre>


.. figure:: _static/bjandbear.jpg
    :align: right
    :figwidth: 40%

    *"I'm B. J. McKay,*
    *and this is my best friend Bear."*
    `🖺 <https://www.memorabletv.com/tv/b-j-bear-nbc-1979-1981-greg-evigan-claude-akins/>`_
    `🖹 <http://www.lyricsondemand.com/tvthemes/bjandthebearlyrics.html>`_

|

Signing off from late '79.
A new futuristic decade awaits,
with an actor as President!

    - *Keep On Truckin'*
    - *Catch you on the flip-side!*
    - *"This is Ripley, last survivor of the Nostromo, signing off."*
    - *Good night, John-boy*

    and…

    - *Whoah-oh Woah…*

            `Goodbye Seventies… <https://www.youtube.com/watch?v=yFimHGt2Nco>`_

|br-all|


.. raw:: html

    <pre class=center>
    ¸¸.·´¯`·.¸¸.·´¯`·.¸¸.·´¯`·.¸¸.·´¯`·.¸¸¸.·´¯`·.¸¸¸
    </pre>


|br-all|


.. raw:: html


    <div id=source style="display: none">Joshua


    ​​​​​​​​​Greetings, Professor Falken.

    Would you like to play a game?


    ​​​​​​⏵ How about​​ Global Thermo​​nuclear​​ War?

    ​​​​​​​​​​Wouldn't you prefer a nice game of chess?


    ​​​​​​⏵ Later.​​ Right now​ let's play​​​​ Global​ Thermo​​nuclear​​ War.

    ​​​​​​​​​​Fine…
    </div>

    <pre id=dest style="color: #6bc; background: #111; min-height: 26em">
    LOGON: </pre>

    <script type="text/javascript">
        let i = 0;
        let source = document.getElementById("source").innerHTML;
        let speed = 100; // ms
        let dest = document.getElementById("dest");

        function type_writer() {
            if (i < source.length) {
                dest.append(source.charAt(i));
                i++;
                setTimeout(type_writer, speed);
            } else {
                 document.getElementById("connect_but").disabled = false;
            }
        }
    </script>
    <button
        id="connect_but" stylez="margin: 0 auto; display: block;"
        onclick="type_writer(); this.disabled = true;"
    > 🖳 Connect Terminal </button>


|br-all|
