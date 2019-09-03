
.. role:: reverse
   :class: reverse

.. raw:: html

    <pre id='logo' class='center'>
    <span style="color:#729fcf">&#9484;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;</span><span style="color:#3465a4">&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9488;</span>
    <span style="color:#729fcf">&#9474;</span>&#160;&#160;&#160;<span style="color:#729fcf">&#9487;&#9473;&#9592;&#9487;</span><span style="color:#3465a4">&#9473;&#9491;&#9487;&#9491;&#9595;&#9487;&#9473;&#9491;&#9487;&#9473;&#9491;&#9595;</span>&#160;&#160;</span><span style="color:#3465a4">&#9487;&#9473;</span><span style="color:#b4b8b0">&#9592;</span>&#160;&#160;&#160;<span style="color:#b4b8b0">&#9474;</span>
    <span style="color:#3465a4">&#9474;</span>&#160;&#160;&#160;<span style="color:#3465a4">&#9475;</span>&#160;&#160;</span><span style="color:#3465a4">&#9475;</span>&#160;</span><span style="color:#3465a4">&#9475;&#9475;&#9495;&#9515;&#9495;&#9473;&#9491;</span><span style="color:#b4b8b0">&#9475;</span>&#160;</span><span style="color:#b4b8b0">&#9475;&#9475;</span>&#160;&#160;<span style="color:#b4b8b0">&#9507;&#9592;</span>&#160;&#160;&#160;&#160;</span><span style="color:#b4b8b0">&#9474;</span>
    <span style="color:#3465a4">&#9474;</span>&#160;&#160;&#160;<span style="color:#3465a4">&#9495;&#9473;&#9592;&#9495;</span><span style="color:#b4b8b0">&#9473;&#9499;&#9593;</span>&#160;</span><span style="color:#b4b8b0">&#9593;&#9495;&#9473;&#9499;&#9495;&#9473;&#9499;&#9495;&#9473;&#9592;&#9495;&#9473;</span><span style="color:#555">&#9592;</span>&#160;&#160;&#160;<span style="color:#555">&#9474;</span>
    <span style="color:#b4b8b0">&#9492;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;</span><span style="color:#555">&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9496;</span>
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

.. rubric:: How do the styles work?

Behind the scenes in
:mod:`console.core`
you've been working with the two main parent classes of those in
:mod:`console.style`:

.. rubric:: Palette Collection:

A collection object holding a large number of Palettes and their associated
Entries, e.g.:

    - ``fg``, ``bg``, ``fx``
    - ``defx`` (for deactivating styles)

While the simplest palettes
(original and effects)
are created up front,
the rest are built up as needed,
on demand.
Like a traffic cop,
palettes direct attribute access to the appropriate code to initialize each
Entry.

Once created,
Entry attributes are cached and available for future use.
This namespace cache may also be cleared in uncommon scenarios using huge
palettes,
with the ``clear()`` method.

.. rubric:: Palette Entries:

Entry objects are what actually produce the escape sequences---\
they are accessed as attributes of a palette collection, e.g.:

    - ``.red``
    - ``.i22``
    - ``.cornflowerblue``

The Entries provide much of the functionality.  They

    - Keep track of their ANSI codes and those they've been added to.
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

    *Can You Dig It?*

.. rubric:: Environment Variables

On rare posix terminals color detection may hang and need to be disabled.

To disable automatic detection of terminal capabilities at import time the
environment variable
``PY_CONSOLE_AUTODETECT`` may be set to ``0``.
Writing a bug at the console repo would help also.

Forcing the support of all palettes ON can also be done externally with an
environment variable,
such as ``CLICOLOR_FORCE``,
if desired.


.. rubric:: Initializing Your Own

To configure auto-detection, palette support,
or detect other output streams besides stdout,
one may create palette builder objects yourself:

::

    ⏵ env PY_CONSOLE_AUTODETECT='0' script.py

.. code-block:: python

    from console.constants import ALL_PALETTES
    from console.style import BackgroundPalette

    # e.g. force all palettes on:
    fullbg = BackgroundPalette(palettes=ALL_PALETTES)



Palette Downgrade
----------------------

When using true or extended colors on a terminal that is not configured to
support it,
console will "downgrade" the colors to their nearest neighbors in the available
palette.

Neat, huh?
It does this using a Euclidian 3D distance method which is quite fast but only
somewhat accurate,
due to the fact that the RGB color space is not uniform.

That lead to some experimentation with
`CIEDE2000 <https://en.wikipedia.org/wiki/Color_difference#CIEDE2000>`_
libraries like colormath and colorzero.
Unfortunately they were both heavy and slow as molasses,
even with numpy loaded,
which is also slow to import.

Fast and inaccurate it is!
Unless someone would like to write a highly optimized C implementation for kicks,
it doesn't seem worth the trouble for this application.

