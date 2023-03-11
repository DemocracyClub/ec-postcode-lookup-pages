import sys
from pathlib import Path

# This is needed to make imports work on AWS Lambda.
# When running there, the `postcode_lookup` directory is the root
# meaning that we can't use that in our imports.
# When running locally, we have to add the `postcode_lookup` directory
# to the path
source_route = Path(__file__).parent.absolute()
sys.path.append(str(source_route))
