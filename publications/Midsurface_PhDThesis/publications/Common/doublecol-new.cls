\NeedsTeXFormat{LaTeX2e}[1995/12/01] \ProvidesClass{singlecol}
              [1998/05/05 v1.3y
 Standard LaTeX document class]

%\def\clsdir{C:/Inderscience/IJBRA-sample}
\RequirePackage{epsf,endnotes,ifthen,dcolumn,graphics,leqno,calc,lastpage,color}

\usepackage{amsmath,amsfonts,amssymb,bm,latexsym}

%\usepackage[LY1]{fontenc}
%
%\edef\@tempa{\rmdefault}
%\def\@tempb {cmr}
%\ifx\@tempa\@tempb
%  \renewcommand*\sfdefault{phv}
%  \renewcommand*\rmdefault{ptm}
%  \renewcommand*\ttdefault{fftt}
%  \renewcommand*\bfdefault{b}
%\fi

\DeclareOldFontCommand{\RMbi}{\rmfamily\bfseries\itshape}{\mathbi}
   \let\bi=\RMbi

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
   {\setlength\paperheight {9.5in}%
    \setlength\paperwidth  {6.5in}}
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
    {8.26in}{11.68in}{-1in}{-1in}}}
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

%\DeclareFontFamily{LY1}{fftt}{}%
%\DeclareFontShape{LY1}{fftt}{m}{n}{<->jmcrxr}
%  {\hyphenchar\font=-1}%
%\DeclareFontShape{LY1}{fftt}{m}{it}{<->jmcrxi}
%  {\hyphenchar\font=-1}%
%\DeclareFontShape{LY1}{fftt}{b}{n}{<->jmcrxb}
%  {\hyphenchar\font=-1}%
%\DeclareFontShape{LY1}{fftt}{b}{it}{<->jmcrxw}
%  {\hyphenchar\font=-1}%

\def\SEVEN{\fontsize{7}{9}\selectfont}
\def\EGT{\fontsize{8}{10}\selectfont}
\def\NINE{\fontsize{9}{10}\selectfont}
\def\TEN{\fontsize{10}{12}\selectfont}
\def\ELEVEN{\fontsize{11}{13}\selectfont}
\def\TWELVE{\fontsize{12}{14}\selectfont}
\def\THIRTEEN{\fontsize{13}{15}\selectfont}
\def\FOURTEEN{\fontsize{14}{16}\selectfont}
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

\newcolumntype{d}[1]{D{.}{.}{#1}}

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
    \begin{tabular}{@{}c@{}}\\[-15pt]%
%    \TEN\hskip -1pt\today\\[27pt]%
  \hbox to \textwidth{\hspace*{36pt}{\TEN\it\spaceskip0.41em\setRRH}\hfill{\TEN\thepage}}
    \end{tabular}
  }}%

\def\setevenRH{\VRHDW{\headheight}{0pt}{0pt}\CROPMARKS%
  \raisebox{0pt}[\headheight][0pt]{%
% \marginnumbering
  \begin{tabular}{@{}c@{}}\\[-15pt]%
%    \TEN\hskip -1pt\today \\[30pt]%
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
     \def\@oddhead{\it \CROPMARKS\TEN \theJOURNALNAME, Vol. \theVOL, No. \theISSUE, \thePUBYEAR\hfill{\rm \thepage}}%
     \let\@evenhead=\@oddhead
     \def\@oddfoot{\NINE Copyright \copyright\ 2009 Inderscience Enterprises Ltd.\hfill}%
     \def\@evenfoot{\NINE Copyright \copyright\ 2009 Inderscience Enterprises Ltd.\hfill}}

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

\def\DS{\displaystyle}

\def\KLUWERLOGO{\epsffile[0 0 16 18]{aglogo3.eps}}%

\def\setfirstoddFOOT{\hfil}
\def\setfirstevenFOOT{\hfil}

\def\JOURNALNAME#1{\gdef\theJOURNALNAME{#1}}%
\def\VOL#1{\gdef\theVOL{#1}}%
\VOL{0}%
\def\PAGES#1{\gdef\thePAGES{#1}}%
\PAGES{\thepage--\pageref{LastPage}}%
\def\PUBYEAR#1{\gdef\thePUBYEAR{#1}}%
\PUBYEAR{20XX}%
\def\ISSUE#1{\gdef\theISSUE{#1}}%
\ISSUE{00}%

\JOURNALNAME{\TEN{\it Int. J. XXX}}%
\def\jtitlefont{\fontsize{16}{22}\selectfont\rm}

\def\Dnum#1{\gdef\theDnum{#1}}%
\Dnum{Please enter the Dekker No}%

\def\CLline{{\CROPMARKS\vskip -36pt \fontsize{9}{12}\selectfont
\TEN\hskip -1pt\\
\NINE{\theJOURNALNAME\\[9pt]
%Vol. \theVOL, No. \theISSUE, pp. \thePAGES, \thePUBYEAR}
}\endgraf}\vspace*{38pt}}%

