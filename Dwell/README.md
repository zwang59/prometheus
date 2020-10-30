# Dwell-Analytics

Note: While pushing changes, Kindly make sure that no-one pushes the changes at the same time simultaneously for the same file.

# Pipeline - Approach as discussed (UPDATED 10/23/2020 - Ajithesh)

We are going to follow layer-based pipline in developing the module.

Base <- Layer 1 <- Layer 2 .... <- Layer n

1. Base is the clustering algorithm.
2. Each Layer contributes towards a specific analysis.
3. Combining the analysis from the layers into the Base gives marked results.

# Example

Layer 1 - Provides insights on user's mode of transport through analysis.
Combining analysis from Layer 1 into the Base marks the user with mode of transport (USER-Car).
USER-Car has now more preference/ target experience than regular user in the cluster.
