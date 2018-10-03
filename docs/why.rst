
.. raw:: html

    <pre id='logo' class='center'>
    <span style="color:#729fcf">&#9484;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;</span><span style="color:#3465a4">&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9488;</span>
    <span style="color:#729fcf">&#9474;</span>&#160;&#160;&#160;<span style="color:#729fcf">&#9487;&#9473;&#9592;&#9487;</span><span style="color:#3465a4">&#9473;&#9491;&#9487;&#9491;&#9595;&#9487;&#9473;&#9491;&#9487;&#9473;&#9491;&#9595;</span>&#160;&#160;</span><span style="color:#3465a4">&#9487;&#9473;</span><span style="color:#b4b8b0">&#9592;</span>&#160;&#160;&#160;<span style="color:#b4b8b0">&#9474;</span>
    <span style="color:#3465a4">&#9474;</span>&#160;&#160;&#160;<span style="color:#3465a4">&#9475;</span>&#160;&#160;</span><span style="color:#3465a4">&#9475;</span>&#160;</span><span style="color:#3465a4">&#9475;&#9475;&#9495;&#9515;&#9495;&#9473;&#9491;</span><span style="color:#b4b8b0">&#9475;</span>&#160;</span><span style="color:#b4b8b0">&#9475;&#9475;</span>&#160;&#160;<span style="color:#b4b8b0">&#9507;&#9592;</span>&#160;&#160;&#160;&#160;</span><span style="color:#b4b8b0">&#9474;</span>
    <span style="color:#3465a4">&#9474;</span>&#160;&#160;&#160;<span style="color:#3465a4">&#9495;&#9473;&#9592;&#9495;</span><span style="color:#b4b8b0">&#9473;&#9499;&#9593;</span>&#160;</span><span style="color:#b4b8b0">&#9593;&#9495;&#9473;&#9499;&#9495;&#9473;&#9499;&#9495;&#9473;&#9592;&#9495;&#9473;</span><span style="color:#555">&#9592;</span>&#160;&#160;&#160;<span style="color:#555">&#9474;</span>
    <span style="color:#b4b8b0">&#9492;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;</span><span style="color:#555">&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9472;&#9496;</span>
    </pre>

.. container:: center

    *"First I was afraid, I was petrified…"*

|


Another One, eh 🤔?
=======================


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
the Ballmer/Suit barrier has finally been breached,
allowing *multi-decade-late*
`improvements
<http://www.nivot.org/blog/post/2016/02/04/Windows-10-TH2-(v1511)-Console-Host-Enhancements>`_
to be made to its until-now pathetic "console."
Often still known as the "DOS Prompt" because it has been stuck in time since
then.
Vaguely analogous to today's virtual terminals,
as a Yugo might compare to a classic BMW.
But now, it's supercharged.

So, all the top platforms support ANSI escape sequences.
Again!
What's old is new again.
Add Unicode and millions of colors and it's now better than ever.

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
this classic answer to this problem also suffers in that it doesn't support
"true" color palettes,
and not included by default on Windows.


Meanwhile, over at the Cheeseshop…
------------------------------------

    *"Not much of a cheese shop really, is it?"*

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

While many of the ANSI modules in the cheeseshop have plenty going for them in
areas of focus,
they generally aren't very comprehensive──\
usually providing 8 colors
and a few styles/effects like bold and underline.
Unfortunately,
one or more important items are often missing:

    - Styles, cursor movements, clearing the screen,
      setting titles, full-screen, etc.

    - Multiple Palettes:

      - 8 color - always
      - 16 color - sometimes
      - 256 extended color - rare
      - Nearest 8-bit color - rarer
      - 16M color - rarer
      - Standard color names

        - X11, Webcolors - rarest

    - Querying the terminal, auto-detection, support and deactivation.

    - Python3 support

    - Still maintained
    - Has tests


Nice to haves
~~~~~~~~~~~~~~~~~

    | *"You've got to, know when to hold 'em,*
    | *know when to fold 'em…"*

Most have an easy to use design,
but may still miss one of these nice to haves:

    - Composable objects
    - Concise names

        - Avoidance of capital, mixed, or camel-case names on instances.
        - Avoidance of punctuation requirements, parens, brackets, quotes, etc.


.. rubric:: Result

Looking over at PyPI with the criteria above finds many interesting pieces but
far from the full Monty.
So, had some fun building my own of course.
Looked at and picked a few design cues from several of these:

    - ansi
    - ansicolors
    - blessed
    - `blessings <https://pypi.org/project/blessings/>`_ - Context Managers
    - click.style and utilities (reminded of pause)
    - colorama.ansi (palette collection objects)
    - `colorful <https://tuxtimo.me/posts/colorful-python>`_
    - colorize
    - escape
    - fabric.colors
    - kolors
    - pycolor
    - pygments (nearest indexed color)
    - style
    - termcolor

etc.
