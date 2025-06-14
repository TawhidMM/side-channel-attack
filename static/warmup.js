/* Find the cache line size by running `getconf -a | grep CACHE` */
const LINESIZE = 64;

function readNlines(n) {
  /*
   * Implement this function to read n cache lines.
   * 1. Allocate a buffer of size n * LINESIZE.
   * 2. Read each cache line (read the buffer in steps of LINESIZE) 10 times.
   * 3. Collect total time taken in an array using `performance.now()`.
   * 4. Return the median of the time taken in milliseconds.
   */

    const buffer = new Uint8Array(n * LINESIZE);
    const timings = [];

    for (let repeat = 0; repeat < 10; repeat++) {
        const start = performance.now();

        for (let i = 0; i < n * LINESIZE; i += LINESIZE) {
          let temp = buffer[i];
        }

        const end = performance.now(); // Step 3: end time
        timings.push(end - start);
    }

    return median(timings);
}


function median(arr) {
    arr.sort((a, b) => a - b);
    const mid = Math.floor(arr.length / 2);

    if (arr.length % 2 === 0) {
        return (arr[mid - 1] + arr[mid]) / 2;
    } else {
        return arr[mid];
    }
}


self.addEventListener("message", function (e) {
  if (e.data === "start") {
    const results = {};

    /* Call the readNlines function for n = 1, 10, ... 10,000,000 and store the result */
    for (let n = 1; n <= 10_000_000; n *= 10) {
      results[n] = readNlines(n);
    }

    self.postMessage(results);
  }
});
