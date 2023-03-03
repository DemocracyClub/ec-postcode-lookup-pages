import sys

sys.path.insert(0, "lib")

from response_builder.v1.builders import LocalBallotBuilder

SINGLE_LOCAL_BALLOT = LocalBallotBuilder().with_candidates(1, verified=False)

print(SINGLE_LOCAL_BALLOT)
print(SINGLE_LOCAL_BALLOT.build().json(indent=4))
