
.. raw:: html

    <pre id='logo' class='center'>
    <span style="color:#729fcf">&#9484;───────────────</span><span style="color:#3465a4">────────────&#9488;</span>
    <span style="color:#729fcf">│</span>   <span style="color:#729fcf">&#9487;&#9473;&#9592;&#9487;</span><span style="color:#3465a4">&#9473;&#9491;&#9487;&#9491;&#9595;&#9487;&#9473;&#9491;&#9487;&#9473;&#9491;&#9595;</span>  </span><span style="color:#3465a4">&#9487;&#9473;</span><span style="color:#b4b8b0">&#9592;</span>   <span style="color:#b4b8b0">│</span>
    <span style="color:#3465a4">│</span>   <span style="color:#3465a4">&#9475;</span>  </span><span style="color:#3465a4">&#9475;</span> </span><span style="color:#3465a4">&#9475;&#9475;&#9495;&#9515;&#9495;&#9473;&#9491;</span><span style="color:#b4b8b0">&#9475;</span> </span><span style="color:#b4b8b0">&#9475;&#9475;</span>  <span style="color:#b4b8b0">&#9507;&#9592;</span>    </span><span style="color:#b4b8b0">│</span>
    <span style="color:#3465a4">│</span>   <span style="color:#3465a4">&#9495;&#9473;&#9592;&#9495;</span><span style="color:#b4b8b0">&#9473;&#9499;&#9593;</span> </span><span style="color:#b4b8b0">&#9593;&#9495;&#9473;&#9499;&#9495;&#9473;&#9499;&#9495;&#9473;&#9592;&#9495;&#9473;</span><span style="color:#555">&#9592;</span>   <span style="color:#555">│</span>
    <span style="color:#b4b8b0">&#9492;───────────────</span><span style="color:#555">────────────&#9496;</span>
    </pre>

.. container:: center

    | *"In your satin tights,*
    | *fighting for your rights,*
    | *and the old red, white, and blue…"*
    | *—Wonder Woman theme*

|

Another One, eh 🤔?
=======================

    *"First I was afraid, I was petrified…"—Gloria Gaynor*

.. raw:: html


    <pre class=center>
     ▏
    ⸝<><><>⸜
    <>✶><><><><>
    <><><><><><✦<>
    (<><><><><><><>)
    <><><><><><><>
    .  <>✶><><><><> .
    : .   `<><><>´    .:
     ::            .      ⭒:
    .⭒.      .       .     .:.
    .:.      .         ⭒     : .
    .: :     :          .      ::.
    .:  :     ⭒           .:     .⭒ :
    :⭒. :      .              :      : ..
    . .                         .      .  .
    </pre>


Background
---------------

    *"CHARLIE DON'T SURF!"—Lt. Col. Kilgore*

So ANSI escape codes for terminals have been standard on UNIX
with the belt-and-suspenders crowd since the late seventies,
and even saw use on DOS, the Amiga, and BBSs back in the day.
With the advent of macOS X (ten),
a whole new generation of lumber-sexuals have exposed themselves(?)
to the terminal environment and command-line
*and liked it*.
 🤔

.. figure:: _static/dilbert_95-06-24.png
    :align: center
    :figwidth: 80%

    Dilbert, on `1995-06-24 <https://dilbert.com/strip/1995-06-24>`_


"I'm a PC"
~~~~~~~~~~~~~~

    *“Oooh! Oooh! Oooh!”—Arnold Horshack*\
    `† <https://www.vulture.com/2012/08/why-welcome-back-kotters-horshack-mattered.html>`_

Not on Windows NT, tho'.
Amazingly,
with recent versions of Windows 10
the Ballmer/Suit barrier was finally breached,
allowing *multi-decade-late*
`improvements
<https://devblogs.microsoft.com/commandline/windows-10-creators-update-whats-new-in-bashwsl-windows-console/>`_
to be made to its until-now pathetic "console."
Often still known as the "DOS Prompt" since it has been frozen that long.
Vaguely analogous to today's virtual terminals,
as a Yugo might compare to a classic BMW.
But now, it's supercharged with VT power.

So, now all the top/extant platforms support ANSI escape sequences.
Again!
What's old is new again.
Add in Unicode and millions of colors and it's now better than ever.

We need great command-line/TUI tools and that's where ``console`` fits in.

