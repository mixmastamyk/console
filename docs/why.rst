
.. ~ <p class=center><i>"First I was afraid, I was petrified…"</i>&nbsp; &nbsp;

.. raw:: html


    <pre class=center>

     ▏
    ,<><><>,
    <>✶><><><><>
    <><><><><><✦<>
    (<><><><><><><>)
    <><><><><><><>
    .  <>✶><><><><> .
    : .   `<><><>`    .:
     ::            :      ⭒:
    .⭒.      .       :     .:.
    .:.      .         :     : .
    .: :     :          :      ::.
    .:  :     .          .:      :⭒ :
    :⭒. :      :             :       : ..
    . .                        .          .
    </pre>


Another One, eh 🤔?
=======================


.. container:: center

    *"First I was afraid, I was petrified…"*


Background
---------------

So ANSI escape codes have been standard on UNIX
with the belt-and-suspenders crowd for several decades,
and even saw use on DOS and BBSs back in the day.
With the advent of macOS (X),
a whole new generation of lumber-sexuals have exposed themselves(?)
to the terminal environment and command-line
*and liked it*.

"I'm a PC"
~~~~~~~~~~~~~~

With Windows 10──\
the  Ballmer-lameo-barrier has finally been breached,
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
We need great command-line tools and that's where ``console`` fits in.

.. container:: center

    *That's the way, uhh huh, uhh huh, I like it…*

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

    *Jive Turkey…*

In the Python world,
there hasn't been much direct support for terminal sequences in the standard
library,
beyond curses and termios
(which mildly overlap in functionality with this package and themselves).
They are low-level interfaces however,
focused on "full screen" terminal apps and tty control respectively,
while continuing to abstract hardware that rarely exists except in museums.
ANSI codes may have won,
but styling a text snippet here and there or setting a title was thought too…
trivial perhaps.


Meanwhile, over at the Cheeseshop…
------------------------------------

    *"Not much of a cheese shop really, is it?"*

And so, now there are ad-hoc ANSI codes being generated in every command-line
app and eleventy micro-libs on the PyPI doing the same.
Looks to be a fun exercise and somewhat of a rite of passage to create one.

(Good luck finding an appropriate name on PyPI for yours.)

.. raw:: html

    <div class=center>
    <i>
    <span id=bas>ᗣ</span><span id=pok>ᗣ</span>
    <span id=sha>ᗣ</span><span id=spe>ᗣ</span>&nbsp;
    <span id=pac>ᗧ</span></i>
    ·····•·····&nbsp;&nbsp;&nbsp;<br>

    <i style="opacity: .7">waka waka waka</i>&nbsp;&nbsp;&nbsp;
    </div>



Often Missing
~~~~~~~~~~~~~~~

While most of the ANSI modules in the cheeseshop have plenty going for them in
areas of focus,
they generally aren't very comprehensive──\
usually providing 8 colors
and a few styles/effects like bold and underline.
Unfortunately,
one or more important items are often missing:

    - Styles, cursor movements, clearing the screen,
      setting titles, querying the terminal, etc.

    - Multiple Palettes:

      - 8 color - always
      - 16 color - sometimes
      - 256 extended color - rare
      - Nearest 8-bit color - rarer
      - 16M color - rarer
      - Standard color names

        - X11, Webcolors - rarest

    - Auto-detection, support and deactivation:

    - Python3 support

      *(currently console requires Python 3.6 for string interpolation but
      back-porting is under consideration)*

    - Still maintained
    - Has tests


Nice to haves
~~~~~~~~~~~~~~~~~

Most have an easy to use design,
but may still miss one of these nice to haves:

    - Composable objects
    - Concise names

        - Avoidance of capital, mixed, or camel-case names on instances.
        - Avoidance of punctuation requirements, parens, brackets, quotes, etc.


.. rubric:: Result

Looking over at PyPI with the criteria above finds many
interesting parts but not the whole.
So, had some fun building my own.
Looked at and picked a few design cues from several of these:

    - ansi
    - ansicolors
    - blessed (terminfo?)
    - blessings
    - click.style and utilities (remembered pause)
    - colorama.ansi (palette collection objects)
    - colorize
    - escape
    - fabric.colors
    - kolors (terminfo)
    - pycolor
    - pygments (nearest indexed color)
    - style
    - termcolor