\def\BottomCatch{%
\vskip -10pt
\thispagestyle{empty}%
\begin{table}[b]%
\NINE\begin{tabular*}{\textwidth}{@{\extracolsep{\fill}}lcr@{}}%
\\[-12pt]
Copyright \copyright\ 20XX Inderscience Enterprises Ltd. & &%
\end{tabular*}%
\vskip -15pt%
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

\def\authorA#1{\gdef\@authorA{\bf #1}}%{\authfont #1}}
\def\authorB#1{\gdef\@authorB{\bf #1}}%{\authfont #1}}
\def\authorC#1{\gdef\@authorC{\bf #1}}%{\authfont #1}}
\def\authorD#1{\gdef\@authorD{\bf #1}}%{\authfont #1}}

\def\affA#1{\gdef\@affA{\TEN #1}}
\def\affB#1{\gdef\@affB{\TEN #1}}
\def\affC#1{\gdef\@affC{\TEN #1}}
\def\affD#1{\gdef\@affD{\TEN #1}}

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
    \parindent10pt\leftskip 12.75pc%\rightskip 3pc%
    \noindent{\bf\TEN \abstractname}\ %\vskip 12.8pt
    \noindent\NINE%
    \ignorespaces}%
\def\endabstract{\egroup}

\newcommand\bioname{\NINE Biographical notes:}
\newbox\t@bio
\def\bio{\@ifnextchar[{\@bio}{\@bio[]}}
\def\@bio[#1]{%
  \global\setbox\t@bio=\vbox\bgroup%
    \parindent10pt\leftskip 12.75pc%\rightskip 3pc%
    \noindent{\bf\TEN \bioname}\ %\vskip 12.8pt
    \noindent\NINE%
    \ignorespaces}%
\def\endbio{\egroup}

%\font\titfont=ARIALBD at 14pt
%\font\authfont=ARIAL at 14pt

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
%        \@maketitle
          \twocolumn[\@maketitle]%
%      \fi
      \thispagestyle{plain}
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
    \let \footnote \thanks%
      {%
       \hyphenpenalty 10000%
        \begin{Flushleft}
        \vskip-1pc
        \leftskip 12.75pc plus 20pc
        \rule{30pc}{1.5pt}\\%[1pt]
        \baselineskip16pt plus .2pt minus .2pt
         \HD{0}{0}\FOURTEEN%\titfont
         {\bf \@title}\\[-8pt]
         \rule{30pc}{1.5pt}\HD{0}{6}%
         \end{Flushleft}
            \par}%
%%%authorA  %GGG
    \ifx\@authorA\undefined%
    \else%
      \begin{Flushleft}%
        \baselineskip16pt plus .25pt minus .24pt
         \leftskip 12.75pc plus 20pc  %\rightskip 3pc plus 20pc
    \HD{19}{0}\FOURTEEN\@authorA\HD{0}{0}
    \end{Flushleft}%
    \fi\par%
    \ifx\@affA\undefined%
    \else
      \begin{Flushleft}%
    \HD{15}{0}%
    \leftskip 12.75pc plus 0pt  %\rightskip 3pc plus 0pt
    \@affA\HD{0}{12}%
      \end{Flushleft}%
          \fi%
%%%
    \ifx\@authorB\undefined%
    \else%
      \begin{Flushleft}%
    \leftskip 12.75pc plus 20pc  %\rightskip 3pc plus 20pc
    \HD{10}{0}\FOURTEEN\@authorB\HD{0}{0}
    \end{Flushleft}
    \fi%
    \ifx\@affB\undefined%
    \else \begin{Flushleft}\HD{15}{0}%
    \leftskip 12.75pc plus 0pc  %\rightskip 3pc plus 20pc
    \@affB\HD{0}{12}%
    \end{Flushleft}%%
    \fi%
%%%
%%%
    \ifx\@authorC\undefined%
    \else%
      \begin{Flushleft}%
    \leftskip 12.75pc plus 20pc  %\rightskip 3pc plus 20pc
    \HD{10}{0}\FOURTEEN\@authorC\HD{0}{0}
    \end{Flushleft}
    \fi%
    \ifx\@affC\undefined%
    \else \begin{Flushleft}\HD{15}{0}%
    \leftskip 12.75pc plus 0pc  %\rightskip 3pc plus 20pc
    \@affC\HD{0}{12}%
    \end{Flushleft}%%
    \fi%
%%%
%%%
    \ifx\@authorD\undefined%
    \else%
      \begin{Flushleft}%
    \leftskip 12.75pc plus 20pc  %\rightskip 3pc plus 20pc
    \HD{10}{0}\FOURTEEN\@authorD\HD{0}{0}
    \end{Flushleft}
    \fi%
    \ifx\@affD\undefined%
    \else \begin{Flushleft}\HD{15}{0}%
    \leftskip 12.75pc plus 0pc  %\rightskip 3pc plus 20pc
    \@affD\HD{0}{12}%
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
    \HD{0}{0}%
%    \tableofcontents
    \noindent\leftskip 12.75pc%\rightskip 3pc%
    {\unvbox\t@abstract}%
%     \end{Center}%
    \ifx\@KEYWORD\undefined%
    \else%
    \noindent\leftskip 12.75pc%\rightskip 3pc%
     \HD{19}{0}\NINE{\bf Keywords:}\ \@KEYWORD \HD{0}{0}\par%
     \fi
        \ifx\@REF\undefined%
    \else%
    \noindent\leftskip 12.75pc%\rightskip 3pc%
     \HD{21}{0}\NINE{\bf Reference}\  \@REF \HD{0}{0}\par%
    \fi%
    \HD{12}{0}{\unvbox\t@bio}%
%%bio
      \noindent\leftskip 0pc%\rightskip 2pc
             \HD{18.5}{0}\rule{42.5pc}{1.5pt}
  \vskip 20pt plus 3pt minus 2pt%
  \relax%
}%


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%-b-THEOREM

