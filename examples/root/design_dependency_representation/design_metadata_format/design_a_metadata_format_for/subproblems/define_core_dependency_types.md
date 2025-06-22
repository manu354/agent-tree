# Define Core Dependency Types

## Type
simple

## Problem
Identify and define the fundamental dependency relationships between tasks in agent-tree execution. Must cover parallel execution (multiple tasks run simultaneously), sequential execution (tasks run one after another), and blocking dependencies (task B waits for task A). Need clear semantics for each type.

## Possible Solution
Create a taxonomy with three core types: PARALLEL (tasks can execute concurrently), SEQUENTIAL (tasks must execute in order), and DEPENDS_ON (explicit blocking dependency). Each type should have clear execution rules and constraints. Include examples showing how these combine for complex workflows.

## Notes
Core dependency types form the foundation for the metadata format. Must consider edge cases like circular dependencies, optional dependencies, and conditional execution. Should align with existing agent-tree execution patterns while enabling new capabilities for expressing complex task relationships.