::

    ¸¸,ø¤º°`°º¤ø,¸¸,ø¤º°`°º¤ø,¸,ø¤°º¤ø,¸¸,ø¤º°`°º¤ø,¸¸



Context Managers
-------------------

    *"I hope you know this violates my warranty!" — Twiki*

.. rubric:: Configuring Output

Console's Palette Entry objects can be used as context managers as well.
We saw this in the readme previously.
An output file may also be set if it needs to be changed from stdout and not
able to be redirected outside the process::

    dodgers = bg.w_dodgerblue
    dodgers.set_output(sys.stderr)

    with dodgers:
        print('Infield: Garvey, Lopes, Russel, Cey, Yeager')
        print('Outfield: Baker, Monday, Smith')

(This feature is somewhat experimental for now. ;-)


.. rubric:: Fullscreen Apps, a la Blessings

Here's a short script to show off console's full-screen abilities::

    from console import fg, fx, defx
    from console.screen import sc as screen
    from console.utils import wait_key, set_title
    from console.constants import ESC

    exit_keys = (ESC, 'q', 'Q')

    with screen:  # or screen.fullscreen():

        set_title(' 🤓 Hi, from console!')
        with screen.location(5, 4):
            print(
                fg.lightgreen('** Hi from a '
                              f'{fx.i}fullscreen{defx.i} app! **'),
                screen.mv_x(5),  # back up, then down
                screen.down(5),
                fg.yellow(f'(Hit the {fx.reverse}ESC{defx.reverse}'
                           ' key to exit): '),
                end='', flush=True,
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

It's in the detection module because that's where it's used,
but also aliased to the package namespace.
For example::

    from console import TermStack

    with TermStack() as fd:
        # shut off echo
        tty.setcbreak(fd, termios.TCSANOW)
        sys.stdout.write(f'{CSI}6n')  # fire!
        sys.stdout.flush()

And off you go.


Screen Stuff
-------------------

    *What's Happening, "Raj" !?!*

The :mod:`console.screen` module is the one you're looking for,
although there is a preconfigured convenience instance in the root of the
package as well::

    >>> from console import sc

    >>> sc.eraseline(1)  # mode 1, clear to left
    '\x1b[1K'

    >>> print('already deleted!', sc.eraseline(1))

    >>>  # this space intentionally left blank ;-)


Progress Bars
-------------------

A progress bar implementation is located in :mod:`console.progress` and may be
demoed thusly:

.. code-block:: shell

    ⏵ python3 -m console.progress -l


There are multiple themes,
but typical use of the module is achieved like so::

    import time

    from console.screen import sc
    from console.utils import clear_line
    from console.progress import ProgressBar

    with sc.hidden_cursor():
        bar = ProgressBar()

        for i in range(0, 101):
            print(clear_line(1), sc.mv_x(1), bar(i),
                  flush=True, end='')
            time.sleep(.2)
        print()

Not all of this code is required, of course.
For example, you may not want to hide the cursor or clear the line each time,
but often will.
There is also a ``HiDefProgressBar`` class that can render itself with sub-cell
unicode block characters for environments with constrained space.



Tips
------------

Not many to list yet,
but here's a couple.

- The styles bold, italic, underline, and strike have one-letter shortcuts as
  they do in HTML,
  if you're into that sort of thing::

    # COWABUNGA, DUDE !
    XTREME_STYLING = fx.b + fx.i + fx.u + fx.s

- When using the extended or truecolor palettes,
  keep in mind that some folks will have dark backgrounds and some light---\
  which could make your fancy colors unreadable.

  Checking the background with the detection module is one strategy,
  though not available on every terminal.
  An argument to change the theme may also be in order.
  (Console does acknowledge several environment variables like ``COLORFGBG``
  as well.)

- ANSI support can be enabled on Windows 10 with the following incantation::

    >>> import console.windows as cw

    >>> cw.enable_vt_processing()
    (0, 0)  # status for (stdout, stderr)



Deeper Dive
------------

    *Get down, boogie oogie oogie…---A Taste of Honey*

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

Did you know that thirty years before
`f.lux <https://en.wikipedia.org/wiki/F.lux>`_
and
`redshift <https://en.wikipedia.org/wiki/Redshift_(software)>`_
debuted that Amber Monochrome monitors where known as the "ergonomic"
choice?
Easier on the eyes for extended periods (i.e. late nights) they said.
Interesting knowledge rediscovered, perhaps.

.. container:: center mt mb

    *"Believe it…*

    *or not!"*

    *---Jack Palance, on Ripley's*


10-7, Signing Off…
--------------------

.. raw:: html

    <pre class=center>
       ♫♪ .ılılıll|̲̅̅●̲̅̅|̲̅̅=̲̅̅|̲̅̅●̲̅̅|llılılı. ♫♪&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
    </pre>


.. figure:: _static/bjandbear.jpg
    :align: right
    :figwidth: 33%

    *"I'm B. J. McKay and this is my best friend Bear."*\
    `🖺 <https://www.memorabletv.com/tv/b-j-bear-nbc-1979-1981-greg-evigan-claude-akins/>`_\
    `🖹 <http://www.lyricsondemand.com/tvthemes/bjandthebearlyrics.html>`_

|

    - *Keep On Truckin'*
    - *Catch you on the flip-side*
    - *Good night, John-boy*
    - and… *Goodbye Seventies*


.. raw:: html

    <br clear=all>
