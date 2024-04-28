%
% CUEDthesis v1.1
% By Harish Bhanderi <harish.bhanderi@cantab.net
% Version 1.0 released 15/07/2002
% Version 1.1 released 14/07/2010
%-------------------------- Modified by  ---------------------
% Dinesh D. Mali For the Students of CMS | UoP 13/08/2012
%-------------------------- identification ---------------------
%\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{Thesis_UoP}[2010/07/14 v1.1 orig CUED thesis class]
%-------------------------- initial code -----------------------
\newif\ifCU@bookmode
\CU@bookmodetrue

%---------------------------Certificate font ------>>
\newcommand\swabfamily{\usefont{U}{yswab}{b}{n}}
\DeclareTextFontCommand{\textswab}{\swabfamily}

\DeclareOption{report}{\CU@bookmodefalse}
\DeclareOption{book}{\CU@bookmodetrue}
\ProcessOptions\relax%

\ifCU@bookmode
\DeclareOption*{\PassOptionsToClass{\CurrentOption}{book}}%
\ProcessOptions\relax%
\ifx\pdfoutput\undefined%
   \LoadClass[dvips, a4paper,oneside,openany,12pt]{book}%
\else%
   \LoadClass[dvips, a4paper,oneside,openany,12pt]{book}%
\fi%
\else
\DeclareOption*{\PassOptionsToClass{\CurrentOption}{report}}%
\ProcessOptions\relax%
\ifx\pdfoutput\undefined%
  \LoadClass[dvips, a4paper,oneside,openany,12pt]{report}%
\else%
   \LoadClass[dvips, a4paper,oneside,openany,12pt]{report}%
\fi%
%\renewcommand{\refname}{References}%
\fi

%\DeclareOption{book}{%
%}%
\usepackage{setspace}
\usepackage{tocbibind}
\usepackage{amssymb}
%\usepackage{graphicx}
\usepackage{fancyhdr}
\usepackage{eucal}
\usepackage[english]{babel}
\usepackage[usenames, dvipsnames]{color}
\usepackage[perpage]{footmisc}
\usepackage[square, numbers, comma, sort&compress]{natbib}
\usepackage{ifthen}
\usepackage{ifpdf}


%Bibliography
%uncomment next line to change bibliography name to references for Book document class
\renewcommand{\bibname}{References}
% note that this doesn't do much if you later define another bibliography style 


