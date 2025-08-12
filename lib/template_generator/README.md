# Base template generation

This script downloads HTML, CSS, and JS from the EC site, processes them and
saves them locally.

It does this in order to set up a base template for our pages to add content to.

We use a 'donor page' that's in the same section as our pages. We then user
BeautifulSoup to parse out the container that we will add content to and
replace the HTML there with `jinja2` block tags.

We do this in order to make maintaining upstream changes form the EC easier.

The EC (or their agency) make ad-hoc changes to the template and design. The
alternative to this script is for us to manually implement the exact same
changes bit by bit. This would be a painful task, so some automation allows us
to pull in all live changes quickly.

We do some things to CSS paths and move some other blocks of code around to
make local serving easier. 

This is done for English and Welsh language versions of the donor pages.
