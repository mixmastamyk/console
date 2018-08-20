
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

|

Additional Topics
=======================

.. rubric:: How do the styles work?

Behind the scenes in
:mod:`console.core`
you've been working with two main parent classes of those in
:mod:`console.style`:

.. rubric:: Palette Builders:

A collection object holding a large number of Palettes and their associated
Entries, e.g.:

    - ``fg``, ``bg``, ``fx``
    - ``defx`` (for deactivating styles)

While the simplest entries are created up front,
the rest are built on demand.
Like a traffic cop,
builders direct attribute access to the appropriate code to initialize them.

Once created,
attributes are cached and available for future use.
The namespace cache may also be cleared in uncommon scenarios using huge
palettes.

.. rubric:: Palette Entries:

These entries,
accessed as attributes of a Palette collection, e.g.:

    - ``.red``
    - ``.i22``
    - ``.w_cornflowerblue``

…are objects that provide much of the functionality from
:mod:`console.style`.
The entries:

    - Keep track of their ANSI codes and those they've been added to.
    - Can be called, "mixed in" with other attributes to render
      themselves and end the style.
    - Can be used as a context-manager.
    - Last but not least,
      can be rendered as an escape sequence string on any form of output.

Similar functionality is available from
:mod:`console.screen`.


.. rubric:: Automatic Detection

When automatic detection is used and palettes are found to not be supported,
palette entries are replaced instead with "dummy" blank objects that render to
nothing.
Well, more specifically empty strings.


.. raw:: html

    <div class=center>
    ·····•·····
    <span id=pac>ᗤ</span>&nbsp;
    <span id=sha>ᗣ</span><span id=spe>ᗣ</span>
    <span id=bas>ᗣ</span><span id=pok>ᗣ</span>&nbsp;&nbsp;&nbsp;&nbsp;<br>

    <i style="opacity: .7">waka waka waka</i>&nbsp;&nbsp;&nbsp;&nbsp;
    </div>


Initializing your Own
------------------------


To control the palette support of an object you can create them yourself::

    from console.style import (BackgroundPalette,
                               ALL_PALETTES)
    # force all palettes on
    fullbg = BackgroundPalette(autodetect=False,
                               palettes=ALL_PALETTES)


.. note::

    Forcing the support of all palettes ON can also be done with an environment
    variable,
    such as ``CLICOLOR_FORCE`` if desired.


*Can You Dig It?*

::

    ¸,ø¤º°`°º¤ø,¸¸,ø¤º°`°º¤ø,¸,ø¤°º¤ø,¸¸,ø¤º°`°º¤ø,¸



Context Managers
-------------------

    *What's Happening, "Raj" !!*

.. rubric:: Configuring Output

Console's Entry objects can be used as context managers as well.
We saw this in the readme previously.
An output file can be set if it needs to be changed from stdout::

    dodgers = bg.w_dodgerblue
    dodgers.set_output(sys.stderr)

    with dodgers:
        print('Infield: Garvey, Lopes, Russel, Cey, Yeager')
        print('Outfield: Baker, Monday, Smith')

There may be a way to streamline this in the future.
(So, don't get too dependent on the set_output function.)


.. rubric:: TermStack

TermStack is a content-manager for making temporary modifications to the
terminal via termios,
that copies the original settings and restores them when finished.

It's in the detection module because that's where it's used,
but is copied to the package namespace.
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

blah_blah_blah




Tips
------------

Don't have many to list yet,
but there's at least one.

- Styles bold, italic, and underline have one-letter shortcuts as does HTML,
  if you're into that sort of thing::

    XTREME_STYLING = fx.b + fx.i + fx.u


Deeper Dive
------------

    *Get down, boogie oogie oogie…*

Still interested?
More than you wanted to know on the subject or terminals and escape codes can
be found below:

    - `Terminal Emulator <https://en.wikipedia.org/wiki/Terminal_emulator>`_
    - `ANSI Escape Codes <http://en.wikipedia.org/wiki/ANSI_escape_code>`_
    - `XTerm Control Sequences
      <http://invisible-island.net/xterm/ctlseqs/ctlseqs.html>`_
      (`PDF <https://www.x.org/docs/xterm/ctlseqs.pdf>`_)


.. rubric:: Warm Colors

Did you know that thirty years before
`f.lux <https://en.wikipedia.org/wiki/F.lux>`_
and
`redshift <https://en.wikipedia.org/wiki/Redshift_(software)>`_
debuted that Amber Monochrome monitors where known as the "ergonomic"
choice?
Easier on the eyes for extended periods (i.e. late nights) they said.

Interesting, knowledge rediscovered?


.. raw:: html

    <pre class=center>
       ♫♪ .ılılıll|̲̅̅●̲̅̅|̲̅̅=̲̅̅|̲̅̅●̲̅̅|llılılı. ♫♪&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
    </pre>



10-7, Signing Off…
--------------------

.. figure:: _static/bjandbear.jpg
    :align: right
    :figwidth: 33%

    *"I'm B. J. McKay and this is my best friend Bear."*
    `🖺 <https://www.memorabletv.com/tv/b-j-bear-nbc-1979-1981-greg-evigan-claude-akins/>`_
    `🖹 <http://www.lyricsondemand.com/tvthemes/bjandthebearlyrics.html>`_

|

    - *Keep On Truckin'*
    - *Catch you on the flip-side*
    - *Good night, John-boy*
    - *Goodbye Seventies*

.. raw:: html

    <br clear=all>
