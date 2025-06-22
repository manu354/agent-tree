# Implement Sequential Chain Handler

## Type
simple

## Problem
Create a handler that processes nodes sequentially when they have dependencies. Each node must wait for its dependencies to complete before executing. Pass outputs from completed nodes to dependent nodes through context.

## Possible Solution
Implement a loop that processes nodes in dependency order. Check completion status of dependencies before starting a node. Pass results through the context system. Handle failures by stopping the chain or implementing retry logic.

## Notes
This is simpler than parallel execution but requires careful state management. Must integrate with existing context propagation system to pass information between sequential steps. Consider how to handle partial failures.