% Nomenclature
\usepackage{nomencl}
\makenomenclature
\renewcommand\nomgroup[1]{%
  \ifthenelse{\equal{#1}{A}}{%
   \item[\textbf{Roman Symbols}] }{%             A - Roman
    \ifthenelse{\equal{#1}{G}}{%
     \item[\textbf{Greek Symbols}]}{%             G - Greek
      \ifthenelse{\equal{#1}{R}}{%
        \item[\textbf{Superscripts}]}{%              R - Superscripts
          \ifthenelse{\equal{#1}{S}}{%
           \item[\textbf{Subscripts}]}{{%             S - Subscripts
	    \ifthenelse{\equal{#1}{X}}{%
	     \item[\textbf{Other Symbols}]}{{%    X - Other Symbols
	    \ifthenelse{\equal{#1}{Z}}{%
	     \item[\textbf{Acronyms}]}%              Z - Acronyms
              			{{}}}}}}}}}}

\ifpdf
%-->
%--> Google.com search "hyperref options"
%--> 
%--> http://www.ai.mit.edu/lab/sysadmin/latex/documentation/latex/hyperref/manual.pdf
%--> http://www.chemie.unibas.ch/~vogtp/LaTeX2PDFLaTeX.pdf 
%--> http://www.uni-giessen.de/partosch/eurotex99/ oberdiek/print/sli4a4col.pdf
%--> http://me.in-berlin.de/~miwie/tex-refs/html/latex-packages.html
%-->
    \usepackage[ pdftex, plainpages = false, pdfpagelabels, 
                 pdfpagelayout = OneColumn, % display single page, advancing flips the page - Sasa Tomic
                 bookmarks,
                 bookmarksopen = true,
                 bookmarksnumbered = true,
                 breaklinks = true,
                 linktocpage,
                 pagebackref,
                 colorlinks = true,
                 linkcolor = blue,
                 urlcolor  = blue,
                 citecolor = red,
                 anchorcolor = green,
                 hyperindex = true,
                 hyperfigures
                 ]{hyperref} 
    \usepackage[pdftex]{graphicx}
    \DeclareGraphicsExtensions{.png, .jpg, .pdf}

    \pdfcompresslevel=9
    \graphicspath{{ThesisFigs/PNG/}{ThesisFigs/PDF/}{ThesisFigs/}}
\else
    \usepackage[ dvips, 
                 bookmarks,
                 bookmarksopen = true,
                 bookmarksnumbered = true,
                 breaklinks = true,
                 linktocpage,
                 pagebackref,
                 colorlinks = true,
                 linkcolor = blue,
                 urlcolor  = blue,
                 citecolor = red,
                 anchorcolor = green,
                 hyperindex = true,
                 hyperfigures
                 ]{hyperref}

    %\usepackage{epsfig}
    \usepackage{graphicx}
    \DeclareGraphicsExtensions{.eps, .ps}
    \graphicspath{{ThesisFigs/EPS/}{ThesisFigs/}}
\fi

%define the page size including an offset for binding
%\setlength{\topmargin}{0.0in}
%\setlength{\oddsidemargin}{0in}
%\setlength{\evensidemargin}{0in}
%\setlength{\textheight}{700pt}
%\setlength{\textwidth}{500pt}

%\setlength{\intextsep}{5pt}%
%\setstretch{2}%
%\setlength{\belowcaptionskip}{-\baselineskip}\addtolength{\belowcaptionskip}{1.6ex}%

\usepackage{etoolbox}% http://ctan.org/pkg/etoolbox

\usepackage{mathptmx} % For times roman font
\usepackage[disable]{todonotes}
\usepackage[final]{changes}
%\usepackage{layouts}
%\setlength{\intextsep}{16pt plus 2pt minus 2pt}
%\setlength{\textfloatsep}{24pt plus 2pt minus 2pt}

\usepackage{geometry}
\newgeometry{
    top=1in,
    bottom=1in,
    outer=1in,
    inner=1.5in,
}

\AtBeginEnvironment{figure}{\addvspace{11pt}}
%\AtEndEnvironment{figure}{\addvspace{3mm}}

%
%\AtBeginEnvironment{table}{\addvspace{3mm}}
%\AtEndEnvironment{table}{\addvspace{3mm}}

%\AtBeginEnvironment{minipage}{\addvspace{3mm}}
%\AtEndEnvironment{minipage}{\addvspace{3mm}}


\setlength{\abovecaptionskip}{11pt plus 2pt minus 1pt}
\setlength{\belowcaptionskip}{11pt plus 2pt minus 1pt}

%A4 settings
\ifpdf
   \pdfpageheight=297mm
   \pdfpagewidth=210mm
\else
   \setlength{\paperheight}{297mm}
   \setlength{\paperwidth}{210mm}
\fi

\setlength{\hoffset}{0.00cm}
\setlength{\voffset}{0.00cm}

%% http://www.iitb.ac.in/newacadhome/rules/Dissertation17june09-10.pdf
%%\setlength{\evensidemargin}{1.96cm}
%%\setlength{\topmargin}{15mm}
%%\setlength{\headheight}{3mm}
%%\setlength{\headsep}{12mm}
%%\setlength{\bottommargin}{22mm}
%%\setlength{\footerheight}{3mm}
%%\setlength{\footersep}{10mm}
%%\setlength{\textheight}{245mm}
%%\setlength{\textwidth}{160mm}
%%
%%\setlength{\marginparsep}{1mm}
%%\setlength{\marginparwidth}{3cm}
%%\setlength{\footskip}{2.36cm}

%\pagestyle{fancy}
%\fancypage*{%
%  \setlength{\fboxsep}{8pt}%
%  \setlength{\shadowsize}{8pt}%
%  \shadowbox}{}
%\fancyhead{bar}

\usepackage{fancyhdr}
\renewcommand{\chaptermark}[1]{\markboth{#1}{}}
\renewcommand{\sectionmark}[1]{\markright{#1}}
\pagestyle{fancy}
\fancyhf{}
%\fancyhead[LE,RO]{\thepage}
\fancyhead[LO]{\normalfont \nouppercase{\rightmark}}
\fancyhead[RE]{\normalfont \nouppercase{\leftmark}}
\fancyfoot[C]{\thepage}
%\renewcommand{\headrulewidth}{0pt}


%
%\pagestyle{fancy}
%%\renewcommand{\chaptermark}[1]{\markboth{\MakeUppercase{\thechapter. #1 }}{}}
%\renewcommand{\chaptermark}[1]{\markboth{\nouppercase{\thechapter. #1 }}{}}
%\renewcommand{\sectionmark}[1]{}
%\fancyhf{}
%\fancyhead[RO]{\bfseries\rightmark}
%\fancyhead[LE]{\bfseries\leftmark}
%\fancyfoot[C]{\thepage}
%\renewcommand{\headrulewidth}{0.5pt}
%\renewcommand{\footrulewidth}{0pt}
%\addtolength{\headheight}{0.5pt}
%\fancypagestyle{plain}{
%  \fancyhead{}
%  \renewcommand{\headrulewidth}{0pt}
%}

%\newcommand{\projectreport}{{A Doctoral Thesis}}
%\newcommand{\entitled}{{entiltled}}
\newcommand{\submit}{{A THESIS SUBMITTED TO}}
\newcommand{\partialfulfilment}{{FOR THE AWARD OF DEGREE OF}}
\newcommand{\inthe}{{IN}}
\newcommand{\subjectof}{{SUBMITTED}}
\newcommand{\guidance}{{UNDER THE GUIDANCE OF}}
\newcommand{\by}{{BY}}
\newcommand{\rc}{{RESEARCH CENTER}}
\newcommand{\yearof}{{AUGUST 2016}}
\newcommand{\guidedept}{{DEPARTMENT OF MECHANICAL ENGINEERING}}
%
%
% DECLARATIONS
%
% These macros are used to declare arguments needed for the
% construction of the title page and other preamble.

% The year and term the degree will be officially conferred
\def\degreedate#1{\gdef\@degreedate{#1}}
% The full (unabbreviated) name of the degree
\def\degree#1{\gdef\@degree{#1}}
% The name of your college or department(eg. Trinity, Pembroke, Maths, Physics)
\def\collegeordept#1{\gdef\@collegeordept{#1}}
% The name of your University
\def\university#1{\gdef\@university{#1}}
% Defining the crest
\def\crest#1{\gdef\@crest{#1}}
% Defining the guide
\def\guide#1{\gdef\@guide{#1}}
% Defining the guide institute
\def\guideinstitute#1{\gdef\@guideinstitute{#1}}
% Defining the subject 
\def\subject#1{\gdef\@subject{#1}}
% These macros define an environment for front matter that is always 
% single column even in a double-column document.

\newenvironment{alwayssingle}{%
       \@restonecolfalse\if@twocolumn\@restonecoltrue\onecolumn
       \else\newpage\fi}
       {\if@restonecol\twocolumn\else\newpage\fi}

%define title page layout
\renewcommand{\maketitle}{%
\pagenumbering{roman} % Sasa Tomic
\setcounter{page}{0}  % Sasa Tomic
\begin{alwayssingle}

%%%%%%%%%%%%% TITLE PAGE %%%%%%%%%%%%%%%%%%%%
\thispagestyle{empty}
\begin{center}
\vspace*{1ex}	{\large {\bfseries {\@title}} \par}
\vspace*{1.5ex}	{{\submit} \par}
\vspace*{1ex}	{{\@university} \par}

\vspace*{2mm} 	\includegraphics[width=40mm]{images/uop_logo}
 
			{{\partialfulfilment}  \par}
\vspace*{1ex} 	{\textcolor{red}{\@degree} \par}
\vspace*{1ex}	{{\inthe} \par}
\vspace*{1ex}	{{\textbf \@subject} \par}
\vspace*{10mm}	{{\subjectof} \par}
			{{\by} \par}
\vspace*{1ex} 	{{\large \textbf \@author} \par}
\vspace*{1ex}	{ {\guidance} \par}
			{\large  {\textbf {\@guide} \par}}

 \vspace*{5mm}    	\includegraphics[width=32mm]{images/coep_logo}
 
\vspace*{1ex}   	{{{\rc} \par}}
\vspace*{1ex}   	{{{\@guideinstitute} \par}}
\vspace*{1ex}   	{{{\guidedept} \par}}
\vspace*{5mm} 	{{\textbf \yearof} \par}
\end{center}

%\begin{center}
%\vspace*{-35mm}	{\Large {\bfseries {\@title}} \par}
%\vspace*{1.5ex}	{\large {\submit} \par}
%\vspace*{1ex}	{\large {\@university} \par}
%
%\vspace*{2mm} 	\includegraphics[width=40mm]{images/uop_logo}
% 
%			{\large {\partialfulfilment}  \par}
%\vspace*{1ex} 	{{\large \@degree} \par}
%\vspace*{1ex}	{\large {\inthe} \par}
%\vspace*{1ex}	{{\large \textbf \@subject} \par}
%\vspace*{5mm}	{\large {\subjectof} \par}
%			{\large {\by} \par}
%\vspace*{1ex} 	{{\large \textbf \@author} \par}
%\vspace*{1ex}	{\large {\guidance} \par}
%			{\large  {\textbf {\@guide} \par}}
%
% \vspace*{2mm}    	\includegraphics[width=32mm]{images/coep_logo}
% 
%\vspace*{1ex}   	{\large {{\rc} \par}}
%\vspace*{1ex}   	{\large {{\@guideinstitute} \par}}
%\vspace*{1ex}   	{\large {{\guidedept} \par}}
%\vspace*{5mm} 	{{\large \textbf \yearof} \par}
%\end{center}


  \null\vfill
\end{alwayssingle}}


% CERTIFICATE
%
% The Certifiacte environment makes sure the certificate gets its
% own page and is set out in verse format.

\newenvironment{certificate}
{\pagestyle{empty}
\begin{alwayssingle}
\begin{center}
\vspace*{1.5cm}
{\Huge \textswab{Certificate} }
\end{center}
\vspace{0.5cm}\begin{quote}}
{\end{quote}\end{alwayssingle}}


% DEDICATION
%
% The dedication environment makes sure the dedication gets its
% own page and is set out in verse format.

\newenvironment{dedication}
{\begin{alwayssingle}
  \pagestyle{empty}
  \begin{center}
  \vspace*{1.5cm}
  {\LARGE }
  \end{center}
  \vspace{0.5cm}
  \begin{quote} \begin{center}}
{\end{center} \end{quote} \end{alwayssingle}}


% ACKNOWLEDGEMENTS
%
% The acknowledgements environment puts a large, bold, centered 
% "Acknowledgements" label at the top of the page. The acknowledgements
% themselves appear in a quote environment, i.e. tabbed in at both sides, and
% on its own page.

\newenvironment{acknowledgements}
{\pagestyle{empty}
\begin{alwayssingle}
\begin{center}
\vspace*{1.5cm}
{\Large \bfseries Acknowledgements}
\end{center}
\vspace{0.5cm}
\begin{quote}}
{\end{quote}\end{alwayssingle}}

% The acknowledgementslong environment puts a large, bold, centered 
% "Acknowledgements" label at the top of the page. The acknowledgement itself 
% does not appears in a quote environment so you can get more in.

\newenvironment{acknowledgementslong}
{\pagestyle{empty}
\begin{alwayssingle}
\begin{center}
\vspace*{1.5cm}
{\Large \bfseries Acknowledgements}
\end{center}
\vspace{0.5cm}\begin{quote}}
{\end{quote}\end{alwayssingle}}

%ABSTRACT
%
%The abstract environment puts a large, bold, centered "Abstract" label at
%the top of the page. The abstract itself appears in a quote environment,
%i.e. tabbed in at both sides, and on its own page.

\newenvironment{abstracts} {\begin{alwayssingle} \pagestyle{empty}
  \begin{center}
  \vspace*{1.5cm}
  {\Large \bfseries  Abstract}
  \end{center}
  \vspace{0.5cm}
   \begin{quote}}
{\end{quote}\end{alwayssingle}}

%The abstractlong environment puts a large, bold, centered "Abstract" label at
%the top of the page. The abstract itself does not appears in a quote
%environment so you can get more in.

\newenvironment{abstractslong} {\begin{alwayssingle} \pagestyle{empty}
  \begin{center}
  \vspace*{1.5cm}
  {\Large \bfseries  Abstract}
  \end{center}
  \vspace{0.5cm} \begin{quote}}
{\end{quote}\end{alwayssingle}}

%The abstractseparate environment is for running of a page with the abstract
%on including title and author etc as required to be handed in separately

\newenvironment{abstractseparate} {\begin{alwayssingle} \pagestyle{empty}
  \vspace*{-1in}
 \begin{center}
    { \Large {\bfseries {\@title}} \par}
    {{\large \vspace*{1ex} \@author} \par}
{\large \vspace*{1ex}
    {{\@collegeordept} \par}
    {{\@university} \par}
\vspace*{1ex}
    {{\it \submittedtext} \par}
    {\it {\@degree} \par}
\vspace*{2ex}
    {\@degreedate}}
  \end{center}}
{\end{alwayssingle}}

%ROMANPAGES
%
% The romanpages environment set the page numbering to lowercase roman one
% for the contents and figures lists. It also resets
% page-numbering for the remainder of the dissertation (arabic, starting at 1).

\newenvironment{romanpages}
{\setcounter{page}{1}
  \renewcommand{\thepage}{\roman{page}}}
{\newpage\renewcommand{\thepage}{\arabic{page}}}
%{\newpage\renewcommand{\thepage}{\arabic{page}}\setcounter{page}{1}}

