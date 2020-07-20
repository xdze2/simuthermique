## Notes & documentations

[⮕ lien vers la doc. en ligne](https://xdze2.github.io/simuthermique/)


## Static website with math equation support

* use Github static site (in `/docs` folder)
* convert markdown file to html using [pandoc](https://pandoc.org/MANUAL.html)

simplest solution to display **math equation** online  
with Katex


* use pandoc's config file `pandoc.yaml` (need last version)

        $ pandoc --defaults=pandoc.yaml

* and use simple **css style** (not the full pandoc [template system](https://github.com/jgm/pandoc-templates))
  * https://benjam.info/panam/
  * https://jez.io/tufte-pandoc-css/
  * https://otsaloma.io/pub/markdown-css-github.html

see also [Building a Website using Pandoc, Markdown, and Static HTML](http://wstyler.ucsd.edu/posts/pandoc_website.html)

* script to automate and create page menu

## Other tools

- https://www.sphinx-doc.org
- https://www.mkdocs.org/
- https://pdoc3.github.io/pdoc/
  * python docstrings to markdown or html