.. container:: center

    *That's the way, uhh huh, uhh huh, I like it…*

.. figure:: _static/kc3.png
    :align: center
    :figwidth: 60%

    (Cue
    `KC and the Sunshine Band,
    <https://www.youtube.com/watch?v=R9DjX6JBpHI>`_
    *uhh-huh, uhh-huh*
    on
    Soul Train…)


Batteries Not Included
------------------------

    *"What'chu talkin' 'bout, Willis?"—Arnold Jackson*

In the Python world,
there hasn't been easy-to-use support for terminal sequences in the standard
library,
beyond curses and termios
(which mildly overlap in functionality with this package and themselves).

Those are low-level interfaces however,
focused on "full screen" terminal apps and tty control respectively,
while continuing to abstract hardware that now only exists in museums.
The ANSI standard may have won,
but styling a text snippet here and there or setting a title without a bunch
of ugly C-style function calls was thought too…
trivial perhaps.

.. rubric:: Terminfo?

Besides the difficulty factor mentioned,
this classic answer to this problem also suffers in that it historically
doesn't support "true" color (24 bit) palettes,
and is not included by default on Windows.


Meanwhile, over at the Cheeseshop…
------------------------------------

    *"Not much of a cheese shop really, is it?"—Monty Python*

And so, now there are ad-hoc ANSI codes being generated in every command-line
app and eleventy micro-libs on "the" PyPI doing the same.
Looks to be a fun exercise and somewhat of a rite of passage to create one.

(On that note:  Good luck finding an appropriate name on PyPI for yours—Taken!)

.. raw:: html

    <div class="center rounded p1 dark">
    <span class=dots>·····•·····</span>&nbsp;&nbsp;
    <i>
    <span id=bas>ᗣ</span><span id=pok>ᗣ</span>
    <span id=sha>ᗣ</span><span id=spe>ᗣ</span>&nbsp;
    <span id=pac>ᗧ</span></i>&nbsp;&nbsp;
    <span class=dots>·····•·····</span>&nbsp;&nbsp;&nbsp;<br>

    <i style="opacity: .7">waka waka waka</i>&nbsp;&nbsp;&nbsp;
    </div>


Often Missing
~~~~~~~~~~~~~~~

    *"Them Dukes! Them Dukes…"—Sheriff Rosco P. Coltrane*

While many of the ANSI modules in the cheeseshop have plenty going for them in
areas of focus,
they generally aren't very comprehensive──\
usually providing 8 colors
and a few styles/effects like bold and underline.
Unfortunately,
one or more important items are often missing:

    - Styles, cursor movements, clearing the screen,
      setting titles, bracketed paste, full-screen, etc.

    - Multiple Palettes:

      - 8 color - always
      - 16 color - sometimes
      - 256 extended color - rare
      - Nearest 8-bit color - rarer
      - 16M color - rarer
      - Standard color names, like X11 & Webcolors - rarest

    - Querying the terminal, auto-detection, support and deactivation.
    - Python3 support/still maintained
    - Has tests


Nice to haves
~~~~~~~~~~~~~~~~~

    | *"You've got to, know when to hold 'em… know when to fold 'em…"*
    | *—Kenny Rogers*

Most are relatively easy to use,
but may still miss one of these nice to haves:

    - Composable objects
    - Concise names

        - Avoidance of capital, mixed, or camel-case names on instances.
        - Avoidance of extra punctuation, parens, brackets, quotes, etc.

    - Nearest neighbor downgrade for unsupported palettes.
    - Progress Bars
    - Hyperlinks


.. rubric:: Result

Looking over at PyPI with the criteria above finds many interesting pieces but
far from the full Monty.
So, had some fun building my own of course.
Looked at and picked out a few design cues from several of these:

    - ansi
    - ansicolors
    - blessed
    - `blessings <https://pypi.org/project/blessings/>`_ (context managers)
    - click.style and utilities (reminded me of pause)
    - colorama.ansi (palette collection objects)
    - `colorful <https://tuxtimo.me/posts/colorful-python>`_
      (why terminfo is a bust)
    - colorize
    - escape
    - fabric.colors
    - kolors
    - pycolor
    - pygments (nearest indexed color)
    - style
    - termcolor
    - ptpython, urwid
    - rich
    - tqdm

etc.
