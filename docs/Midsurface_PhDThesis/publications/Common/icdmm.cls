%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% 
%% Class file for the paper of the ICAME TEMPLATE 2013 conf
%% MKM 20012010
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{icame_template}[2013/01/30 ICAME TEMPLATE class]  
\ProcessOptions\relax

%\DeclareOption{10pt}{\OptionNotUsed}  
\DeclareOption{12pt}{\OptionNotUsed}  
%\DeclareOption{twocolumn}{\OptionNotUsed}  
\DeclareOption*{\PassOptionsToClass{\CurrentOption}{article}}  
  
\ProcessOptions\relax  
  
\LoadClass[10pt,a4paper]{article}  
  
%\RequirePackage[latin1]{inputenc}   % for unix users
\RequirePackage[ansinew]{inputenc}  %  for windows users
%\RequirePackage[aplemac]{inputenc}  % for mac users

\RequirePackage[T1]{fontenc}
\RequirePackage{times}
\RequirePackage{graphicx}
\RequirePackage{wrapfig}
\RequirePackage{verbatim}
\RequirePackage{graphicx}
\RequirePackage{tabularx}
\RequirePackage{amsmath,amsfonts,amssymb,amsthm,amsbsy,amsmath}
\RequirePackage{latexsym}
\RequirePackage{bm}
\RequirePackage{a4}
\RequirePackage{fancyhdr}
\RequirePackage{engord}
\RequirePackage{epsfig,vmargin,booktabs}
\RequirePackage{color}
\RequirePackage{hyperref}
\RequirePackage[all]{hypcap}
\RequirePackage{url}
\RequirePackage{array}

\setpapersize{A4}  % needs vmargin package
%\setmarginsrb{left}{top}{right}{bottom}{headh1gt}{headsep}{foothgt}{footskip}
%\setmarginsrb{30mm}{5mm}{30mm}{5mm}{25mm}{0mm}{0mm}{25mm}
\setmarginsrb{14.32mm}{19mm}{14.32mm}{43mm}{25mm}{0mm}{0mm}{25mm}
% headsep:  Distance from bottom of header to the body of text on a page.
% foorskip: Distance from bottom of body to the bottom of the footer (the footer is the text at the bottom of each page).


\parindent=0pt
%\parskip0pc
\parskip=2ex


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Hyperlinks
\hypersetup{colorlinks=true}
\hypersetup{
    citecolor=black,
    filecolor=black,
    linkcolor=black,
    urlcolor=blue
}
\urlstyle{same}
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% The LABEL extensions for proofing. J. Kaipio, 4.4.1995
%% CAPTIONS FOR TABLES AND FIGURES
%%
%%  There's a new logical variable \tablecap, which is
%%  set \true by saying \tablecaptrue and \false by
%%  \tablecapfalse. The variable is expanded by saying
%%  \iftablecap. Then there are two separate \caption
%%  macros: \tabcaption and \figcaption, the definition
%%  of which are obvious. The \iftablecap is performed in
%%  \@makecaption, which now contains two different
%%  captioning styles.
%%                               J. Kaipio 3.10.1990.
\newif\iftablecap
\def\tabcaption#1{\tablecaptrue\caption{#1}}
\def\figcaption#1{\tablecapfalse\caption{#1}}
\newlength{\t@bindwidth} \setlength{\t@bindwidth}{1cm}
\newlength{\c@pwidth} \setlength{\c@pwidth}{\hsize}
\addtolength{\c@pwidth}{-2\t@bindwidth}

\long\def\@makecaption#1#2{
   %\vskip 10pt
   \vskip 0.5ex
   \iftablecap                           % Is it a table?
     \setbox\@tempboxa\hbox{#2}
     \ifdim \wd\@tempboxa > \c@pwidth      % IF longer than one line-2cm:
         \hbox to\hsize{\hfil{\sc #1}\hfil}
         \begin{list}{}{\leftmargin\t@bindwidth
             \rightmargin\t@bindwidth}
             {\item \footnotesize  #2}
         \end{list}  
     \else                               % ELSE  center.
         \hbox to\hsize{\hfil{\sc #1}\hfil}
         \hbox to\hsize{\hfil{\footnotesize #2}\hfil}
     \fi                                   % of \ifdim
   \else                                 % Not a table: a picture
     \setbox\@tempboxa\hbox{\small{\bf #1}. #2}
     \ifdim \wd\@tempboxa >\c@pwidth       % IF longer than one line-2cm:
        \begin{list}{}{\leftmargin\t@bindwidth
           \rightmargin\t@bindwidth}
           {\small \item {\bf #1}. #2}
         \end{list}                        % THEN set as ordinary paragraph.
     \else                               % ELSE  center.
         \hbox to\hsize{\hfil\box\@tempboxa\hfil}
     \fi                                   % of \ifdim
   \fi                                   % of \if\tablecaptrue
   }                                     % \@makecaption

%  End of \@makecaption modifications.
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% SECTIONS 
\renewcommand\section{\@startsection {section}{1}{\z@}{-3.5ex plus -1ex minus-.2ex}{0.2ex}{\normalsize\bfseries}}
\def\subsection{\@startsection{subsection}{2}{\z@}{-1.75ex plus -1ex minus-.2ex}{0.2ex}{\normalsize\bfseries}}
\def\subsubsection{\@startsection{subsubsection}{3}{\z@}{-1.75ex plus -1ex minus-.2ex}{0.2ex}{\normalsize\bfseries}}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

\newcommand\keywordssec{\@startsection{paragraph}{4}{\z@}{6pt}{-1.1ex}{\bfseries}}

\def\keywords{
\begin{normalsize}
\keywordssec{Keywords:\space}
}
\def\endkeywords{\end{normalsize}}

\renewcommand\refname{REFERENCES} 


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% My defs....
\newcommand{\dd}[1]{\mbox{${\mathrm d}{#1}$}} % d
\newcommand{\grad}{\operatorname{grad}}
\newcommand{\dev}{\operatorname{dev}}
\newcommand{\tr}{\operatorname{tr}}
\newcommand{\ov}[1]{\mbox{$\bm{#1}$}} 				% vectors
\newcommand{\om}[1]{\mbox{$\bm{#1}$}} 				% matrices
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%



\AtBeginDocument{%    
  \pagestyle{empty}
  \thispagestyle{fancy}
  \fancyhf{} % clear all header and footer fields
  \renewcommand{\headrulewidth}{0pt}
  \rhead{International Conference on Design, Manufacturing and Mechatronics\\
		KJEI's Trinity College of Engineering and Research,Pune, India \vspace{35mm}}
		}  

\endinput

