%%
%% This is file `article.cls',
%% generated with the docstrip utility.
%%
%% The original source files were:
%%
%% classes.dtx  (with options: `article')
%%
%% This is a generated file.
%%
%% Copyright 1993 1994 1995 1996 1997
%% The LaTeX3 Project and any individual authors listed elsewhere
%% in this file.
%%
%% For further copyright information, and conditions for modification
%% and distribution, see the file legal.txt, and any other copyright
%% notices in this file.
%%
%% This file is part of the LaTeX2e system.
%% ----------------------------------------
%%   This system is distributed in the hope that it will be useful,
%%   but WITHOUT ANY WARRANTY; without even the implied warranty of
%%   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
%%
%%   For error reports concerning UNCHANGED versions of this file no
%%   more than one year old, see bugs.txt.
%%
%%   Please do not request updates from us directly.  Primary
%%   distribution is through the CTAN archives.
%%
%%
%% IMPORTANT COPYRIGHT NOTICE:
%%
%% You are NOT ALLOWED to distribute this file alone.
%%
%% You are allowed to distribute this file under the condition that it
%% is distributed together with all the files listed in manifest.txt.
%%
%% If you receive only some of these files from someone, complain!
%%
%%
%% Permission is granted to copy this file to another file with a
%% clearly different name and to customize the declarations in that
%% copy to serve the needs of your installation, provided that you
%% comply with the conditions in the file legal.txt.
%%
%% However, NO PERMISSION is granted to generate or to distribute a
%% modified version of this file under its original name.
%%
%% You are NOT ALLOWED to change this file.
%%
%%
%% MODIFICATION ADVICE:
%%
%% If you want to customize this file, it is best to make a copy of
%% the source file(s) from which it was produced.  Use a different
%% name for your copy(ies) and modify the copy(ies); this will ensure
%% that your modifications do not get overwritten when you install a
%% new release of the standard system.  You should also ensure that
%% your modified source file does not generate any modified file with
%% the same name as a standard file.
%%
%% You can then easily distribute your modifications by distributing
%% the modified and renamed copy of the source file, taking care to
%% observe the conditions in legal.txt; this will ensure that other
%% users can safely use your modifications.
%%
%% You will also need to produce your own, suitably named, .ins file to
%% control the generation of files from your source file; this file
%% should contain your own preambles for the files it generates, not
%% those in the standard .ins files.
%%
%% The names of the source files used are shown above.
%%
%%
%%
%% \CharacterTable
%%  {Upper-case    \A\B\C\D\E\F\G\H\I\J\K\L\M\N\O\P\Q\R\S\T\U\V\W\X\Y\Z
%%   Lower-case    \a\b\c\d\e\f\g\h\i\j\k\l\m\n\o\p\q\r\s\t\u\v\w\x\y\z
%%   Digits        \0\1\2\3\4\5\6\7\8\9
%%   Exclamation   \!     Double quote  \"     Hash (number) \#
%%   Dollar        \$     Percent       \%     Ampersand     \&
%%   Acute accent  \'     Left paren    \(     Right paren   \)
%%   Asterisk      \*     Plus          \+     Comma         \,
%%   Minus         \-     Point         \.     Solidus       \/
%%   Colon         \:     Semicolon     \;     Less than     \<
%%   Equals        \=     Greater than  \>     Question mark \?
%%   Commercial at \@     Left bracket  \[     Backslash     \\
%%   Right bracket \]     Circumflex    \^     Underscore    \_
%%   Grave accent  \`     Left brace    \{     Vertical bar  \|
%%   Right brace   \}     Tilde         \~}
\NeedsTeXFormat{LaTeX2e}[1995/12/01]
\ProvidesClass{article}
              [1998/05/05 v1.3y
 Standard LaTeX document class]
\RequirePackage{epsf,amsmath,ifthen,dcolumn,graphics,leqno,color}
\newcommand\@ptsize{}
\newif\if@restonecol
\newif\if@titlepage
\@titlepagefalse
\if@compatibility\else
\DeclareOption{a4paper}
   {\setlength\paperheight {297mm}%
    \setlength\paperwidth  {210mm}}
\DeclareOption{a5paper}
   {\setlength\paperheight {210mm}%
    \setlength\paperwidth  {148mm}}
\DeclareOption{b5paper}
   {\setlength\paperheight {250mm}%
    \setlength\paperwidth  {176mm}}
\DeclareOption{letterpaper}
   {\setlength\paperheight {11in}%
    \setlength\paperwidth  {8.5in}}
\DeclareOption{legalpaper}
   {\setlength\paperheight {14in}%
    \setlength\paperwidth  {8.5in}}
\DeclareOption{executivepaper}
   {\setlength\paperheight {10.5in}%
    \setlength\paperwidth  {7.25in}}
\DeclareOption{landscape}
   {\setlength\@tempdima   {\paperheight}%
    \setlength\paperheight {\paperwidth}%
    \setlength\paperwidth  {\@tempdima}}
\fi
\if@compatibility
  \renewcommand\@ptsize{0}
\else
\DeclareOption{10pt}{\renewcommand\@ptsize{0}}
\fi
\DeclareOption{11pt}{\renewcommand\@ptsize{1}}
\DeclareOption{12pt}{\renewcommand\@ptsize{2}}
\if@compatibility\else
\DeclareOption{oneside}{\@twosidefalse \@mparswitchfalse}
\fi
\DeclareOption{twoside}{\@twosidetrue  \@mparswitchtrue}
\DeclareOption{draft}{\setlength\overfullrule{5pt}%
  \AtBeginDocument{\PagePositionCropYes
    {7pc}{5.3pc}{5.9pc}{7pt}
    {7in}{10in}{-1in}{-1in}}}
\DeclareOption{boxdraft}{\setlength\overfullrule{5pt}%
  \AtBeginDocument{\PagePositionBoxYes
    {7pc}{5.3pc}{5.9pc}{7pt}
    {7in}{10in}{-1in}{-1in}}}
\DeclareOption{final}{\setlength\overfullrule{0pt}%
  \AtBeginDocument{\PagePositionCropYes
    {4pc}{4pc}{3.77pc}{7pt}
    {6.3in}{9.5in}{.1in}{-.32in}}}
\DeclareOption{finalcro}{\setlength\overfullrule{0pt}%
  \AtBeginDocument{\PagePositionCropYes
    {7pc}{5.3pc}{5.9pc}{7pt}
    {7in}{10in}{-1in}{-1in}}}
\DeclareOption{titlepage}{\@titlepagetrue}
\if@compatibility\else
\DeclareOption{notitlepage}{\@titlepagefalse}
\fi
\if@compatibility\else
\DeclareOption{onecolumn}{\@twocolumnfalse}
\fi
\DeclareOption{twocolumn}{\@twocolumntrue}
\DeclareOption{leqno}{\input{leqno.clo}}
\DeclareOption{fleqn}{\input{fleqn.clo}}
\DeclareOption{openbib}{%
  \AtEndOfPackage{%
   \renewcommand\@openbib@code{%
      \advance\leftmargin\bibindent
      \itemindent -\bibindent
      \listparindent \itemindent
      \parsep \z@
      }%
   \renewcommand\newblock{\par}}%
}
\ExecuteOptions{letterpaper,10pt,twoside,onecolumn,final}
\ProcessOptions
\input{size1\@ptsize.clo}
\setlength\lineskip{1\p@}
\setlength\normallineskip{1\p@}
\renewcommand\baselinestretch{}
\setlength\parskip{0\p@ \@plus \p@}
\@lowpenalty   51
\@medpenalty  151
\@highpenalty 301
\setcounter{topnumber}{2}
\renewcommand\topfraction{.7}
\setcounter{bottomnumber}{1}
\renewcommand\bottomfraction{.3}
\setcounter{totalnumber}{3}
\renewcommand\textfraction{.2}
\renewcommand\floatpagefraction{.5}
\setcounter{dbltopnumber}{2}
\renewcommand\dbltopfraction{.7}
\renewcommand\dblfloatpagefraction{.5}

\def\SEVEN{\fontsize{7}{9}\selectfont}
\def\EGT{\fontsize{8}{10}\selectfont}
\def\NINE{\fontsize{9}{10}\selectfont}
\def\TEN{\fontsize{10}{12}\selectfont}
\def\TWELVE{\fontsize{12}{12}\selectfont}
\def\THIRTEEN{\fontsize{13}{15}\selectfont}
\def\FOURTEEN{\fontsize{14}{16}\titfont}
\def\SIXTEEN{\fontsize{16}{22}\selectfont}

\newdimen\markwidth
\newdimen\blth
\newdimen\marklength
\newdimen\markdistance
\newdimen\trimwidth
\newdimen\trimheight
\newdimen\auxaaa
\newdimen\auxbbb
\newdimen\auxccc
\newdimen\auxddd

\long\def\koo#1#2#3{\vbox to0pt{\hsize0pt\kern #2\hbox to0pt{\kern
#1{#3}\hss}\vss}}
\long\def\zeroCC#1{\vbox to0pt{\vss\hbox to0pt{\hss #1\hss}\vss}}
\long\def\zeroLC#1{\vbox to0pt{\vss\hbox to0pt{\hss #1\hss}}}
\long\def\zeroUC#1{\vbox to0pt{\hbox to0pt{\hss #1\hss}\vss}}
\long\def\zeroLR#1{\vbox to0pt{\vss\hbox to0pt{\hss #1}}}
\long\def\zeroLL#1{\vbox to0pt{\vss\hbox to0pt{#1\hss}}}
\long\def\zeroUR#1{\vbox to0pt{\hbox to0pt{\hss #1}\vss}}
\long\def\zeroUL#1{\vbox to0pt{\hbox to0pt{#1\hss}\vss}}
\long\def\zeroCL#1{\vbox to0pt{\vss\hbox to0pt{#1\hss}\vss}}
\long\def\zeroCR#1{\vbox to0pt{\vss\hbox to0pt{\hss #1}\vss}}

%%%%%%%%%%%%%%%%%%% Numbers supplied down here!
\markwidth=.5pt %0.4 truept % Thickness of the mark line
\blth=0.2pt
\marklength=20 truept % Length of the mark line
\markdistance=3 truept % Distance of the real corner to the beg. of the mark
%%% \trimwidth=\textwidth+\oddsidemargin+\evensidemargin

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
\auxaaa\marklength\advance\auxaaa\markdistance
\def\oddevenswitch{\ifodd\c@page \auxbbb=\oddsidemargin
 \else\auxbbb=\evensidemargin\fi}%

%%% First reset all page position parameters depending on the job:
% \PagePositionCropYes - should be just for testing
% \PagePositionCropNo  - should be the default behavior
% \PagePositionBoxYes  - gives the page box for testing

\def\PagePositionCropYes#1#2#3#4#5#6#7#8{%
  \oddsidemargin=#1%  % [3] inner margin / gutter
  \evensidemargin=#2% % [4] outside margin
  \topmargin=#3%      % [5] \rhsink = \topmargin + \headheight (=12pt here)
  \headheight=#4%     % [6] VERY IMPORTANT! (see above)
  \trimwidth=#5%      % [7]
  \trimheight=#6%     % [8]
  \hoffset=#7%        % = -1in to move the area in the upper left corner
  \voffset=#8%        % = -1in to move the area in the upper left corner
%%%
 \def\CROPMARKS{\oddevenswitch
 \hbox to0pt{\kern-\auxbbb
   \vbox to0bp{\kern-\topmargin\kern-\headheight
   \hbox to\trimwidth{%
     \koo{-\auxaaa}{-\markwidth}{\VRHDW{\markwidth}{0pt}{\marklength}}%
     \koo{-\markwidth}{-\auxaaa}{\VRHDW{0pt}{\marklength}{\markwidth}}%
     \hfill
     \koo{\markdistance}{-\markwidth}{\VRHDW{\markwidth}{0pt}{\marklength}}%
     \koo{0pt}{-\auxaaa}{\VRHDW{0pt}{\marklength}{\markwidth}}}%
   \nointerlineskip\vskip\trimheight
   \nointerlineskip
   \hbox to\trimwidth{%
     \koo{-\auxaaa}{0pt}{\VRHDW{0pt}{\markwidth}{\marklength}}%
     \koo{-\markwidth}{\markdistance}{\VRHDW{0pt}{\marklength}{\markwidth}}%
     \hfill
     \koo{\markdistance}{0pt}{\VRHDW{0pt}{\markwidth}{\marklength}}%
     \koo{0pt}{\markdistance}{\VRHDW{0pt}{\marklength}{\markwidth}}}%
   \vss}\hss}}%
}%

\def\PagePositionCropNo#1#2#3#4#5#6#7#8{%
  \oddsidemargin=#1%  % [3] inner margin / gutter
  \evensidemargin=#2% % [4] outside margin
  \topmargin=#3%      % [5] \rhsink = \topmargin + \headheight (=12pt here)
  \headheight=#4%     % [6] VERY IMPORTANT! (see above)
  \trimwidth=#5%      % [7]
  \trimheight=#6%     % [8]
  \hoffset=#7%        % = -1in to move the area in the upper left corner
  \voffset=#8%        % = -1in to move the area in the upper left corner
%%%
\def\CROPMARKS{}%
}%

\def\PagePositionBoxYes#1#2#3#4#5#6#7#8{%
  \oddsidemargin=#1%  % [3] inner margin / gutter
  \evensidemargin=#2% % [4] outside margin
  \topmargin=#3%      % [5] \rhsink = \topmargin + \headheight (=12pt here)
  \headheight=#4%     % [6] VERY IMPORTANT! (see above)
  \trimwidth=#5%      % [7]
  \trimheight=#6%     % [8]
  \hoffset=#7%        % = -1in to move the area in the upper left corner
  \voffset=#8%        % = -1in to move the area in the upper left corner
%%%
 \def\CROPMARKS{\oddevenswitch
 \hbox to0pt{\kern-\auxbbb
   \vbox to0bp{\kern-\topmargin\kern-\headheight
   \hbox to\trimwidth{%
     \auxccc=\trimwidth \advance\auxccc by 2\blth
     \auxddd=\trimheight \advance\auxddd by 2\blth
     \koo{-\blth}{0pt}{\zeroLL{\VRHDW{\blth}{0pt}{\auxccc}}}%
     \koo{-\blth}{-\blth}{\zeroUL{\VRHDW{\auxddd}{0pt}{\blth}}}%
     \koo{\trimwidth}{-\blth}{\zeroUL{\VRHDW{\auxddd}{0pt}{\blth}}}%
     \koo{-\blth}{\trimheight}{\zeroUL{\VRHDW{\blth}{0pt}{\auxccc}}}\hss}%
   \vss}\hss}}%
}%

\def\LRH#1{\gdef\setLRH{#1}}\def\setLRH{}%
\def\RRH#1{\gdef\setRRH{#1}}\def\setRRH{}%

\LRH{author}
\RRH{short title}

\def\ps@headings{\let\@mkboth\markboth
  \def\@oddfoot{\setoddFOOT}%
  \def\@evenfoot{\setevenFOOT}%
  \def\@evenhead{\setevenRH}%
  \def\@oddhead{\setoddRH}%
  \def\sectionmark##1{}%
  \def\subsectionmark##1{}}%

%%%%%%%%%%%%%%%%%%% Standard settings:

\def\setoddRH{\VRHDW{\headheight}{0pt}{0pt}\CROPMARKS%
  \raisebox{0pt}[\headheight][0pt]{%
%    \marginnumbering
    \begin{tabular}{@{}c@{}}\\[-50pt]%
%    \TEN\hskip -1pt\today\\[27pt]%
  \hbox to \textwidth{\hfill{\TEN\it\spaceskip0.41em\setRRH}\hspace*{30pt}{\TEN\thepage}}
    \end{tabular}
  }}%

% \def\Stamp#1{\gdef\theStamp{#1}}%
% \Stamp{Please enter the STAMP VALUE}%

\def\setevenRH{\VRHDW{\headheight}{0pt}{0pt}\CROPMARKS%
  \raisebox{0pt}[\headheight][0pt]{%
% \marginnumbering
  \begin{tabular}{@{}c@{}}\\[-50pt]%
%    \TEN\hskip -1pt\today \\[27pt]%
  \hbox to \textwidth{\spaceskip0.41em{\TEN\thepage}\hspace*{30pt}\TEN\it%
  \setLRH}%
    \end{tabular}
  }}%

\def\setevenFOOT{\hfil}
\def\setoddFOOT{\hfil}

\let\savesetevenRH=\setevenRH
\let\savesetoddRH=\setoddRH
\let\savesetoddFOOT=\setoddFOOT
\let\savesetevenFOOT=\setevenFOOT

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\ps@plain
\def\ps@plain{\let\@mkboth\@gobbletwo
     \def\@oddhead{\hfil}%
     \let\@evenhead=\@oddhead
     \def\@oddfoot{\hfil}%
     \def\@evenfoot{\hfil}}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\ps@empty
\def\ps@empty{\let\@mkboth\@gobbletwo
     \def\@oddhead{\hfil}%
     \let\@evenhead=\@oddhead
     \def\@oddfoot{\hfil}%
     \let\@evenfoot=\@oddfoot}

\def\jname{ETC}

\def\boxtext{\begin{tabular}{l}
\\[-190pt]
\hbox to \textwidth{\hfill{\parbox{16pc}
    {\EGT
    \begin{tabular}{c}
    \jname\ \artname\quad Pe:\ \penumber/LE/CP/DISK (LaTeX)\\
   \today\quad \printtime\quad Ist Proof
    \end{tabular}
    }
}\enskip}
\end{tabular}}


\def\KLUWERLOGO{\epsffile[0 0 16 18]{aglogo3.eps}}%

\def\setfirstoddFOOT{\hfil}
\def\setfirstevenFOOT{\hfil}

\def\JOURNALNAME#1{\gdef\theJOURNALNAME{#1}}%
\def\VOL#1{\gdef\theVOL{#1}}%
\VOL{0}%
\def\PAGES#1{\gdef\thePAGES{#1}}%
\PAGES{\thepage--\pageref{LastPage}}%
\def\PUBYEAR#1{\gdef\thePUBYEAR{#1}}%
\PUBYEAR{2004}%
\def\ISSUE#1{\gdef\theISSUE{#1}}%
\ISSUE{00}%

\JOURNALNAME{\TEN{\it Int. J. Accounting, Auditing and Performance Evaluation, Vol. \theVOL, No. \theISSUE, \thePAGES}\hfill \thepage}%
\def\jtitlefont{\fontsize{16}{22}\selectfont\rm}

\def\Dnum#1{\gdef\theDnum{#1}}%
\Dnum{Please enter the Dekker No}%

\def\CLline{{\CROPMARKS\vskip -33pt \fontsize{9}{12}\selectfont
\TEN\hskip -1pt\\
\NINE{\theJOURNALNAME\\[9pt]
%Vol. \theVOL, Nos. \theISSUE, pp. \thePAGES, \thePUBYEAR}
}\endgraf}\vspace*{38pt}}%

\def\BottomCatch{%
\vskip 10pt
\thispagestyle{empty}%
\begin{table}[b]%
\NINE\begin{tabular*}{\textwidth}{@{\extracolsep{\fill}}lcr@{}}%
\\[1pt]
Copyright \copyright\ 200x Inderscience Enterprises Ltd. & &%
\end{tabular*}%
\vskip -40pt%
\end{table}%
}%

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%SSS
%%%%%% \Trivlist, \TRivlist, \Center, \Flushleft, \Flushright
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
\def\Trivlist{\parskip0pt\topsep=0pt\parsep0pt\partopsep0pt\@nmbrlistfalse
  \@trivlist \labelwidth\z@ \leftmargin\z@
  \itemindent\z@ \def\makelabel##1{##1}}

\def\endTrivlist{\if@newlist\@noitemerr\fi
   \if@inlabel\indent\fi
   \ifhmode\unskip \par\fi
   \if@noparlist \else
      \ifdim\lastskip >\z@ \@tempskipa\lastskip \vskip -\lastskip
         \advance\@tempskipa\parskip \advance\@tempskipa -\@outerparskip
         \vskip\@tempskipa
   \fi\@endparenv\fi}

\def\TRivlist{\parskip0pt\topsep=12pt plus 5pt minus 5pt
  \parsep0pt\partopsep0pt\@nmbrlistfalse
  \@trivlist \labelwidth\z@
  \leftmargin 0pt \rightmargin 0pt
  \itemindent\z@ \def\makelabel##1{##1}}

\def\endTRivlist{\if@newlist\@noitemerr\fi
   \if@inlabel\indent\fi
   \ifhmode\unskip \par\fi
   \if@noparlist \else
      \ifdim\lastskip >\z@ \@tempskipa\lastskip \vskip -\lastskip
         \advance\@tempskipa\parskip \advance\@tempskipa -\@outerparskip
         \vskip\@tempskipa
   \fi\@endparenv\fi}

\def\Center{\Trivlist \centering\item[]}
\let\endCenter=\endTrivlist
\def\Flushleft{\Trivlist \raggedright\item[]}
\let\endFlushleft=\endTrivlist
\def\Flushright{\Trivlist \raggedleft\item[]}
\let\endFlushright=\endTrivlist

\newcommand{\up}{\HD{9}{0}}% for tables
\newcommand{\down}{\HD{0}{6}}%

%%%%%%%%%%koo.sty
\def\VRHDW#1#2#3{\vrule height #1 depth #2 width #3}
\def\HRHDW#1#2#3{\hrule height #1 depth #2 width #3}
\def\HD#1#2{\vrule height #1pt depth #2pt width 0pt\relax}
\def\halmos{\VRHDW{8pt}{0pt}{4pt}}%

\newcommand\abstractname{\NINE Abstract:}
%\newcommand\keywordname{Keywords:\null}

\newbox\t@abstract
\newbox\t@receivedname
\newbox\temptbox
\newdimen\tempdime

\def\authorA#1{\gdef\@authorA{\Large\bfseries #1}}
\def\authorB#1{\gdef\@authorB{\Large\bfseries #1}}
\def\authorC#1{\gdef\@authorC{\authfont #1}}
\def\authorD#1{\gdef\@authorD{\authfont #1}}

\def\affA#1{\gdef\@affA{\TEN #1}}
\def\affB#1{\gdef\@affB{\TEN #1}}
\def\affC#1{\gdef\@affC{\NINE #1}}
\def\affD#1{\gdef\@affD{\NINE #1}}

\def\HISTORY#1{\gdef\@HISTORY{\NINE #1}}
\def\ADDITIONAL#1{\gdef\@ADDITIONAL{\NINE #1}}
\def\PRESENTED#1{\gdef\@PRESENTED{\NINE #1}}
\def\DEDICATED#1{\gdef\@DEDICATED{{\TWELVE\it #1}}}

\def\REF#1{\gdef\@REF{\NINE #1}}
\def\BIO#1{\gdef\@BIO{\NINE #1}}
\def\JEL#1{\gdef\@JEL{\NINE #1}}
\def\PACS#1{\gdef\@PACS{\NINE #1}}
\def\KEYWORD#1{\gdef\@KEYWORD{\NINE #1}}

%%
\def\sechead#1{\def\@sechead{#1}}
\def\docHeading#1{\def\@docHeading{#1}}
\def\subtitle#1{\def\@subtitle{\uppercase{#1}}}

\def\address#1{\def\@address{#1}}
\def\Date#1{\def\@Date{Accepted~#1}}
\def\abstract{\@ifnextchar[{\@abstract}{\@abstract[]}}

\def\@abstract[#1]{%
  \global\setbox\t@abstract=\vbox\bgroup%
    \parindent10pt\leftskip 3pc\rightskip 3pc%
    \noindent{\bf\TEN \abstractname}\quad%\vskip 12.8pt
    \noindent\NINE%
    \ignorespaces}%
\def\endabstract{\egroup}

%\font\titfont=tib at 14pt
%\font\authfont=tib at 14pt

\newcommand\maketitle{\par
  \begingroup
      \gdef\thefootnote{\alph{footnote}}
    \def\@makefnmark{\hbox
    to 0pt{$^{\@thefnmark}$\hss}}
    \long\def\@makefntext##1{\noindent
      \ifnum\c@footnote=1\hbox{*\,}\else
      \hbox{\@textsuperscript{\normalfont\@thefnmark}\,}\fi
      \foot ##1}%
%      \ifnum \col@number=\@ne
%        \@maketitle
%      \else
        \@maketitle
%          \twocolumn[\@maketitle]%
%      \fi
%      \thispagestyle{firstpage}
  \@thanks
  \endgroup
  \setcounter{footnote}{0}%
  \global\let\maketitle\relax\global\let\@maketitle\relax
}

\long\gdef\ARTICLEOPENING#1{\long\gdef\@maketitle{#1}}%
\ARTICLEOPENING{}%

%FFF
\def\@maketitle{%
%  \begin{Center}%
    \ifx\@subtitle\undefined%
    \else%
        \begin{Flushleft}%
            \TEN\vskip -65pt  \HD{0}{3}\@subtitle%
        \end{Flushleft}%
     \fi%
    \let \footnote \thanks%
      {%
    \ifx\@docHeading\undefined\else{\@docHeading\par}\fi%
       \hyphenpenalty 10000%
        \begin{Flushleft}
        \rule{30pc}{2pt}\\%[1pt]
        \rightskip 2pc plus 20pc
        \baselineskip16pt plus .2pt minus .2pt
        \Large\bfseries%
         \HD{14}{0}\@title\\[-8pt]
         \rule{30pc}{2pt}\HD{10}{6}%
         \end{Flushleft}
            \par}%
%%%authorA  %GGG
    \ifx\@authorA\undefined%
    \else%
      \begin{Flushleft}%
        \baselineskip16pt plus .25pt minus .24pt
         \leftskip 3pc plus 20pc  \rightskip 3pc plus 20pc
    \HD{24}{0}\@authorA\HD{0}{0}
    \end{Flushleft}%
    \fi\par%
    \ifx\@affA\undefined%
    \else
      \begin{Flushleft}%
    \HD{18}{0}%
    \leftskip 3pc plus 0pt  \rightskip 3pc plus 0pt
    \@affA\HD{0}{9}%
      \end{Flushleft}%
          \fi%
%%%
    \ifx\@authorB\undefined%
    \else%
      \begin{Flushleft}%
    \leftskip 3pc plus 20pc  \rightskip 3pc plus 20pc
    \HD{16}{0}\@authorB\HD{0}{0} \end{Flushleft}\fi%
    \ifx\@affB\undefined%
    \else \begin{Flushleft}\HD{22}{0}%
    \leftskip 0pc plus 20pc  \rightskip 0pc plus 20pc
    \@affB\HD{0}{9}%
    \end{Flushleft}%%
    \fi%
%%%

    \ifx\@Date\undefined\else{\footnotesize%
    \@Date%
    \par}\vskip24pt\fi%
    \HD{3}{0}%
    \ifx\@ADDITIONAL\undefined%
    \else%
        \@ADDITIONAL \HD{0}{20}\par%
    \fi%
    \ifx\@PRESENTED\undefined%
    \else%
        \@PRESENTED\HD{0}{20}\par%
    \fi%
    \ifx\@HISTORY\undefined%
    \else%
        \@HISTORY \HD{9}{0}\par%
    \fi%
    \HD{6}{0}%
%    \tableofcontents
    {\unvbox\t@abstract}%
%     \end{Center}%
    \ifx\@KEYWORD\undefined%
    \else%
    \noindent\leftskip 3pc\rightskip 3pc%
     \HD{19}{0}\NINE{\bf Keywords:}\quad\@KEYWORD \HD{0}{0}\par%
     \fi
        \ifx\@REF\undefined%
    \else%
    \noindent\leftskip 3pc\rightskip 3pc%
     \HD{21}{0}\NINE{\bf Reference}\quad\@REF \HD{0}{0}\par%
    \fi%
    \ifx\@BIO\undefined%
    \else%
    \noindent\leftskip 3pc\rightskip 3pc%
     \HD{19.6}{0}\NINE{\bf Biographical notes:}\quad\@BIO \HD{0}{0}\par%
    \fi%
      \noindent\leftskip 0pc\rightskip 2pc
             \HD{18.5}{0}\rule{30pc}{2pt}
        %\ifx\@JEL\undefined%
    %\else%
     % \noindent\NINE {\it JEL Classification:}\ \@JEL \HD{20}{0}\par%
    %\fi%
    %\ifx\@PACS\undefined%
    %\else%
    % \EGT   {\it PACS:}\ \@PACS \HD{20}{0}\par%
    %\fi%
  \vskip 8pt plus 3pt minus 2pt%
  \relax%
}%

%%% BIBLIOGRAPHY

\def\@biblabel#1{[#1]}
 \def\@cite#1{[#1]}

%%%%%%%%%%%%%%%%%BIBLIOGRAPHY %%%%%%%%%%%%BBBBBB

\def\thebibliography#1{%
    \par{\section*{References and Notes}}%
    \list{}{\settowidth\labelwidth{#1}
    \setlength{\topsep}{0pt}
    \labelsep 0pt\labelwidth 0pt
    \leftmargin 8pt
     \itemindent-8pt
    \itemsep  5pt
    \def\bibitem{\item \NINE
     \baselineskip10pt plus 0.3pt minus 0.25pt\relax}}
    \def\newblock{\hskip .11em plus .33em minus .07em}
    \sloppy\clubpenalty4000\widowpenalty4000
    \sfcode`\.=1000\relax}