\RequirePackage{theorem}

\gdef\th@TH{%
  \def\theorem@headerfont{\normalfont\mdseries\bf}%
  \theorempreskipamount=12pt plus 1pt minus 1pt%
  \theorempostskipamount=12pt plus 1pt minus 1pt%
  \def\@begintheorem##1##2{\normalfont\it%
        \item[\noindent\hskip\labelsep\theorem@headerfont\bf ##1\ ##2:]\enskip}%
  \def\@opargbegintheorem##1##2##3{\normalfont\it%
        \item[\noindent\hskip\labelsep\theorem@headerfont{\bf ##3:}]\enskip}}

%This is defined to get Rule Case, definition, Example etc.
\gdef\th@THrm{%
  \def\theorem@headerfont{\normalfont\mdseries\bf}%
  \theorempreskipamount=12pt plus 1pt minus 1pt%
  \theorempostskipamount=12pt plus 1pt minus 1pt%
  \labelsep 0.5em %%10pt
  \def\@begintheorem##1##2{\normalfont\rm
        \item[\noindent\hskip\labelsep\theorem@headerfont{\bf ##1\ ##2:}]\enskip}%
  \def\@opargbegintheorem##1##2##3{\normalfont\rm
        \item[\noindent\hskip\labelsep\theorem@headerfont {{\bf ##3:}}]\enskip}}

\gdef\th@THhit{%
  \def\theorem@headerfont{\normalfont\mdseries\scshape}%
  \theorempreskipamount=12pt plus 1pt minus 1pt%
  \theorempostskipamount=12pt plus 1pt minus 1pt%
  \labelsep 0.5em %%10pt
  \def\@begintheorem##1##2{\it
        \item[\noindent\hskip\labelsep\theorem@headerfont {\bf ##1}\ {\bf ##2:}]\enskip}%
  \def\@opargbegintheorem##1##2##3{\normalfont\it
        \item[\noindent\hskip\labelsep\theorem@headerfont {\bf ##3:}]\enskip}}

\gdef\th@THkeyall{%
  \def\theorem@headerfont{\normalfont\mdseries\scshape}%
  \theorempreskipamount=12pt plus 6pt minus 3pt%
  \theorempostskipamount=12pt plus 6pt minus 3pt%
  \labelsep 0.5em %%10pt
  \def\@begintheorem##1##2{\normalfont\it
        \item[\indent\hskip\labelsep \theorem@headerfont ##1.]}%
  \def\@opargbegintheorem##1##2##3{\normalfont\it
        \item[\indent]{\theorem@headerfont {##3}\hskip\labelsep}\ignorespaces}}

\gdef\th@EX{%
  \def\theorem@headerfont{\normalfont\mdseries\scshape}%
  \theorempreskipamount=0pt\theorempostskipamount=0pt
  \labelsep 0.5em %%10pt
  \def\@begintheorem##1##2{\normalfont\upshape
        \item[\indent\hskip\labelsep \theorem@headerfont ##1\ ##2.]}%
  \def\@opargbegintheorem##1##2##3{\normalfont\upshape
        \item[\indent\hskip\labelsep \theorem@headerfont ##1\ ##2\ {##3.}]}}

\gdef\th@EXkey{%
  \def\theorem@headerfont{\normalfont\mdseries\scshape}%
  \theorempreskipamount=13pt\theorempostskipamount=13pt
  \labelsep 0.5em %%10pt
  \def\@begintheorem##1##2{\normalfont\upshape
        \item[\indent\hskip\labelsep \theorem@headerfont ##1\ ##2.]}%
  \def\@opargbegintheorem##1##2##3{\normalfont\upshape
        \item[\indent\hskip\labelsep \theorem@headerfont {##3}]}}

\gdef\th@EXkeyall{%
  \def\theorem@headerfont{\normalfont\mdseries\scshape}%
  \theorempreskipamount=0pt\theorempostskipamount=0pt
  \labelsep 0.5em %%10pt
  \def\@begintheorem##1##2{\normalfont\upshape
        \item[\indent\hskip\labelsep \theorem@headerfont ##1\ ##2.]}%
  \def\@opargbegintheorem##1##2##3{\normalfont\upshape
        \item[\indent\hskip\labelsep]{\theorem@headerfont {##3}}}}

\def\problem#1{\noindent{\bf Problem #1.\/}\enskip\rm}
\def\endproblem{\hfill$\square$\vskip 10pt}

\def\theo#1{\vskip 10pt \noindent{\bi Theorem #1.\/}\enskip\it}
\def\endtheo{\hfill$\square$\vskip 12pt}
%% Use for proper proofs that end with extra space (regardless of the use
%% or non-use of \qed (=the black box)
\def\THTrivlist{\parskip0pt\topsep=1.2em plus 0.3em minus 0.2em
  \parsep0pt\partopsep0pt\@nmbrlistfalse
  \@trivlist \labelwidth\z@ \leftmargin\z@
  \itemindent\z@ \def\makelabel##1{##1}}

\let\endTHTrivlist=\endlist

\def\proof#1{\THTrivlist %%\addvspace{0pt}
  \item[\hspace*{0pt}\hskip\labelsep{\it #1}:\enskip]\ignorespaces}
\def\endproof{\hfill $\square$\endTHTrivlist}

\def\endSQproof{\hfill\endTHTrivlist}
% this is to remove square from end of Proof

\def\thproof#1{\vskip-\lastskip\par{ #1.\/}\enskip\rm}
\def\endthproof{\hfill$\square$\vskip 12pt}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%-e-THEOREM

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

\def\notesname{Notes}% <------ JK
\def\enoteheading{\section*{\notesname}%
 \leavevmode\par}

\def\enoteformat{\rightskip\z@ \leftskip6pt \parindent=0em
     \leavevmode\llap{\hbox{$^{\@theenmark}$}}}

\def\enotesize{\footnotesize}

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

\clubpenalty 10000
\widowpenalty 10000
\predisplaypenalty=10000
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

\def\@startsection#1#2#3#4#5#6{\if@noskipsec \leavevmode \fi
   \par \@tempskipa #4\relax
   \@afterindentfalse
   \ifdim \@tempskipa <\z@ \@tempskipa -\@tempskipa \@afterindentfalse\fi
   \if@nobreak \everypar{}\else
     \addpenalty{\@secpenalty}\addvspace{\@tempskipa}\fi \@ifstar
     {\@ssect{#3}{#4}{#5}{#6}}{\@dblarg{\@sect{#1}{#2}{#3}{#4}{#5}{#6}}}}

\def\@sect#1#2#3#4#5#6[#7]#8{%
     \ifnum #2>\c@secnumdepth
       \let\@svsec\@empty
     \else
       \refstepcounter{#1}%
       \edef\@svsec{\csname the#1\endcsname\hskip 9.3pt}%
     \fi
     \@tempskipa #5\relax
      \ifdim \@tempskipa>\z@
        \begingroup #6{\relax
               \parindent0pt
               \@hangfrom{\hskip #3\relax\@svsec}{\interlinepenalty \@M #8\par}}%
        \endgroup
       \csname #1mark\endcsname{#7}\addcontentsline
         {toc}{#1}{\ifnum #2>8 %%%\c@secnumdepth
                     \else
                      \protect\numberline{\csname the#1\endcsname}\fi
                    #7}\else
        \def\@svsechd{#6\hskip #3\relax  %% \relax added 2 May 90
                   \@svsec #8.\csname #1mark\endcsname
                      {#7}\addcontentsline
                           {toc}{#1}{\ifnum #2>\c@secnumdepth \else
                             \protect\numberline{\csname the#1\endcsname}\fi
                       #7}}\fi
     \@xsect{#5}}

\def\@xsect#1{\@tempskipa #1\relax
      \ifdim \@tempskipa>\z@
       \par \nobreak
       \vskip \@tempskipa
       \@afterheading
    \else \global\@nobreakfalse \global\@noskipsectrue
       \everypar{\if@noskipsec \global\@noskipsecfalse
                   \clubpenalty\@M \hskip -\parindent
                   \begingroup \@svsechd \endgroup \unskip
                   \hskip -#1\relax  % relax added 14 Jan 91
                  \else \clubpenalty \@clubpenalty
                    \everypar{}\fi}\fi\ignorespaces}

\def\@ssect#1#2#3#4#5{\@tempskipa #3\relax
   \ifdim \@tempskipa>\z@
     \begingroup #4{\@hangfrom{\hskip #1}{\interlinepenalty \@M #5\par}}\endgroup
   \else \def\@svsechd{#4\hskip #1\relax #5}\fi
    \@xsect{#3}}

\def\section{\@startsection {section}{1}{\z@}
    {24pt plus 4pt minus 4pt}
    {12pt}
    {\reset@font\hyphenpenalty9999\ELEVEN\bfseries\hangindent1.33pc}}

\def\subsection{\@startsection{subsection}{2}{\z@}
    {12pt plus 4pt minus 4pt}
    {10pt}
    {\reset@font\hyphenpenalty9999\ELEVEN\it\raggedright\hangindent1.95pc}}

\def\subsubsection{\@startsection{subsubsection}{3}{\z@}
    {12pt plus 4pt minus 4pt}
    {8pt}
    {\reset@font\hyphenpenalty9999\ELEVEN\it\hangindent1.95pc}}

\def\paragraph{\@startsection{paragraph}{4}{0pt}
    {12pt plus 4pt minus 2pt}
    {-8pt}
    {\reset@font\hyphenpenalty9999\it\hangindent1.95pc}}

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
               {\list{}{\NINE\rightmargin 14pt\leftmargin 14pt}%
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
\setlength\arraycolsep{1\p@}
\setlength\tabcolsep{6\p@}
\setlength\arrayrulewidth{.4\p@}
\setlength\doublerulesep{2\p@}
\setlength\tabbingsep{\labelsep}
\skip\@mpfootins = \skip\footins
\setlength\fboxsep{3\p@}
\setlength\fboxrule{.4\p@}
\newdimen\mathindent
\mathindent=9pt
\renewcommand \theequation {\@arabic\c@equation}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%EQUATIONS
% They are indented from left 2 picas and have on the right eqno as "[23]"
%\def\EQtrivlist{\parskip0pt\topsep=10pt plus 5pt minus 6pt
%   \parsep0pt\partopsep0pt\@nmbrlistfalse
%   \@trivlist \labelwidth\z@ \leftmargin\z@\listparindent\z@
%   \itemindent\z@ \def\makelabel##1{##1}}%
%\def\endEQtrivlist{\if@newlist\@noitemerr\fi
%   \if@inlabel\indent\fi
%   \ifhmode\unskip \par\fi
%   \if@noparlist \else
%      \ifdim\lastskip >\z@ \@tempskipa\lastskip \vskip -\lastskip
%         \advance\@tempskipa\parskip \advance\@tempskipa -\@outerparskip
%         \vskip\@tempskipa
%   \fi\@endparenv\fi}%
%
%%%%%%%%%%%%%%%%%%%%%%-B-fleqn.sty-(modified)
\def\[{\relax\ifmmode\@badmath\else
       \begin{trivlist}%
 \@beginparpenalty\predisplaypenalty
  \@endparpenalty\postdisplaypenalty
  \item[]\leavevmode
  \hbox to\linewidth\bgroup $\m@th\displaystyle
  \hskip\mathindent\bgroup\fi}

\def\]{\relax\ifmmode \egroup $\hfil\displaywidth\linewidth
  \egroup \end{trivlist}\else \@badmath \fi\noindent\ignorespaces}

\def\equation{\@beginparpenalty\predisplaypenalty
  \@endparpenalty\postdisplaypenalty
  \refstepcounter{equation}\trivlist \item[]\leavevmode
  \hbox to\linewidth\bgroup $\m@th\displaystyle\hskip\mathindent}

\def\endequation{$\hfil\displaywidth\linewidth\@eqnnum\egroup\endtrivlist}

\def\VVV{\@beginparpenalty\predisplaypenalty
  \@endparpenalty\postdisplaypenalty
  \EQtrivlist \item[]\leavevmode
  \hbox to\linewidth\bgroup $\m@th\displaystyle\hskip\mathindent}

\def\endVVV{$\hfil\displaywidth\linewidth\egroup\endEQtrivlist}

\def\eqnarray{\stepcounter{equation}\let\@currentlabel=\theequation
  \global\@eqnswtrue
  \global\@eqcnt\z@\tabskip\mathindent\let\\=\@eqncr
  \abovedisplayskip 12pt plus 5pt minus 5pt
  \belowdisplayskip\abovedisplayskip
  \belowdisplayshortskip\abovedisplayskip
  \abovedisplayshortskip\abovedisplayskip
  $$\m@th\halign to\linewidth\bgroup\@eqnsel
  \hskip\@centering
  $\displaystyle\tabskip\z@
  {##}$&\global\@eqcnt\@ne \hfil$\displaystyle{{}##{}}$\hfil
  &\global\@eqcnt\tw@ $\displaystyle{##}$\hfil
   \tabskip\@centering&\llap{##}\tabskip\z@\cr}

\def\endeqnarray{\@@eqncr\egroup
      \global\advance\c@equation\m@ne$$\global\@ignoretrue}

\newdimen\mathindent
\mathindent=9pt %%% \leftmargini

%%%%%%%%%%%%%%%%%%%%-E-fleqn.sty-(modified)


\newcounter{figure}
\renewcommand \thefigure {\@arabic\c@figure}
\def\fps@figure{tbp}
\def\ftype@figure{1}
\def\ext@figure{lof}
\def\fnum@figure{\bf\figurename~\thefigure}
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
\def\fnum@table{\bf\tablename~\thetable}
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
%\long\def\@makecaption#1#2{\parindent0pt
%\ifx\@captype\@tabtxt
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%TABLE
%\NINE
%\par\noindent\hbox to\textwidth{\hfil\parbox{\tabw}{\noindent %
%   {\tabnamefont #1.}\quad\hangindent3.3pc #2\HD{0}{18}\endgraf}\hfil}
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%\else %% if it is a figure!
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%FIGURE
%\NINE
%\par\noindent{\fignamefont #1\HD{7}{0}}\quad
%\hangindent3.2pc\raggedright #2\vspace{6pt} \fi}

\long\def\@makecaption#1#2{\parindent0pt
\ifx\@captype\@tabtxt
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%TABLE
\NINE
\par\noindent\hbox to\textwidth{\hfil\parbox{\tabw}{\noindent %
   {\tabnamefont #1.}\quad\raggedright\hangindent3.3pc #2\HD{0}{18}\endgraf}\hfil}
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
\else %% if it is a figure!
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%FIGURE
\NINE\par\noindent{\fignamefont #1\HD{7}{0}}\quad
\hangindent3.29pc\raggedright #2\vspace{6pt} \fi}

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

\newenvironment{NLh}[1]{%
 \setbox\boxH=\hbox{{\rm #1}}%
 \raggedright
 \begin{list}{\rm{\arabic{enumii}.}}{%
 \usecounter{enumii}%
 \topsep=10pt plus .5pt minus .5pt%
 \partopsep=0pt%
 \itemsep=6pt%
 \parsep=0pt%
 \labelsep=14pt%
 \labelwidth=\wd\boxH%
 \leftmargin=\labelwidth%
 \advance\leftmargin\labelsep%
 \rightmargin=0pt%
 \listparindent=0em%
 \itemindent 0pt\ignorespaces}\mathindent=0pt}{\end{list}}%

\def\LM{\leavevmode }
\newenvironment{BL}{%
 \begin{list}{\LM\hbox{$\bullet$}}{%
\raggedright
 \topsep=10pt plus 4pt minus 4pt
 \partopsep=0pt
 \itemsep=6pt %2pt
 \parsep=0pt
 \labelsep=14pt
 \labelwidth=10pt
 \rightmargin=0pt
 \listparindent=0pt
 \itemindent=0pt %=\leftmargin
 \leftmargin=20pt}\mathindent=0pt}{\end{list}}%

\floatsep 16pt plus 4pt minus 4pt
\textfloatsep 16pt plus 4pt minus 4pt
\intextsep 14pt plus 4pt minus 4pt
\@fptop 0pt plus 1fil \@fpsep 8pt plus
2fil \@fpbot 0pt plus 1fil

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
\def\fnum@table{\tabnamefont\bf\tablename\ \thetable}
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
    \noindent\NINE\HD{8}{0}{\bf #1}\quad
    \raggedright\hangindent3.05pc  #2\HD{0}{6}\endgraf
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
  \setbox\temptboxA=\hbox{{\NINE#1}}%
  \setbox\temptbox=\hbox{{\EGT#2}}%
  \tempdime\wd\temptbox%
  \tempdimeA\wd\temptboxA%
  \@TABLE{\hangindent3.1pc {#1}\vs{2}}{#2}{#3}{\tempdime}}

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
%\def\fnum@figure{\bf Figure\ \thefigure}
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

\renewcommand{\footnote}{\endnote}
\def\enotesize{\NINE}

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

%\font\bb=qp3tir at 10pt
%\def\sst{\mbox{\bb\char"019}}
%\def\aet{\mbox{\bb\char"01A}}
%\def\oet{\mbox{\bb\char"01B}}
%\def\oot{\mbox{\bb\char"01C}}
%\def\AEt{\mbox{\bb\char"01D}}
%\def\OEt{\mbox{\bb\char"01E}}
%\def\OOt{\mbox{\bb\char"01F}}
%
%\font\bs=qp3tir at 9pt
%\def\ssr{\mbox{\bs\char"019}}
%\def\aer{\mbox{\bs\char"01A}}
%\def\oer{\mbox{\bs\char"01B}}
%\def\oor{\mbox{\bs\char"01C}}
%\def\AEr{\mbox{\bs\char"01D}}
%\def\OEr{\mbox{\bs\char"01E}}
%\def\OOr{\mbox{\bs\char"01F}}
%
%\font\gs=r1-tii at 10pt
%\def\UPalpha{\mbox{\gs\char"0C1}}
%\def\UPbeta{\mbox{\gs\char"0C2}}
%\def\UPgamma{\mbox{\gs\char"0C3}}
%\def\UPdelta{\mbox{\gs\char"0C4}}
%\def\UPepsilon{\mbox{\gs\char"0C5}}
%\def\UPzeta{\mbox{\gs\char"0C6}}
%\def\UPeta{\mbox{\gs\char"0C7}}
%\def\UPtheta{\mbox{\gs\char"0C8}}
%\def\UPiota{\mbox{\gs\char"0C9}}
%\def\UPkappa{\mbox{\gs\char"0CA}}
%\def\UPlambda{\mbox{\gs\char"0CB}}
%\def\UPmu{\mbox{\gs\char"0CC}}
%\def\UPnu{\mbox{\gs\char"0CD}}
%\def\UPxi{\mbox{\gs\char"0CE}}
%\def\UPpi{\mbox{\gs\char"0CF}}
%\def\UPrho{\mbox{\gs\char"0D0}}
%\def\UPsigma{\mbox{\gs\char"0D1}}
%\def\UPtau{\mbox{\gs\char"0D2}}
%\def\UPupsilon{\mbox{\gs\char"0D3}}
%\def\UPphi{\mbox{\gs\char"0D4}}
%\def\UPchi{\mbox{\gs\char"0D5}}
%\def\UPpsi{\mbox{\gs\char"0D6}}
%\def\UPomega{\mbox{\gs\char"0D7}}

%%For Table rule

\def\toprule{\noalign{\ifnum0=`}\fi \hrule \@height 2.0pt \hrule
\@height 2pt \@width 0pt \futurelet\@tempa\@xhline}

\def\midrule{\noalign{\ifnum0=`}\fi \hrule \@height 2pt \@width 0pt
\hrule \@height 0.7pt \hrule \@height 2pt \@width 0pt
\futurelet\@tempa\@xhline}

\def\botrule{\noalign{\ifnum0=`}\fi \hrule
\@height 2pt \@width 0pt \hrule \@height 2.0pt
\futurelet\@tempa\@xhline}

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
\topmargin12pt
\headheight12pt
\headsep 14pt
\topskip=4pt %% \headsep + \topskip s/b here 27pt (17+10)
\footskip 36pt
\textheight=704pt %% = 46 x 12 + 10 = 47 lines of text 10/12
\textwidth=42.5pc
\columnsep 22pt
\columnseprule 0pt

\def\ps@kumaresh{\let\@mkboth\markboth
  \def\@oddfoot{\setoddFOOT}%
  \def\@evenfoot{\setevenFOOT}%
  \def\@evenhead{{\VRHDW{\headheight}{0pt}{0pt}\CROPMARKS%
  \raisebox{0pt}[\headheight][0pt]{%
%\hspace*{-25pt}    \marginnumbering\hspace*{18pt}
  \begin{tabular}{@{}c@{}}\\[-15pt]%
  \hbox to
  \textwidth{\spaceskip0.41em{%\TEN\thepage
  }\hfill\centerline{%\TEN\it\setLRH
  }}
    \end{tabular}
  }}}%
  \def\@oddhead{{\VRHDW{\headheight}{0pt}{0pt}\CROPMARKS%
  \raisebox{0pt}[\headheight][0pt]{%
%\hspace*{-25pt}    \marginnumbering\hspace*{18pt}
    \begin{tabular}{@{}c@{}}\\[-15pt]%
 \hbox to \textwidth{\hfill{%\TEN\it\spaceskip0.41em\setRRH
 }\hfill{%\TEN\thepage
 }}
    \end{tabular}
  }}}%
  \def\sectionmark##1{}%
  \def\subsectionmark##1{}}

\newcommand{\querypage}[1]{\def\testquerypage{#1}%
\newpage\thispagestyle{kumaresh}%
\begin{center}
\HD{5}{0}\fontsize{14}{16}\selectfont\bf\MakeUppercase\@title\HD{3}{30}\par
{\TEN \setLRH}\vskip1pc\par
{\TEN Author Queries}
\vskip1pc
\end{center}
\hangindent3.7pc\Q}

\def\Q#1{\noindent \hangindent3.7pc\h{AQ#1 Au:}}

\def\mgpl#1{\marginpar{{\hspace*{-1.8pc}}\EGT #1}}
\def\mgpr#1{\marginpar{{\hspace*{.8pc}\EGT #1}}}


%\def\mgp#1{\marginpar{\kern-6pt{\EGT #1}}}
\def\x{\end{document}}
\def\h{\hbox}
\def\p#1{\phantom{#1}}
\def\vvp{\vadjust{\vfill\pagebreak}}
\def\vvsp#1{\vadjust{\vspace{#1pt}\pagebreak}}
\def\vvSP#1{\HD{0}{#1}\pagebreak}
\def\tra#1{\spaceskip 0.#1em plus 0.15em minus 0.09em\relax}%
\def\vs#1{\vadjust{\vspace{#1pt}}}
\def\mathtight{
\thickmuskip2mu \thinmuskip1mu \medmuskip=1.5mu\relax}

\def\today{\ifcase\month\or
  January\or February\or March\or April\or May\or June\or
  July\or August\or September\or October\or November\or December\fi
  \space\number\day, \number\year}
\setlength\columnsep{22\p@}
\setlength\columnseprule{0\p@}
\setlength\parindent{14\p@}
\pagestyle{headings}

\clubpenalty 10000 \widowpenalty 10000 \predisplaypenalty=10000
\interdisplaylinepenalty=100 \displaywidowpenalty 1500
\postdisplaypenalty 0 %%%500
\interlinepenalty 0
\brokenpenalty 500 % Plain default = 100
\adjdemerits=100 % Plain default = 10000
\linepenalty=10 \doublehyphendemerits=10000 \finalhyphendemerits=5000
\hyphenpenalty=10 \exhyphenpenalty=50
\binoppenalty=150 % 700
\relpenalty=100 % 500
\interfootnotelinepenalty=100
%\nulldelimiterspace=1.2pt
\lefthyphenmin=15
\righthyphenmin=15
\tolerance=9999
\emergencystretch=1.6pc
\frenchspacing

\thinmuskip=3mu
\medmuskip=4mu% plus 1mu minus 1mu
\thickmuskip=5mu% plus 3mu
\def\enotesize{\NINE}

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
%% End of file `doublecol.cls'.
