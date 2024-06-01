%% myConf.cls
\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{myConf}%
[2014/03/14 Style for the Any Conference]

%% Author: Yogesh Kulkarni, Original: Hans-Peter Schroecker, http://geometrie.uibk.ac.at/schroecker/

%% Load ``article.cls'', using options ``12pt'' a4 paper size, and twocolumn layout. 

\LoadClass[a4paper,12pt,twocolumn]{article}

%% Load additional packages

% font selection
\RequirePackage{mathptmx}
\RequirePackage{courier}
\RequirePackage[scaled]{helvet}
\RequirePackage{textcomp}

% page size
\RequirePackage[%
  top=3.00cm,%
  bottom=3.00cm,%
  foot=0.7cm,%
  right=2.00cm,%
  left=2.00cm,%
  includefoot,%
]{geometry}

% two-column layout
\setlength{\columnsep}{7.4mm}

% title and section formatting
\RequirePackage{titlesec}
\RequirePackage{ragged2e}

\titleformat{\section}[hang]
  {\fontsize{12}{12}\normalfont\bfseries}
  {\thesection.}{0.2em}{}
\titlespacing*{\section}{0pt}{1.5ex}{-0.0ex}

\titleformat{\subsection}[hang]
  {\normalfont\bfseries}
  {\thesubsection}{0.2em}{}
\titlespacing*{\subsection}{0pt}{1.5ex}{-0.0ex}

\titleformat{\subsubsection}[runin]
  {\normalfont\normalsize\bfseries}
  {}{0pt}{}[.]

\titleformat{\paragraph}[runin]
  {\normalfont\normalsize\itshape}
  {}{0pt}{}[.]

\titleformat{\subparagraph}[runin]
  {\normalfont\normalsize}
  {}{0pt}{}[.]

% redefine macros for document title and authors

\newcommand*{\@affiliation}{}%
\newcommand{\affiliation}[1]{\gdef\@affiliation{#1}}

\renewcommand*{\@maketitle}{%
  \vspace*{-15.20mm}
  \noindent{\fontsize{10.5}{12}\selectfont\textsf{%
    Conference Name goes here ...%
    \hfill{\footnotesize\textcopyright}20XX Conf%
    }\\
    %\rule[2.40ex]{\linewidth}{0.4pt}\\[-3.5ex]
    \textsf{AA--BB MM, YYYY, PLACE, COUNTRY}}\\
  \rlap{\smash{\parbox[t]{10mm}{\vspace*{248.00mm}Paper~\#\@papernumber}}}
  \vspace*{6.35mm}
  \begin{center}%
    {\normalfont\bfseries\fontsize{14}{17.5}\selectfont
      \@title\par}%
    \vspace*{6.50mm}
    {\begin{tabular}[t]{c}
        % \large
        \bfseries
        \@author
      \end{tabular}\par
    }%
    \vspace*{-0.8mm}
    {\begin{tabular}[t]{c}
        % \large
        \@affiliation
      \end{tabular}\par
    }%
  \end{center}%
}%

% papernumber
\newcommand*{\@papernumber}{}%
\newcommand{\papernumber}[1]{\gdef\@papernumber{#1}}

% abstract and keywords
\renewenvironment{abstract}%
    {\vspace*{4.65mm}\noindent\textbf{Abstract}\\}%
    {\thispagestyle{empty}\pagestyle{myheadings}
      \normalsize\par\vspace*{1.1cm}}%
\newcommand{\keywords}[1]{%
  \vspace*{0.2cm}
  {\par\raggedright\noindent\textbf{Keywords:}~#1}
  \vspace*{0.1cm}}

% bibliography
%\RequirePackage[numbers,sort,compress]{natbib}
\bibliographystyle{PLAIN}

% hyperlinks
\RequirePackage{hyperref}

% math formulas
\RequirePackage{amsmath}

%% Close class file:
\endinput
%% End of ``myConf.cls''
