% -----------------------------------------------------------------------------
% LaTeX class for submissions to GMP 2015
% 
% Kai Hormann <kai.hormann@usi.ch>
% -----------------------------------------------------------------------------
%%
%% This file is 'gmp2015.cls'
%% 
%% It may be distributed and/or modified under the
%% conditions of the LaTeX Project Public License, either version 1.3c
%% of this license or (at your option) any later version.
%% The latest version of this license is in
%%    http://www.latex-project.org/lppl.txt
%% and version 1.3c or later is part of all distributions of LaTeX
%% version 2005/12/01 or later.

\NeedsTeXFormat{LaTeX2e}[1995/12/01]
\ProvidesClass{gmp2015}[2014/10/10 GMP 2015 paper class]

%%
%% use option "submission" to omit author names and affiliations and show the submission number only
%%
\newif\if@submission
\@submissionfalse
\DeclareOption{submission}{\@submissiontrue}

%%
%% include main features from the standard article class
%%
\DeclareOption*{\PassOptionsToClass{\CurrentOption}{article}} 
\ProcessOptions\relax
\LoadClass[twocolumn]{article}

%%
%% enable special characters
%%
\RequirePackage[T1]{fontenc}
\RequirePackage[latin1]{inputenc}

%%
%% section headers in sans-serif
%%
\RequirePackage[sf,bf,small]{titlesec}

%%
%% page settings
%%
\RequirePackage[a4paper,hscale=0.8,vscale=0.85]{geometry}

%%
%% captions settings
%%
\RequirePackage[small,sf,bf]{caption}

%%
%% hyperref settings
%%
\RequirePackage[colorlinks,linkcolor=blue,citecolor=blue,urlcolor=blue]{hyperref}

%%
%% graphics settings
%%
\RequirePackage{graphicx}

%%
%% stick to ams math style
%%
\RequirePackage{amsmath,amsthm,amssymb}

%%
%% commonly uses blackboard letters
%%
\def\NN{\mathbb{N}}
\def\ZZ{\mathbb{Z}}
\def\QQ{\mathbb{Q}}
\def\RR{\mathbb{R}}
\def\CC{\mathbb{C}}

%%
%% Theorems, Lemmas, etc.
%%
\newtheorem{theorem}{\sffamily Theorem}
\newtheorem{lemma}[theorem]{\sffamily Lemma}
\newtheorem{corollary}[theorem]{\sffamily Corollary}
\newtheorem{proposition}[theorem]{\sffamily Proposition}
\newtheorem{definition}[theorem]{\sffamily Definition}
\newtheorem{remark}[theorem]{\sffamily Remark}
\newtheorem{example}[theorem]{\sffamily Example}

