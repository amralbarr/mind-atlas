# Big O Notation / Algorithmic Complexity

Big O notation describes how an algorithm's running time (or memory use) grows as the size of its input grows — not the exact number of operations or seconds, but the *shape* of the growth curve. It's the standard vocabulary for reasoning about whether an approach will still be fast enough at 10x or 1000x the current data size, independent of any specific machine's speed.

## Why "Growth Rate," Not "Exact Time"

Two algorithms measured on the same input might take different actual milliseconds depending on hardware, language, and implementation details — but Big O deliberately ignores all of that to answer a more durable question: as `n` (the input size) grows, does the work grow linearly? Quadratically? Not at all? That answer doesn't change when you swap machines, but the actual millisecond timing does.

## The Common Complexity Classes, From Best to Worst

| Notation | Name | Growth as `n` doubles |
|---|---|---|
| `O(1)` | Constant | Stays exactly the same |
| `O(log n)` | Logarithmic | Barely increases |
| `O(n)` | Linear | Doubles |
| `O(n log n)` | Linearithmic | Slightly more than doubles |
| `O(n²)` | Quadratic | Quadruples |
| `O(2ⁿ)` | Exponential | Squares (catastrophic for large `n`) |
| `O(n!)` | Factorial | Effectively unusable beyond tiny `n` |

```text
n = 1,000:
O(1)        → 1 operation
O(log n)    → ~10 operations
O(n)        → 1,000 operations
O(n log n)  → ~10,000 operations
O(n²)       → 1,000,000 operations
O(2ⁿ)       → astronomically large — this is why exponential algorithms
              are only viable for very small n
```

## Concrete Examples

```javascript
// O(1) — constant: array index access doesn't depend on array size
function first(arr) { return arr[0]; }

// O(n) — linear: must look at every element in the worst case
function contains(arr, target) {
  for (const item of arr) {
    if (item === target) return true;
  }
  return false;
}

// O(n²) — quadratic: nested loop over the same input
function hasDuplicate(arr) {
  for (let i = 0; i < arr.length; i++) {
    for (let j = i + 1; j < arr.length; j++) {
      if (arr[i] === arr[j]) return true;
    }
  }
  return false;
}

// O(log n) — logarithmic: binary search halves the search space each step
function binarySearch(sortedArr, target) {
  let lo = 0, hi = sortedArr.length - 1;
  while (lo <= hi) {
    const mid = Math.floor((lo + hi) / 2);
    if (sortedArr[mid] === target) return mid;
    if (sortedArr[mid] < target) lo = mid + 1;
    else hi = mid - 1;
  }
  return -1;
}
```

The `hasDuplicate` example is the classic "accidentally quadratic" bug pattern — a nested loop over the same collection, often introduced innocently (looping to enrich each item with a lookup from the same list) and invisible at small `n`, but the reason a feature that "worked fine in testing" becomes unusably slow once real data volume arrives.

## Worst Case, Average Case, Best Case

Big O most commonly refers to **worst-case** complexity — the upper bound on how bad it can get — but the same algorithm can have different complexities depending on which case is being discussed:

| Case | Example: searching an unsorted array for a target |
|---|---|
| **Best case** | `O(1)` — the target happens to be the first element checked |
| **Average case** | `O(n)` — on average, about half the array is checked |
| **Worst case** | `O(n)` — the target is last, or absent entirely |

Worst case is the default assumption in most discussions (including interviews) because it's the guarantee that actually matters for reliability — an algorithm that's usually fast but occasionally catastrophic is a real production risk.

## Space Complexity

Big O also describes memory usage, not just time — the same notation, applied to how much extra memory an algorithm needs relative to input size:

```javascript
// O(1) space — no extra memory proportional to n
function sum(arr) {
  let total = 0;
  for (const x of arr) total += x;
  return total;
}

// O(n) space — a new array/set proportional to input size
function unique(arr) {
  return [...new Set(arr)];
}
```

Time and space complexity are often in tension — a common technique (memoization/caching intermediate results) deliberately trades additional memory (`O(n)` space) for a large reduction in time (turning an exponential recursive algorithm into a linear one), which is exactly the trade-off behind dynamic programming.

## Why This Matters Beyond Interviews

Big O reasoning shows up constantly in real production decisions, not just algorithm-puzzle interviews:

- **[Database indexing](../../databases/relational/indexing.md)** — the entire value proposition of an index is turning an `O(n)` full table scan into an `O(log n)` B-tree lookup.
- **The [N+1 query problem](../../backend/data/n-plus-1-problem.md)** — `1 + N` queries is `O(n)` round-trips where a single joined query would be `O(1)` round-trips, regardless of how fast any individual query runs.
- **Choosing a data structure** — a hash map gives `O(1)` average-case lookup versus an array's `O(n)` linear scan; this single choice alone can be the difference between a feature that scales and one that silently degrades as data grows.
- **API [pagination](../../backend/api/pagination.md)** — offset-based [pagination](../../backend/api/pagination.md) degrades because `OFFSET` itself does `O(offset)` work to skip rows, which is exactly why cursor-based [pagination](../../backend/api/pagination.md) (`O(log n)` via an index seek) scales better at depth.

## Common Questions

**Is `O(n log n)` always better than `O(n²)` in practice?**
> Asymptotically yes, but for small `n` an `O(n²)` algorithm with very little per-iteration overhead can outperform an `O(n log n)` algorithm with heavier constant costs — this is why some sorting implementations switch strategies (e.g. insertion sort for small sub-arrays) below a size threshold. Big O describes the growth trend, not a guarantee about any specific, small input size.

**Does `O(1)` mean an operation is always literally fast?**
> No — it means the time doesn't grow with input size, not that the constant time itself is small. An `O(1)` operation that does a very expensive fixed amount of work (a slow network call, say) can still be slower in absolute terms than a small, fast `O(n)` loop over a tiny array.

**Why do interviewers care so much about this?**
> Because it's a fast, language-agnostic proxy for whether a candidate's solution will hold up as real data grows, and for whether they instinctively notice a hidden nested loop or an avoidable full scan — exactly the kind of thing that's invisible in a small test case and expensive in production.

## Related

- [Interview 02 — Coding Topics](../../../interview/interview-02/topics/) — every topic's Complexity section links back here, with worked practice/solution code
- [Database Indexing](../../databases/relational/indexing.md)
- [The N+1 Query Problem](../../backend/data/n-plus-1-problem.md)
- [Pagination](../../backend/api/pagination.md)
