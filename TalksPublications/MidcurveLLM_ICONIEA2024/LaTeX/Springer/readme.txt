This directory holds the 8 components of the SVMult tool package:

(1) the Springer document class "svmult.cls"

(2) a subdirectory "styles" with
- the Springer MakeIndex style file "svind.ist"
- the Springer MakeIndex style file "svindd.ist" - german version
- the Springer BibTeX styles "spbasic.bst", "spmpsci.bst", "spphys.bst"

(3) a subdirectory "author" with
- the sample text file "authorsample.tex",
- the sample figure file "figure.eps"
- the sample reference file "references.tex"
- the pdf file "authorsample.pdf" as an example of a "contribution"
with preset class options, packages and coding examples;

Tip: Copy all these files to your working directory, run LaTeX
and produce your own example *.dvi file; rename the template files as
you see fit and use them for your own input.

(4) a subdirectory "editor" containing

      -- the sample root file "editor.tex"
         with preset class options, packages and coding examples;
      -- the sample text files
         --- "dedication.tex" (dedication),
         --- "foreword.tex" (foreword),
         --- "preface.tex" (preface),
         --- "acknowledgement.tex" (acknowledgements),
         --- "contriblist.tex" (list of contributors),
         --- "acronym.tex" (common list of acronyms),
         --- "part.tex" (part title),
         --- "author.tex" (contribution),
         --- "figure.eps" (sample figure)
         --- "glossary.tex" (common glossary)
         --- "appendix.tex" (common appendix)
         --- "figure.eps" (sample figure)

         Tip: Copy all these files to your working directory,
              run LaTeX and produce your own example *.dvi file;
              rename the template files as you see fit and
              use them for your own input.

    - the pdf file "editorsample.pdf" as an example of a "complete book"


(5) a subdirectory "guideline" with

- the pdf/tex file "quickstart.pdf/quickstart.tex" with "essentials" for an easy implementation of the "SVMult" package (2 pages)
- the pdf/tex file "authorinst.pdf/authorinst.tex" with style and coding instructions specific to -- Contributed Volumes

Tip: Follow these instructions to set up your files, to type in your
text and to obtain a consistent formal style; use these pages as
checklists before you submit your ready-to-print manuscript.

- the pdf/tex file "refguide.pdf/refguide.tex" describing the
SVMult document class features independent of any specific style
requirements.

Tip: Use it as a reference if you need to alter or enhance the
default settings of the SVMult document class and/or the templates.

- the pdf/tex file "editorinst.pdf/editorinst.tex" with step-by-step 
instructions for compiling all contributions to a single book.


(6) a file "history.txt" with version history

(7) .\spmpsci.bst 
    .\spbasic.bst

      -   “n.separate" function that call within page range
                              removed(because lengthy page ranges get affected)
							  
(8) .\spbasic.bst

      -   “et~al." - end dot inserted based on feedback							  

(9) Special elements 
    .\editor\author.tex
    .\editor\editorsample.pdf
    .\author\authorsample.tex
    .\author\authorsample.pdf
    .\author\svmult.cls (V5.5)
    
    -- Trailer Head
    -- Questions
    -- Important
    -- Attention 
    -- Program Code
    -- Tips
    -- Overview
    -- Background Information
    -- Legal Text
(10) Fast publishing suggestions given to author added in the documentation. 