\def\endthebibliography{\endlist}

\def\NUMBIB{\def\@biblabel##1{\bf ##1}%
\def\thebibliography##1{%
  \par{\section*{References and Notes\HD{0}{0}}}%
  \list
  {\@biblabel{\arabic{enumiv}}}{\NINE
    \baselineskip 10pt plus 0.3pt minus 0.25pt\relax
    \settowidth\labelwidth{\@biblabel{##1}}%
    \leftmargin\labelwidth
    \advance\leftmargin\labelsep
    \usecounter{enumiv}%
    \let\p@enumiv\@empty
    \labelsep 8pt\labelwidth 13.5pt
    \itemsep  2pt
    \parskip4pt\topsep4pt
    \def\theenumiv{\arabic{enumiv}}}%
    \def\newblock{\hskip .11em plus.33em minus.07em}%
    \sloppy\clubpenalty4000\widowpenalty4000
    \sfcode`\.=1000\relax
    \parsep0pt}}

\setcounter{secnumdepth}{3}
\newcounter {part}
\newcounter {section}
\newcounter {subsection}[section]
\newcounter {subsubsection}[subsection]
\newcounter {paragraph}[subsubsection]
\newcounter {subparagraph}[paragraph]
\renewcommand \thepart {\@Roman\c@part}
\renewcommand \thesection {\@arabic\c@section}
\renewcommand\thesubsection   {\thesection.\@arabic\c@subsection}
\renewcommand\thesubsubsection{\thesubsection .\@arabic\c@subsubsection}
\renewcommand\theparagraph    {\thesubsubsection.\@arabic\c@paragraph}
\renewcommand\thesubparagraph {\theparagraph.\@arabic\c@subparagraph}
\newcommand\part{\par
   \addvspace{4ex}%
   \@afterindentfalse
   \secdef\@part\@spart}

\def\@part[#1]#2{%
    \ifnum \c@secnumdepth >\m@ne
      \refstepcounter{part}%
      \addcontentsline{toc}{part}{\thepart\hspace{1em}#1}%
    \else
      \addcontentsline{toc}{part}{#1}%
    \fi
    {\parindent \z@ \raggedright
     \interlinepenalty \@M
     \normalfont
     \ifnum \c@secnumdepth >\m@ne
       \Large\bfseries \partname~\thepart
       \par\nobreak
     \fi
     \huge \bfseries #2%
     \markboth{}{}\par}%
    \nobreak
    \vskip 3ex
    \@afterheading}
\def\@spart#1{%
    {\parindent \z@ \raggedright
     \interlinepenalty \@M
     \normalfont
     \huge \bfseries #1\par}%
     \nobreak
     \vskip 3ex
     \@afterheading}

\def\section{\@startsection {section}{1}{\z@}
    {23pt plus 1pt minus 1pt}
    {12pt}
    {\reset@font\hyphenpenalty9999\TEN\bfseries\hangindent1.33pc}}

\def\subsection{\@startsection{subsection}{2}{\z@}
    {20pt plus 1pt minus 1pt}
    {10pt}
    {\reset@font\hyphenpenalty9999\TEN\it\hangindent1.95pc}}

\def\subsubsection{\@startsection{subsubsection}{3}{\z@}
    {12pt plus 6pt minus 6pt}
    {12pt}
    {\reset@font\TEN\SECRR}}

\def\paragraph{\@startsection{paragraph}{4}{0pt}
    {13pt plus 4pt minus 2pt}
    {-10pt}
    {\reset@font\TEN\SECRR\it }}

\def\subparagraph{\@startsection{subparagraph}{5}{18pt}
    {13pt plus 4pt minus 2pt}
    {-10pt}
    {\reset@font\TEN\SECRR\bf }}
\if@twocolumn
  \setlength\leftmargini  {2em}
\else
  \setlength\leftmargini  {2.5em}
\fi
\leftmargin  \leftmargini
\setlength\leftmarginii  {2.2em}
\setlength\leftmarginiii {1.87em}
\setlength\leftmarginiv  {1.7em}
\if@twocolumn
  \setlength\leftmarginv  {.5em}
  \setlength\leftmarginvi {.5em}
\else
  \setlength\leftmarginv  {1em}
  \setlength\leftmarginvi {1em}
\fi
\setlength  \labelsep  {.5em}
\setlength  \labelwidth{\leftmargini}
\addtolength\labelwidth{-\labelsep}
\@beginparpenalty -\@lowpenalty
\@endparpenalty   -\@lowpenalty
\@itempenalty     -\@lowpenalty
\renewcommand\theenumi{\@arabic\c@enumi}
\renewcommand\theenumii{\@alph\c@enumii}
\renewcommand\theenumiii{\@roman\c@enumiii}
\renewcommand\theenumiv{\@Alph\c@enumiv}
\newcommand\labelenumi{\theenumi.}
\newcommand\labelenumii{(\theenumii)}
\newcommand\labelenumiii{\theenumiii.}
\newcommand\labelenumiv{\theenumiv.}
\renewcommand\p@enumii{\theenumi}
\renewcommand\p@enumiii{\theenumi(\theenumii)}
\renewcommand\p@enumiv{\p@enumiii\theenumiii}
\newcommand\labelitemi{\textbullet}
\newcommand\labelitemii{\normalfont\bfseries \textendash}
\newcommand\labelitemiii{\textasteriskcentered}
\newcommand\labelitemiv{\textperiodcentered}
\newenvironment{description}
               {\list{}{\labelwidth\z@ \itemindent-\leftmargin
                        \let\makelabel\descriptionlabel}}
               {\endlist}
\newcommand*\descriptionlabel[1]{\hspace\labelsep
                                \normalfont\bfseries #1}
\newenvironment{verse}
               {\let\\\@centercr
                \list{}{\itemsep      \z@
                        \itemindent   -1.5em%
                        \listparindent\itemindent
                        \rightmargin  \leftmargin
                        \advance\leftmargin 1.5em}%
                \item\relax}
               {\endlist}
\newenvironment{quotation}
               {\list{}{\listparindent 1.5em%
                        \itemindent    \listparindent
                        \rightmargin   \leftmargin
                        \parsep        \z@ \@plus\p@}%
                \item\relax}
               {\endlist}
\newenvironment{quote}
               {\list{}{\rightmargin\leftmargin}%
                \item\relax}
               {\endlist}
\if@compatibility
\newenvironment{titlepage}
    {%
      \if@twocolumn
        \@restonecoltrue\onecolumn
      \else
        \@restonecolfalse\newpage
      \fi
      \thispagestyle{empty}%
      \setcounter{page}\z@
    }%
    {\if@restonecol\twocolumn \else \newpage \fi
    }
\else
\newenvironment{titlepage}
    {%
      \if@twocolumn
        \@restonecoltrue\onecolumn
      \else
        \@restonecolfalse\newpage
      \fi
      \thispagestyle{empty}%
      \setcounter{page}\@ne
    }%
    {\if@restonecol\twocolumn \else \newpage \fi
     \if@twoside\else
        \setcounter{page}\@ne
     \fi
    }
\fi
\newcommand\appendix{\par
  \setcounter{section}{0}%
  \setcounter{subsection}{0}%
  \renewcommand\thesection{\@Alph\c@section}}
\setlength\arraycolsep{5\p@}
\setlength\tabcolsep{6\p@}
\setlength\arrayrulewidth{.4\p@}
\setlength\doublerulesep{2\p@}
\setlength\tabbingsep{\labelsep}
\skip\@mpfootins = \skip\footins
\setlength\fboxsep{3\p@}
\setlength\fboxrule{.4\p@}
\renewcommand \theequation {\@arabic\c@equation}
\newcounter{figure}
\renewcommand \thefigure {\@arabic\c@figure}
\def\fps@figure{tbp}
\def\ftype@figure{1}
\def\ext@figure{lof}
\def\fnum@figure{\figurename~\thefigure}
\newenvironment{figure}
               {\@float{figure}}
               {\end@float}
\newenvironment{figure*}
               {\@dblfloat{figure}}
               {\end@dblfloat}
\newcounter{table}
\renewcommand\thetable{\@arabic\c@table}
\def\fps@table{tbp}
\def\ftype@table{2}
\def\ext@table{lot}
\def\fnum@table{\tablename~\thetable}
\newenvironment{table}
               {\@float{table}}
               {\end@float}
\newenvironment{table*}
               {\@dblfloat{table}}
               {\end@dblfloat}
\newlength\abovecaptionskip
\newlength\belowcaptionskip
\setlength\abovecaptionskip{10\p@}
\setlength\belowcaptionskip{0\p@}
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\@makecaption!!!
%%%%%%%%%%%%%%%%%%%%%%%%%%%ragu
\long\def\@makecaption#1#2{\parindent0pt
\ifx\@captype\@tabtxt
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%TABLE
\NINE
\par\noindent\hbox to\textwidth{\hfil\parbox{\tabw}{\noindent %
   {\tabnamefont #1.}\quad #2\HD{0}{18}\endgraf}\hfil}
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
\else %% if it is a figure!
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%FIGURE
\NINE
\par\noindent{\fignamefont #1\HD{7}{0}}\qquad
#2\vspace{6pt}
\fi}

\DeclareOldFontCommand{\rm}{\normalfont\rmfamily}{\mathrm}
\DeclareOldFontCommand{\sf}{\normalfont\sffamily}{\mathsf}
\DeclareOldFontCommand{\tt}{\normalfont\ttfamily}{\mathtt}
\DeclareOldFontCommand{\bf}{\normalfont\bfseries}{\mathbf}
\DeclareOldFontCommand{\it}{\normalfont\itshape}{\mathit}
\DeclareOldFontCommand{\sl}{\normalfont\slshape}{\@nomath\sl}
\DeclareOldFontCommand{\sc}{\normalfont\scshape}{\@nomath\sc}
\DeclareRobustCommand*\cal{\@fontswitch\relax\mathcal}
\DeclareRobustCommand*\mit{\@fontswitch\relax\mathnormal}
\newcommand\@pnumwidth{1.55em}
\newcommand\@tocrmarg{2.55em}
\newcommand\@dotsep{4.5}
\setcounter{tocdepth}{3}
\newcommand\tableofcontents{%
    \section*{\contentsname
        \@mkboth{%
           \MakeUppercase\contentsname}{\MakeUppercase\contentsname}}%
    \@starttoc{toc}%
    }
\newcommand*\l@part[2]{%
  \ifnum \c@tocdepth >-2\relax
    \addpenalty\@secpenalty
    \addvspace{2.25em \@plus\p@}%
    \begingroup
      \parindent \z@ \rightskip \@pnumwidth
      \parfillskip -\@pnumwidth
      {\leavevmode
       \large \bfseries #1\hfil \hb@xt@\@pnumwidth{\hss #2}}\par
       \nobreak
       \if@compatibility
         \global\@nobreaktrue
         \everypar{\global\@nobreakfalse\everypar{}}%
      \fi
    \endgroup
  \fi}
\newcommand*\l@section[2]{%
  \ifnum \c@tocdepth >\z@
    \addpenalty\@secpenalty
    \addvspace{1.0em \@plus\p@}%
    \setlength\@tempdima{1.5em}%
    \begingroup
      \parindent \z@ \rightskip \@pnumwidth
      \parfillskip -\@pnumwidth
      \leavevmode \bfseries
      \advance\leftskip\@tempdima
      \hskip -\leftskip
      #1\nobreak\hfil \nobreak\hb@xt@\@pnumwidth{\hss #2}\par
    \endgroup
  \fi}
\newcommand*\l@subsection{\@dottedtocline{2}{1.5em}{2.3em}}
\newcommand*\l@subsubsection{\@dottedtocline{3}{3.8em}{3.2em}}
\newcommand*\l@paragraph{\@dottedtocline{4}{7.0em}{4.1em}}
\newcommand*\l@subparagraph{\@dottedtocline{5}{10em}{5em}}
\newcommand\listoffigures{%
    \section*{\listfigurename
      \@mkboth{\MakeUppercase\listfigurename}%
              {\MakeUppercase\listfigurename}}%
    \@starttoc{lof}%
    }
\newcommand*\l@figure{\@dottedtocline{1}{1.5em}{2.3em}}
\newcommand\listoftables{%
    \section*{\listtablename
      \@mkboth{%
          \MakeUppercase\listtablename}{\MakeUppercase\listtablename}}%
    \@starttoc{lot}%
    }
\let\l@table\l@figure

\def\LM{\leavevmode }
\newenvironment{BL}{%
 \begin{list}{\LM\hbox{$\bullet$}}{%
 \topsep=6pt plus 3pt minus 2pt
 \partopsep=0pt
 \itemsep=4pt %2pt
 \parsep=0pt
 \labelsep=15pt
 \labelwidth=10pt
 \rightmargin=0pt
 \listparindent=0pt
 \itemindent=0pt %=\leftmargin
 \leftmargin=20pt}}{\end{list}}%

\floatsep 16pt plus 1pt minus 0pt
\textfloatsep 16pt plus 1pt minus 0pt
\intextsep 0pt plus 12.5pt minus 0pt
\@fptop 0pt plus 1fil
\@fpsep 8pt plus 2fil
\@fpbot 0pt plus 1fil

\newenvironment{inFig}
{\vskip 14pt\noindent\hskip -0pt}
{\vskip 10pt}

\newif\if@ttirotate \@ttirotatefalse
\def\ttirotate{\global\@ttirotatetrue}
\def\endttirotate{\global\@ttirotatefalse}

%------ Figures intro
\newcommand\listfigurename{List of Figures}
\def\thefigure{\arabic{figure}}
\def\fignamefont{\NINE}
\def\tabnamefont{\NINE}

%------ Tables intro
\newbox\@tempboxb
\newcommand\tablename{Table}
\newcommand\listtablename{List of Tables}
\renewcommand\thetable{\arabic{table}}
\def\fps@table{tbp}\def\ftype@table{2}\def\ext@table{lot}
\def\fnum@table{{\tabnamefont\bf\tablename\ \thetable}}
\def\table{\let\@makecaption\@tablecaption\@float{table}}
\let\endtable\end@float
\@namedef{table*}{\let\@makecaption\@tablecaption\@dblfloat{table}}
\@namedef{endtable*}{\end@dblfloat}

\long\def\@tablecaption#1#2{%
% Set TN followed by the caption see the length
  \setbox\@tempboxa
  \hbox{\NINE{\it #1}\quad #2}%
% Set the caption only to examine its existence and length if any
  \setbox\@tempboxb
  \hbox{\NINE#2}%
% If no caption, TN centers with no period after it
  \ifdim\wd\@tempboxb < 3pt
    \begin{Center}\NINE
    \HD{8}{0}{\it #1}\HD{0}{6}\end{Center}
  \else
% If TN+caption shorter than the table
  \ifdim\wd\@tempboxa < \tempdime
    %\begin{Center}
    \NINE \HD{8}{0}{\it #1}\qquad #2\HD{0}{6}%\end{Center}
  \else
% If TN+caption longer than the table
    \noindent\NINE\HD{8}{0}{\it #1}\quad
    #2\HD{0}{6}\endgraf
  \fi\fi}

%------TABLE

\newbox\boxH
\newbox\boxHrunin
\newbox\temptbox
\newbox\temptboxA

\newdimen\tempdime
\newdimen\tempdimeA
\newdimen\rboxh
\newdimen\rboxw
\def\EGT{\footnotesize}

\newcommand{\TABLE}[3]{%
  \setbox\temptbox=\hbox{{\EGT#2}}%
  \tempdime\wd\temptbox%
  \@TABLE{#1\vs{2}}{#2}{#3}{\tempdime}}

\newcommand{\@TABLE}[4]{%
\long\def\testtabnote{#3}%
\long\def\itis@empty{}%
\ifx\testtabnote\itis@empty
  \long\def\tabnote##1{\relax}%
\else
  \long\def\tabnote##1{\par{\NINE \vspace*{4pt} ##1\endgraf}}%
\fi
\if@ttirotate
  \setbox4=\hbox to #4 %%\textheight
  {\vbox to \textwidth{\hsize #4 %%%\textheight
  \vss\overfullrule=0pt
  \begin{minipage}[c]{#4}%
    \caption{#1}%
    {\NINE#2}
    \tabnote{\hspace*{3pc}#3}%
  \end{minipage}%
  \vss}}
\else
  \setbox4=\hbox to \hsize{\hss
  % Table should be indented by 2pc
  %  from left margin
  \begin{minipage}[t]{#4}%
    \caption{#1}%
    {\NINE#2}%
    \tabnote{\hspace*{3pc}#3}%
  \end{minipage}\hss}
\fi
\if@ttirotate
  \setbox5=\zeroCC{\box4}%
  \par\noindent\hspace*{0.5\textwidth}%
  \vrule width 0pt height 0.5\textheight depth 0.499\textheight
  \rotatebox{90}{\box5}%
\else
  \noindent\box4%
\fi
}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%-b-figures-and-tables

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%BBB
%%% FIGURES AND TABLES

\setcounter{topnumber}{3}
\def\topfraction{0.99}
\setcounter{bottomnumber}{2}
\def\bottomfraction{.99}
\setcounter{totalnumber}{5}
\def\textfraction{.08}
\def\floatpagefraction{.55}
\setcounter{dbltopnumber}{3}
\def\dbltopfraction{.9}
\def\dblfloatpagefraction{.5}

% FIGURE

\def\fps@figure{tbp}
\def\ftype@figure{1}
\def\ext@figure{lof}
\def\fnum@figure{\bf Figure\ \thefigure}
\def\figure{\@float{figure}}
\let\endfigure\end@float
\@namedef{figure*}{\@dblfloat{figure}}
\@namedef{endfigure*}{\end@dblfloat}

\newenvironment{theindex}
               {\if@twocolumn
                  \@restonecolfalse
                \else
                  \@restonecoltrue
                \fi
                \columnseprule \z@
                \columnsep 35\p@
                \twocolumn[\section*{\indexname}]%
                \@mkboth{\MakeUppercase\indexname}%
                        {\MakeUppercase\indexname}%
                \thispagestyle{plain}\parindent\z@
                \parskip\z@ \@plus .3\p@\relax
                \let\item\@idxitem}
               {\if@restonecol\onecolumn\else\clearpage\fi}
\newcommand\@idxitem{\par\hangindent 40\p@}
\newcommand\subitem{\@idxitem \hspace*{20\p@}}
\newcommand\subsubitem{\@idxitem \hspace*{30\p@}}
\newcommand\indexspace{\par \vskip 10\p@ \@plus5\p@ \@minus3\p@\relax}
\renewcommand\footnoterule{%
  \kern-3\p@
  \hrule\@width.4\columnwidth
  \kern2.6\p@}
\newcommand\@makefntext[1]{%
    \parindent 1em%
    \noindent
    \hb@xt@1.8em{\hss\@makefnmark}#1}
\newcommand\contentsname{Contents}
\newcommand\refname{References}
\newcommand\indexname{Index}
\newcommand\figurename{Figure}
\newcommand\partname{Part}
\newcommand\appendixname{Appendix}
\def\p#1{\phantom{#1}}
\def\vvp{\vadjust{\vfill\pagebreak}}
\def\vvsp#1{\vadjust{\vspace{#1pt}\pagebreak}}
\def\vvSP#1{\HD{0}{#1}\pagebreak}
\def\tra#1{\spaceskip 0.#1em plus 0.15em minus 0.09em\relax}%
\def\vs#1{\vadjust{\vspace{#1pt}}}
\def\mathtight{
\thickmuskip2mu \thinmuskip1mu \medmuskip=1.5mu\relax}

\def\hline{\noalign{\ifnum0=`}\fi\hrule \@height .5pt \futurelet
  \reserved@a\@xhline}
\def\@xhline{\ifx\reserved@a\hline\vskip\doublerulesep
  \vskip-0.5pt\fi\ifnum0=`{\fi}}

% Thick 1 pt table rules
\def\Hline{\noalign{\ifnum0=`}\fi\hrule \@height .7pt \futurelet
  \reserved@a\@xHLINE}
