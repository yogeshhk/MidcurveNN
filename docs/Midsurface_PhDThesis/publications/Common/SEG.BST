%%% ======================================================================
%%%  @LaTeX-style-file{
%%%     filename        = "seg.bst",
%%%     version         = "0.9",
%%%     date            = "September 12, 1993",
%%%     ISO-date        = "1993.9.12",
%%%     time            = "00.00.00",
%%%     author          = "Martin Karrenbach",
%%%     contact         = "Stanford Exploration Project",
%%%     address         = "366 Mitchell
%%%                        Stanford, CA 94305",
%%%     telephone       = "(415) 723-6007",
%%%     email           = "martin@sep.stanford.edu (Internet)",
%%%     supported       = "maybe",
%%%     archived        = "not yet",
%%%     keywords        = "REVTeX, version 3.0, main style,
%%%                        Society of Exploration Geophysicists",
%%%     codetable       = "ISO/ASCII",
%%%     docstring       = "This is the BIBTeX society-specific style file for
%%%                        the Society of Exploration Geophysicists
%%%                        under REVTeX 3.0
%%%                        (release of September 9, 1993)."
%%%
%%% ======================================================================
%
%
% Martin Karrenbach    (last updated: 9-9-1993)
% Martin Karrenbach    (last updated: 4-16-1994)
% 
%   Citation format: [author-last-name, year]
%		     [author-last-name and author-last-name, year]
%		     [author-last-name {\em et al.}, year]
%
%   Reference list ordering: alphabetical by author or whatever passes
%	for author in the absence of one.
%
% the following lives in segbib.sty:
% This BibTeX style has support for short (year only) citations.  This
% is done by having the citations actually look like
%         \citeauthoryear{author-info}{year}
% The LaTeX style has to have the following (or similar)
%     \let\@internalcite\cite
%     \def\cite{\def\citeauthoryear##1##2{##1, ##2}\@internalcite}
%     \def\shortcite{\def\citeauthoryear##1{##2}\@internalcite}
%     \def\@biblabel#1{\def\citeauthoryear##1##2{##1, ##2}[#1]\hfill}
% which makes \shortcite the macro for short citations.

ENTRY
  { address
    author
    booktitle
    chapter
    edition
    editor
    howpublished
    institution
    journal
    key
    month
    note
    number
    organization
    pages
    publisher
    school
    series
    title
    type
    volume
    year
    meeting
  }
  {}    
  { label extra.label sort.label }

% examples:
%label \protect...   
%extra.label is a in 1990a 
%sort.label karrenbach1990

INTEGERS { output.state before.all mid.sentence after.sentence after.block }

FUNCTION {init.state.consts}
{ #0 'before.all :=
  #1 'mid.sentence :=
  #2 'after.sentence :=
  #3 'after.block :=
}

STRINGS { s t }

FUNCTION {output.with.dash}
{ 's :=
  output.state mid.sentence =
    { "--" * write$ }
    { output.state after.block =
	{ add.period$ write$
	  newline$
	  "\newblock " write$
	}
	{ output.state before.all =
	    'write$
	    { add.period$ " " * write$ }
	  if$
	}
      if$
      mid.sentence 'output.state :=
    }
  if$
  s
}

FUNCTION {output.with.colon}
{ 's :=
  output.state mid.sentence =
    { ": " * write$ }
    { output.state after.block =
	{ add.period$ write$
	  newline$
	  "\newblock " write$
	}
	{ output.state before.all =
	    'write$
	    { add.period$ ": " * write$ }
	  if$
	}
      if$
      mid.sentence 'output.state :=
    }
  if$
  s
}

FUNCTION {output.with.space}
{ 's :=
  output.state mid.sentence =
    { " " * write$ }
    { output.state after.block =
	{ add.period$ write$
	  newline$
	  "\newblock " write$
	}
	{ output.state before.all =
	    'write$
	    { add.period$ " " * write$ }
	  if$
	}
      if$
      mid.sentence 'output.state :=
    }
  if$
  s
}

FUNCTION {output.nonnull}
{ 's :=
  output.state mid.sentence =
    { ", " * write$ }
    { output.state after.block =
	{ add.period$ write$
	  newline$
	  "\newblock " write$
	}
	{ output.state before.all =
	    'write$
	    { add.period$ " " * write$ }
	  if$
	}
      if$
      mid.sentence 'output.state :=
    }
  if$
  s
}

FUNCTION {output}
{ duplicate$ empty$
    'pop$
    'output.nonnull
  if$
}

FUNCTION {output.space.check}
{ 't :=
  duplicate$ empty$
    { pop$ "empty " t * " in " * cite$ * warning$ }
    'output.with.space
  if$
}

FUNCTION {output.colon.check}
{ 't :=
  duplicate$ empty$
    { pop$ "empty " t * " in " * cite$ * warning$ }
    'output.with.colon
  if$
}

FUNCTION {output.check}
{ 't :=
  duplicate$ empty$
    { pop$ "empty " t * " in " * cite$ * warning$ }
    'output.nonnull
  if$
}

FUNCTION {output.same.author.check}
{ extra.label "" = 
  { 
  't :=
  duplicate$ empty$
    { pop$ "empty " t * " in " * cite$ * warning$ }
    'output.nonnull
  if$
%  "no label" warning$
  }
  { extra.label "a"  =
    {
      't :=
      duplicate$ empty$
        { pop$ "empty " t * " in " * cite$ * warning$ }
        'output.nonnull
      if$
%      "label a" warning$
    }
    {
           't :=
      duplicate$ empty$
        { pop$ "empty " t * " in " * cite$ * warning$ }
        'output.with.space
      if$
%      "label other" warning$
    }
    if$
  }
 if$
}

FUNCTION {output.bibitem}
{ newline$

  "\bibitem[" write$
  label write$
  "]{" write$

  cite$ write$
  "}" write$
  newline$
  ""
  before.all 'output.state :=
}

FUNCTION {fin.entry}
{ add.period$
  write$
  newline$
}

FUNCTION {new.block}
{ output.state before.all =
    'skip$
    { after.block 'output.state := }
  if$
}

FUNCTION {new.sentence}
{ output.state after.block =
    'skip$
    { output.state before.all =
	'skip$
	{ after.sentence 'output.state := }
      if$
    }
  if$
}

FUNCTION {not}
{   { #0 }
    { #1 }
  if$
}

FUNCTION {and}
{   'skip$
    { pop$ #0 }
  if$
}

FUNCTION {or}
{   { pop$ #1 }
    'skip$
  if$
}

FUNCTION {new.block.checka}
{ empty$
    'skip$
    'new.block
  if$
}

FUNCTION {new.block.checkb}
{ empty$
  swap$ empty$
  and
    'skip$
    'new.block
  if$
}

FUNCTION {new.sentence.checka}
{ empty$
    'skip$
    'new.sentence
  if$
}

FUNCTION {new.sentence.checkb}
{ empty$
  swap$ empty$
  and
    'skip$
    'new.sentence
  if$
}

FUNCTION {field.or.null}
{ duplicate$ empty$
    { pop$ "" }
    'skip$
  if$
}

FUNCTION {emphasize}
{ duplicate$ empty$
    { pop$ "" }
    { "{\bf " swap$ * "}" * }
  if$
}

INTEGERS { nameptr namesleft numnames }

FUNCTION {format.names}
{ 's :=
  #1 'nameptr :=
  s num.names$ 'numnames :=
  numnames 'namesleft :=
    { namesleft #0 > }

    { s nameptr "{vv~}{ll}{jj}{, f.}" format.name$ 't :=

      nameptr #1 >
	{ namesleft #1 >
	    { ", " * t * }
	    { numnames #2 >
		{ ", " * }
		'skip$
	      if$
	      t "others" =
		{ ", et~al." * }
		{
                   numnames #2 =
		   { ", and " * t * }
		   { " and " * t * }
	           if$
		}
	      if$
	    }
	  if$
	}
	't
      if$
      nameptr #1 + 'nameptr :=
      namesleft #1 - 'namesleft :=
    }
  while$
}

%FUNCTION {format.authors}
%{ author empty$
%    { "" }
%    { author format.names }
%  if$
%}

FUNCTION {format.authors}
{ author empty$
    { "" }
    { extra.label "" = 
	{author format.names }
        {extra.label "a"  =
	  {author format.names }
	  { "--------" }
        if$
        }
      if$
    }
  if$
}

FUNCTION {format.editors}
{ editor empty$
    { "" }
    { editor format.names
      editor num.names$ #1 >
	{ ", Eds." * }
	{ ", Ed." * }
      if$
    }
  if$
}

FUNCTION {format.title}
{ title empty$
    { "" }
    {
    editor empty$
      { title "t"  change.case$ ":" * }
      { title "t"  change.case$ }
    if$
    } 
  if$
}

FUNCTION {n.dashify}
{ 't :=
  ""
    { t empty$ not }
    { t #1 #1 substring$ "-" =
	{ t #1 #2 substring$ "--" = not
	    { "--" *
	      t #2 global.max$ substring$ 't :=
	    }
	    {   { t #1 #1 substring$ "-" = }
		{ "-" *
		  t #2 global.max$ substring$ 't :=
		}
	      while$
	    }
	  if$
	}
	{ t #1 #1 substring$ *
	  t #2 global.max$ substring$ 't :=
	}
      if$
    }
  while$
}

FUNCTION {format.sep.date}
{ year empty$
    { month empty$
	{ "" }
	{ "there's a month but no year in " cite$ * warning$
	  month
	}
      if$
    }
    { month empty$
        {
%	'year
        year extra.label *
        }
	{ month " " * year * }
      if$
    }
  if$
}

FUNCTION {format.date}
{ year empty$
    { month empty$
	{ "" }
	{ "there's a month but no year in " cite$ * warning$
	  month
	}
      if$
    }
    { month empty$
	'year
	{ month " " * year * }
      if$
    }
  if$
}

FUNCTION {format.btitle}
{ title emphasize
}

FUNCTION {tie.or.space.connect}
{ duplicate$ text.length$ #3 <
    { "~" }
    { " " }
  if$
  swap$ * *
}

FUNCTION {either.or.check}
{ empty$
    'pop$
    { "can't use both " swap$ * " fields in " * cite$ * warning$ }
  if$
}

FUNCTION {format.bvolume}
{ volume empty$
    { "" }
    { "volume" volume tie.or.space.connect
      series empty$
	'skip$
	{ " of " * series emphasize * }
      if$
      "volume and number" number either.or.check
    }
  if$
}

FUNCTION {format.number.series}
{ volume empty$
    { number empty$
	{ series field.or.null }
	{ output.state mid.sentence =
	    { "number" }
	    { "Number" }
	  if$
	  number tie.or.space.connect
	  series empty$
	    { "there's a number but no series in " cite$ * warning$ }
	    { " in " * series * }
	  if$
	}
      if$
    }
    { "" }
  if$
}

FUNCTION {format.edition}
{ edition empty$
    { "" }
    { output.state mid.sentence =
	{ edition "l" change.case$ " edition" * }
	{ edition "t" change.case$ " edition" * }
      if$
    }
  if$
}

INTEGERS { multiresult }

FUNCTION {multi.page.check}
{ 't :=
  #0 'multiresult :=
    { multiresult not
      t empty$ not
      and
    }
    { t #1 #1 substring$
      duplicate$ "-" =
      swap$ duplicate$ "," =
      swap$ "+" =
      or or
	{ #1 'multiresult := }
	{ t #2 global.max$ substring$ 't := }
      if$
    }
  while$
  multiresult
}

FUNCTION {format.pages}
{ pages empty$
    { "" }
    { pages multi.page.check
	{ "pages" pages n.dashify tie.or.space.connect }
	{ "page" pages tie.or.space.connect }
      if$
    }
  if$
}

FUNCTION {format.proceed.pages}
{ pages empty$
    { "" }
    { pages multi.page.check
	{ ""  pages n.dashify tie.or.space.connect }
	{ ""  pages tie.or.space.connect }
      if$
    }
  if$
}

FUNCTION {format.vol.num.pages}
{ volume field.or.null emphasize
  number empty$
    'skip$
    { ", no. " number *  *
      volume empty$
	{ "there's a number but no volume in " cite$ * warning$ }
	'skip$
      if$
    }
  if$
  pages empty$
    'skip$
    { duplicate$ empty$
	{ pop$ format.pages }
	{ ", " * pages n.dashify * }
      if$
    }
  if$
}

FUNCTION {format.chapter.pages}
{ chapter empty$
    'format.pages
    { type empty$
	{ "chapter" }
	{ type "l" change.case$ }
      if$
      chapter tie.or.space.connect
      pages empty$
	'skip$
	{ ", " * format.pages * }
      if$
    }
  if$
}

FUNCTION {format.in.ed.booktitle}
{ booktitle empty$
    { "" }
    { editor empty$
	{ "{\it in} " booktitle * }
	{ "{\it in} " format.editors * ", " * booktitle * ":" * }
      if$
    }
  if$
}

FUNCTION {empty.misc.check}
{ author empty$ title empty$ howpublished empty$
  month empty$ year empty$ note empty$
  and and and and and

  key empty$ not and

    { "all relevant fields are empty in " cite$ * warning$ }
    'skip$
  if$
}

FUNCTION {format.thesis.type}
{ type empty$
    'skip$
    { pop$
      type "t" change.case$
    }
  if$
}

FUNCTION {format.tr.number}
{ type empty$
    { "Technical Report" }
    'type
  if$
  number empty$
    { "t" change.case$ }
    { number tie.or.space.connect }
  if$
}

FUNCTION {format.article.crossref}
{ key empty$
    { journal empty$
	{ "need key or journal for " cite$ * " to crossref " * crossref *
	  warning$
	  ""
	}
	{ "In {\em " journal * "\/}" * }
      if$
    }
    { "In " key * }
  if$
  " \shortcite{" * crossref * "}" *
}

FUNCTION {format.crossref.editor}
{ editor #1 "{vv~}{ll}" format.name$
  editor num.names$ duplicate$
  #2 >
    { pop$ " et~al." * }
    { #2 <
	'skip$
	{ editor #2 "{ff }{vv }{ll}{ jj}" format.name$ "others" =
	    { " et~al." * }
	    { " and " * editor #2 "{vv~}{ll}" format.name$ * }
	  if$
	}
      if$
    }
  if$
}

FUNCTION {format.book.crossref}
{ volume empty$
    { "empty volume in " cite$ * "'s crossref of " * crossref * warning$
      "In "
    }
    { "Volume" volume tie.or.space.connect
      " of " *
    }
  if$
  editor empty$
  editor field.or.null author field.or.null =
  or
    { key empty$
	{ series empty$
	    { "need editor, key, or series for " cite$ * " to crossref " *
	      crossref * warning$
	      "" *
	    }
	    { "{\em " * series * "\/}" * }
	  if$
	}
	{ key * }
      if$
    }
    { format.crossref.editor * }
  if$
  " \shortcite{" * crossref * "}" *
}

FUNCTION {format.incoll.inproc.crossref}
{ editor empty$
  editor field.or.null author field.or.null =
  or
    { key empty$
	{ booktitle empty$
	    { "need editor, key, or booktitle for " cite$ * " to crossref " *
	      crossref * warning$
	      ""
	    }
	    { "In {\em " booktitle * "\/}" * }
	  if$
	}
	{ "In " key * }
      if$
    }
    { "In " format.crossref.editor * }
  if$
  " \shortcite{" * crossref * "}" *
}

FUNCTION {sortify.sep}
{ purify$
  "l" change.case$
}

FUNCTION {sepreport}
{ output.bibitem
  format.authors "author" output.check
%  format.sep.date "year" output.check
  format.sep.date "year" output.same.author.check
  format.title "title" output.check
  crossref missing$
    { organization "organization" output.space.check
      format.vol.num.pages output.with.dash
    }
    { format.article.crossref output.nonnull
      format.pages output
    }
  if$
  new.block
  note output
  fin.entry
}



FUNCTION {article}
{ output.bibitem
  format.authors "author" output.check
%  format.sep.date "year" output.check
  format.sep.date "year" output.same.author.check
  format.title "title" output.check
  crossref missing$
    { journal "journal" output.space.check
      format.vol.num.pages output
    }
    { format.article.crossref output.nonnull
      format.pages output
    }
  if$
  fin.entry
}

FUNCTION {book}
{ output.bibitem
  author empty$
    { format.editors "author and editor" output.check }
    { format.authors output.nonnull
      crossref missing$
	{ "author and editor" editor either.or.check }
	'skip$
      if$
    }
  if$
%  format.sep.date "year" output.check
  format.sep.date "year" output.same.author.check
  format.title "title" output.check
  crossref missing$
    { format.bvolume output
      format.number.series output
      publisher "publisher" output.space.check
      address output
    }
    {
      format.book.crossref output.nonnull
    }
  if$
  format.edition output
  fin.entry
}

FUNCTION {booklet}
{ output.bibitem
  format.authors output
  new.block
  format.title "title" output.check
  howpublished address new.block.checkb
  howpublished output
  address output
  format.date output
  new.block
  note output
  fin.entry
}

FUNCTION {inbook}
{ output.bibitem
  author empty$
    { format.editors "author and editor" output.check }
    { format.authors output.nonnull
    }
  if$
%  format.sep.date "year" output.check
  format.sep.date "year" output.same.author.check
  format.title "title" output.check
  format.in.ed.booktitle booktitle output.check
  crossref missing$
    { 
      publisher "publishers" output.space.check
      series empty$
	{}
	{series "series" output.check }
      if$
      volume empty$
      {}
      {	volume "volume" output.check }
      if$
      format.proceed.pages output	
    }
    { format.chapter.pages "chapter and pages" output.check
      new.block
      format.book.crossref output.nonnull
    }
  if$
  format.edition output
  new.block
  note output
  fin.entry
}

FUNCTION {incollection}
{ output.bibitem
  format.authors "author" output.check
%  format.sep.date "year" output.check
  format.sep.date "year" output.same.author.check
  format.title "title" output.check
  crossref missing$
    { 
      editor empty$
      { booktitle output.with.space }
      { format.in.ed.booktitle output.with.space 
        publisher empty$
        {}
	{ publisher output.with.colon }
        if$
      }
      if$
    }
    { format.incoll.inproc.crossref output.nonnull
    }
  if$
  format.proceed.pages output
  fin.entry
}

FUNCTION {inproceedings}
{ output.bibitem
  format.authors "author" output.check
%  format.sep.date "year" output.check
  format.sep.date "year" output.same.author.check
  format.title "title" output.check
  crossref missing$
    { 
      howpublished empty$
        {meeting output.with.space}
        {"Presented at the" output.with.space meeting output.with.space}
      if$
      publisher output
      booktitle output
    }
    { format.incoll.inproc.crossref output.nonnull
    }
  if$
  howpublished empty$
    {format.proceed.pages output}
    {}
  if$
  fin.entry
}

FUNCTION {conference} { inproceedings }

FUNCTION {manual}
{ output.bibitem
  author empty$
    { organization empty$
	'skip$
	{ organization output.nonnull
	  address output
	}
      if$
    }
    { format.authors output.nonnull }
  if$
  new.block
  format.btitle "title" output.check
  author empty$
    { organization empty$
	{ address new.block.checka
	  address output
	}
	'skip$
      if$
    }
    { organization address new.block.checkb
      organization output
      address output
    }
  if$
  format.edition output
  format.date output
  new.block
  note output
  fin.entry
}

FUNCTION {mastersthesis}
{ output.bibitem
  format.authors "author" output.check
%  format.sep.date "year" output.check
  format.sep.date "year" output.same.author.check
  format.title "title" output.check
  "Master's thesis" output.with.space
  school "school" output.check
  address output
  fin.entry
}

FUNCTION {misc}
{
  output.bibitem
  format.authors output
  title howpublished new.block.checkb
  format.title output
  howpublished new.block.checka
  howpublished output
  format.date output
  new.block
  note output
  fin.entry
  empty.misc.check
}

FUNCTION {phdthesis}
{ output.bibitem
  format.authors "author" output.check
%  format.sep.date "year" output.check
  format.sep.date "year" output.same.author.check
  format.title "title" output.check
  "Ph.D. thesis" output.with.space
  school "school" output.check
  address output
  fin.entry
}

FUNCTION {proceedings}
{ output.bibitem
  editor empty$
    { organization output }
    { format.editors output.nonnull }
  if$
  new.block
  format.btitle "title" output.check
  format.bvolume output
  format.number.series output
  address empty$
    { editor empty$
	{ publisher new.sentence.checka }
	{ organization publisher new.sentence.checkb
	  organization output
	}
      if$
      publisher output
      format.date "year" output.check
    }
    { address output.nonnull
      format.date "year" output.check
      new.sentence
      editor empty$
	'skip$
	{ organization output }
      if$
      publisher output
    }
  if$
  new.block
  note output
  fin.entry
}

FUNCTION {techreport}
{ output.bibitem
  format.authors "author" output.check
  format.title "title" output.check
  format.tr.number output.nonnull
  institution "institution" output.check
  address output
  format.date "year" output.check
  fin.entry
}

FUNCTION {unpublished}
{ output.bibitem
  format.authors "author" output.check
  format.title "title" output.check
  note "note" output.check
  format.date output
  fin.entry
}

FUNCTION {default.type} { misc }

MACRO {acmcs} {"ACM Computing Surveys"}

MACRO {acta} {"Acta Informatica"}

MACRO {cacm} {"Communications of the ACM"}

MACRO {ibmjrd} {"IBM Journal of Research and Development"}

MACRO {ibmsj} {"IBM Systems Journal"}

MACRO {ieeese} {"IEEE Transactions on Software Engineering"}

MACRO {ieeetc} {"IEEE Transactions on Computers"}

MACRO {ieeetcad}
 {"IEEE Transactions on Computer-Aided Design of Integrated Circuits"}

MACRO {ipl} {"Information Processing Letters"}

MACRO {jacm} {"Journal of the ACM"}

MACRO {jcss} {"Journal of Computer and System Sciences"}

MACRO {scp} {"Science of Computer Programming"}

MACRO {sicomp} {"SIAM Journal on Computing"}

MACRO {tocs} {"ACM Transactions on Computer Systems"}

MACRO {tods} {"ACM Transactions on Database Systems"}

MACRO {tog} {"ACM Transactions on Graphics"}

MACRO {toms} {"ACM Transactions on Mathematical Software"}

MACRO {toois} {"ACM Transactions on Office Information Systems"}

MACRO {toplas} {"ACM Transactions on Programming Languages and Systems"}

MACRO {tcs} {"Theoretical Computer Science"}

MACRO {aapgb}  {"AAPG Bull."}				  
MACRO {aapge}  {"AAPG Explorer"}			  
MACRO {ag}     {"Advances Geophys."}			   
MACRO {baseg}  {"Bull., Austral. Soc. Expl. Geophys."}	   
MACRO {ssa}    {"Bull., Seis. Soc. Am."}		   
MACRO {eg}     {"Expl. Geophys."}			  
MACRO {fb}     {"First Break"}				   
MACRO {gb}     {"Geobyte"}				   
MACRO {gj}     {"Geol. J."}				   
MACRO {geol}   {"Geology"}				   
MACRO {gjras}  {"Geophys. J.Roy. Astr. Soc."}		  
MACRO {gp}     {"Geophys. Prosp."}			  
MACRO {grb}    {"Geophys. Res. Bull."}			  
MACRO {grl}    {"Geophys. Res. Lett."}			   
MACRO {gs}     {"Geophys. Surv."}			   
MACRO {geop}   {"Geophysics"}				   
MACRO {ge}     {"Geotherm. Energy"}			   
MACRO {geoth}  {"Geothermics"}				   
MACRO {geot}   {"Geotimes"}				   
MACRO {gw}     {"Groundwater"}				  
MACRO {ieeeoe} {"IEEE, J. Oceanic Eng."}		   
MACRO {ieeegrs}{"IEEE Trans. Geosc. Remote Sensing"}	   
MACRO {jasa}   {"J. Acoust. Soc. Am."}			   
MACRO {jap}    {"J. Appl. Phys."}			   
MACRO {jcpt}   {"J. Can. Petr. Tech."}			   
MACRO {jgs}    {"J. Geol. Soc."}			   
MACRO {jg}     {"J. Geophysics"}			  
MACRO {jgr}    {"J. Geophys. Res."}			   
MACRO {me}     {"Mining Eng."}				  
MACRO {os}     {"Offshore"}				   
MACRO {og}     {"Oil and Gas J."}			   
MACRO {pepi}   {"Phys. Earth Plan. Int."}		   
MACRO {pieee}  {"Proc. IEEE"}				   
MACRO {rsl}    {"Proc., Roy. Soc. London, Ser. A"} 	   
MACRO {pag}    {"Pure Appl. Geophysics"}		   
MACRO {rs}     {"Radio Sci."}				   
MACRO {ifp}    {"Rev. Inst. Fran. Petr."}		   
MACRO {rmre}   {"Rock Mech. Rock Eng."}			   
MACRO {tle}    {"The Leading Edge"}			   
MACRO {siamjam}{"SIAM J. Appl. Math."}			   
MACRO {wo}     {"World Oil"}				   
MACRO {sep}    {"Stanford Exploration Project Report"}

READ

FUNCTION {sortify}
{ purify$
  "l" change.case$
}

INTEGERS { len }

FUNCTION {chop.word}
{ 's :=
  'len :=
  s #1 len substring$ =
    { s len #1 + global.max$ substring$ }
    's
  if$
}

INTEGERS { et.al.char.used }

FUNCTION {initialize.et.al.char.used}
{ #0 'et.al.char.used :=
}

EXECUTE {initialize.et.al.char.used}

FUNCTION {format.lab.names}
{ 's :=
  s num.names$ 'numnames :=

  numnames #1 =
    { s #1 "{vv }{ll}" format.name$ }
    { numnames #2 =
        { s #1 "{vv }{ll }and " format.name$ s #2 "{vv }{ll}" format.name$ *
        }
        { s #1 "{vv }{ll }\bgroup et al.\egroup " format.name$ }
      if$
    }
  if$

}

FUNCTION {author.key.label}
{ author empty$
    { key empty$

	{ cite$ #1 #3 substring$ }

	{ key }
      if$
    }
    { author format.lab.names }
  if$
}

FUNCTION {author.editor.key.label}
{ author empty$
    { editor empty$
	{ key empty$

	    { cite$ #1 #3 substring$ }

	    { key }
	  if$
	}
	{ editor format.lab.names }
      if$
    }
    { author format.lab.names }
  if$
}

FUNCTION {author.key.organization.label}
{ author empty$
    { key empty$
	{ organization empty$

	    { cite$ #1 #3 substring$ }

	    { "The " #4 organization chop.word #3 text.prefix$ }
	  if$
	}
	{ key }
      if$
    }
    { author format.lab.names }
  if$
}

FUNCTION {editor.key.organization.label}
{ editor empty$
    { key empty$
	{ organization empty$

	    { cite$ #1 #3 substring$ }

	    { "The " #4 organization chop.word #3 text.prefix$ }
	  if$
	}
	{ key }
      if$
    }
    { editor format.lab.names }
  if$
}

FUNCTION {calc.label}
{ type$ "book" =
  type$ "inbook" =
  or
    'author.editor.key.label
    { type$ "proceedings" =
	'editor.key.organization.label
	{ type$ "manual" =
	    'author.key.organization.label
	    'author.key.label
	  if$
	}
      if$
    }
  if$
  duplicate$

  "\protect\citeauthoryear{" swap$ * "}{" *
  year field.or.null purify$ *  % CHANGED - pfps - 15 Feb 1989
  'label :=
  year field.or.null purify$ *

  sortify 'sort.label :=
}

FUNCTION {sort.format.names}
{ 's :=
  #1 'nameptr :=
  ""
  s num.names$ 'numnames :=
  numnames 'namesleft :=
    { namesleft #0 > }
    { nameptr #1 >
	{ "   " * }
	'skip$
      if$

      s nameptr "{vv{ } }{ll{ }}{  ff{ }}{  jj{ }}" format.name$ 't :=

      nameptr numnames = t "others" = and
	{ "et al" * }
	{ t sortify * }
      if$
      nameptr #1 + 'nameptr :=
      namesleft #1 - 'namesleft :=
    }
  while$
}

FUNCTION {sort.format.title}
{ 't :=
  "A " #2
    "An " #3
      "The " #4 t chop.word
    chop.word
  chop.word
  sortify
  #1 global.max$ substring$
}

FUNCTION {author.sort}
{ author empty$
    { key empty$
	{ "to sort, need author or key in " cite$ * warning$
	  ""
	}
	{ key sortify }
      if$
    }
    { author sort.format.names }
  if$
}

FUNCTION {author.editor.sort}
{ author empty$
    { editor empty$
	{ key empty$
	    { "to sort, need author, editor, or key in " cite$ * warning$
	      ""
	    }
	    { key sortify }
	  if$
	}
	{ editor sort.format.names }
      if$
    }
    { author sort.format.names }
  if$
}

FUNCTION {author.organization.sort}
{ author empty$
    { organization empty$
	{ key empty$
	    { "to sort, need author, organization, or key in " cite$ * warning$
	      ""
	    }
	    { key sortify }
	  if$
	}
	{ "The " #4 organization chop.word sortify }
      if$
    }
    { author sort.format.names }
  if$
}

FUNCTION {editor.organization.sort}
{ editor empty$
    { organization empty$
	{ key empty$
	    { "to sort, need editor, organization, or key in " cite$ * warning$
	      ""
	    }
	    { key sortify }
	  if$
	}
	{ "The " #4 organization chop.word sortify }
      if$
    }
    { editor sort.format.names }
  if$
}

FUNCTION {presort}

{ calc.label
  sort.label
  "    "
  *
  type$ "book" =

  type$ "inbook" =
  or
    'author.editor.sort
    { type$ "proceedings" =
	'editor.organization.sort
	{ type$ "manual" =
	    'author.organization.sort
	    'author.sort
	  if$
	}
      if$
    }
  if$

  *

  "    "
  *
  year field.or.null sortify
  *
  "    "
  *
  title field.or.null
  sort.format.title
  *
  #1 entry.max$ substring$
  'sort.key$ :=
}

ITERATE {presort}

SORT

STRINGS { longest.label last.sort.label next.extra }

INTEGERS { longest.label.width last.extra.num }

FUNCTION {initialize.longest.label}
{ "" 'longest.label :=
  #0 int.to.chr$ 'last.sort.label :=
  "" 'next.extra :=
  #0 'longest.label.width :=
  #0 'last.extra.num :=
}

FUNCTION {forward.pass}
{ last.sort.label sort.label =
    { last.extra.num #1 + 'last.extra.num :=
      last.extra.num int.to.chr$ 'extra.label :=
    }
    { "a" chr.to.int$ 'last.extra.num :=
      "" 'extra.label :=
      sort.label 'last.sort.label :=
    }
  if$
}

FUNCTION {reverse.pass}
{ next.extra "b" =
    { "a" 'extra.label := }
    'skip$
  if$
  label extra.label * "}" * 'label :=   % CHANGED - pfps 15 Feb 1989
  label width$ longest.label.width >
    { label 'longest.label :=
      label width$ 'longest.label.width :=
    }
    'skip$
  if$
  extra.label 'next.extra :=
}

EXECUTE {initialize.longest.label}

ITERATE {forward.pass}

REVERSE {reverse.pass}

FUNCTION {begin.bib}

{ et.al.char.used
    { "\newcommand{\etalchar}[1]{$^{#1}$}" write$ newline$ }
    'skip$
  if$
  preamble$ empty$

    'skip$
    { preamble$ write$ newline$ }
  if$

  "\begin{thebibliography}{}" write$ newline$

}

EXECUTE {begin.bib}

EXECUTE {init.state.consts}

ITERATE {call.type$}

FUNCTION {end.bib}
{ newline$
  "\end{thebibliography}" write$ newline$
}

EXECUTE {end.bib}
