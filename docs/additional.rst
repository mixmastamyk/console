
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

    <div class=center>
    ·····•·····
    <span id=pac>ᗤ</span>&nbsp;
    <span id=sha>ᗣ</span><span id=spe>ᗣ</span>
    <span id=bas>ᗣ</span><span id=pok>ᗣ</span><br>

    <i style="opacity: .7">waka waka waka</i>
    </div>

    <div class=center style="padding: .6em">
        <i>Can You Dig It?</i><br><br>
    </div>


Additional Topics
=======================

.. rubric:: How does it work?

Behind the scenes in
:mod:`console.core`
you've been working with two main parent classes:

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
The cache may also be cleared in uncommon scenarios using huge palettes.

.. rubric:: Palette Entries:

These entries,
accessed as attributes of a Palette collection, e.g.:

    - ``.red``
    - ``.i22``
    - ``.w_cornflowerblue``

are objects that provide much of the functionality in
:mod:`console.style`:

    - They keep track of their own ANSI codes and those they've been added to.
    - They can be called and "mixed in" with other attributes to render
      themselves.
    - They can be used as a context-manager.
    - Last but not least,
      they can be rendered as an escape sequence string on any form of output.

Similar functionality is available from
:mod:`console.screen`.


.. rubric:: Automatic Detection

When automatic detection is used and palettes are found to not be supported,
palette entries are replaced instead with "dummy" blank objects that render to
nothing.
Well, more specifically empty strings.


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



Context Managers
-------------------

Console's Palette Entry objects can be used as context managers as well.
We saw this in the readme previously::

    with bg.w_dodgerblue:
        print('Infield: Garvey, Lopes, Russel, Cey, Yeager')
        print('Outfield: Baker, Monday, Smith')

I've not quite gotten around to figure the best way to pass arguments.

.. rubric:: Configuring Output

On init, you can use an ``out`` param that will be saved to ``._out``
and is used by the context manager.
Defaults to printing to stdout.

.. rubric:: TermStack

TermStack is a content-manager for making temporary modifications to the
terminal via termios,
that will copy the original settings then restore then when finished.

For example::

    with TermStack() as fd:

        tty.setcbreak(fd, termios.TCSANOW)  # shut off echo
        sys.stdout.write(f'{CSI}6n')
        sys.stdout.flush()
















::

    °º¤ø,¸¸,ø¤º°`°º¤ø,¸,ø¤°º¤ø,¸¸,ø¤º°`°º¤ø,¸



    ¯`·.¸¸.·´¯`·.¸¸.·´¯`·.¸¸.·´¯`·.¸¸



*Get down, boogie oogie oogie*
- outta sight!

- Jive Turkey

- What's happenin'

- Dynomite!


.. rubric:: Warm Colors

Did you know that thirty years before
`f.lux <https://en.wikipedia.org/wiki/F.lux>`_
and
`redshift <https://en.wikipedia.org/wiki/Redshift_(software)>`_
debuted that Amber Monochrome monitors where known as the "ergonomic"
choice?
Easier on the eyes for extended periods (late nights) they said.

Perhaps knowledge rediscovered.




Deeper Dive
------------

More than you wanted to know on the subject or terminals and escape codes can
be found below:

    - `Terminal Emulator <https://en.wikipedia.org/wiki/Terminal_emulator>`_
    - `ANSI Escape Codes <http://en.wikipedia.org/wiki/ANSI_escape_code>`_
    - `XTerm Control Sequences
      <http://invisible-island.net/xterm/ctlseqs/ctlseqs.html>`_
      (`PDF <https://www.x.org/docs/xterm/ctlseqs.pdf>`_)


.. raw:: html

    <pre class=center>
       ♫♪ .ılılıll|̲̅̅●̲̅̅|̲̅̅=̲̅̅|̲̅̅●̲̅̅|llılılı. ♫♪&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
    </pre>

.. figure:: _static/bjandbear.jpg
    :align: right
    :figwidth: 30%

    *"I'm B. J. McKay and this is my best friend Bear."*

10-7, Signing Off…
--------------------


..

asdf

    - *Catch you on the flip-side*
    - *Keep On Truckin'*
    - *Good night, John-boy*
    - *Any other good seventies expressions?*


asdf



- http://www.lyricsondemand.com/tvthemes/bjandthebearlyrics.html
- https://www.memorabletv.com/tv/b-j-bear-nbc-1979-1981-greg-evigan-claude-akins/