%%
%% new commands to pass authors and affiliations
%%
\def\addtok#1#2{\global#1\expandafter{\the#1#2}}
\newcounter{n@authors}
\newtoks\@authors
\renewcommand{\author}[2]{%
  \stepcounter{n@authors}%
  \ifnum \then@authors > 1 \addtok\@authors{, } \fi%
  \addtok\@authors{#1$^{\,#2}$}%
}
\newcounter{n@affiliations}
\newtoks\@affiliations
\newcommand{\affiliation}[2]{%
  \stepcounter{n@affiliations}%
  \ifnum \then@affiliations > 1 \addtok\@affiliations{\newline} \fi%
  \addtok\@affiliations{$^{#1\,}$#2}%
}

%%
%% title page
%%
\renewcommand{\maketitle}{\twocolumn[%
  \newpage\null\vskip2em%
  \if@submission\noindent\emph{\large Submission to GMP 2015}\vskip.75em\fi%
  {\noindent\LARGE\sffamily\bfseries\@title\par}\vskip1em%
  \if@submission\vskip.5em{\large Submission number: }\@SubNumber\vskip1.5em%
  \else\noindent\large\the\@authors\par\vskip1em\noindent\small\the\@affiliations\vskip2em%
  \fi]%
}

%%
%% new command to pass submission number
%%
\newcommand{\SubNumber}[1]{\gdef\@SubNumber{#1}}
\newcommand{\@SubNumber}{\@latex@error{No \noexpand\SubNumber given}\@ehc}

%%
%% abstract 
%%
\renewenvironment{abstract}{
  \hrule\vskip.7em%
  \small\noindent%
  {\sffamily\bfseries\abstractname\vskip.3em}%
  \noindent\ignorespaces%
}{
  \vskip.8em\hrule\vskip1.5em%
  \global\@topnum\z@
}

%%
%% bibliography settings
%%
\renewenvironment{thebibliography}[1]
  {\subsection*{\refname}\small%
  \@mkboth{\MakeUppercase\refname}{\MakeUppercase\refname}%
  \list{\@biblabel{\@arabic\c@enumiv}}%
       {\itemsep 2pt plus 1pt minus 1pt%
        \parsep 1pt%
        \settowidth\labelwidth{\@biblabel{#1}}%
        \leftmargin\labelwidth
        \advance\leftmargin\labelsep
        \@openbib@code
        \usecounter{enumiv}%
        \let\p@enumiv\@empty
        \renewcommand\theenumiv{\@arabic\c@enumiv}}%
  \sloppy
  \clubpenalty4000
  \@clubpenalty \clubpenalty
  \widowpenalty4000%
  \sfcode`\.\@m}
  {\def\@noitemerr
   {\@latex@warning{Empty `thebibliography' environment}}%
  \endlist}

%%
%% font sizes and vertical spacings
%%
\setlength\parindent{1.5em}
\setlength\partopsep{2\p@ \@plus 1\p@ \@minus 1\p@}
\def\@listi{\leftmargin\leftmargini
            \parsep 2\p@ \@plus\p@ \@minus\p@
            \topsep 4\p@ \@plus\p@ \@minus2\p@
            \itemsep2\p@ \@plus\p@ \@minus\p@}
\let\@listI\@listi
\@listi
\def\@listii {\leftmargin\leftmarginii
              \labelwidth\leftmarginii
              \advance\labelwidth-\labelsep
              \topsep    2\p@ \@plus\p@\@minus\p@
              \parsep    \z@
              \partopsep \p@ \@plus\z@ \@minus\p@
              \itemsep   \parsep}
\def\@listiiii {\leftmargin\leftmarginiii
              \labelwidth\leftmarginiii
              \advance\labelwidth-\labelsep}
\def\@listiv {\leftmargin\leftmarginiv
              \labelwidth\leftmarginiv
              \advance\labelwidth-\labelsep}
\def\@listv  {\leftmargin\leftmarginv
              \labelwidth\leftmarginv
              \advance\labelwidth-\labelsep}
\def\@listvi {\leftmargin\leftmarginvi
              \labelwidth\leftmarginvi
              \advance\labelwidth-\labelsep}

\renewcommand\normalsize{%
    \@setfontsize\normalsize\@ixpt{10.5}%
    \abovedisplayskip 7\p@ \@plus3\p@ \@minus4\p@
    \abovedisplayshortskip \z@ \@plus3\p@
    \belowdisplayshortskip 5\p@ \@plus3\p@ \@minus3\p@
    \belowdisplayskip \abovedisplayskip
    \let\@listi\@listI}
\normalsize
\renewcommand\small{%
    \@setfontsize\small\@viiipt{9.5}%
    \abovedisplayskip 6\p@ \@plus3\p@ \@minus4\p@
    \abovedisplayshortskip \z@ \@plus2\p@
    \belowdisplayshortskip 4\p@ \@plus2\p@ \@minus2\p@
    \def\@listi{\leftmargin\leftmargini
                \topsep 4\p@ \@plus2\p@ \@minus2\p@
                \parsep 2\p@ \@plus\p@ \@minus\p@
                \itemsep \parsep}%
    \belowdisplayskip \abovedisplayskip}
\renewcommand\footnotesize{%
    \@setfontsize\footnotesize\@viipt\@viiipt
    \abovedisplayskip 5\p@ \@plus3\p@ \@minus4\p@
    \abovedisplayshortskip \z@ \@plus\p@
    \belowdisplayshortskip 3\p@ \@plus\p@ \@minus\p@
    \def\@listi{\leftmargin\leftmargini
                \topsep 3\p@ \@plus\p@ \@minus\p@
                \parsep 2\p@ \@plus\p@ \@minus\p@
                \itemsep \parsep}%
    \belowdisplayskip \abovedisplayskip}
\renewcommand\scriptsize{\@setfontsize\scriptsize\@vipt\@viipt}
\renewcommand\tiny{\@setfontsize\tiny\@vpt\@vipt}
\renewcommand\large{\@setfontsize\large\@xpt\@xiipt}
\renewcommand\Large{\@setfontsize\Large\@xiipt{14}}
\renewcommand\LARGE{\@setfontsize\LARGE\@xivpt{18}}
\renewcommand\huge{\@setfontsize\huge\@xviipt{22}}
\renewcommand\Huge{\@setfontsize\Huge\@xxpt{25}}

\renewcommand\section{\@startsection {section}{1}{\z@}%
  {-2.5ex \@plus -1ex \@minus -.2ex}%
  {1.3ex \@plus.2ex}%
  {\normalfont\large\sffamily\bfseries}}
\renewcommand\subsection{\@startsection{subsection}{2}{\z@}%
  {-2.25ex\@plus -1ex \@minus -.2ex}%
  {1ex \@plus .2ex}%
  {\normalfont\normalsize\sffamily\bfseries}}
\renewcommand\subsubsection{\@startsection{subsubsection}{3}{\z@}%
  {-2.25ex\@plus -1ex \@minus -.2ex}%
  {1ex \@plus .2ex}%
  {\normalfont\normalsize\sffamily\bfseries}}
\renewcommand\paragraph{\@startsection{paragraph}{4}{\z@}%
  {2.25ex \@plus1ex \@minus.2ex}%
  {-1em}%
  {\normalfont\normalsize\sffamily\bfseries}}
\renewcommand\subparagraph{\@startsection{subparagraph}{5}{\parindent}%
  {2.25ex \@plus1ex \@minus .2ex}%
  {-1em}%
  {\normalfont\normalsize\sffamily\bfseries}}
