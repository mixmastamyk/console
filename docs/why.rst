
Why?
=========


Another One, huh 🤔
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Well, ANSI escape codes have been standard on UNIX
with the belt-and-suspenders crowd for several decades,
and even saw use on DOS and BBS back in the day.
With the advent of macOS (X),
a whole new generation of bearded-hipsters have been exposed to the command-line
and terminal environment and liked it.

Finally with Windows 10──\
the "I'm a PC" Ballmer-barrier has been breached,
finally allowing *multi-decade-late*
`improvements
<http://www.nivot.org/blog/post/2016/02/04/Windows-10-TH2-(v1511)-Console-Host-Enhancements>`_
to be made to its until-now pathetic "console."
Often still known as the "DOS Prompt" because it hadn't changed since then.
Vaguely analogous to a virtual terminal,
as a Yugo is to a BMW.
But, it's now supercharged.

So, the three major platforms now support ANSI escape sequences.
Again!
What's old is new again.
We need great command-line tools and that's where "console" fits in.

(Cue
`KC and the Sunshine Band,
<https://www.youtube.com/watch?v=OM7zRfHG0no>`_
uh-huh uh-huh)


Meanwhile, over at the Cheeseshop…
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In the Python world,
there hasn't been much direct support for terminal sequences in the standard
library,
beyond curses and termios
(which overlap somewhat in functionality with this package and themselves).
They are low-level interfaces however,
focused on "full screen" terminal apps and tty control respectively,
abstracting hardware support that no longer really exists except in museums.
Styling a text snippet here and there or setting a title was thought too…
trivial perhaps.

And so, now there are ad-hoc ANSI codes being generated in every command-line
app and eleventy million micro-libs on the PyPI Cheeseshop doing the same.
Looks to be a fun exercise and somewhat of a rite of passage to create one---\
good luck finding an appropriate name on PyPI.

While most of the modules have plenty going for them in their areas of focus,
they generally aren't very comprehensive──\
usually providing 8 colors,
and a few styles/effects like bold and underline.
Unfortunately,
one or more important items are often missing:

    - Python3 support
      (currently 3.6 is required but porting under consideration)

    - Palette auto-detection, support and deactivation:

      - 16 color palette
      - 256 extended color palette - rare
      - Nearest 8-bit color - rare
      - 16M color palette - rarer
      - Standard color names - X11, Webcolors

    - Styles, cursor movements, clearing the screen,
      setting titles, etc.
    - Still maintained
    - Has tests

Most have an easy to use design, but may still miss one of these nice to haves:

    - Composable objects
    - Concise names
    - Discourage capital, mixed, camel-case names on instances.
