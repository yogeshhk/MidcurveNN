%
% 8/4/'90
%Ciaran McHale
%Department of Computer Science, Trinity College, Dublin 2, Ireland.
%Telephone: +353-1-772941 ext 1538    FAX: +353-1-772204   Telex: 93782 TCD EI
%email: cjmchale@cs.tcd.ie       or      cjmchale%cs.tcd.ie@cunyvm.cuny.edu
% Hacked together by Ciaran McHale (cjmchale@cs.tcd.ie) to translate
% BibTeX bibliographies into refer format
% Based on a bib style file by Kannan Varadhan
%


ENTRY
  {                                     % entry fields
        abstract                % non standard
    address
        annote                  % non standard
    author
    booktitle
    chapter
    edition
    editor
    howpublished
    institution
    journal
    key
        keywords                % non standard
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
  }
  {}                                    % no integer entry variables
  { label extra.label sort.label }      % label entry variables


STRINGS { s t a.name }


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

INTEGERS { nameptr namesleft numnames }

FUNCTION {handle.names}
{ 't :=         % type e.g. "A" for authors, "E" for editors
  's :=         % the string containing the names
  #1 'nameptr :=
  s num.names$ 'numnames :=
  numnames 'namesleft :=
    { namesleft #0 > }

    { s nameptr "{ff~}{vv~}{ll}{, jj}" format.name$ 'a.name :=

      a.name "others" =
        'skip$  % don't print out "%A others"
        { "%" t * " " * a.name * write$ newline$ }
      if$
      nameptr #1 + 'nameptr :=
      namesleft #1 - 'namesleft :=
    }
  while$
}

FUNCTION {handle.maybe.empty}
{
  't :=
  duplicate$
  empty$
    'pop$
    { "%" t * " " * swap$ * write$ newline$ }
  if$
}

FUNCTION {translate}
{
  newline$      % get a blank line between each entry

  title "T" handle.maybe.empty
  booktitle "B" handle.maybe.empty

  % there may be multiple authors so handle it differently
  author empty$
    { " empty author in " cite$ * warning$ }
    { author "A" handle.names }
  if$
  editor "E" handle.maybe.empty
  journal "J" handle.maybe.empty
  keywords "K" handle.maybe.empty
  cite$ "L" handle.maybe.empty
  volume "V" handle.maybe.empty
  abstract "X" handle.maybe.empty

  % The date, if present may be just the year or both the month and year
  % or might even be just the month
  month empty$ year empty$ and
    'skip$      % no date of publication so nothing to do
    {
      month empty$      % I'm using the if statement because I'm not
        { "" }          % sure that--- month " " year * --- would work.
        { month " " * } % (The manual doesn't mention anything about
      if$               % this so I'm playing safe)
      year empty$
        { "" }
        { year }
      if$
      *
      "D" handle.maybe.empty
    }
  if$
  pages "P" handle.maybe.empty
  note "O" handle.maybe.empty
  number "N" handle.maybe.empty
  series "S" handle.maybe.empty
  annote "Y" handle.maybe.empty
  address "C" handle.maybe.empty

}


FUNCTION {article} { translate }
FUNCTION {book} { translate }
FUNCTION {booklet} { translate }
FUNCTION {inbook} { translate }
FUNCTION {incollection} { translate }
FUNCTION {inproceedings} { translate }
FUNCTION {manual} { translate }
FUNCTION {mastersthesis} { translate }
FUNCTION {misc} { translate }
FUNCTION {phdthesis} { translate }
FUNCTION {proceedings} { translate }
FUNCTION {techreport} { translate }
FUNCTION {unpublished} { translate }
FUNCTION {default.type} { translate }


READ

ITERATE {call.type$}




