
Another One, eh 🤔?
=======================

.. raw:: html

    <pre class=center>

     ▏
    ,<><><>,
    <><><><><><>
    <><><><><><✦<>
    (<><><><><><><>)
    <><><><><><><>
    .  <>✶><><><><> .
    : .   `<><><>`    .:
     ::             :     ⭒:
    .⭒.       .      :     .:.
    .:.       .        :     : .
    .: :       :        :      ::.
    .:  :      .         :.      :⭒ :
    :⭒. :       :          :      :   ..
    . :                     :             :
    </pre>

    <p class=center><i>"First I was afraid, I was petrified."</i></p>


Background
---------------

ANSI escape codes have been standard on UNIX
with the belt-and-suspenders crowd for several decades,
and even saw use on DOS and BBS back in the day.
With the advent of macOS (née X),
a whole new generation of lumber-sexuals have exposed themselves(?)
to the command-line and terminal environment *and liked it*.

"I'm a PC"
~~~~~~~~~~~~~~

With Windows 10──\
the  Ballmer-barrier has finally been breached,
allowing *multi-decade-late*
`improvements
<http://www.nivot.org/blog/post/2016/02/04/Windows-10-TH2-(v1511)-Console-Host-Enhancements>`_
to be made to its until-now pathetic "console."
Often still known as the "DOS Prompt" because it hadn't changed since then.
Vaguely analogous to a virtual terminal,
as a Yugo would compare to a BMW.
But now it's supercharged.

So, the three major platforms now support ANSI escape sequences.
Again!
What's old is new again.

We need great command-line tools and that's where "console" fits in.
*That's the way, uhh huh, I like it…*

.. figure:: _static/kc3.png
    :align: center
    :figwidth: 60%

    The Sunshine Band on Soul Train


(Cue
`KC and the Sunshine Band,
<https://www.youtube.com/watch?v=OM7zRfHG0no>`_
*uhh-huh, uhh-huh*)


Batteries Not Included
------------------------

In the Python world,
there hasn't been much direct support for terminal sequences in the standard
library,
beyond curses and termios
(which mildly overlap in functionality with this package and themselves).
They are low-level interfaces however,
focused on "full screen" terminal apps and tty control respectively,
while abstracting hardware that no longer really exists except in museums.
ANSI codes won,
but styling a text snippet here and there or setting a title was thought too…
trivial perhaps.


Meanwhile, over at the Cheeseshop…
------------------------------------

And so, now there are ad-hoc ANSI codes being generated in every command-line
app and eleventy million micro-libs on the PyPI Cheeseshop doing the same.
Looks to be a fun exercise and somewhat of a rite of passage to create one.

Good luck finding an appropriate name on PyPI for yours.


Often Missing
~~~~~~~~~~~~~~~

.. raw:: html

    <div class=center>
    <i>
    <span id=bas>ᗣ</span><span id=pok>ᗣ</span>
    <span id=sha>ᗣ</span><span id=spe>ᗣ</span>&nbsp;
    <span id=pac>ᗧ</span></i>
    ·····•·····<br>

    <i style="opacity: .7">waka waka waka</i>
    </div>


While most of the modules on the cheeseshop have plenty going for them in their
areas of focus,
they generally aren't very comprehensive──\
usually providing 8 colors
and a few styles/effects like bold and underline.
Unfortunately,
one or more important items are often missing:

    - Python3 support

      *(currently 3.6 is required for string interpolation but back-porting
      under consideration)*

    - Multiple Palettes:

      - 8 color - always
      - 16 color - sometimes
      - 256 extended color - rare
      - Nearest 8-bit color - rarer
      - 16M color - rarer
      - Standard color names

        - X11, Webcolors - rarest
    - Palette auto-detection, support and deactivation:

    - Styles, cursor movements, clearing the screen,
      setting titles, etc.
    - Still maintained
    - Has tests


Nice to haves
~~~~~~~~~~~~~~~~~

Most have an easy to use design,
but may still miss one of these nice to haves:

    - Composable objects
    - Concise names
    - Avoidance of capital, mixed, or camel-case names on instances.
    - Avoidance excessive punctuation, parens, brackets, quotes, etc.


Resulting Design
~~~~~~~~~~~~~~~~~

Had been looking over at PyPI with the criteria above and found some
interesting parts but not the whole.
So, had some fun building my own.

Picked a few design cues from several of these:

    - ansi
    - ansicolors
    - blessed (terminfo?)
    - blessings
    - click.style and utilities
    - colorama.ansi (palette collection objects)
    - colorize
    - escape
    - fabric.colors
    - kolors (terminfo)
    - pycolor
    - pygments (nearest indexed color)
    - style
    - termcolor