\def\@xHline{\ifx\reserved@a\Hline\vskip0.5pt\vskip\doublerulesep
  \vskip-1pt\fi\ifnum0=`{\fi}}

% Thick 2 pt table rules
\def\HLINE{\noalign{\ifnum0=`}\fi\hrule \@height 2.0pt \futurelet
  \reserved@a\@xHLINE}
\def\@xHLINE{\ifx\reserved@a\HLINE\vskip1pt\vskip\doublerulesep
  \vskip-1pt\fi\ifnum0=`{\fi}}
\headsep -3.7pt
\topskip=6pt %% \headsep + \topskip s/b here 27pt (17+10)
\footskip 0pt
\textheight=578pt %% = 46 x 12 + 10 = 47 lines of text 10/12
\textwidth=30pc
\columnsep 12pt\columnseprule 0pt

\def\today{\ifcase\month\or
  January\or February\or March\or April\or May\or June\or
  July\or August\or September\or October\or November\or December\fi
  \space\number\day, \number\year}
\setlength\columnsep{10\p@}
\setlength\columnseprule{0\p@}
\pagestyle{headings}
\pagenumbering{arabic}
\if@twoside
\else
  \raggedbottom
\fi
\if@twocolumn
  \twocolumn
  \sloppy
  \flushbottom
\else
  \onecolumn
\fi
\endinput
%%
%% End of file `article.cls'.
